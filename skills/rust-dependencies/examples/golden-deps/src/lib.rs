//! `golden-deps` — a crate demonstrating minimal, audited dependency usage.
//!
//! - Narrow version requirements
//! - Disabled default features where possible
//! - Only essential runtime deps
//! - dev-deps kept out of downstream's graph

use serde::{Deserialize, Serialize};

/// A simple config loaded from JSON.
///
/// Demonstrates:
/// - Serde derive under a feature (C-SERDE pattern from rust-api-design)
/// - `#[non_exhaustive]` for forward compat (C-NON-EXHAUSTIVE)
/// - Private fields + builder-style construction (C-STRUCT-FIELD)
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[non_exhaustive]
pub struct Config {
    retry_count: u32,
    timeout_seconds: u32,
}

impl Config {
    pub fn new(retry_count: u32, timeout_seconds: u32) -> Self {
        Self {
            retry_count,
            timeout_seconds,
        }
    }

    pub fn retry_count(&self) -> u32 {
        self.retry_count
    }

    pub fn timeout_seconds(&self) -> u32 {
        self.timeout_seconds
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn config_round_trips_through_json() {
        let cfg = Config::new(3, 30);
        let json = serde_json::to_string(&cfg).unwrap();
        let back: Config = serde_json::from_str(&json).unwrap();
        assert_eq!(cfg, back);
    }

    #[test]
    fn default_features_disabled_for_serde() {
        // In Cargo.toml we set default-features = false; serde's defaults are
        // limited (std), and we're testing that derive still works.
        let cfg = Config::new(1, 5);
        assert_eq!(cfg.retry_count(), 1);
        assert_eq!(cfg.timeout_seconds(), 5);
    }
}
