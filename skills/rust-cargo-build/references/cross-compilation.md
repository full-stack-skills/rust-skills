# Cross-compilation

## Basic Workflow

```bash
rustup target add aarch64-unknown-linux-gnu
cargo build --target aarch64-unknown-linux-gnu
```

Installing Rust targets does not guarantee that the system linker, C compiler, and libraries for the target platform are ready. The `.cargo/config.toml` file can be configured as follows:

```toml
[target.aarch64-unknown-linux-gnu]
linker = "aarch64-linux-gnu-gcc"
```

Verification steps include:

- `rustc --print target-list`
- `cargo build --target <triple>`
- Checking the architecture and dynamic dependencies of the produced artifacts.
- Executing tests on the target device, emulator, or trusted runner.

Do not claim cross-compilation success merely because "host cargo check" succeeds; actual runtime execution must be verified on the target platform.

Official source: https://doc.rust-lang.org/cargo/reference/config.html
