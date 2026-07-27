# Cargo Dependencies, Features, and Resolvers

Use [Specifying Dependencies](https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html), [Overriding Dependencies](https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html), [Features](https://doc.rust-lang.org/cargo/reference/features.html), and [Dependency Resolution](https://doc.rust-lang.org/cargo/reference/resolver.html) as the authority.

## Dependency scopes and sources

| Declaration | Consumer |
|---|---|
| `[dependencies]` | Library and binary targets |
| `[dev-dependencies]` | Tests, examples, and benches |
| `[build-dependencies]` | `build.rs`, compiled for the host |
| `[target.'cfg(...)'.dependencies]` | Selected target platforms |
| `[workspace.dependencies]` | Shared declaration inherited explicitly by members |

Prefer registry requirements for published dependencies. Use path dependencies for local composition and Git dependencies for explicit source control needs. A dependency may carry both `path` and `version` so local workspace development uses the path while the published package remains registry-resolvable.

Pin Git dependencies to `rev` when reproducibility matters. A tag or branch is still a moving repository reference unless organizational policy guarantees immutability.

## Features

```toml
[dependencies]
serde = { version = "1.0.219", optional = true, features = ["derive"] }

[features]
default = []
json = ["dep:serde"]
```

- Design features as additive capabilities.
- Use `dep:name` when the optional dependency should not implicitly expose a same-named feature.
- Use `dependency/feature` to forward a dependency feature.
- Use `dependency?/feature` when forwarding should not itself activate the optional dependency.
- Avoid mutually exclusive features; if unavoidable, detect invalid combinations with a clear compile error and test the matrix.
- Do not use `cfg(feature = "...")` inside target dependency table keys.

Inspect the effective result:

```bash
cargo tree -e features
cargo tree -e features -i <dependency>
```

## Resolver

- Treat the resolver as a workspace-wide setting.
- Edition 2021 normally selects resolver 2.
- Edition 2024 normally selects resolver 3.
- Virtual workspaces cannot infer a resolver from a package edition; declare one explicitly.
- Resolver 2 changes unification across build, dev, and target-specific dependency contexts.
- Resolver 3 adds MSRV-aware version-selection behavior; verify current defaults against the installed Cargo.

Test both intended MSRV and current stable toolchains when dependency resolution is part of the compatibility promise.

## Overrides

Use mechanisms by intent:

| Need | Mechanism |
|---|---|
| Test a compatible replacement for a registry package across the graph | `[patch.<source>]` |
| Use a local implementation as a direct dependency | `path` dependency |
| Redirect an equivalent registry source to a mirror or vendor directory | Source replacement |
| Select a different compatible resolved version | `cargo update -p <pkg> --precise <version>` where supported |

Do not use source replacement to substitute different crate contents. Avoid legacy `[replace]` in new designs.

## Validation

```bash
cargo metadata --format-version 1 --locked
cargo tree --duplicates
cargo tree -e features
cargo check --workspace --all-targets --all-features
```

Define a feature matrix when `--all-features` is not a supported combination. Route crate selection, advisories, license policy, and bans to `rust-dependencies`.
