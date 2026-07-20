# Manifest and Build Targets

## Minimum Package Configuration

```toml
[package]
name = "example"
version = "0.1.0"
edition = "2024"
rust-version = "1.85"
license = "Apache-2.0"
description = "Example crate"
repository = "https://example.com/repository"
```

The default targets are `src/lib.rs` and `src/main.rs`. Explicit configuration of `[lib]`, `[[bin]]`, `[[example]]`, `[[test]]`, or `[[bench]]` is only required when the path, name, or crate type does not conform to conventions.

When publishing a crate, ensure that all fields—specifically description, license/license-file, repository, readme, keywords, and categories—are populated. Verify package contents using `cargo package --list`.

Official documentation: https://doc.rust-lang.org/cargo/reference/manifest.html
