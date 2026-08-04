# 目录路径对齐验证与迁移后核对

本文档是 `rust-java-migration/references/directory-path-alignment.md` 的测试
与验证配套。当迁移完成后，如何验证目录路径 1:1 对应、语义功能 100% 覆盖、
以及常见回归问题的检测。

## 一、精确路径核对脚本（迁移后第一步）

迁移完成后，必须验证 Rust 文件路径与 Java 包路径精确 1:1 对应。
这是 `MISPLACED` → `IMPLEMENTED` 的前置条件。

### 核对脚本

```python
import os, re

def to_snake(name):
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    s = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s)
    return s.lower()

java_root = "/path/to/java/com/example/module"
rust_root = "src"

java_files = {}
for dirpath, dirs, files in os.walk(java_root):
    for f in sorted(files):
        if f.endswith(".java") and f != "package-info.java":
            rel = os.path.relpath(os.path.join(dirpath, f), java_root)
            java_name = f.replace(".java", "")
            snake = to_snake(java_name)
            java_dir = os.path.dirname(rel)
            expected = f"{java_dir}/{snake}.rs" if java_dir else f"{snake}.rs"
            java_files[expected] = rel

rust_files = set()
for dirpath, dirs, files in os.walk(rust_root):
    for f in sorted(files):
        if f.endswith(".rs") and f not in ("mod.rs", "tests.rs", "missing_tests.rs", "lib.rs"):
            rel = os.path.relpath(os.path.join(dirpath, f), rust_root)
            rust_files.add(rel)

matched = sum(1 for ep in java_files if ep in rust_files)
wrong = []
for ep, jp in java_files.items():
    if ep not in rust_files:
        fn = os.path.basename(ep)
        found = [rf for rf in rust_files if os.path.basename(rf) == fn]
        actual = found[0] if found else "MISSING"
        wrong.append((jp, ep, actual))

print(f"精确匹配: {matched}/{len(java_files)}")
print(f"不一致: {len(wrong)}")
for jp, ep, actual in wrong:
    print(f"  {jp} → 期望 {ep}，实际 {actual}")
```

### 验证标准

- **323/323 = 100% 精确匹配** = 路径完全对齐
- **文件名匹配但路径不同** = `MISPLACED`，需要修正
- **完全缺失** = `MISSING`，需要创建

### 测试中的使用

将此脚本集成到 xtask migration audit 测试中，使 CI 能自动检测路径漂移：

```rust
// xtask/tests/spawn_binary.rs
#[test]
fn xtask_migration_audit_strict_accepts_flag_alias() {
    // 读取 file-map.csv，检查每行的 rust_file 是否在磁盘上存在
    // 任何缺失即为测试失败
}
```

## 二、目录搬移后的 6 类编译错误检测

文件搬移后常见的编译错误模式，以及它们的检测和修复方法：

### 类型 1：E0583 file not found for module（50+ 错误）

**原因**：文件移到了新目录，但父 `mod.rs` 仍引用旧路径。

**检测**：
```bash
cargo check -p <crate> --all-features 2>&1 | grep "E0583"
```

**修复**：在每个新目录创建 `mod.rs`，声明所有子模块。

### 类型 2：E0761 file for module found at both

**原因**：同一目录下同时存在 `xxx.rs` 和 `xxx/mod.rs`。

**检测**：
```bash
cargo check -p <crate> --all-features 2>&1 | grep "E0761"
```

**修复**：删除冲突文件，保留 `mod.rs`。

### 类型 3：E0405 cannot find trait

**原因**：文件改名后（如 `converter_trait.rs` → `converter.rs`），glob 重导出链断裂。

**检测**：
```bash
cargo check -p <crate> --all-features 2>&1 | grep "E0405"
```

**修复**：更新 `mod.rs` 的 `pub use` 声明。

### 类型 4：E0425 cannot find type

**原因**：类型移到了新目录但 `core/mod.rs` 的重导出路径未更新。

**检测**：
```bash
cargo check -p <crate> --all-features 2>&1 | grep "E0425"
```

**修复**：在 `core/mod.rs` 中添加 `pub use crate::new_path::TypeName;`。

### 类型 5：E0659 ambiguous

**原因**：`pub use bigdecimal::BigDecimal` 在 `mod.rs` 中让 `bigdecimal` 变成
模块路径，与外部 crate 产生歧义。

**检测**：
```bash
cargo check -p <crate> --all-features 2>&1 | grep "E0659"
```

**修复**：使用 `::` 前缀：`pub use ::bigdecimal::BigDecimal;`

### 类型 6：测试 fixture 路径断裂

**原因**：fixtures 搬移后 `include_str!` 的相对路径失效。

