# Profiles 与产物优化

```toml
[profile.release]
lto = "thin"
codegen-units = 1
strip = "symbols"

[profile.release-small]
inherits = "release"
opt-level = "z"
panic = "abort"
```

先定义目标：吞吐、延迟、编译时间、二进制大小、调试能力或 unwind 行为。每次只调整少量参数并测量。

- `lto` 与低 `codegen-units` 可能改善运行时或大小，但增加链接时间。
- `strip` 会影响符号诊断。
- `panic = "abort"` 改变错误恢复与 FFI 行为。
- 依赖覆盖使用 `[profile.<name>.package.<name>]`，仍必须写在根清单。

官方来源：https://doc.rust-lang.org/cargo/reference/profiles.html
