---
name: rust-stable
description: 使用当前稳定版 Rust 编写、审查、调试和迁移代码，覆盖所有权与生命周期、trait 与泛型、集合与迭代器、错误处理、智能指针、模块和常用标准库。Use for stable Rust language and std questions; begin by checking rustc --version, consult the pinned release reference for version-sensitive APIs, and hand specialized Cargo, async, unsafe, macro, CLI, Web, embedded, testing, review, or style work to the matching Rust skill.
---

# Rust Stable 语言与标准库

把本技能作为 Rust 语言与标准库问题的总入口。先确认项目实际工具链和 MSRV，再选择通用语言资料或转交专项技能；不要仅凭技能名称假定用户正在使用最新版。

## 开始前必须确认

1. 运行 `rustc --version --verbose` 和 `cargo --version`。
2. 检查 `rust-toolchain.toml`、`rust-toolchain` 和 `Cargo.toml` 中的 `rust-version`。
3. 区分三个版本：本机工具链、项目 MSRV、当前官方 stable。
4. 遇到版本敏感 API 时，读取 [当前稳定版基线](references/release-current.md)，并以官方 release notes 与 API 页为最终依据。
5. 如果项目锁定旧版本，只使用该版本已经稳定的语法和 API。

当前离线基线：**Rust 1.97.1，2026-07-16 发布**。这是维护快照，不代表未来会自动更新。

## 能力边界

### 适合处理

- 所有权、借用、生命周期和 move 语义。
- struct、enum、模式匹配、trait、泛型和关联类型。
- `Option`、`Result`、错误传播和自定义错误。
- `Vec`、`String`、`HashMap`、迭代器和闭包。
- `Box`、`Rc`、`Arc`、`Cell`、`RefCell`、`OnceLock`、`LazyLock`。
- 模块、可见性、属性、格式化和常用 `std` I/O。
- 普通编译错误、借用检查错误和稳定版迁移判断。

### 转交专项技能

| 用户意图 | 首选技能 | 必要时联合加载 |
|---|---|---|
| 项目布局、模块树、workspace 结构 | `rust-project-structure` | `rust-cargo-build` |
| Cargo.toml、依赖、feature、profile、发布 | `rust-cargo-build` | `rust-testing` |
| 线程、锁、原子、channel、Tokio | `rust-concurrency` | `rust-stable` |
| 单元测试、集成测试、doctest、覆盖率 | `rust-testing` | `rust-project-structure` |
| 裸指针、内存布局、FFI、Miri | `rust-unsafe-ffi` | `rust-code-review` |
| macro_rules、derive、过程宏 | `rust-macros` | `rust-stable` |
| clap、终端、文件型 CLI | `rust-cli` | `rust-testing` |
| axum、serde、sqlx、reqwest | `rust-web` | `rust-concurrency` |
| no_std、HAL、Cortex-M、RTIC | `rust-embedded` | `rust-unsafe-ffi` |
| 风险、正确性、API 与安全审查 | `rust-code-review` | `rust-style-clippy` |
| rustfmt、Clippy、Edition 迁移 | `rust-style-clippy` | `rust-code-review` |

不要用本技能替代领域技能中的完整工作流。

## 工作流

Step 1. **确定版本边界** — 记录工具链、edition、MSRV 和目标平台。

Step 2. **缩小问题范围** — 判断属于所有权、类型系统、标准库、编译错误还是专项领域。

Step 3. **读取最小资料** — 只打开与问题直接相关的 reference；不要一次加载整个资料集。

Step 4. **实现最小正确方案** — 优先使用稳定标准库、清晰所有权和显式错误传播。

Step 5. **运行质量门禁** — 至少执行 `cargo fmt --check`、`cargo check` 和相关测试。

Step 6. **处理版本差异** — 如果 API 不受 MSRV 支持，选择旧 API、兼容实现或明确提高 MSRV。

