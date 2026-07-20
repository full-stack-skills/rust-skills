mod domain;

pub use domain::Greeting;

pub fn greet(name: impl Into<String>) -> Greeting {
    Greeting::new(name)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exposes_a_small_public_api() {
        assert_eq!(greet("Ferris").message(), "Hello, Ferris!");
    }
}
