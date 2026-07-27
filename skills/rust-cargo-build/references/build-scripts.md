# Cargo Build Scripts

Use [Build Scripts](https://doc.rust-lang.org/cargo/reference/build-scripts.html) and [Build Script Examples](https://doc.rust-lang.org/cargo/reference/build-script-examples.html) for supported instructions and native-link patterns.

## Contract

`build.rs` compiles and executes before the package. It runs on the host even when the package targets another platform.

```rust
fn main() {
    println!("cargo::rerun-if-changed=proto/schema.proto");
    println!("cargo::rerun-if-env-changed=EXAMPLE_SYS_ROOT");
}
```

- The `cargo::KEY=VALUE` form requires Cargo 1.77 or newer. Use the legacy `cargo:KEY=VALUE` form when the package's supported Cargo/MSRV is older.
- Write generated artifacts only to `OUT_DIR`.
- Do not assume `OUT_DIR` is empty between builds; overwrite owned outputs deterministically and avoid consuming stale undeclared files.
- Include generated Rust with `include!` or expose documented metadata deliberately.
- Declare every file and environment input that should trigger a rerun.
- Keep standard output limited to Cargo instructions; use stderr for human diagnostics.
- Do not fetch unpinned network resources during a build.
- Do not write generated source back into the package unless the project has an explicit regeneration workflow separate from normal builds.
- Preserve instruction order when it affects linker argument order.

## Native dependencies

Use `[build-dependencies]` for `cc`, `pkg-config`, bindgen, code generators, or platform probes used only by the build script. Keep host/target distinctions explicit through `HOST`, `TARGET`, and the selected toolchain.

The `links` manifest key and `cargo::rustc-link-*` instructions affect downstream native linking. Treat their names and emitted metadata as compatibility contracts.

Prefer mature `-sys` crates and established system-discovery conventions. Validate:

- clean build and incremental rebuild;
- host build script on every supported cross target;
- static/dynamic link choice;
- absence and incompatible version diagnostics;
- paths containing spaces or non-ASCII characters where relevant.

## Rebuild diagnosis

```bash
cargo build -vv
cargo build --timings
```

If a build script reruns unexpectedly, inspect declared inputs, environment dependencies, generated outputs, and native tool timestamps before deleting caches.

## Testing

Move parsing and generation logic into a normal library when it benefits from unit tests. Keep `build.rs` as a thin adapter that reads Cargo inputs and emits instructions. Compile generated artifacts in a clean target directory and on the actual target environment.
