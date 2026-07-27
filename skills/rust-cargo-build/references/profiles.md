# Cargo Profiles and Build Performance

Use [Profiles](https://doc.rust-lang.org/cargo/reference/profiles.html) for exact keys and [Optimizing Build Performance](https://doc.rust-lang.org/cargo/guide/build-performance.html) for measured workflow guidance.

## Define the objective

Choose one or more measurable goals:

- faster `cargo check` feedback;
- faster test compilation or execution;
- faster clean CI builds;
- faster incremental rebuilds;
- smaller release artifacts;
- better runtime throughput or latency;
- usable debugger information and backtraces.

Do not copy release settings between projects without measuring their trade-offs.

## Profile layout

Define profiles only at the workspace root:

```toml
[profile.release]
lto = "thin"
codegen-units = 1
strip = "symbols"

[profile.release-small]
inherits = "release"
opt-level = "z"
panic = "abort"

[profile.dev.package."*"]
debug = false
```

- LTO and fewer codegen units can improve runtime or size while increasing link time.
- `strip` reduces symbol information used by debugging and crash analysis.
- `panic = "abort"` changes recovery and FFI behavior.
- Per-package settings tune dependencies without changing workspace-member defaults.
- Custom profiles must inherit from a built-in or another supported profile as documented.

## Measurement workflow

```bash
cargo clean
cargo build --timings
cargo build --release --timings
```

Run destructive cleanup only after resolving the target directory and when a clean-build comparison is required. Also measure representative incremental changes.

Use `build-cache-diagnostics.md` to interpret timings and duplicate builds. Use `rust-performance` when the question is runtime behavior rather than Cargo build behavior.

## Nightly options

Alternative codegen backends, experimental feature-unification modes, profile extensions, and build-analysis features may require nightly. Keep them in a separate experiment with a pinned toolchain, stable fallback, and removal condition; see `unstable-features.md`.