Step 7. **转交专项技能** — 进入 async、unsafe、宏、Web、嵌入式等领域后加载对应技能。

## 设计规则

- 优先借用 `&T` / `&mut T`；只有需要所有权转移或独立生命周期时才 clone。
- 用类型表达不变量；优先 enum/newtype，避免布尔参数和无约束字符串。
- 库代码返回结构化错误；应用边界再补充上下文并决定如何展示。
- 优先迭代器和标准集合，但不要为了链式写法牺牲可读性。
- 不把 `unsafe` 当作借用检查器的逃生口；先证明安全抽象无法表达需求。
- 不默认引入第三方 crate；先比较标准库、MSRV、维护成本和供应链风险。
- 不声称某 API 在某版本稳定，除非 release notes 或带 `since` 标记的官方 API 页可以证明。

## 验证门禁

按风险从低到高运行：

```bash
cargo fmt --all --check
cargo check --all-targets --all-features
cargo test --all-targets --all-features
cargo clippy --all-targets --all-features -- -D warnings
```

如果项目不支持 `--all-features` 或包含平台专用目标，记录原因并使用项目定义的 feature/target 矩阵。涉及 unsafe 时增加 `cargo miri test`；涉及 MSRV 时在声明的最低工具链上重复 `cargo check` 和测试。

## 按需读取的资料

### 版本与语言

- [当前稳定版基线](references/release-current.md)：最新版、兼容性说明和更新步骤。
- [所有权与生命周期](references/ownership-lifetimes.md)：借用设计、返回值和生命周期判断。
- [Trait 与泛型](references/traits-generics.md)：bounds、关联类型、trait object 和 API 取舍。
- [模式与惯用法](references/patterns.md)：builder、newtype、RAII、typestate。
- [风格指南](references/style-guide.md)：命名、模块、文档与 API 风格。

### 标准库

- [标准库导航](references/std-index.md)：按任务选择模块和 reference。
- [Vec](references/vec.md)、[String](references/string.md)、[HashMap](references/hashmap.md)。
- [迭代器](references/iterators.md)与[格式化](references/fmt.md)。
- [I/O](references/io.md)、[文件系统](references/fs.md)、[路径](references/path.md)。
- [错误处理](references/errors.md)、[智能指针](references/smart-pointers.md)。
- [内部可变性](references/interior-mutability.md)与[类型转换](references/conversions.md)。

### 可复制示例

- [快速工作流](examples/quickstart-workflows.md)
- [所有权模式](examples/ownership-patterns.md)
- [集合模式](examples/collections-patterns.md)
- [Trait 设计](examples/trait-design-patterns.md)
- [错误处理](examples/error-handling-patterns.md)
- `examples/golden-basic/`：由仓库 CI 编译的最小黄金示例。

## 常见陷阱

1. 把“当前 stable”与项目 MSRV 混为一谈。
2. 只运行 `cargo check`，遗漏测试、示例、bench 或 feature 组合。
3. 为消除借用错误而盲目 `clone`、`Arc<Mutex<_>>` 或 `unsafe`。
4. 在 async 代码中跨 `.await` 持有同步锁或借用。
5. 把带版本号的历史文档描述成持续更新资料。
6. 复制代码片段后不补齐依赖、feature、错误类型和平台约束。

## 官方来源

- [Rust Release Notes](https://doc.rust-lang.org/stable/releases.html)
- [The Rust Programming Language](https://doc.rust-lang.org/book/)
- [Rust Standard Library](https://doc.rust-lang.org/std/)
- [Rust Reference](https://doc.rust-lang.org/reference/)
- [Rust by Example](https://doc.rust-lang.org/rust-by-example/)
- [Rust Edition Guide](https://doc.rust-lang.org/edition-guide/)

## 数据隐私

本技能只提供本地知识、示例和验证流程，不收集、存储或传输用户数据。访问官方文档前遵循用户的网络访问要求。
