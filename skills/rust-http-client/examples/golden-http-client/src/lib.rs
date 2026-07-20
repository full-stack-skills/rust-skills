use std::io::Read;
use std::time::Duration;

#[derive(Debug)]
pub enum FetchError {
    Transport(reqwest::Error),
    TooLarge,
    Io(std::io::Error),
}

impl From<reqwest::Error> for FetchError {
    fn from(error: reqwest::Error) -> Self {
        Self::Transport(error)
    }
}

impl From<std::io::Error> for FetchError {
    fn from(error: std::io::Error) -> Self {
        Self::Io(error)
    }
}

pub struct HttpClient {
    inner: reqwest::blocking::Client,
    max_body_bytes: u64,
}

impl HttpClient {
    pub fn new(max_body_bytes: u64) -> Result<Self, reqwest::Error> {
        let inner = reqwest::blocking::Client::builder()
            .connect_timeout(Duration::from_secs(2))
            .timeout(Duration::from_secs(5))
            .redirect(reqwest::redirect::Policy::none())
            .no_proxy()
            .build()?;
        Ok(Self {
            inner,
            max_body_bytes,
        })
    }

    pub fn get_text(&self, url: &str) -> Result<String, FetchError> {
        let mut response = self.inner.get(url).send()?.error_for_status()?;
        if response
            .content_length()
            .is_some_and(|length| length > self.max_body_bytes)
        {
            return Err(FetchError::TooLarge);
        }

        let mut bytes = Vec::new();
        response
            .by_ref()
            .take(self.max_body_bytes + 1)
            .read_to_end(&mut bytes)?;
        if bytes.len() as u64 > self.max_body_bytes {
            return Err(FetchError::TooLarge);
        }
        String::from_utf8(bytes).map_err(|error| {
            FetchError::Io(std::io::Error::new(std::io::ErrorKind::InvalidData, error))
        })
    }
}

#[cfg(test)]
mod tests {
    use std::io::{Read as _, Write as _};
    use std::net::TcpListener;
    use std::thread;

    use super::*;

    fn serve_once(body: &'static str) -> (String, thread::JoinHandle<()>) {
        let listener = TcpListener::bind("127.0.0.1:0").expect("bind local server");
        let address = listener.local_addr().expect("read local address");
        let handle = thread::spawn(move || {
            let (mut stream, _) = listener.accept().expect("accept request");
            let mut request = [0_u8; 1024];
            let _ = stream.read(&mut request).expect("read request");
            write!(
                stream,
                "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
                body.len(),
                body
            )
            .expect("write response");
        });
        (format!("http://{address}/value"), handle)
    }

    #[test]
    fn reads_a_bounded_response_from_a_real_local_server() {
        let (url, server) = serve_once("hello");
        let client = HttpClient::new(16).expect("build client");
        assert_eq!(client.get_text(&url).expect("fetch body"), "hello");
        server.join().expect("join server");
    }

    #[test]
    fn rejects_an_advertised_body_over_the_limit() {
        let (url, server) = serve_once("body-too-large");
        let client = HttpClient::new(4).expect("build client");
        assert!(matches!(client.get_text(&url), Err(FetchError::TooLarge)));
        server.join().expect("join server");
    }
}
