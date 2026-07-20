#[derive(Debug, Eq, PartialEq)]
pub struct Response {
    pub status: u16,
    pub body: String,
}

pub fn greet(name: Option<&str>) -> Response {
    match name.map(str::trim).filter(|value| !value.is_empty()) {
        Some(name) => Response {
            status: 200,
            body: format!("Hello, {name}!"),
        },
        None => Response {
            status: 400,
            body: "name is required".to_owned(),
        },
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn validates_input_at_the_boundary() {
        assert_eq!(greet(None).status, 400);
        assert_eq!(greet(Some("Ferris")).status, 200);
    }
}
