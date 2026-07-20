# Rust 风格指南

## 命名

- 类型与 trait：`UpperCamelCase`
- 函数、方法、模块和变量：`snake_case`
- 常量与静态量：`SCREAMING_SNAKE_CASE`
- 构造函数通常使用 `new`，转换遵循 `from_*`、`into_*`、`as_*`、`to_*`

## 模块与 API

- 按领域能力组织模块，不按 struct/trait/impl 文件类型拆分。
- 默认私有，只公开稳定且有意维护的接口。
- 在 crate 根重导出主要公共类型，避免用户依赖深层内部路径。
- 对公共错误、panic、unsafe 和平台限制编写 rustdoc 章节。
- 示例优先写成可执行 doctest。

## 格式与 lint

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features -- -D warnings
```

不要为了消除 lint 直接全局 `allow`；记录为何不适用并把 allow 缩到最小范围。

更深入的 lint、Edition 迁移和错误码分析转到 `rust-style-clippy`。

官方来源：https://doc.rust-lang.org/style-guide/
