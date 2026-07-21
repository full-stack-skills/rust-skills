//! The lowest-level crate. No dependencies except std.
//!
//! Every other crate in the workspace depends on this.

/// A semver-style version triple.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Version {
    /// Major version — incremented for incompatible API changes.
    pub major: u32,
    /// Minor version — incremented for backwards-compatible features.
    pub minor: u32,
    /// Patch version — incremented for backwards-compatible fixes.
    pub patch: u32,
}

impl Version {
    /// Create a new version.
    pub fn new(major: u32, minor: u32, patch: u32) -> Self {
        Self {
            major,
            minor,
            patch,
        }
    }

    /// Render as `MAJOR.MINOR.PATCH`.
    pub fn as_string(&self) -> String {
        format!("{}.{}.{}", self.major, self.minor, self.patch)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn version_renders() {
        assert_eq!(Version::new(1, 2, 3).as_string(), "1.2.3");
    }
}
