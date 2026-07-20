# Dependency Selection and Governance for Production

Dependency selection is not about selecting the "best crate" but rather choosing minimal capabilities tailored to specific boundaries, while verifying maintenance status, MSRV (Minimum Supported Rust Version), features, platform compatibility, licenses, and attack surface. The following tool combinations are derived from rmux production cases; versions must be validated against the target project's `Cargo.lock` file and official documentation.

## Tool Map

| Problem | Candidate Tools | Applicable Boundaries & Considerations |
|---|---|---|
| CLI Parameters | `clap` (derive/builder) | Large command surfaces can be normalized to internal commands after derivation; lock large version syntaxes. |
| Async Runtime | `tokio` | Enable only the required features (`rt/net/io-util/sync/time/process`, etc.). |
| Structured Diagnostics | `tracing` | Use spans and fields for concurrent chains; govern sensitive fields and high-cardinality data. |
| DTO/Configuration | `serde`, `serde_json`, `toml` | Versioning and compatibility strategies must be defined for external formats; explicitly define policies for unknown fields. |
| Local Binary IPC | `bincode` (and others) | Must include version constraints, length limits, and trust boundaries; do not directly port to untrusted networks without validation. |
| Error Types | `thiserror` | Libraries expose structured errors; application boundaries decide on display or exit codes. |
| POSIX Capabilities | `rustix` | Use features (`fs`, `net`, `process`, `pty`, `termios`) selectively over bare libc/unsafe to reduce complexity and risk. |
| Windows APIs | `windows-sys` | Enable only required Win32 features; encapsulate into platform-specific crates. |
| Signals | `signal-hook` / Tokio signal | Select based on signal safety, synchronous vs asynchronous boundaries. |
| TUI/Terminal UIs | `ratatui`, `crossterm`, `unicode-width` | Maintain fixed compatible combinations and perform real terminal/snapshot testing. |
| Compact Strings | `compact_str` | Adopt only when profiling demonstrates significant benefits from short string usage. |
| Dependency Strategy | `cargo-deny` | Governance of advisories, licenses, bans, sources in a single operation. |
| Test Scheduling | `cargo-nextest` | Use test groups to limit shared daemon/database resources that are expensive or critical. |

## Selection Steps

1. Define required APIs, supported platforms, MSRV, and no_std/WASM boundaries along with security constraints.
2. Verify crate official documentation, repository activity, release/security policies, and license terms.
3. Inspect default features and transitive dependencies using `cargo info` or `cargo tree -e features`.
4. Compare compilation time, binary size, duplicate versions, and unsafe/native dependency usage before/after introducing the new tooling.
5. Test on minimal feature sets, default configurations, and explicitly declared supported combinations.
6. Document selection rationale in manifest comments, ADRs (Architecture Decision Records), or security exceptions; do not leave decisions solely within chat logs.

## Feature Isolation by Platform

rmux places Web-specific password dependencies under the `web` feature flag and Unix/Windows capabilities into target-specific dependencies. This pattern suits expensive or platform-exclusive libraries:

```toml
[dependencies]
serde = { version = "1", features = ["derive"], optional = true }

[features]
default = []
config = ["dep:serde"]

[target.'cfg(unix)'.dependencies]
rustix = { version = "1", features = ["fs", "net"] }

[target.'cfg(windows)'.dependencies]
windows-sys = { version = "0.61", features = ["Win32_Foundation"] }
```

Do not express feature-based target dependencies using `cfg(feature = ...)`; Cargo requires explicit `[features]` and optional dependency declarations instead.

## Version Constraint Trade-offs

- General-compatible libraries typically use semver requirements and submit lockfiles to applications.
- For CLI parsers, TUI renderers, generators, or reproducible byte artifacts with known compatibility differences: pin versions precisely and record deprecation conditions;
- In workspace configurations: `path` enables easy cross-project debugging while `version` ensures published packages can be resolved correctly;
- Avoid using broad Git branches as release dependencies; fix specific revisions when necessary.
- Duplicate versions shown by `cargo tree -d` serve as review signals but are not mandatory to zero out entirely.

## Supply Chain Gatekeeping

```bash
cargo metadata --format-version 1 --locked
cargo tree -e features
cargo tree -d
cargo deny check
cargo check --workspace --all-targets --locked
```

`cargo-deny` simultaneously checks advisories, licenses, banned/repeated crates, and source origins. Security exceptions must include: advisory ID, exposed boundary justification, why the vulnerability is not exploitable in this context, remediation/removal conditions, and review owner assignment. For rmux's local IPC serialization vulnerabilities specifically, exception logic relies on bounded judgment; if a shared codec exposes to network traffic, that rationale immediately becomes invalid.

## Profile Optimization by Crate Size

Reserve `opt-level = 3` for measured hot paths. Thin protocol or platform layers may use `opt-level = "s"`, but only when artifact-size and performance measurements justify it. LTO, codegen units, stripping, and panic policies are controlled at the workspace root; do not copy them between projects without compatibility and performance verification.

## Key References

- [Cargo specifying dependencies](https://doc.rust-lang.org/stable/cargo/reference/specifying-dependencies.html)
- [Cargo features documentation](https://doc.rust-lang.org/cargo/reference/features.html)
- [cargo-deny checks guide](https://embarkstudios.github.io/cargo-deny/checks/index.html)
- [cargo-nextest test groups configuration](https://nexte.st/docs/configuration/test-groups/)
- [clap derive reference](https://docs.rs/clap/latest/clap/_derive/)
- [rustix documentation](https://docs.rs/rustix/latest/rustix/)
