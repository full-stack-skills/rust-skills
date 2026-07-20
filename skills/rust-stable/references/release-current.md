# Current Stable Baseline

**Snapshot**: 2026-07-20.

## Current Version

- **Stable**: Rust 1.97.1 (2026-07-16).
- **Current Edition**: 2024.
- The minimum stable toolchain for Edition 2024 is Rust 1.85.0.
- Cargo resolver version 3 became available since Rust 1.84 and is the default selection for Edition 2024.

Always verify your user environment using one of the following commands; do not treat this file as a runtime probe result:

```bash
rustc --version --verbose
cargo --version
rustup show active-toolchain
```

## Rust 1.97 Highlights

- Introduced `cfg(target_has_atomic_primitive_alignment)`.
- Relaxed trailing `self` syntax in some import statements.
- Stabilized integer APIs for highest bit, lowest bit, and bit width.
- Stabilized Cargo configurations: `build.warnings` and `resolver.lockfile-path`.
- Fixed LLVM optimization-related miscompilation issues; prioritize Rust 1.97.1 over 1.97.0.

Before using these capabilities, verify the project's Minimum Supported Rust Version (MSRV). Do not introduce APIs that the project's supported toolchain cannot compile.

## Update This Baseline

1. Open the first entry in the official Release Notes.
2. Update version number, release date, and highlights for this page.
3. Check language standard library, Cargo, Clippy, Rustdoc, and compatibility documentation.
4. Compile golden examples separately on the declared MSRV and the current supported stable toolchain.
5. Update TRACE/Eval baseline versions and plugin versions.

## Official Sources

- https://doc.rust-lang.org/stable/releases.html
- https://blog.rust-lang.org/releases/
- https://doc.rust-lang.org/edition-guide/
- https://doc.rust-lang.org/cargo/reference/resolver.html
