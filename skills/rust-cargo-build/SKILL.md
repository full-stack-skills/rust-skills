---
name: rust-cargo-build
description: 配置和诊断 Rust Cargo 构建，包括 Cargo.toml、依赖来源与版本、features、resolver、profiles、build.rs、workspace、交叉编译、打包和发布。Use when users ask about Cargo manifests, dependency resolution, feature unification, build output, MSRV-aware resolution, cargo commands, or crates.io publishing; hand module layout to rust-project-structure and test design to rust-testing.
---

# Rust Cargo 构建系统

以项目实际 Cargo 版本、MSRV 和 workspace 根清单为准配置构建。详细字段按需读取 references，不要凭记忆生成未经当前 Cargo 验证的配置。

## 开始前检查

```bash
rustc --version --verbose
cargo --version
cargo metadata --no-deps --format-version 1
```

同时检查：

- 根 `Cargo.toml` 是 package 还是 virtual workspace。
- `edition`、`rust-version`、`resolver` 和 `Cargo.lock` 是否一致。
- 依赖来自 crates.io、Git、本地路径还是 workspace inheritance。
- 构建目标、feature 组合、目标平台和发布注册表。

## 能力边界

### 适合处理

- package、lib、bin、example、test、bench 目标。
- 普通、开发、构建、目标平台和 workspace 依赖。
- additive features、可选依赖和 feature unification。
- dev/release/custom profiles 与产物体积优化。
- `build.rs`、原生链接、生成文件和重构建条件。
- workspace members、共享依赖和共享 package 字段。
- target、linker、runner 与交叉编译配置。
- `cargo package`、`cargo publish`、yank 和发布前检查。

### 转交其他技能

- 模块树、crate API 和文件布局 → `rust-project-structure`
- 测试策略、doctest 和覆盖率 → `rust-testing`
- rustfmt、Clippy 和 Edition 迁移 → `rust-style-clippy`
- Rust 语法与标准库 → `rust-stable`

## 工作流

Step 1. **定位根清单** — 用 `cargo locate-project --workspace` 确认生效的 workspace。

Step 2. **声明兼容边界** — 明确 edition、MSRV、支持平台和 feature 策略。

Step 3. **设计依赖** — 优先 crates.io 版本；只在明确需要时使用 Git/path，并限制 feature。

Step 4. **配置构建** — 按需设置 targets、profiles、build script 和 `.cargo/config.toml`。

Step 5. **检查解析结果** — 使用 `cargo metadata`、`cargo tree -e features` 和 `cargo tree -d`。

Step 6. **执行质量门禁** — 运行 fmt、check、test、clippy；对目标平台执行实际 target 构建。

Step 7. **验证包内容** — 发布前运行 `cargo package --list` 和 `cargo package`。

## 关键决策

### Edition、MSRV 与 resolver

- Edition 控制语言兼容模式，不等于编译器最低版本。
- 用 `package.rust-version` 声明 MSRV，并在该工具链上验证。
- resolver 是 workspace 全局设置；依赖清单中的值会被忽略。
- Edition 2021 默认 resolver 2；Edition 2024 默认 resolver 3。
- resolver 3 的核心变化是默认使用 `incompatible-rust-versions = "fallback"`，不是“隔离每个 crate 的 features”。
- virtual workspace 应在 `[workspace]` 中显式声明 resolver。

### Feature

- 把 feature 设计为可加和能力，不要设计互斥 feature。
- 用 `dep:name` 控制可选依赖是否公开成同名 feature。
- 用 `crate/feature` 或 `crate?/feature` 转发依赖 feature。
- 用 `cargo tree -e features` 验证实际启用来源。

### build.rs

- 只生成到 `OUT_DIR`，通过 `include!` 或环境变量使用产物。
- 对每个输入声明 `cargo::rerun-if-changed` 或 `cargo::rerun-if-env-changed`。
- 输出原生链接参数时限制作用目标，避免污染整个 workspace。
- 不在 build script 中下载不可复现资源；改用固定依赖或预生成资产。

### Profile

- 先测量瓶颈，再调整 `lto`、`codegen-units`、`strip` 和 `panic`。
- profile 只在 workspace 根清单生效。
- 不要用 release 构建结果推断 debug 行为，反之亦然。

## 验证命令

```bash
cargo fmt --all --check
cargo metadata --format-version 1 --locked
cargo check --workspace --all-targets --all-features
cargo test --workspace --all-targets --all-features
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo package --list
```

如果 workspace 明确不支持 `--all-features`，建立 feature 矩阵，不要静默跳过。

## 按需读取的资料

- [Manifest 与目标](references/manifest-targets.md)
- [依赖、features 与 resolver](references/dependencies-features-resolver.md)
- [Workspace](references/workspaces.md)
- [Profiles 与产物优化](references/profiles.md)
- [Build scripts](references/build-scripts.md)
- [交叉编译](references/cross-compilation.md)
- [打包与发布](references/publishing.md)
- [命令速查](references/references.md)
- [可复制示例](examples/examples.md)
- `examples/golden-features/`：CI 编译的 feature 示例。

## 常见陷阱

1. 在 virtual workspace 中遗漏 resolver，导致成员 edition 无法替根清单选择 resolver。
2. 误以为关闭某个依赖位置的 feature 能抵消其他位置已经启用的 feature。
3. 同时使用 `include` 和 `exclude`，或没有检查最终发布包内容。
4. 在成员清单配置 profile，以为能覆盖 workspace 根配置。
5. 修改 build script 输入却未声明重跑条件。
6. 把 `Cargo.lock` 策略一概而论：应用通常提交，库仍应在 CI 中验证锁定与最新依赖两种情况。
7. 只在宿主机 `cargo check`，没有真正验证目标平台 linker、系统库和运行时。
8. 使用宽泛 Git branch 或未固定来源，破坏可重复构建。

## 官方来源

- [Cargo Book](https://doc.rust-lang.org/cargo/)
- [Manifest Format](https://doc.rust-lang.org/cargo/reference/manifest.html)
- [Dependency Resolution](https://doc.rust-lang.org/cargo/reference/resolver.html)
- [Features](https://doc.rust-lang.org/cargo/reference/features.html)
- [Build Scripts](https://doc.rust-lang.org/cargo/reference/build-scripts.html)
- [Workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html)
- [Publishing](https://doc.rust-lang.org/cargo/reference/publishing.html)

## 数据隐私

本技能不收集、存储或传输用户数据。执行 `cargo publish`、访问私有 registry 或更改凭据前，必须确认用户授权和目标环境。
