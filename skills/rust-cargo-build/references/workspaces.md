```toml
[workspace]
members = ["crates/*"]
resolver = "3"

[workspace.package]
edition = "2024"
license = "Apache-2.0"

[workspace.dependencies]
serde = { version = "1", features = ["derive"] }
```

Members inherit dependencies or package fields via `{ workspace = true }`.

Rules:

- `profile` is only effective at the root of a workspace.
- A shared `Cargo.lock` and target directory are used across all members in a workspace.
- The default-members field affects member selection when no explicit package name is provided for each member.
- Members with an exclude path must be validated against their actual directory structure alongside glob patterns.
- Virtual workspaces do not have access to the `edition` field, which can help infer resolver behavior; therefore, a specific resolver should always be explicitly specified in such cases.

Official source: https://doc.rust-lang.org/cargo/reference/workspaces.html
