# Production-Level Workspace Boundaries

The multi-crate layout of `rmux` demonstrates a reusable direction: delegating the reasons for change to distinct components. Do not replicate crate counts; only split crates when independent APIs, dependencies, or platform boundaries exist.

## Recommended Dependency Direction

```text
types
  -> proto
  -> core

os -> ipc -> client/sdk
os -> pty -> server

core + proto + ipc + pty -> server
sdk -> integration adapters
client + server + adapters -> binary
```

Key Constraints:

- `types` should contain only platform-neutral, minimal-dependency value types;
- `proto` should hold wire DTOs, versions, frames, and wire-safe errors—no business handlers;
- `core` is a pure memory-domain model; minimize dependencies on Tokio, CLI, or OS;
- `os`/`pty` isolate configuration (`cfg`), handles, and unsafe code;
- `server` owns concurrent state and I/O lifecycles;
- `sdk` exposes stable facades/handles without leaking internal transports;
- The final binary is responsible for process entrypoint, config combination, and runtime policies.

## When to Split into Crates

Split a crate if **at least one** of the following conditions holds:

1. Requires independent publishing or third-party reuse;
2. Requires distinct feature/target/no_std/WASM boundaries;
3. Requires compile-time prohibition of reverse dependencies;
4. Has an independently public API with compatibility commitments;
5. Test and build lifecycles are significantly different.

Do not split crates solely due to file count, team size, or "clean appearance"; modules typically remain lighter than full crates.

## Protocol Identity vs Display Position Separation

`rmux` distinguishes stable pane IDs from mutable display indices. Reusability principles:

- Protocol/Sdk handles preserve stable identities;
- UI ordering, array indices, and names are not persistent identifiers;
- Each operation re-parses current position by stable ID or explicit version;
- Encapsulate IDs in `newtype` to avoid mixing `u64/u32/String`;
- Overflow, reuse, and cross-process scope of IDs must be protocol-invariant.

## Public API Facade

External crates may use facade + builder + opaque handle patterns:

- Constructing handles does not implicitly perform I/O; method names explicitly declare behavior like `connect`/`connect_or_start`;
- Builders record configuration; side effects only occur during execution methods;
- `pub use` exports stable entry points while keeping transport/state private to the crate;
- Return slice/reference-only read-accessors instead of directly exposing internal `Vec/HashMap`;
- When evolving enums with `#[non_exhaustive]`, callers must retain wildcards;
- Errors exposed across crates should be in stable categories and sources, not leaking internal implementation types.

## Platform Modules

Platform-specific differences are best kept in dedicated crates/modules:

```rust
#[cfg(unix)]
mod unix;
#[cfg(windows)]
mod windows;

pub use imp::LocalStream;
```

The public layer should consume consistent abstractions without erasing platform semantics—e.g., Unix socket permissions, Windows named pipe identities, PTY resizing behavior, or signal handling.

## Dependency Boundary Validation

```bash
cargo metadata --format-version 1 --no-deps
cargo tree -p my-core
cargo tree -p my-proto -e features
cargo check --workspace --all-targets
```

Additional source gates may prohibit:

- `core/proto` importing Tokio, CLI, HTTP, or platform APIs;
- Platform-neutral crates using `cfg(target_os)`;
- SDK public API leaking server-private types;
- Calling `process::exit` outside the binary crate;
- Expensive dependencies remaining compiled after feature flags are disabled.

## Primary Resources

- [Cargo workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html)
- [Rust modules](https://doc.rust-lang.org/reference/items/modules.html)
- [Visibility and privacy](https://doc.rust-lang.org/reference/visibility-and-privacy.html)
- [API Guidelines](https://rust-lang.github.io/api-guidelines/)
