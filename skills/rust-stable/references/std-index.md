# 标准库任务导航

| 任务 | 首选模块或类型 | 本地资料 |
|---|---|---|
| 动态数组、排序、过滤 | `Vec<T>`、slice | [vec.md](vec.md) |
| UTF-8 文本 | `String`、`str` | [string.md](string.md) |
| 键值索引 | `HashMap<K, V>`、entry API | [hashmap.md](hashmap.md) |
| 惰性数据处理 | `Iterator` | [iterators.md](iterators.md) |
| 结构化错误 | `Result`、`Error`、`From` | [errors.md](errors.md) |
| 缓冲读写 | `Read`、`Write`、`BufRead` | [io.md](io.md) |
| 文件和目录 | `std::fs` | [fs.md](fs.md) |
| 跨平台路径 | `Path`、`PathBuf` | [path.md](path.md) |
| 堆与共享所有权 | `Box`、`Rc`、`Arc` | [smart-pointers.md](smart-pointers.md) |
| 内部可变性 | `Cell`、`RefCell`、`OnceLock` | [interior-mutability.md](interior-mutability.md) |
| 类型转换 | `From`、`TryFrom`、`AsRef` | [conversions.md](conversions.md) |
| 格式化 | `Display`、`Debug` | [fmt.md](fmt.md) |

如果任务涉及线程同步，转到 `rust-concurrency`；涉及裸指针或布局，转到 `rust-unsafe-ffi`。

查阅 API 时检查页面中的稳定版本标记，并与项目 MSRV 比较。
