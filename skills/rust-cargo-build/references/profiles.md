# Profiles and Product Optimization

```toml
[profile.release]
lto = "thin"
codegen-units = 1
strip = "symbols"

[profile.release-small]
inherits = "release"
opt-level = "z"
panic = "abort"
```

Define the target: throughput, latency, compilation time, binary size, debugging capabilities, or unwind behavior. Adjust only a few parameters at a time and measure results.

- `lto` combined with low `codegen-units` may improve runtime performance or binary size but increases link time.
- `strip` affects symbol diagnostics.
- Setting `panic = "abort"` changes error recovery and FFI behavior.
- Dependencies are covered using `[profile.<name>.package.<name>]`, though they must still be listed at the root level.

Official source: https://doc.rust-lang.org/cargo/reference/profiles.html
