---
name: rust-project-structure
description: Rust 项目结构与脚手架技能 — package、crate、模块树、可见性、re-export 和 workspace 布局。Use when creating or reorganizing Rust projects, public module boundaries, multi-crate workspaces, or file layouts; hand manifest, dependency, feature, and build settings to rust-cargo-build.
---

# Rust 项目结构与脚手架

> 基于 The Rust Programming Language ch 7 与 The Rust Reference ch 7（Items & Modules）。

## Capability Boundaries

### ✅ 强项
1. 包（package）与 crate（二进制/库）的概念与约定
2. 模块文件系统布局（src/lib.rs、src/main.rs、子模块文件/目录）
3. mod 声明与模块嵌套
4. pub 可见性体系（pub、pub(crate)、pub(super)、pub(self)）
5. use 路径模式（绝对/相对、嵌套 `A::{B,C}`、glob `A::*`、别名 `A as B`、re-export）
6. 外部 crate 引用
7. 工作空间（workspace）多包项目布局
8. 条件编译与 cfg 属性
9. 项目模板与脚手架（cargo new、cargo-generate）

### ⚠️ 前置要求
1. 理解 Rust 所有权与模块基础（可参考 `rust-stable` 技能）

### ❌ 不适用范围
1. Cargo.toml 配置 → 使用 `rust-cargo-build` 技能
2. Rust 语法基础 → 使用 `rust-stable` 技能
3. 测试组织 → 使用 `rust-testing` 技能

## 何时使用

- "组织 Rust 项目结构"
- "模块之间怎么引用"
- "pub 可见性规则"
- "多 crate 工作空间布局"

## Data Privacy

本技能不收集、存储或传输任何用户数据。

---

## 一、包与 Crate

```rust
// package 二进制 + 库混合布局
my-project/
├── Cargo.toml
├── src/
│   ├── lib.rs        # 库 crate 根
│   └── main.rs       # 二进制 crate 根

// 多二进制 crate 布局
my-project/
├── Cargo.toml
└── src/
    ├── lib.rs
    ├── main.rs
    └── bin/
        ├── other.rs
        └── another.rs  // 每个 bin/ 文件独立二进制
```

## 二、模块系统

```rust
// lib.rs — 声明模块
pub mod front_of_house;      // 从 front_of_house.rs 或 front_of_house/mod.rs 加载
mod back_of_house;           // 私有模块，仅当前 crate 可见
pub(crate) mod utils;        // 对整个 crate 公开但外部不可见

// front_of_house.rs
pub mod hosting;             // 从 hosting.rs 加载

// front_of_house/hosting.rs
pub fn add_to_waitlist() {}
fn seat_at_table() {}        // 默认私有
```

## 三、可见性体系

```rust
pub fn public_fn() {}             // 外部可见
fn private_fn() {}                // 默认私有（当前模块 + 子模块）
pub(crate) fn crate_visible() {}  // 整个 crate 可见
pub(super) fn parent_visible() {} // 父模块可见
pub(self) fn module_visible() {}  // 当前模块可见（等价默认）
pub(in crate::foo) fn restricted() {}  // 指定路径可见（nightly）
```

## 四、use 路径模式

```rust
// 绝对路径 — crate:: 或 根
use crate::front_of_house::hosting;
use std::collections::HashMap;

// 相对路径 — self:: 或 super::
use self::back_of_house::Cook;
use super::parent_module::helper;

// 嵌套路径
use std::{cmp::Ordering, io};
use std::io::{self, Write};

// Glob（谨慎使用）
use std::collections::*;

// 别名
use std::fmt::Result as FmtResult;

// 重新导出（pub use）
pub use crate::front_of_house::hosting;
// 外部现在可以通过 my_crate::hosting 访问
```

## 五、工作空间（Workspace）

```toml
# Cargo.toml (workspace root)
[workspace]
members = [
    "crates/core",
    "crates/utils",
    "app",
]
resolver = "3"
```

```text
my-workspace/
├── Cargo.toml          # workspace 定义
├── crates/
│   ├── core/
│   │   ├── Cargo.toml  # [package] + [dependencies]
│   │   └── src/lib.rs
│   └── utils/
│       ├── Cargo.toml
│       └── src/lib.rs
├── app/
│   ├── Cargo.toml
│   └── src/main.rs
└── Cargo.lock          # 共享 lock 文件
```

```toml
# crates/utils/Cargo.toml — 引用 workspace 内 crate
[dependencies]
core = { path = "../core" }
```

## 六、条件编译

```rust
#[cfg(target_os = "linux")]
fn only_linux() {}

#[cfg(not(target_os = "windows"))]
fn not_windows() {}

#[cfg(feature = "serde")]
fn with_serde() {}

// cfg! 宏（运行时检查）
if cfg!(target_os = "linux") {
    println!("Running on Linux");
}

// cfg_attr
#[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
struct Config;
```

## 七、项目脚手架

```bash
cargo new my-app              # 二进制项目
cargo new my-lib --lib        # 库项目
cargo init                    # 当前目录初始化
cargo new --vcs none          # 不初始化 git

# 使用模板（需要 cargo-generate）
cargo install cargo-generate
cargo generate --git https://github.com/rust-unofficial/patterns.git
```

## Workflow

Step 1. 确认项目类型 — 单 crate 包、多 crate 包还是工作空间
Step 2. 选择命名约定 — 按项目用途确定二进制和库名称（snake_case）
Step 3. 规划模块层次 — 从 lib.rs 开始按功能域拆分模块文件和目录
Step 4. 设计可见性接口 — 确定哪些类型/函数是 pub/pub(crate) 还是私有
Step 5. 组织路径与 use — 配置 use 导入，确保不违反模块可见性规则
Step 6. 验证 — cargo check 确认编译通过，检查 IDE 模块导航正常


## Gotchas

1. crate:: vs ::crate_name:: - crate:: 引用当前 crate 根；::other_crate:: 是绝对路径引用外部 crate
2. pub(crate) 在 2015 edition 中不可用 - 需要 edition 2018+
3. mod.rs 已弃用 - 2018 edition 起推荐 module_name.rs 而非 module_name/mod.rs
4. workspace resolver 是全局设置；Edition 2021 默认 resolver 2，Edition 2024 默认 resolver 3
5. #[path] 属性绕过文件系统约定 - 使用后模块路径不再遵循默认文件树


## 按需资源

- [布局示例](examples/examples.md)
- [概念速查](references/references.md)
- `examples/golden-layout/`：CI 编译的模块边界示例

## 官方参考

- [The Book ch 7](https://doc.rust-lang.org/book/ch07-00-managing-growing-projects-with-packages-crates-and-modules.html)
- [Rust Reference ch 7 (Items)](https://doc.rust-lang.org/reference/items.html)
- [Rust Reference ch 7.2 (Modules)](https://doc.rust-lang.org/reference/items/modules.html)
- [Cargo Workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html)
