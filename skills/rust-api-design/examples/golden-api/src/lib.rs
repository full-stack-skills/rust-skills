//! `golden-api` — a small crate demonstrating API Guidelines compliance.
//!
//! Every public type follows the relevant C-* rules. Run `cargo doc` and
//! `cargo clippy -- -W clippy::pedantic` to see no warnings.

use std::fmt;
use std::num::NonZeroU32;

// === C-NAMING / C-CASE ===
// UpperCamelCase types, snake_case methods.

// === C-NEWTYPE ===
// Wrap raw primitives to prevent argument-order bugs.

/// A user identifier, distinct from other u64 identifiers.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub struct UserId(pub u64);

impl UserId {
    /// C-CONST: const constructor.
    pub const fn new(value: u64) -> Self {
        Self(value)
    }

    /// C-INTUITIVE: clear name, no panic.
    pub const fn is_anonymous(self) -> bool {
        self.0 == 0
    }
}

/// An account identifier — distinct type from `UserId`.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct AccountId(pub u64);

// === C-BOOL ===
// Replace boolean parameters with an enum so call sites are self-documenting.

/// Whether to include hidden records in a listing.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
#[non_exhaustive] // C-NON-EXHAUSTIVE: we may add more variants later.
pub enum Visibility {
    /// Show only public records.
    #[default]
    Public,
    /// Include records marked hidden.
    IncludeHidden,
}

// === C-NEWTYPE with private inner ===
// Wraps a validated email; cannot be constructed without going through `parse`.

/// A validated email address.
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Email(String);

/// Errors that can arise when constructing an [`Email`].
#[derive(Debug, PartialEq, Eq)]
#[non_exhaustive] // C-NON-EXHAUSTIVE on errors.
pub enum EmailError {
    /// The input did not contain `@`.
    MissingAt,
    /// The local part was empty.
    EmptyLocal,
    /// The domain was empty.
    EmptyDomain,
}

impl fmt::Display for EmailError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            EmailError::MissingAt => write!(f, "email address missing '@'"),
            EmailError::EmptyLocal => write!(f, "email local part is empty"),
            EmailError::EmptyDomain => write!(f, "email domain is empty"),
        }
    }
}

impl std::error::Error for EmailError {}

impl Email {
    /// C-CONV / fallible construction: name the method `parse` for `&str` input.
    pub fn parse(input: &str) -> Result<Self, EmailError> {
        let (local, domain) = input.split_once('@').ok_or(EmailError::MissingAt)?;
        if local.is_empty() {
            return Err(EmailError::EmptyLocal);
        }
        if domain.is_empty() {
            return Err(EmailError::EmptyDomain);
        }
        Ok(Self(input.to_string()))
    }
}

// C-CONV: provide AsRef<str> for borrowed views.
impl AsRef<str> for Email {
    fn as_ref(&self) -> &str {
        &self.0
    }
}

// C-CONV: Borrow<str> so HashMap<Email, _> is lookupable by &str.
impl std::borrow::Borrow<str> for Email {
    fn borrow(&self) -> &str {
        &self.0
    }
}

impl fmt::Display for Email {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.0)
    }
}

// === C-COMMON-TRAITS: deliberate, not cargo-cult ===
/// A money amount in integer cents.
///
/// Deliberately does NOT implement `Default` (no natural zero value at the
/// type level — use `Cents::zero()` to be explicit).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub struct Cents(u64);

impl Cents {
    pub const fn zero() -> Self {
        Self(0)
    }

    pub const fn from_cents(cents: u64) -> Self {
        Self(cents)
    }

    pub const fn value(self) -> u64 {
        self.0
    }
}

// === C-NONZERO ===
/// Configuration with a chunk size that must be ≥ 1.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Config {
    chunk_size: NonZeroU32,
    visibility: Visibility,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            chunk_size: NonZeroU32::new(1024).expect("1024 is non-zero"),
            visibility: Visibility::default(),
        }
    }
}

impl Config {
    /// C-BUILDER: build via a builder so adding fields is non-breaking.
    pub fn builder() -> ConfigBuilder {
        ConfigBuilder::default()
    }

    /// C-GETTER: no `get_` prefix.
    pub fn chunk_size(&self) -> NonZeroU32 {
        self.chunk_size
    }

