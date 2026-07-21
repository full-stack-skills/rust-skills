//! `golden-semver` — a crate that demonstrates a non-breaking minor version bump.
//!
//! Imagine version 0.1.0 had only `User::new`. Version 0.2.0 adds:
//! - `User::with_email` (additive)
//! - `Email` newtype (additive)
//! - `UserId` newtype (additive)
//!
//! All changes are additive, so this is a MINOR bump (0.1.0 → 0.2.0).

use std::fmt;
use std::str::FromStr;

/// User identifier, distinct from other `u64` IDs.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct UserId(pub u64);

/// Validated email address.
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Email(String);

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum EmailError {
    MissingAt,
    EmptyLocal,
    EmptyDomain,
}

impl fmt::Display for EmailError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            EmailError::MissingAt => write!(f, "missing '@'"),
            EmailError::EmptyLocal => write!(f, "empty local part"),
            EmailError::EmptyDomain => write!(f, "empty domain"),
        }
    }
}

impl std::error::Error for EmailError {}

impl Email {
    /// Parse an email from a string slice.
    ///
    /// # Errors
    ///
    /// Returns [`EmailError::MissingAt`] if `s` has no `@`,
    /// [`EmailError::EmptyLocal`] if the local part is empty, or
    /// [`EmailError::EmptyDomain`] if the domain is empty.
    pub fn parse(s: &str) -> Result<Self, EmailError> {
        let (local, domain) = s.split_once('@').ok_or(EmailError::MissingAt)?;
        if local.is_empty() {
            return Err(EmailError::EmptyLocal);
        }
        if domain.is_empty() {
            return Err(EmailError::EmptyDomain);
        }
        Ok(Self(s.to_string()))
    }
}

impl FromStr for Email {
    type Err = EmailError;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        Self::parse(s)
    }
}

impl AsRef<str> for Email {
    fn as_ref(&self) -> &str {
        &self.0
    }
}

impl fmt::Display for Email {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.0)
    }
}

/// A user record.
///
/// `id` is private so adding fields later is non-breaking.
/// The constructor pattern reserves room to evolve.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct User {
    id: UserId,
    email: Option<Email>,
}

impl User {
    /// Original constructor — preserved from 0.1.0 for backward compatibility.
    pub fn new(id: UserId) -> Self {
        Self { id, email: None }
    }

    /// New in 0.2.0 — additive constructor.
    pub fn with_email(id: UserId, email: Email) -> Self {
        Self {
            id,
            email: Some(email),
        }
    }

    pub fn id(&self) -> UserId {
        self.id
    }

    /// New in 0.2.0 — additive accessor.
    pub fn email(&self) -> Option<&Email> {
        self.email.as_ref()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn backward_compatible_construction() {
        // Original 0.1.0 API still works:
        let u = User::new(UserId(1));
        assert_eq!(u.id().0, 1);
        assert_eq!(u.email(), None);
    }

    #[test]
    fn new_in_0_2_0_additive_constructor() {
        let email = Email::parse("a@b.com").unwrap();
        let u = User::with_email(UserId(2), email);
        assert_eq!(u.email(), Some(&Email::parse("a@b.com").unwrap()));
    }

    #[test]
    fn email_parse_errors_match_documented_contract() {
        assert_eq!(Email::parse("noat").unwrap_err(), EmailError::MissingAt);
        assert_eq!(Email::parse("@x").unwrap_err(), EmailError::EmptyLocal);
        assert_eq!(Email::parse("x@").unwrap_err(), EmailError::EmptyDomain);
    }

    #[test]
    fn email_implements_fromstr_asref_display() {
        let e: Email = "a@b.com".parse().unwrap();
        assert_eq!(e.as_ref(), "a@b.com");
        assert_eq!(format!("{e}"), "a@b.com");
    }
}
