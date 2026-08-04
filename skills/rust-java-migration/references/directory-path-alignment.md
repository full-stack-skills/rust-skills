# 目录路径精确对齐规则与实战模式

本文档总结了 Java→Rust 迁移中目录结构与文件路径精确对齐的通用规则、
常见错误模式和验证方法。基于真实 EasyExcel（323 个 Java 类）迁移项目的
实践提炼。

## 一、命名转换规律

| 规则 | Java | Rust | 示例 |
|------|------|------|------|
| **文件名** | PascalCase | snake_case | `XlsListSheetListener.java` → `xls_list_sheet_listener.rs` |
| **类型名** | PascalCase | **PascalCase 不变** | `XlsListSheetListener` → `XlsListSheetListener` |
| **方法名** | camelCase | snake_case | `loadOrCreate` → `load_or_create` |
| **常量名** | UPPER_SNAKE | UPPER_SNAKE | 不变 |
| **包名** | 全小写点分 | 全小写目录 | `com.alibaba.excel.analysis.v03` → `analysis/v03/` |

### camelCase → snake_case 转换陷阱

转换不是简单的"在大写字母前加下划线"。需要处理连续大写字母：

```
DefaultConverterLoader → default_converter_loader（正确）
HttpClientUtil → http_client_util（正确）
URLImageConverter → url_image_converter（正确，不是 u_r_l_image_converter）
```

通用转换函数（Python）：

```python
def to_snake(name):
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    s = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s)
    return s.lower()
```

## 二、目录映射规则

```
Java 包路径                        → Rust 目录路径
com.alibaba.excel                   → easyexcel/src/（crate 根）
com.alibaba.excel.analysis          → analysis/
com.alibaba.excel.analysis.v03      → analysis/v03/
com.alibaba.excel.write.metadata    → write/metadata/
com.alibaba.excel.read.metadata     → read/metadata/
```

**规则**：去掉 Java 的包名前缀（`com.alibaba.excel.`），剩余部分用 `/` 连接即为
Rust 目录路径。

### 同名子包在不同父包下

Java 中有**同名子包在不同父包下**的情况，Rust 必须保持相同的层级关系：

- `read/metadata/` ≠ `write/metadata/` ≠ `metadata/`（三个不同包，不同位置）
- `read/metadata/holder/` ≠ `write/metadata/holder/`（各自在父包下）

**规则**：`metadata` 在 `read` 下和 `write` 下是不同的 Java 包，Rust 必须保持
对应层级，不能合并到一个 `metadata/` 目录。

## 三、文件级 1:1 对应规则

```
Java 文件                              → Rust 文件（精确路径）
EasyExcel.java                         → easyexcel/src/easy_excel.rs
ExcelReader.java                       → easyexcel/src/excel_reader.rs
analysis/v03/XlsSaxAnalyser.java       → analysis/v03/xls_sax_analyser.rs
write/metadata/holder/WriteHolder.java → write/metadata/holder/write_holder.rs
```

### 排除项（Rust 独有，不对应 Java）

以下文件是 Rust 独有的，不参与 Java 对应：

- `mod.rs`（每个目录的模块声明文件）
- `lib.rs`（crate 根）
- `tests.rs` / `missing_tests.rs`（测试文件）
- Rust 独有的实现文件（如 `template/` 模块）

### `package-info.java` 排除

Java 的 `package-info.java` 文件是包级文档声明，不对应任何 Rust 对象文件，
在核对时应排除。

## 四、迁移过程中的 7 个常见错误模式

### 错误 1：路径扁平化

```
❌ metadata/data/CellExtra.java → metadata/cell_extra.rs（去掉了 data/ 子目录）
✅ metadata/data/CellExtra.java → metadata/data/cell_extra.rs（保持层级）
```

**原因**：Rust 开发者倾向于扁平化目录结构，但 Java 的子包是有语义的。
`metadata.data` 是 Java 中一个独立的包，包含所有数据模型类型。

**防范**：核对时检查 Java 文件的完整包路径，不要只看文件名。

### 错误 2：跨包放置

```
❌ context/AnalysisContext.java → event/analysis_context.rs（放到了错误的包）
✅ context/AnalysisContext.java → context/analysis_context.rs（Java 在哪个包，Rust 就在哪个目录）
```

**原因**：开发者按功能归类而非按 Java 包结构归类。AnalysisContext 在逻辑上是
"事件分析"，但 Java 源码中它在 `context` 包下。

**防范**：始终以 Java 源码的 `package` 声明为准，不以功能归类决定目录。

### 错误 3：双重嵌套

```
❌ write/write/excel_builder.rs（Rust 独有的嵌套）
✅ write/excel_builder.rs（与 Java 包结构一致）
```

**原因**：重构过程中遗留的中间状态。Rust 的模块系统允许文件同名时自动
关联（`write.rs` + `write/` 目录），导致意外的嵌套。

**防范**：迁移后检查是否有 `<dir>/<dir>/` 形式的双重嵌套。

### 错误 4：文件名偏离 Java 类名

```
❌ converters/Converter.java → converters/converter_trait.rs（加了 _trait 后缀）
✅ converters/Converter.java → converters/converter.rs（与 Java 类名精确对应）
```

**原因**：Rust 社区习惯用 `_trait` 后缀标记 trait，但与 Java 1:1 对应要求
文件名精确匹配 Java 类名的 snake_case 转换。

