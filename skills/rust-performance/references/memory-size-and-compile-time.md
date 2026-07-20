# Memory, Binary Size, and Compile Time

## Memory

Separate peak RSS, retained heap, allocation count and bytes, fragmentation, mapped files, stacks, caches, and kernel buffers. Reproduce steady-state and peak phases independently. Use DHAT or platform heap tools for allocation paths and retention, then confirm under production-like load.

Bound caches, queues, body buffers, batches, and per-connection state. A leak-like graph may be intended cache growth without a capacity contract.

## Binary size

Inspect release profiles, debug symbols, panic strategy, LTO, codegen units, target features, optional dependencies, and duplicated generic instantiations. Use `cargo bloat` to attribute code size and inspect the final packaged artifact rather than only `target/release`.

Do not enable aggressive size settings without measuring runtime and compile-time effects.

## Compile time

Use Cargo build timings for crate-level scheduling and time. Use `cargo-llvm-lines` to identify monomorphization-heavy code. Compare clean, incremental, check, test, and release builds separately.

Reduce unnecessary features, macro expansion, generated code, build-script invalidation, and generic fan-out before splitting crates solely for compilation speed.

## Sources

- [Cargo build timings](https://doc.rust-lang.org/cargo/reference/timings.html)
- [cargo-bloat](https://github.com/RazrFalcon/cargo-bloat)
- [cargo-llvm-lines](https://github.com/dtolnay/cargo-llvm-lines)
- [DHAT](https://docs.rs/dhat/)
