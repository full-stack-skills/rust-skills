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
