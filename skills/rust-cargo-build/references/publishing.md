# Packaging and Publishing

## Pre-release Gatekeeping

```bash
cargo fmt --all --check
cargo test --all-targets --all-features
cargo clippy --all-targets --all-features -- -D warnings
cargo package --list
cargo publish
```

Additional checks:

- Version compatibility with SemVer.
- `license` or `license-file`.
- README, repository URL, description, and documentation links.
- Package contents must not include secrets, fixture private data, or large irrelevant files.
- All non-dev dependencies must be resolvable from the target registry.
- Workspace internal dependency declarations should specify publishable versions.

`cargo publish` is an external state change that requires confirmation of the registry URL, account credentials, token source, and user authorization. On crates.io, a published version cannot be deleted and can only be yanked; verify the policy of any other registry separately.

Official documentation: https://doc.rust-lang.org/cargo/reference/publishing.html
