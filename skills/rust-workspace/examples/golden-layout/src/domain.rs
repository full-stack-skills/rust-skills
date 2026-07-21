#[derive(Debug, Eq, PartialEq)]
pub struct Greeting(String);

impl Greeting {
    pub(crate) fn new(name: impl Into<String>) -> Self {
        Self(format!("Hello, {}!", name.into()))
    }

    pub fn message(&self) -> &str {
        &self.0
    }
}