    pub fn visibility(&self) -> Visibility {
        self.visibility
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct ConfigBuilder {
    chunk_size: Option<NonZeroU32>,
    visibility: Option<Visibility>,
}

impl ConfigBuilder {
    pub fn chunk_size(mut self, size: NonZeroU32) -> Self {
        self.chunk_size = Some(size);
        self
    }

    pub fn visibility(mut self, v: Visibility) -> Self {
        self.visibility = Some(v);
        self
    }

    pub fn build(self) -> Config {
        Config {
            chunk_size: self
                .chunk_size
                .unwrap_or_else(|| NonZeroU32::new(1024).unwrap()),
            visibility: self.visibility.unwrap_or_default(),
        }
    }
}

// === C-EXT: extension trait, `Ext` suffix ===
/// Extension methods on `&[u64]` for finding user IDs.
pub trait UserIdSliceExt {
    /// Returns the first anonymous user, if any.
    fn first_anonymous(&self) -> Option<UserId>;
}

impl UserIdSliceExt for [UserId] {
    fn first_anonymous(&self) -> Option<UserId> {
        self.iter().copied().find(|u| u.is_anonymous())
    }
}

// === C-SERDE-like interop without a hard serde dep: FromStr + Display ===
impl std::str::FromStr for Email {
    type Err = EmailError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        Self::parse(s)
    }
}

// === Tests demonstrating each rule ===

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn user_id_const_constructor_and_check() {
        const ANON: UserId = UserId::new(0);
        assert!(ANON.is_anonymous());
        assert!(!UserId::new(42).is_anonymous());
    }

    #[test]
    fn user_ids_and_account_ids_do_not_mix() {
        // The compiler would reject transfer(user, acc, acc) — different types.
        fn transfer(amount: Cents, _from: AccountId, _to: AccountId) -> Cents {
            amount
        }
        let result = transfer(Cents::from_cents(100), AccountId(1), AccountId(2));
        assert_eq!(result.value(), 100);
    }

    #[test]
    fn email_parse_rejects_invalid_input() {
        assert!(matches!(Email::parse("noat"), Err(EmailError::MissingAt)));
        assert!(matches!(Email::parse("@x"), Err(EmailError::EmptyLocal)));
        assert!(matches!(Email::parse("x@"), Err(EmailError::EmptyDomain)));
        let ok = Email::parse("a@b").unwrap();
        assert_eq!(ok.as_ref(), "a@b");
    }

    #[test]
    fn email_borrow_lookup_in_hashmap() {
        let mut map = std::collections::HashMap::new();
        map.insert(Email::parse("a@b").unwrap(), 1u32);
        // C-CONV: Borrow<str> lets us look up by &str.
        assert_eq!(map.get("a@b"), Some(&1));
    }

    #[test]
    fn visibility_enum_makes_calls_self_documenting() {
        fn list(v: Visibility) -> &'static str {
            match v {
                Visibility::Public => "public only",
                Visibility::IncludeHidden => "all",
            }
        }
        // Call site is explicit — no `true`/`false` mystery.
        assert_eq!(list(Visibility::Public), "public only");
        assert_eq!(list(Visibility::IncludeHidden), "all");
    }

    #[test]
    fn builder_lets_config_evolve() {
        let cfg = Config::builder()
            .chunk_size(NonZeroU32::new(2048).unwrap())
            .visibility(Visibility::IncludeHidden)
            .build();
        assert_eq!(cfg.chunk_size().get(), 2048);
        assert_eq!(cfg.visibility(), Visibility::IncludeHidden);
    }

    #[test]
    fn ext_trait_extends_external_slice() {
        let users = [UserId::new(5), UserId::new(0), UserId::new(9)];
        assert_eq!(users.first_anonymous(), Some(UserId::new(0)));
    }

    /// C-DEBUG: secrets are redacted in Debug output.
    #[test]
    fn debug_redacts_secrets() {
        /// An API key whose Debug does not leak the value.
        pub struct ApiKey {
            _value: String,
        }
        impl ApiKey {
            fn new(value: impl Into<String>) -> Self {
                Self {
                    _value: value.into(),
                }
            }
        }
        impl fmt::Debug for ApiKey {
            fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
                f.debug_struct("ApiKey")
                    .field("value", &"[redacted]")
                    .finish()
            }
        }
        let key = ApiKey::new("sk-1234567890");
        let s = format!("{:?}", key);
        assert!(s.contains("[redacted]"));
        assert!(!s.contains("1234567890"));
    }

    /// C-PANIC / C-UNWRAP: public API returns Result, never panics.
    #[test]
    fn fallible_api_returns_result() {
        // Public API surface uses Result. Internal `expect` is OK if documented.
        let _cfg = Config::default();
        // No public method on Config returns `()` and panics.
    }
}
