# Concurrency References

## Key std types
| Type | Module | Use |
|------|--------|-----|
| `thread::spawn` | std::thread | OS threads |
| `Mutex<T>` | std::sync | Mutual exclusion |
| `Arc<T>` | std::sync | Atomic ref counting |
| `mpsc` | std::sync::mpsc | Multi-producer channel |
| `AtomicU64` | std::sync::atomic | Lock-free atomics |
| `tokio` | tokio crate | Async runtime |
| `rayon` | rayon crate | CPU-bound data parallelism |
| `crossbeam` | crossbeam crates | Channels, queues, deques, scoped threads |
| `loom` | loom crate | Concurrent execution model testing |

## Further reading
- std::thread docs: https://doc.rust-lang.org/std/thread/
- std::sync docs: https://doc.rust-lang.org/std/sync/
- Tokio tutorial: https://tokio.rs/tokio/tutorial
- Rayon docs: https://docs.rs/rayon/
- Crossbeam docs: https://docs.rs/crossbeam/
- Loom docs: https://docs.rs/loom/
