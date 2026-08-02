//! The lowest-level crate. No dependencies except std.

/// A semver-style version triple.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Version {
    /// Major version.
    pub major: u32,
    /// Minor version.
    pub minor: u32,
    /// Patch version.
    pub patch: u32,
}

impl Version {
    /// Creates a version value.
    pub fn new(major: u32, minor: u32, patch: u32) -> Self {
        Self {
            major,
            minor,
            patch,
        }
    }

    /// Renders `MAJOR.MINOR.PATCH`.
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
