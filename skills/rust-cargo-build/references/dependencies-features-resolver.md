# Dependencies, Features, and Resolver

## Dependency Sources

- **crates.io**: Prefer clear SemVer requirements.
- **Git**: Fixed revision ensures reproducibility; branches/tags may still undergo governance changes.
- **Path**: Suitable for internal development in the same repository. A crates.io publication cannot depend on an unpublished path alone; provide an appropriate registry version when the published package must resolve that dependency.
- **Workspace**: Use `[workspace.dependencies]` to unify versions and common features across all members of a workspace.

## Features

```toml
[dependencies]
serde = { version = "1", optional = true, features = ["derive"] }

[features]
default = []
json = ["dep:serde"]
```

Features are additive within the same dependency graph. Verification commands:

```bash
cargo tree -e features
cargo tree -i serde
```

## Resolver

- **resolver 2**: Default for Edition 2021; improves feature unification of dev/build/target dependencies.
- **resolver 3**: Default for Edition 2024; sets fallback versions by default for packages incompatible with the specified `rust-version`.
- The resolver is a workspace-wide configuration setting; virtual workspaces must explicitly declare their own resolver settings.

Official documentation:

- https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html
- https://doc.rust-lang.org/cargo/reference/features.html
- https://doc.rust-lang.org/cargo/reference/resolver.html
