# Path 与 PathBuf

- 使用 `Path` 接受借用路径，使用 `PathBuf` 保存或构造拥有路径。
- 不把路径强制转换为 UTF-8；展示时按需要使用 `display()` 或 `to_string_lossy()`。
- 使用 `join` 组合路径，不手工拼接分隔符。
- `canonicalize` 会访问文件系统且可能解析符号链接，不能只当字符串标准化。
- `extension`、`file_name` 和 `parent` 都可能返回 `None`。
- 处理不可信路径时，单纯检查 `..` 不足以建立沙箱边界；还需考虑绝对路径、符号链接和竞态。

官方来源：https://doc.rust-lang.org/std/path/
