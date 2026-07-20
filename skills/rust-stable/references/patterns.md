# Rust Patterns & Idioms

## Newtype Pattern

```rust
struct Email(String);                   // wrapper type
impl Email {
    fn validate(&self) -> bool { self.0.contains('@') }
}
```

## Builder Pattern

```rust
struct RequestBuilder {
    url: String,
    method: String,
    body: Option<String>,
}

impl RequestBuilder {
    fn new(url: &str) -> Self {
        Self { url: url.into(), method: "GET".into(), body: None }
    }
    fn method(mut self, method: &str) -> Self {
        self.method = method.into(); self
    }
    fn body(mut self, body: &str) -> Self {
        self.body = Some(body.into()); self
    }
    fn build(self) -> Request {
        Request { url: self.url, method: self.method, body: self.body }
    }
}
```

## RAII Guard

```rust
struct TimerGuard<'a>(&'a str, std::time::Instant);
impl<'a> Drop for TimerGuard<'a> {
    fn drop(&mut self) {
        println!("{} took {:?}", self.0, self.1.elapsed());
    }
}
fn timed(name: &str) -> TimerGuard<'_> {
    TimerGuard(name, std::time::Instant::now())
}
```

## Typestate Pattern

```rust
struct Open;
struct Closed;
struct Door<State> { _state: std::marker::PhantomData<State> }
impl Door<Closed> { fn open(self) -> Door<Open> { Door { _state: PhantomData } } }
impl Door<Open> { fn close(self) -> Door<Closed> { Door { _state: PhantomData } } }
```
