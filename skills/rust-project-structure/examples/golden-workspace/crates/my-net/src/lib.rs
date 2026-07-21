//! A mid-level crate that depends on `my-core`.
//!
//! Demonstrates the workspace dependency direction:
//! `my-net` ─► `my-core` (allowed)
//! `my-core` ─► `my-net` (forbidden — cycle)

pub use my_core::Version;

/// A user-agent header value, parameterized by version.
pub fn user_agent(name: &str, version: Version) -> String {
    format!("{name}/{}", version.as_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn user_agent_formats() {
        assert_eq!(user_agent("my-app", Version::new(0, 1, 0)), "my-app/0.1.0");
    }
}
