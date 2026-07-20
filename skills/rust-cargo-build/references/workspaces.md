# Workspace

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

成员通过 `{ workspace = true }` 继承依赖或 package 字段。

规则：

- profile 只在 workspace 根生效。
- workspace 共享一个 `Cargo.lock` 和 target 目录。
- `default-members` 只影响根目录未指定 package 时的默认选择。
- `exclude` 与 glob 成员需要和实际目录结构一起验证。
- virtual workspace 没有 package edition 可帮助推断 resolver，因此应显式写 resolver。

官方来源：https://doc.rust-lang.org/cargo/reference/workspaces.html
