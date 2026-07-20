---
name: rust-testing
description: Rust 测试与基准测试技能 — 单元测试、集成测试、doctest、cargo test、稳定版 Criterion 基准、覆盖率与失败路径设计。Use when users ask to design, write, run, debug, or assess Rust tests and benchmarks; distinguish stable Criterion from the nightly-only libtest bench attribute, and hand project layout to rust-project-structure.
---

# Rust 测试与基准测试

> 基于 The Rust Programming Language ch 11 与 Rustdoc Book。

## Capability Boundaries

### ✅ 强项
1. 单元测试（#[test]、测试模块 `#[cfg(test)]` 组织）
2. 断言宏（assert!、assert_eq!、assert_ne!、debug_assert!）
3. 测试属性（#[should_panic]、#[ignore]、#[cfg(test)]）
4. 集成测试（tests/ 目录与共享模块）
5. 文档测试（```rust 代码块、# 隐藏行、should_panic、no_run、ignore）
6. cargo test 运行器（过滤、--nocapture、--test-threads、--include-ignored）
7. 稳定版 Criterion 基准，以及明确标注为 nightly-only 的 libtest `#[bench]`
8. 代码覆盖率（cargo-llvm-cov 的使用）

### ⚠️ 前置要求
1. 理解 Rust 模块系统（rust-project-structure）

### ❌ 不适用范围
1. 属性测试（proptest）→ 暂不涉及
2. Mock 对象 → 暂不涉及
3. Rust 语法基础 → 使用 `rust-stable` 技能

## 何时使用

- "写单元测试"
- "集成测试放哪里"
- "文档测试怎么写"
- "性能基准测试"
- "检查代码覆盖率"

## Data Privacy

本技能不收集、存储或传输任何用户数据。

---

## 一、单元测试

```rust
// src/lib.rs
pub fn add(a: i32, b: i32) -> i32 { a + b }
pub fn divide(a: i32, b: i32) -> i32 {
    if b == 0 { panic!("divide by zero"); }
    a / b
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(2, 2), 4);
    }

    #[test]
    fn test_add_negative() {
        assert_eq!(add(-1, 1), 0, "addition with negative");
    }

    #[test]
    #[should_panic(expected = "divide by zero")]
    fn test_divide_by_zero() {
        divide(1, 0);
    }

    #[test]
    #[ignore = "not implemented"]
    fn test_future() { unimplemented!() }
}
```

## 二、集成测试

```text
my-project/
├── Cargo.toml
├── src/lib.rs
└── tests/
    ├── common/          # 测试共享模块
    │   └── mod.rs
    ├── integration_test.rs
    └── api_test.rs
```

```rust
// tests/integration_test.rs — 每个文件是独立 crate
use my_project::add;

#[test]
fn integration_test() {
    assert_eq!(add(1, 2), 3);
}

// tests/common/mod.rs — 共享辅助函数
pub fn setup() { /* ... */ }
```

## 三、文档测试（doctest）

```rust
/// 将两个数相加。
///
/// ```
/// use my_crate::add;
/// assert_eq!(add(2, 3), 5);
/// ```
///
/// ```rust,should_panic
/// my_crate::divide(1, 0);
/// ```
///
/// ```rust,no_run
/// // 编译但不运行
/// loop {}
/// ```
pub fn add(a: i32, b: i32) -> i32 { a + b }
```

## 四、cargo test 命令

```bash
cargo test                    # 运行所有测试
cargo test test_name          # 按名称过滤
cargo test -- --nocapture     # 显示 println 输出
cargo test -- --test-threads=1 # 单线程
cargo test -- --skip test_name # 跳过特定测试
cargo test -- --ignored       # 只运行 #[ignore] 测试
cargo test -- --include-ignored # 包含忽略的
cargo test --doc              # 只运行文档测试
cargo test -p my-crate        # 特定包
```

## 五、基准测试

稳定版项目优先使用 Criterion。内置 libtest `#[bench]` 仍依赖 nightly 的 `#![feature(test)]`，不能写成 stable 默认方案。

```rust
// nightly-only 内置方案（不要用于 stable 门禁）
#![feature(test)]
extern crate test;

#[cfg(test)]
mod benches {
    use test::Bencher;
    use super::*;

    #[bench]
    fn bench_add(b: &mut Bencher) {
        b.iter(|| add(1, 2));
    }
}

// 稳定版使用 criterion
// [dev-dependencies] criterion = { version = "0.5", features = ["html_reports"] }
use criterion::{black_box, Criterion};

fn bench_add(c: &mut Criterion) {
    c.bench_function("add", |b| b.iter(|| add(black_box(1), black_box(2))));
}
criterion_group!(benches, bench_add);
criterion_main!(benches);
```

## 六、代码覆盖率

```bash
# 安装
cargo install cargo-llvm-cov

# 使用
cargo llvm-cov                   # 运行并报告
cargo llvm-cov --open            # 生成 HTML 报告
cargo llvm-cov --lcov --output-path lcov.info  # LCOV 格式
```

## Workflow

Step 1. 准备测试环境 — 确保 cargo test 可用，确认测试类型（单元/集成/文档）
Step 2. 编写单元测试 — 在 #[cfg(test)] 模块中编写 #[test] 函数
Step 3. 添加集成测试 — 在 tests/ 目录创建独立 crate 类型的测试文件
Step 4. 添加文档测试 — 在 /// 注释中嵌入可执行代码块
Step 5. 运行与调试 — cargo test，用 --nocapture 和 --test-threads 控制输出
Step 6. 覆盖率检查 — cargo llvm-cov 检查测试覆盖范围


## Gotchas

1. #[cfg(test)] 模块中的代码不会编译进 release - 测试辅助函数应放在 tests/common/mod.rs
2. 集成测试文件是独立 crate - 不能使用 super:: 或 crate::
3. 文档测试中的 # 行会被隐藏但仍是可执行代码
4. cargo test 默认并行运行 - 共享状态时需要 --test-threads=1
5. #[bench] 需要 #![feature(test)] - stable Rust 需使用 criterion


## 按需资源

- [测试示例](examples/examples.md)
- [测试宏与命令速查](references/references.md)
- `examples/golden-tests/`：CI 编译并运行 doctest 的黄金示例

## 官方参考

- [The Book ch 11](https://doc.rust-lang.org/book/ch11-00-testing.html)
- [Rustdoc Book — doctest](https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html)
- [cargo test](https://doc.rust-lang.org/cargo/commands/cargo-test.html)
- [criterion.rs](https://docs.rs/criterion/)
