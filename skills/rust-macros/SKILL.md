---
name: rust-macros
description: Rust 宏系统技能 — macro_rules、TT muncher、derive、属性宏、函数式过程宏、syn、quote、hygiene 和展开测试。Use when creating, debugging, or reviewing Rust macros and compile-time DSLs; use stable cargo-expand and trybuild by default, and hand ordinary trait or generic design to rust-stable.
---

# Rust 宏系统

> 基于 The Rust Programming Language ch 19.6 与 Rust Reference（Macros By Example & Procedural Macros）。

## Capability Boundaries

### ✅ 强项
1. 声明宏（macro_rules!）全部片段类型符与重复模式
2. TT muncher 模式（递归处理 Token Tree）
3. 过程宏三类（derive、attribute、function-like）
4. syn crate（DeriveInput/ItemFn/Type 等语法解析）
5. quote crate（TokenStream 生成、#var 插值）
6. 宏调试（稳定版优先 `cargo expand`、编译错误测试和最小复现；nightly 可选 `trace_macros!`）
7. 宏 hygiene 与 $crate 引用

### ⚠️ 前置要求
1. 熟悉 Rust 语法（`rust-stable`）

### ❌ 不适用范围
1. 基础 derive 使用（如 `#[derive(Debug)]`）→ 使用 `rust-stable` 技能
2. 宏在 CLI/Web 项目中应用 → 对应领域技能

## 何时使用

- "写一个 macro_rules!" / "声明宏怎么写"
- "过程宏和声明宏的区别"
- "自定义 derive 宏"
- "减少重复代码"

## Data Privacy

本技能不收集、存储或传输任何用户数据。

---

## 一、声明宏（macro_rules!）

```rust
// 基础模式
macro_rules! my_vec {
    // 匹配空
    () => { Vec::new() };

    // 匹配 `$elem; $n` — 重复
    ($elem:expr; $n:expr) => {{
        let mut v = Vec::with_capacity($n);
        v.resize($n, $elem);
        v
    }};

    // 匹配逗号分隔列表 — $()* 重复
    ($($x:expr),* $(,)?) => {{
        let mut v = Vec::new();
        $(v.push($x);)*
        v
    }};
}

// 片段类型符
// expr → 表达式       ident → 标识符     ty → 类型
// pat → 模式         stmt → 语句       block → 代码块
// item → 项          meta → 属性       tt → token 树（最通用）
// lifetime → 生命周期  literal → 字面量

// 重复操作符
// $()* → 零或多次    $()+ → 一次或多次  $()? → 零或一次

// assert_eq! 模式（来自标准库）
macro_rules! assert_eq {
    ($left:expr, $right:expr $(,)?) => {
        match (&$left, &$right) {
            (left_val, right_val) => {
                if !(*left_val == *right_val) {
                    $crate::panicking::assert_failed(
                        $crate::panicking::AssertKind::Eq,
                        &*left_val, &*right_val,
                        $crate::option::Option::None,
                    );
                }
            }
        }
    };
    ($left:expr, $right:expr, $($arg:tt)+) => { /* ... */ };
}
```

## 二、TT Muncher 模式

```rust
// 递归解析 token 序列
macro_rules! parse_args {
    // 基本情况
    () => { Vec::<String>::new() };

    // 递归步骤：`--flag value, rest...`
    (--$name:ident $val:expr $(, $($rest:tt)*)?) => {{
        let mut v = parse_args!($($($rest)*)?);
        v.push(format!("--{}={}", stringify!($name), $val));
        v
    }};
}
```

## 三、过程宏

```rust
// Cargo.toml — 过程宏 crate 配置
// [lib]
// proc-macro = true
//
// [dependencies]
// syn = { version = "2", features = ["full"] }
// quote = "1"
// proc-macro2 = "1"

use proc_macro::TokenStream;
use syn::{parse_macro_input, DeriveInput, ItemFn};
use quote::quote;

// 1. derive 宏
#[proc_macro_derive(MyTrait)]
pub fn my_derive(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    let name = &input.ident;

    let expanded = quote! {
        impl MyTrait for #name {
            fn method(&self) {
                println!("MyTrait for {}", stringify!(#name));
            }
        }
    };
    TokenStream::from(expanded)
}

// 2. 属性宏
#[proc_macro_attribute]
pub fn log_call(_attr: TokenStream, item: TokenStream) -> TokenStream {
    let input = parse_macro_input!(item as ItemFn);
    let name = &input.sig.ident;

    let expanded = quote! {
        fn #name() {
            println!("Called: {}", stringify!(#name));
            #input
        }
    };
    TokenStream::from(expanded)
}

// 3. 函数式宏
#[proc_macro]
pub fn sql(input: TokenStream) -> TokenStream {
    let sql_str = input.to_string();
    let expanded = quote! {
        format!("EXPLAIN {sql_str}")
    };
    TokenStream::from(expanded)
}
```

## 四、宏调试与 Hygiene

```rust
// 启用宏跟踪（nightly）
#![feature(trace_macros)]

fn main() {
    trace_macros!(true);
    let v = vec![1, 2, 3];
    trace_macros!(false);
}

// $crate — 始终引用宏定义所在的 crate
// 确保 macro 中使用 $crate:: 而非绝对路径
macro_rules! make_error {
    () => {
        $crate::MyError::new()
    };
}

// stable 项目优先运行：cargo expand --test <test-name>
```

## Workflow

Step 1. 确定宏类型 — 选择声明宏（macro_rules!）还是过程宏（derive/attribute/function-like）
Step 2. 编写宏 — 声明宏用匹配+替换；过程宏用 syn 解析 + quote 生成
Step 3. 测试宏展开 — stable 优先使用 cargo expand、doctest 和 trybuild；仅在 nightly 诊断时使用 trace_macros!()
Step 4. 处理 hygiene — 使用 $crate 避免命名冲突
Step 5. 完善文档 — 为宏添加文档注释和 doctest 示例
Step 6. 发布 — 过程宏需独立 proc-macro crate，测试不同上下文的行为


## Gotchas

1. 声明宏中 $crate 必须用于引用外部 crate - 直接用 crate 名会导致 scope 冲突
2. 过程宏 crate 只能导出 proc_macro - 不能同时包含其他 pub 函数作为库 API
3. macro_rules! 匹配规则顺序敏感 - 通用匹配应在最后
4. proc_macro_derive 注册名是 #[proc_macro_derive(MyTrait)] 中的 MyTrait - 函数名无关
5. 过程宏应保留 `Span` 并生成针对输入位置的 `syn::Error`，不要用字符串拼接 TokenStream


## 按需资源

- [宏示例](examples/examples.md)
- [宏概念速查](references/references.md)
- `examples/golden-macro/`：CI 编译的声明宏示例

## 官方参考

- [The Book ch 19.6](https://doc.rust-lang.org/book/ch19-06-macros.html)
- [Rust Reference — Macros By Example](https://doc.rust-lang.org/reference/macros-by-example.html)
- [Rust Reference — Procedural Macros](https://doc.rust-lang.org/reference/procedural-macros.html)
- [syn crate](https://docs.rs/syn/)
- [quote crate](https://docs.rs/quote/)
