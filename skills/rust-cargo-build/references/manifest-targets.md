# Manifest 与构建目标

## 最小 package

```toml
[package]
name = "example"
version = "0.1.0"
edition = "2024"
rust-version = "1.85"
license = "Apache-2.0"
description = "Example crate"
repository = "https://example.com/repository"
```

默认目标是 `src/lib.rs` 和 `src/main.rs`。只有路径、名称或 crate type 不符合约定时才显式配置 `[lib]`、`[[bin]]`、`[[example]]`、`[[test]]` 或 `[[bench]]`。

发布 crate 时补齐 description、license/license-file、repository、readme、keywords 和 categories，并用 `cargo package --list` 检查内容。

官方来源：https://doc.rust-lang.org/cargo/reference/manifest.html
