use golden_migration_tests::{EvidenceLevel, MigrationError};
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
