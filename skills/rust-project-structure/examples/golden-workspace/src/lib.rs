//! Root package: thin facade over the workspace members.
//!
//! This file is intentionally small. The actual logic lives in `my-core`
//! (low-level types) and `my-net` (network helpers). The root package just
//! re-exports a curated surface for users who want one import.

pub use my_core::Version;
pub use my_net::user_agent;

/// Convenience entry point.
pub fn build_user_agent(version: Version) -> String {
    user_agent("my-app", version)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn build_user_agent_uses_workspace_types() {
        let v = Version::new(0, 1, 0);
        assert_eq!(build_user_agent(v), "my-app/0.1.0");
    }
}