**检测**：
```bash
cargo test -p <crate> --all-features 2>&1 | grep "couldn't read"
```

**修复**：更新 `include_str!` 的相对路径，或用 `env!("CARGO_MANIFEST_DIR")`
构建绝对路径。

## 三、语义功能覆盖验证

### Golden 测试（Java 语义对拍）

Golden 测试是验证 Java→Rust 语义等价的最强证据：

1. **Java golden exporter**：运行 Java 项目生成期望输出（JSON/XLSX/CSV）
2. **Rust 实现**：运行相同输入，生成实际输出
3. **逐 case 比对**：每个 case 的输出必须 `MATCH`

```rust
#[test]
fn golden_simple_data_xlsx_write() {
    // 读取 Java 生成的期望 JSON
    let expected = include_str!(
        "../../../easyexcel-test/tests/golden/simple_data_xlsx_write.expected.json"
    );
    // 运行 Rust 实现
    let actual = run_rust_write(...);
    // 逐字段比对
    assert_eq!(normalize(actual), normalize(expected));
}
```

### 覆盖率验证（cargo-llvm-cov）

```bash
# 在 CI 环境中运行
cargo llvm-cov --workspace --all-features
```

**门禁规则**：
- 95% fail-under 作为回归保护（不是 100%，因为存在数学不可达的残差）
- 残差需逐行验证为不可达（测试代码 `?` 错误边、防御分支、derive 属性行）

### xtask Migration Audit

`xtask` 测试验证 `file-map.csv` 中的每条 Rust 路径在磁盘上存在：

```bash
cargo test -p xtask --test spawn_binary xtask_migration_audit_strict_accepts_flag_alias
```

**门禁规则**：任何 `missing rust file` 都为测试失败。

## 四、回归测试检查清单

迁移完成后，依次验证以下检查项：

| # | 检查项 | 命令 | 通过标准 |
|---|---|---|---|
| 1 | 编译检查 | `cargo check --workspace --all-features --all-targets` | 0 error |
| 2 | 格式检查 | `cargo fmt --all -- --check` | 0 diff |
| 3 | Clippy 检查 | `cargo clippy --workspace --all-features --all-targets -- -D warnings` | 0 warning |
| 4 | 全量测试 | `cargo test --workspace --all-features` | 0 failed |
| 5 | Golden 测试 | `cargo test -p <project>-test --test java_golden_tests` | 88/88 passed |
| 6 | 路径核对 | Python 核对脚本 | 323/323 = 100% |
| 7 | xtask audit | `cargo test -p xtask --test spawn_binary` | 0 missing |
| 8 | 覆盖率 | `cargo llvm-cov --workspace --all-features` | ≥ 95% |

## 五、file-map.csv 同步验证

每次文件搬移后，`docs/migration/file-map.csv` 必须同步更新。
xtask 测试会验证 CSV 中每条 `rust_file` 路径在磁盘上存在。

### 更新脚本

```python
import csv, os, re

def to_snake(name):
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    s = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s)
    return s.lower()

# 构建 Java → 期望 Rust 路径映射
java_to_expected = {}
for dirpath, dirs, files in os.walk(java_root):
    for f in files:
        if f.endswith(".java") and f != "package-info.java":
            rel = os.path.relpath(os.path.join(dirpath, f), java_root)
            snake = to_snake(f.replace(".java", ""))
            java_dir = os.path.dirname(rel)
            expected = f"easyexcel/src/{java_dir}/{snake}.rs" if java_dir else f"easyexcel/src/{snake}.rs"
            java_col = f"easyexcel-core/src/main/java/com/alibaba/excel/{rel}"
            java_to_expected[java_col] = expected

# 更新 file-map.csv
with open('docs/migration/file-map.csv', 'r') as f:
    rows = list(csv.reader(f))
rust_col = rows[0].index('rust_file')
for row in rows[1:]:
    if row[0] in java_to_expected:
        row[rust_col] = java_to_expected[row[0]]
```

## 六、fixtures 路径迁移验证

fixtures 搬移后，`include_str!` 的相对路径必须正确：

```bash
# 检测断裂的 include_str! 路径
cargo test -p <crate> --all-features 2>&1 | grep "couldn't read"
```

**修复规则**：
- 计算从源文件到 fixtures 目录的相对路径
- 对于深层嵌套文件，可能需要 `../../../` 多级回溯
- 或使用 `env!("CARGO_MANIFEST_DIR")` 构建绝对路径

## 七、性能回归验证

目录迁移不应引入性能回归：

```bash
# 百万行基准
cargo run --release -p <crate> --example million_rows -- 1000000 /tmp/bench.xlsx
```

**验证标准**：写/读时间与迁移前在同一量级（±10% 以内）。
