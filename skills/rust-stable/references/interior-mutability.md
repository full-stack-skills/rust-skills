# 内部可变性

| 类型 | 线程 | 检查时机 | 适用场景 |
|---|---|---|---|
| `Cell<T>` | 单线程 | 无运行时借用 | Copy 值或整体替换 |
| `RefCell<T>` | 单线程 | 运行时借用 | 动态借用、测试替身 |
| `OnceCell<T>` | 单线程 | 单次初始化 | 惰性或延迟初始化 |
| `OnceLock<T>` | 多线程 | 单次初始化 | 全局或共享初始化 |
| `Mutex<T>` | 多线程 | 运行时加锁 | 互斥修改 |
| `RwLock<T>` | 多线程 | 运行时加锁 | 读多写少且经过测量 |

规则：

- 内部可变性把部分错误从编译期移到运行时，应缩小封装边界。
- 不跨 `.await` 持有 `std::sync` 锁；异步场景转到 `rust-concurrency`。
- 避免在锁内执行用户回调、阻塞 I/O 或长时间计算。
- `RefCell` 借用冲突会 panic；尽量缩短 guard 生命周期。

官方来源：

- https://doc.rust-lang.org/std/cell/
- https://doc.rust-lang.org/std/sync/
