# 交叉编译

## 基本流程

```bash
rustup target add aarch64-unknown-linux-gnu
cargo build --target aarch64-unknown-linux-gnu
```

Rust target 安装不等于系统 linker、C compiler 和目标系统库已经就绪。`.cargo/config.toml` 可配置：

```toml
[target.aarch64-unknown-linux-gnu]
linker = "aarch64-linux-gnu-gcc"
```

验证：

- `rustc --print target-list`
- `cargo build --target <triple>`
- 检查产物架构和动态依赖。
- 在目标设备、模拟器或可信 runner 上执行测试。

不要通过“宿主机 cargo check 成功”宣称交叉编译或目标运行成功。

官方来源：https://doc.rust-lang.org/cargo/reference/config.html
