# Scaffolding and Binding Generation

Read this reference when setting up Cargo, `build.rs`, UDL scaffolding, `uniffi.toml`, `uniffi-bindgen`, or reproducible generation.

## Baseline Inspection

```bash
rustc --version --verbose
cargo metadata --format-version 1
cargo tree -e features
cargo tree -i uniffi
```

Record the locked UniFFI version and features. The `uniffi` package may expose separate `build`, `bindgen`, `cli`, `cargo-metadata`, runtime, tracing, Tokio, or WASM-related features depending on release. Enable only those required by the chosen workflow.

## Procedural-Macro-Only Setup

Use library mode and place this exactly once in the crate:

```rust
uniffi::setup_scaffolding!();
```

Do not also include UDL-generated scaffolding. Keep exported items in ordinary Rust modules and verify the final library contains UniFFI metadata.

Example manifest shape:

```toml
[lib]
crate-type = ["lib", "cdylib", "staticlib"]

[dependencies]
uniffi = "=<locked-version>"
```

Select only artifact kinds required by the actual hosts:

- `lib` keeps ordinary Rust integration and tests available;
- `cdylib` commonly supports dynamic loading by foreign runtimes;
- `staticlib` supports static Apple or other native packaging flows.

Artifact selection is a release decision, not generic boilerplate.

## UDL Setup

The common UDL flow has three coordinated pieces:

1. A namespace and interface in `src/<namespace>.udl`.
2. A build dependency with UniFFI build support.
3. A `build.rs` that generates scaffolding plus one `include_scaffolding!` call.

Representative shape:

```rust
fn main() {
    uniffi::generate_scaffolding("src/example.udl")
        .expect("failed to generate UniFFI scaffolding");
}
```

```rust
uniffi::include_scaffolding!("example");
```

Verify the selected release's exact function and feature names. Add `cargo:rerun-if-changed` behavior if the generator does not already cover every relevant UDL/config input. Never commit a build script that silently uses a globally installed, unpinned generator.

## Mixed Setup

In mixed mode:

- keep one UDL scaffolding include;
- do not call `setup_scaffolding!`;
- make crate name and UDL namespace match;
- declare UDL-referenced types in UDL;
- place macro-exported additions in separate impl blocks;
- test both UDL-defined and macro-defined calls from foreign code.

## Configuration Layers

UniFFI binding generation can combine:

- command-line language/output options;
- a per-crate `uniffi.toml`;
- a global configuration file;
- crate locations discovered through Cargo metadata;
- explicit global `[crate-roots]` entries.

Record precedence and make every CI input visible. Avoid generation that depends on an accidental working directory or a developer-only global config.

When avoiding Cargo metadata, a global configuration may map crate names to roots:

```toml
[crate-roots]
example = "./crates/example"
```

Paths are relative to the global config file. Verify that each root exposes the expected UDL and/or `uniffi.toml`.

Library-mode generation may invoke `cargo metadata` from the generator's current
working directory. Run it from the owning Cargo workspace or provide explicit
crate roots; invoking it from an unrelated directory can fail even when the
dynamic library itself is valid.

## Generation Pipeline

Prefer generation from the exact compiled library that will ship:

```bash
cargo build --locked --release --target <target-triple>
uniffi-bindgen generate \
  --config global.toml \
  --language swift \
  --out-dir generated/swift \
  target/<target-triple>/release/<library-file>
```

CLI spellings vary by release; run `uniffi-bindgen --help` from the pinned tool before automation. Never infer the platform library filename:

- Linux commonly uses `lib<name>.so`;
- macOS commonly uses `lib<name>.dylib`;
- Windows commonly uses `<name>.dll`;
- static archives commonly use `.a` or `.lib`.

Use Cargo metadata or an explicit artifact manifest rather than brittle filename guessing.

## Reproducibility

- Pin Rust, UniFFI, bindgen backend, and host-language tool versions.
- Use `--locked` in CI and preserve the application/workspace lockfile.
- Generate into a clean directory.
- Fail on unexpected dirty diffs if generated sources are committed.
- Include config, UDL, features, target, and library hash in generation evidence.
- Keep generated code and native artifacts from the same build.
- Avoid developer-specific absolute paths in committed config or generated headers/module maps.

## Conditional Compilation

Put platform `#[cfg]` outside exported impl blocks:

```rust
#[cfg(target_os = "android")]
#[uniffi::export]
impl PlatformService {
    pub fn platform_name(&self) -> String {
        "android".to_owned()
    }
}
```

Conditional items nested inside an exported block can still produce incompatible scaffolding. If only the binding surface should be optional, use a reviewed `cfg_attr` pattern and test both feature states.

## Generation Failure Checklist

- Is the generator version compatible with the runtime metadata?
- Was the correct final library passed, rather than an rlib or stale artifact?
- Are UDL namespace, crate package name, and Rust crate identifier aligned?
- Is scaffolding initialized exactly once?
- Are required UniFFI features active for the generation tool?
- Can Cargo metadata locate every participating crate?
- Are `[crate-roots]` relative to the intended config file?
- Is `uniffi.toml` loaded from the expected crate?
- Does a clean release build reproduce the same generated output?

## Official Sources

- [Tutorial: Rust scaffolding](https://mozilla.github.io/uniffi-rs/latest/tutorial/Rust_scaffolding.html)
- [Tutorial: Foreign-language bindings](https://mozilla.github.io/uniffi-rs/latest/tutorial/foreign_language_bindings.html)
- [Procedural-macro build workflow](https://mozilla.github.io/uniffi-rs/latest/proc_macro/index.html#build-workflow)
- [Generating bindings](https://mozilla.github.io/uniffi-rs/latest/bindings.html)
- [Customizing binding generation](https://mozilla.github.io/uniffi-rs/latest/configuration.html)
