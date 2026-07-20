# std::fs

## 常用操作

- 小文件：`fs::read`、`fs::read_to_string`、`fs::write`
- 流式大文件：`File` 配合 `BufReader` / `BufWriter`
- 目录：`create_dir_all`、`read_dir`、`remove_dir`
- 元数据：`metadata`、`symlink_metadata`
- 原子替换：在同一文件系统写临时文件、flush/sync 后 rename

## 规则

- 不要在库代码中吞掉 `io::Error`；保留路径和操作上下文。
- 处理符号链接时明确使用 `metadata` 还是 `symlink_metadata`。
- 不假设 `read_dir` 顺序稳定；需要确定性时显式排序。
- 删除、覆盖和递归操作前验证精确目标，避免宽泛 glob。
- 安全敏感代码警惕检查后使用的 TOCTOU 竞争。

官方来源：https://doc.rust-lang.org/std/fs/
