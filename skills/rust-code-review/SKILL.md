---
name: rust-code-review
description: Rust 代码审查技能 — 按严重级别检查正确性、unsafe 不变量、错误处理、clone 与分配、锁范围、API 兼容性、测试缺口和依赖风险。Use when reviewing Rust diffs, pull requests, libraries, or unsafe boundaries; report actionable findings before summaries and combine with rust-style-clippy for automated lint gates.
---

# Rust 代码审查

> Rust 代码审查指南，基于 Rust 社区 11,500+ 源码文件模式分析与官方风格指南。

## Capability Boundaries

### ✅ 强项
1. 命名规范与代码风格检查（PascalCase/snake_case/SCREAMING_CASE）
2. 常见反模式识别（冗余 clone、unwrap 滥用、不必要堆分配）
3. unsafe 代码安全审查（safety 文档、不变条件、指针有效区域）
4. 性能热点识别（不必要的分配、锁竞争、序列化开销）
5. API 设计审查（类型安全、错误处理暴露、trait 对象安全）
6. 并发安全审查（数据竞争检测、锁范围、死锁可能性）
7. 依赖安全（cargo-audit、RUSTSEC 公告检查）
8. 文档完整性检查（缺失 doc、doctest 正确性）

### ⚠️ 前置要求
1. 代码可通过 `cargo check` 编译

### ❌ 不适用范围
1. 语法教学 → 使用 `rust-stable` 技能
2. 格式化与 Clippy 配置 → 使用 `rust-style-clippy` 技能

## 何时使用

- "Review 这段 Rust 代码"
- "这段代码有什么问题"
- "帮我检查代码质量"

## Data Privacy

本技能不收集、存储或传输任何用户数据。

---

## 审查清单

### 一、命名与风格

```
✅ type/struct/enum → PascalCase         (UserConfig)
✅ fn/method/variable → snake_case       (get_user_by_id)
✅ const → SCREAMING_SNAKE_CASE          (MAX_RETRY_COUNT)
✅ macro → snake_case                    (vec!, assert_eq!)
✅ 类型参数 → 简洁: T, U, E, K, V
✅ 生命周期 → 'a, 'b, 'ctx, 'env
✅ 错误类型 → XxxError 或 XxxErr
❌ 不要缩写不必要的名称
❌ 不要使用匈牙利命名法
```

### 二、常见反模式

```rust
// ❌ 不必要的 clone
fn process(data: &Vec<String>) {
    let cloned = data.clone();  // 仅读取不需要 clone
    for item in cloned { /* ... */ }
}

// ✅ 改为引用
fn process(data: &[String]) {
    for item in data { /* ... */ }
}

// ❌ unwrap 滥用
let value = map.get(&key).unwrap();

// ✅ 使用 proper 错误处理
let value = map.get(&key).ok_or(MyError::NotFound)?;

// ❌ 大锁范围
let data = arc.lock().unwrap();
// ... 大量不相关代码 ...
drop(data);  // 锁持有太久

// ✅ 缩小锁范围
let item = {
    let data = arc.lock().unwrap();
    data.get(idx).clone()
};

// ❌ String 循环拼接（O(n²)）
let mut s = String::new();
for item in items { s.push_str(item); }  // OK for few items
// 大量 → 用 collect
let s: String = items.iter().flat_map(|s| s.chars()).collect();

// ❌ 不必要的 Box
let b = Box::new(42);  // i32 不需要堆分配

// ❌ 大枚举变体导致栈拷贝
enum Large { A([u8; 1024]), B([u8; 1024]) }
// ✅ 改为 Box
enum Large { A(Box<[u8; 1024]>), B(Box<[u8; 1024]>) }
```

### 三、unsafe 审查清单

```
□ safety 文档是否说明调用者需维护的不变条件
□ unsafe 块是否尽可能小
□ 裸指针是否来自有效分配
□ 指针偏移是否在分配范围内
□ transmute 的类型大小是否一致
□ MaybeUninit::assume_init 前是否已初始化
□ 是否避免了悬垂指针
□ 外部函数调用是否处理了错误（errno/错误码）
□ 全局可变状态是否线程安全
□ 自定义 Send/Sync 实现是否满足安全要求
```

### 四、API 设计审查

```
□ 错误类型是否实现 std::error::Error + Display
□ 是否需要 pub 所有字段/使用 getter
□ 泛型约束是否过松/过紧
□ trait 是否对象安全（object safe）
□ 是否应为 fallible 操作返回 Result 而非 panic
□ 是否需要 `#[must_use]`
□ 默认参数是否合理
□ 是否考虑了并发访问（Send + Sync）
```

### 五、依赖安全

```bash
# 安全检查
cargo audit                    # 已知漏洞
cargo deny check               # 许可 + 漏洞
cargo outdated                 # 过时依赖
cargo update                   # 更新依赖到最新兼容版本

# 检查 RUSTSEC 公告
# https://rustsec.org/
```

## Workflow

Step 1. 检查命名规范 — 确认所有类型/函数/变量遵循 Rust 命名约定
Step 2. 检查 unsafe 安全 — 审查所有 unsafe 块的 safety 文档和不变条件
Step 3. 检查错误处理 — 确认所有 Result 被正确处理，不使用 unwrap()
Step 4. 检查性能 — 识别不必要的 clone、分配、锁竞争
Step 5. 检查 API 设计 — 审查类型安全、trait 对象安全、泛型约束
Step 6. 工具检查 — cargo clippy + cargo fmt --check + cargo audit


## Gotchas

1. `unsafe_op_in_unsafe_fn` 默认 lint 等级取决于 edition；在 crate 根显式 `#![deny(unsafe_op_in_unsafe_fn)]` 并为每个操作使用最小 `unsafe {}`
2. expect() 比 unwrap() 稍好但仍有 panic 风险 - 推荐用 ? 运算符
3. cargo audit 只检查 Cargo.lock - 锁文件过期时结果不准确
4. 潜在数据竞争不总是在编译期暴露 - Mutex 只保证互斥不保证逻辑顺序


## 按需资源

- [审查示例](examples/examples.md)
- [工具与清单速查](references/references.md)
- `examples/golden-review/`：CI 编译的显式错误处理示例

## 官方参考

- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- [Rust Style Guide](https://doc.rust-lang.org/style-guide/)
- [The Rustonomicon — Safety](https://doc.rust-lang.org/nomicon/)
