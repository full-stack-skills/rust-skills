# Standard Library Task Navigation

| Task | Preferred Module or Type | Local Documentation |
|---|---|---|
| Dynamic Arrays, Sorting, Filtering | `Vec<T>`, slice | [vec.md](vec.md) |
| UTF-8 Text | `String`、`str` | [string.md](string.md) |
| Key-Value Indexing | `HashMap<K, V>`、entry API | [hashmap.md](hashmap.md) |
| Lazy Data Processing | `Iterator` | [iterators.md](iterators.md) |
| Structured Errors | `Result`, `Error`, `From` | [errors.md](errors.md) |
| Buffered I/O | `Read`, `Write`, `BufRead` | [io.md](io.md) |
| Files and Directories | `std::fs` | [fs.md](fs.md) |
| Cross-Platform Paths | `Path`, `PathBuf` | [path.md](path.md) |
| Heap & Shared Ownership | `Box`, `Rc`, `Arc` | [smart-pointers.md](smart-pointers.md) |
| Interior Mutability | `Cell`, `RefCell`, `OnceLock` | [interior-mutability.md](interior-mutability.md) |
| Type Conversion | `From`, `TryFrom`, `AsRef` | [conversions.md](conversions.md) |
| Formatting | `Display`, `Debug` | [fmt.md](fmt.md)

If a task involves thread synchronization, refer to `rust-concurrency`. If it involves raw pointers or layout details, refer to `rust-unsafe-ffi`. When consulting APIs, verify the stable version marker in the documentation page and compare with your project's MSRV.
