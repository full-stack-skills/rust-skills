---
name: rust-style-clippy
description: Rust 格式化与静态分析技能 — stable rustfmt、Clippy lint 与配置、Edition 2015/2018/2021/2024 迁移、cargo fix 和 rustc 错误码。Use when formatting, linting, migrating editions, configuring CI quality gates, or diagnosing compiler errors; hand semantic code-review findings to rust-code-review.
---

# Rust 风格格式化与静态分析

> 基于 [rustfmt Book](https://doc.rust-lang.org/rustfmt/)、[Clippy Book](https://doc.rust-lang.org/clippy/index.html)、[Edition Guide](https://doc.rust-lang.org/edition-guide/) 与 [Error Code Index](https://doc.rust-lang.org/error_codes/).

## Capability Boundaries

### ✅ 强项
1. 稳定版 rustfmt 配置（edition、max_width、tab_spaces、use_field_init_shorthand 等）
2. Clippy lint 体系（cargo clippy、lint 等级、clippy.toml 配置）
3. 关键 Clippy lint 群组（correctness、style、complexity、perf、pedantic、nursery、restriction）
4. Edition 迁移（2015→2018→2021→2024，各版关键变化与 cargo fix）
5. 编译器错误码解读（rustc --explain、常见错误码对照表）

### ⚠️ 前置要求
1. Rust 工具链安装完成

### ❌ 不适用范围
1. Rust 语法基础 → 使用 `rust-stable` 技能
2. 代码审查 → 使用 `rust-code-review` 技能

## 何时使用

- "格式化 Rust 代码"
- "运行 Clippy"
- "迁移到新 Edition"
- "编译器报错 E0xxx 是什么意思"

## Data Privacy

本技能不收集、存储或传输任何用户数据。

---

## 一、rustfmt 配置

```toml
# .rustfmt.toml
max_width = 100                    # 行宽（默认 100）
tab_spaces = 4                     # 缩进空格
edition = "2024"                   # Rust edition
merge_derives = true               # 合并 derive
use_field_init_shorthand = true    # 字段初始化简写
use_try_shorthand = true            # 使用 ? 简写
```

```bash
cargo fmt                           # 格式化所有文件
cargo fmt --check                   # 检查格式（CI 使用）
cargo fmt -- --config max_width=80  # 使用特定配置
```

`imports_granularity`、`group_imports`、`reorder_impl_items` 等选项可能仍要求 nightly rustfmt；不要把它们放进必须由 stable CI 通过的默认配置。

## 二、Clippy

```bash
cargo clippy                        # 运行所有 lint
cargo clippy -- -W clippy::pedantic # 启用额外 lint 群组
cargo clippy --fix                  # 自动修复
```

```rust
// 控制 lint 级别
#[allow(clippy::needless_return)]
fn my_fn() { return 42; }

#[deny(clippy::unwrap_used)]
fn safe_fn() -> Result<i32, Error> {
    let v = risky()?;  // 不能用 unwrap
    Ok(v)
}

// clippy.toml（项目根目录）
// disallowed-macros = ["unwrap", "expect"]
// cognitive-complexity-threshold = 25
```

关键 lint 群组：

| 群组 | 说明 | 常用 lint |
|------|------|-----------|
| correctness | 编译正确性（默认） | `clippy::almost_swap` |
| style | 代码风格（默认） | `clippy::enum_variant_names` |
| complexity | 复杂度提示 | `clippy::too_many_arguments` |
| perf | 性能提示 | `clippy::large_enum_variant` |
| pedantic | 严格模式（需主动启用） | `clippy::cast_possible_truncation` |
| nursery | 实验性 | `clippy::use_self` |
| restriction | 限制性最强 | `clippy::unwrap_used`, `clippy::expect_used` |

## 三、Edition 迁移

```bash
# 查看当前 edition
cargo metadata --format-version 1 | jq '.packages[0].edition'

# 迁移步骤（以 2021 → 2024 为例）
cargo fix --edition               # 自动迁移代码
cargo build                       # 检查编译
cargo test                        # 验证功能

# 更新 Cargo.toml
# edition = "2024"
```

各 edition 关键变化：

| Edition | 关键变化 |
|---------|---------|
| 2015→2018 | NLL 借用检查、模块系统（不再 `extern crate` + `mod.rs` → `name.rs`）、trait 默认导入、union 改进 |
| 2018→2021 | 闭包捕获改进（`||` 仅捕获需要的字段）、`IntoIterator` for 数组、panic 宏一致化、`Cargo.toml` `[workspace]` 继承 |
| 2021→2024 | 默认类型推断改进、`impl Trait` 位置更灵活、`unsafe` 块可包含更多模式、`assert!(expr)` 消息改进、`unsafe_op_in_unsafe_fn` 默认 warn |

## 四、编译器错误码速查

```bash
# 查看错误详情
rustc --explain E0277
```

| 错误码 | 含义 | 典型场景 |
|--------|------|---------|
| E0277 | trait 未实现 | `T: Trait` bound 不满足 |
| E0308 | 类型不匹配 | 期望类型 A，但给了 B |
| E0502 | 借用冲突 | 不能可变借用 + 不可变借用 simultaneously |
| E0597 | 生命周期不足 | 引用超出借用值的作用域 |
| E0432 | 导入不存在 | `use` 路径有误 |
| E0061 | 参数数量不匹配 | 函数调用参数数错误 |
| E0106 | 生命周期缺失 | 函数签名需要显式生命周期 |
| E0382 | 使用已移动值 | 所有权已转移 |
| E0499 | 同时可变借用 | 只能一个 `&mut` |
| E0716 | 临时值生命周期不足 | 临时值的引用超出其作用域 |

## Workflow

1. 格式化代码 — cargo fmt 确保代码风格一致
2. 运行 Clippy — cargo clippy 发现潜在错误和改进机会
3. 配置 Clippy — 按项目需求启用/禁用特定 lint（clippy.toml）
4. 检查 Edition — 确认 Cargo.toml 中 edition 是最新的
5. 依赖安全 — cargo audit 扫描已知漏洞
6. CI 集成 — 集成 fmt --check + clippy + audit 到 CI 流程


## Gotchas

1. cargo clippy --fix 只修复 MachineApplicable 级别的 lint
2. rustfmt 配置文件名是 .rustfmt.toml - 非 rustfmt.toml
3. Edition 迁移后可能出新的 warning - 特别是 2024 的 unsafe_op_in_unsafe_fn
4. cargo fix --edition 不会修复所有问题 - 迁移后仍需手动检查


## 按需资源

- [格式与 Clippy 示例](examples/examples.md)
- [Lint 群组速查](references/references.md)
- `examples/golden-style/`：CI 通过 rustfmt 与 Clippy 的黄金示例

## 官方参考

- [rustfmt Book](https://doc.rust-lang.org/rustfmt/)
- [Clippy Book](https://doc.rust-lang.org/clippy/)
- [Edition Guide](https://doc.rust-lang.org/edition-guide/)
- [Compiler Error Index](https://doc.rust-lang.org/error_codes/)
