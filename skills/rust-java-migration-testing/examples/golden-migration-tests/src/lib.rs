//! Minimal migration-verification example.

use std::{error::Error, fmt, io};

/// Evidence produced for one compatibility contract.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum EvidenceLevel {
    /// A Rust test mirrors a Java test, but Java did not execute.
    Mirrored,
    /// A pinned Java exporter produced the expected fixture.
    GoldenDifferential,
    /// Pinned Java and Rust implementations executed the same case.
    LiveDifferential,
}

/// Public migration error with a redacted display and preserved source.
#[derive(Debug)]
pub struct MigrationError {
    source: io::Error,
}

impl MigrationError {
    /// Wrap an I/O error without exposing its message through `Display`.
    #[must_use]
    pub const fn new(source: io::Error) -> Self {
        Self { source }
    }
}

impl fmt::Display for MigrationError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str("migration operation failed")
    }
}

impl Error for MigrationError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        Some(&self.source)
    }
}

#[cfg(test)]
mod tests {
    use super::{EvidenceLevel, MigrationError};
    use std::{error::Error, io};

    #[test]
    fn mirrored_evidence_is_not_differential() {
        assert_ne!(EvidenceLevel::Mirrored, EvidenceLevel::GoldenDifferential);
        assert_ne!(EvidenceLevel::Mirrored, EvidenceLevel::LiveDifferential);
    }

    #[test]
    fn public_display_is_redacted_while_source_is_preserved() {
        let error = MigrationError::new(io::Error::other("credential-value"));

        assert_eq!(error.to_string(), "migration operation failed");
        assert!(!error.to_string().contains("credential-value"));
        assert_eq!(
            error
                .source()
                .expect("source must be preserved")
                .to_string(),
            "credential-value"
        );
    }
}
