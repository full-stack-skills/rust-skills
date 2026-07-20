# 依赖、Features 与 Resolver

## 依赖来源

- crates.io：优先使用清晰的 SemVer requirement。
- Git：固定 rev 最可复现；branch/tag 仍可能发生治理变化。
- Path：适合同仓库开发，不可单独发布为外部依赖来源。
- Workspace：使用 `[workspace.dependencies]` 统一版本和常用 feature。

## Features

```toml
[dependencies]
serde = { version = "1", optional = true, features = ["derive"] }

[features]
default = []
json = ["dep:serde"]
```

Feature 在同一解析图中是可加和的。验证来源：

```bash
cargo tree -e features
cargo tree -i serde
```

## Resolver

- resolver 2：Edition 2021 默认，改进 dev/build/target dependency 的 feature unification。
- resolver 3：Edition 2024 默认，把不兼容 `rust-version` 的依赖版本默认设为 fallback。
- resolver 是 workspace 全局配置；virtual workspace 应显式声明。

官方来源：

- https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html
- https://doc.rust-lang.org/cargo/reference/features.html
- https://doc.rust-lang.org/cargo/reference/resolver.html
