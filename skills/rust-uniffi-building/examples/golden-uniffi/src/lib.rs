use std::sync::Arc;

uniffi::setup_scaffolding!();

/// A value transferred to foreign-language callers.
#[derive(Clone, Debug, PartialEq, Eq, uniffi::Record)]
pub struct Greeting {
    pub message: String,
    pub language: Language,
}

/// Languages supported by the example greeter.
#[derive(Clone, Copy, Debug, PartialEq, Eq, uniffi::Enum)]
pub enum Language {
    English,
    Chinese,
}

/// A Rust-owned object exposed through a foreign reference.
#[derive(uniffi::Object)]
pub struct Greeter {
    prefix: String,
}

#[uniffi::export]
impl Greeter {
    #[uniffi::constructor]
    pub fn new(prefix: String) -> Arc<Self> {
        Arc::new(Self { prefix })
    }

    pub fn greet(&self, name: String, language: Language) -> Greeting {
        let punctuation = match language {
            Language::English => "!",
            Language::Chinese => "！",
        };
        Greeting {
            message: format!("{} {name}{punctuation}", self.prefix),
            language,
        }
    }
}

#[uniffi::export]
pub fn normalize_name(name: String) -> String {
    name.trim().to_owned()
}

#[cfg(test)]
mod tests {
    use super::{Greeter, Language, normalize_name};

    #[test]
    fn exports_value_and_object_semantics() {
        let greeter = Greeter::new("Hello".to_owned());
        let greeting = greeter.greet("UniFFI".to_owned(), Language::English);

        assert_eq!(greeting.message, "Hello UniFFI!");
        assert_eq!(greeting.language, Language::English);
    }

    #[test]
    fn keeps_boundary_normalization_explicit() {
        assert_eq!(normalize_name("  Rust  ".to_owned()), "Rust");
    }
}