**防范**：文件名只做 PascalCase → snake_case 转换，不加任何 Rust 特有后缀。

### 错误 5：holder/ 目录位置错误

```
❌ read/holder/（放在了 read/ 顶层）
✅ read/metadata/holder/（Java 在 read.metadata.holder 包下）
```

**原因**：开发者按 Rust 惯例简化路径，忽略了 Java 的完整包层级。
`read.metadata.holder` 是三级包，对应三级目录 `read/metadata/holder/`。

**防范**：保留 Java 包的所有层级，即使路径看起来"太深"。

### 错误 6：mod.rs 声明遗漏

搬移文件后，父目录的 `mod.rs` 未更新——导致 `E0583: file not found for module`。

**修复规则**：每搬移一个文件到新目录，必须在该目录的 `mod.rs` 中添加：

```rust
pub mod xxx;
pub use xxx::*;
```

**防范**：批量搬移后立即检查每个涉及目录的 `mod.rs`。

### 错误 7：向后兼容重导出断裂

当 `core/mod.rs` 作为薄重导出层时，引用了已搬走的子模块：

```rust
// 错误：converter_trait 已改名为 converter，路径也变了
❌ pub use crate::core::converter_trait::Converter;

// 正确：指向新位置
✅ pub use crate::converters::converter::Converter;
```

**防范**：保留一个 `core/mod.rs` 薄重导出层，但确保所有 `pub use` 指向
正确的新路径。使用 `::` 前缀避免外部 crate 名歧义（如 `::bigdecimal`）。

## 五、通用迁移步骤

### 步骤 1：git mv 搬移文件

```bash
# Java 的 analysis/v03/handlers/ 对应 Rust 的 analysis/v03/handlers/
git mv old/path/file.rs new/path/file.rs
```

搬移时不改代码内容，只改路径。

### 步骤 2：创建/更新 mod.rs

每个新目录需要有 `mod.rs`：

```rust
//! 对应 Java：`com.alibaba.excel.xxx`

pub mod sub_module_a;
pub mod sub_module_b;

pub use sub_module_a::*;
pub use sub_module_b::*;
```

### 步骤 3：批量改写 import 路径

```bash
# 批量替换 crate::old_path → crate::new_path
find easyexcel/src -name "*.rs" -exec perl -pi -e \
  's/crate::core::old_sub::/crate::new_module::/g' {} +
```

### 步骤 4：更新 lib.rs / core/mod.rs 重导出

```rust
// lib.rs
pub mod analysis;
pub mod annotation;
pub mod cache;
// ...

// core/mod.rs（薄重导出层）
pub use crate::metadata::*;
pub use crate::converters::*;
pub use crate::enums::*;
```

### 步骤 5：编译验证

```bash
cargo check -p <crate> --all-features
```

### 步骤 6：全量测试验证

```bash
cargo test --workspace --all-features
```

## 六、验证脚本（可复用）

以下 Python 脚本适用于任何 Java→Rust 迁移项目，只需修改 `java_root`
和 `rust_root` 两个参数：

```python
import os, re

def to_snake(name):
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    s = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s)
    return s.lower()

java_root = "/path/to/java/com/alibaba/excel"
rust_root = "easyexcel/src"

# 递归收集 Java 文件的相对路径
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

# 收集 Rust 文件（排除 mod.rs/tests.rs/lib.rs）
rust_files = set()
for dirpath, dirs, files in os.walk(rust_root):
    for f in sorted(files):
        if f.endswith(".rs") and f not in ("mod.rs", "tests.rs", "missing_tests.rs", "lib.rs"):
            rel = os.path.relpath(os.path.join(dirpath, f), rust_root)
            rust_files.add(rel)

# 精确路径匹配
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

## 七、bigdecimal/url 等外部 crate 歧义问题

当 `core/mod.rs` 做 `pub use bigdecimal::BigDecimal` 时，`bigdecimal` 变成
一个公开模块路径，与外部 crate `bigdecimal` 产生歧义（E0659）。

**修复**：使用 `::` 前缀显式引用外部 crate：

```rust
// core/mod.rs 中
pub use ::bigdecimal::BigDecimal;  // 而不是 pub use bigdecimal::BigDecimal
pub use ::num_bigint::BigInt;
pub use ::url::Url;
```

**同时**：在 `lib.rs` 中也用 `::` 前缀重导出，避免二次歧义：

```rust
// lib.rs 中
pub use ::bigdecimal::BigDecimal;
pub use ::num_bigint::BigInt;
pub use ::url::Url;
```

## 八、proc-macro crate 不能合并

Rust 规定 proc-macro crate（`#[proc_macro_derive]` 等）必须是独立 crate，
不能与普通 lib crate 合并。迁移时：

- 保持 `easyexcel-macro` 为独立 proc-macro crate
- 主 crate 通过 `dependencies` 引用它
- 宏展开时用 `proc_macro_crate::crate_name` 探测消费方 crate 名

## 九、fixtures 不应在 src/ 下

测试数据文件（`.b64`、`.gz`、`.json` fixtures）不应在生产源码目录中。
应放在 `<project>-test/tests/fixtures/` 下，通过 `include_str!` 的相对路径
引用。搬移后更新 `include_str!` 路径即可，不需要改变运行时行为。
