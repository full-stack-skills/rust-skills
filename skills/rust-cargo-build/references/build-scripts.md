# Build Scripts

`build.rs` 在编译 package 前运行。只用它完成 Cargo 无法直接表达的本地构建步骤。

```rust
fn main() {
    println!("cargo::rerun-if-changed=proto/schema.proto");
    println!("cargo::rerun-if-env-changed=EXAMPLE_SYS_ROOT");
}
```

规则：

- 生成文件写入 `OUT_DIR`。
- 每个文件和环境输入都声明重跑条件。
- 标准输出只写 Cargo 指令；诊断写 stderr。
- 不依赖当前工作目录以外的隐式路径。
- 原生依赖优先使用成熟 `-sys` crate 和 pkg-config/cmake 约定。
- 生成 Rust 代码时确保输出可复现并由正常编译流程检查。

官方来源：https://doc.rust-lang.org/cargo/reference/build-scripts.html
