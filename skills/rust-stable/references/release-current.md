# 当前稳定版基线

维护快照：2026-07-20。

## 当前版本

- Stable：Rust 1.97.1（2026-07-16）。
- 当前 Edition：2024。
- Edition 2024 的最低稳定工具链是 Rust 1.85.0。
- Cargo resolver 3 自 Rust 1.84 起可用，并由 Edition 2024 默认选择。

始终通过以下命令确认用户环境，不要把本文件当成运行时探测结果：

```bash
rustc --version --verbose
cargo --version
rustup show active-toolchain
```

## Rust 1.97 重点

- 新增 `cfg(target_has_atomic_primitive_alignment)`。
- 放宽部分 import 中尾随 `self` 的写法。
- 稳定一组整数最高位、最低位和 bit width API。
- Cargo 稳定 `build.warnings` 和 `resolver.lockfile-path` 配置。
- Rust 1.97.1 修复 LLVM 优化相关误编译，应优先于 1.97.0。

使用这些能力前同时检查项目 MSRV。不要因为本机 stable 支持就把新 API 引入旧 MSRV 项目。

## 更新本基线

1. 打开官方 Release Notes 的首个版本条目。
2. 更新版本号、发布日期和本页重点。
3. 检查语言、标准库、Cargo、Clippy、Rustdoc 和兼容性说明。
4. 在最新版与声明的 MSRV 上编译黄金示例。
5. 更新 TRACE/Eval 基线和插件版本。

## 官方来源

- https://doc.rust-lang.org/stable/releases.html
- https://blog.rust-lang.org/releases/
- https://doc.rust-lang.org/edition-guide/
- https://doc.rust-lang.org/cargo/reference/resolver.html
