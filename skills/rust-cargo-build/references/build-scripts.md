# Build Scripts

The `build.rs` script runs before compiling a package. It is used to perform local build steps that Cargo cannot express directly in the standard compilation process.

```rust
fn main() {
    println!("cargo::rerun-if-changed=proto/schema.proto");
    println!("cargo::rerun-if-env-changed=EXAMPLE_SYS_ROOT");
}
```

Rules:

- Files are written to `OUT_DIR`.
- Each file and each environment input is declared with a re-run condition.
- Standard output should only contain Cargo commands; diagnostics go to stderr.
- Do not rely on implicit paths outside the current working directory.
- Native dependencies should prefer mature `-sys` crate usage and pkg-config/cmake conventions.
- Ensure generated Rust code produces reproducible outputs that can be checked by normal compilation workflows.

Official source: https://doc.rust-lang.org/cargo/reference/build-scripts.html
