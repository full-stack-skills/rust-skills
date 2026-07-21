# Std Module Index — Task → Module Map

> Companion to `SKILL.md`. Use this as the "where do I look first" map. Canonical source: [Rust Standard Library](https://doc.rust-lang.org/std/).

## Numbers

| Need | Type / Module | Notes |
|------|---------------|-------|
| Integers | `i8 i16 i32 i64 i128 isize` / unsigned counterparts | `isize`/`usize` are pointer-width |
| Floats | `f32`, `f64` | IEEE 754; NaN-aware compare via `total_cmp` |
| Non-zero | `NonZeroU8..`, `NonZeroI8..`, `NonZeroUsize` | Layout optimization, infallible `?` |
| Big integers | `num_bigint` crate (BigInt / BigUint) | Third-party |
| Fixed-point | `fixed`, `rust_decimal` crates | Third-party |
| Random | `rand` crate | Third-party (no RNG in std) |
| Parsing | `str::parse::<T>()` / `FromStr` | |

## Collections

| Need | Type | See |
|------|------|-----|
| Default sequence | `Vec<T>` | `collections.md` |
| Key-value, unordered | `HashMap<K, V>` | `collections.md` |
| Key-value, sorted | `BTreeMap<K, V>` | `collections.md` |
| Two-ended queue | `VecDeque<T>` | `collections.md` |
| Linked list | `LinkedList<T>` (rarely) | `collections.md` |
| Priority queue | `BinaryHeap<T>` | `collections.md` |
| Membership, unordered | `HashSet<T>` | `collections.md` |
| Membership, sorted | `BTreeSet<T>` | `collections.md` |

## Strings

| Need | Type | See |
|------|------|-----|
| Function parameter | `&str` | `string-types.md` |
| Owned UTF-8 | `String` | `string-types.md` |
| Platform-native | `OsString` / `OsStr` | `string-types.md` |
| Filesystem | `PathBuf` / `Path` | `string-types.md` |
| Borrowed-or-owned | `Cow<'a, str>` | `string-types.md`, `smart-pointers.md` |
| Format into String | `format!`, `to_string`, `write!` | |
| Print | `println!`, `eprintln!`, `print!` | |

## Files and I/O

| Need | Type / Module | See |
|------|---------------|-----|
| Open / create | `fs::File`, `OpenOptions` | `process-and-fs.md` |
| Read bytes | `io::Read` trait | `io-streams.md` |
| Buffered read | `io::BufReader`, `BufRead` | `io-streams.md` |
| Write bytes | `io::Write` trait | `io-streams.md` |
| Random access | `io::Seek` trait | `io-streams.md` |
| In-memory | `io::Cursor<T>` | `io-streams.md` |
| Stdin/stdout/stderr | `io::stdin()`, `io::stdout()`, `io::stderr()` | `io-streams.md` |
| One-shot read/write | `fs::read`, `fs::read_to_string`, `fs::write` | `process-and-fs.md` |
| Async I/O | `tokio::io` (`AsyncRead`/`AsyncWrite`) | `rust-concurrency` |
| Byte buffers | `bytes::Buf` / `BufMut` (third-party) | `io-streams.md` |

## Threads and Sync

| Need | Type / Module | See |
|------|---------------|-----|
| OS thread | `thread::spawn` | `std-concurrency.md` |
| Borrow across threads | `thread::scope` (Rust 1.63+) | `std-concurrency.md` |
| Channel, single consumer | `sync::mpsc::channel` | `std-concurrency.md` |
| Bounded channel | `sync::mpsc::sync_channel` | `std-concurrency.md` |
| Multi-consumer channel | `crossbeam-channel` crate | `std-concurrency.md` |
| Shared ownership | `sync::Arc<T>` | `smart-pointers.md` |
| Exclusive lock | `sync::Mutex<T>` | `std-concurrency.md` |
| Many readers | `sync::RwLock<T>` | `std-concurrency.md` |
| Barrier / Once / Condvar | `sync::{Barrier, Once, Condvar}` | `std-concurrency.md` |
| Lock-free counters | `sync::atomic::{AtomicBool, AtomicUsize, …}` | `std-concurrency.md` |
| Async runtime | `tokio`, `async-std` | `rust-concurrency` |

## Time

| Need | Type | Notes |
|------|------|-------|
| Span of time | `time::Duration` | `from_secs`, `from_millis`, `from_micros` |
| Monotonic moment | `time::Instant` | Use for benchmarks; never serialized |
| Wall clock | `time::SystemTime` | Can jump; use for timestamps |
| Date / calendar | `chrono` or `time` crate | Third-party (no calendar in std) |
| Sleep / timeout | `thread::sleep`, async `tokio::time` | |

## Path

| Need | Type | See |
|------|------|-----|
| Borrowed path | `path::Path` | `string-types.md` |
| Owned path | `path::PathBuf` | `string-types.md` |
| Components | `Path::components`, `file_name`, `extension` | |

## Network

| Need | Type | Notes |
|------|------|-------|
| TCP client | `net::TcpStream` | Sync; async via `tokio::net` |
| TCP server | `net::TcpListener` | `.incoming()` iterator |
| UDP | `net::UdpSocket` | |
| IP address | `net::IpAddr`, `Ipv4Addr`, `Ipv6Addr` | |
| Socket address | `net::SocketAddr` | |
| Hostname resolution | `lookup_host` | Returns iterator of `SocketAddr` |
| HTTP / TLS | `reqwest`, `hyper`, `rustls` crates | Third-party |

## Memory

| Need | Type / Module | Notes |
|------|---------------|-------|
| Swap / replace | `mem::swap`, `mem::replace`, `mem::take` | |
| Drop and replace | `mem::replace` | |
| Size / align | `mem::size_of`, `mem::align_of` | |
| Initialize with zero | `mem::MaybeUninit::zeroed` | `unsafe` to assume_init |
| Pinning | `pin::Pin` | For self-referential / async |
| Allocator hook | `alloc::Allocator` trait | `Global` default; custom allocators stable |

## Conversions

| Trait | Direction | Notes |
|-------|-----------|-------|
| `From<T>` / `Into<U>` | Infallible, ref-to-ref or owned | `Into` is reciprocal of `From` |
| `TryFrom<T>` / `TryInto<U>` | Fallible, returns `Result` | |
| `AsRef<T>` / `AsMut<T>` | Cheap reference-to-reference | For function params |
| `Borrow<T>` / `ToOwned` | Borrowed vs owned (HashMap keys, Cow) | |
| `FromStr` | `&str → T` via `parse` | |

## Formatting

| Need | Use |
|------|-----|
| `Display` / `Debug` | `format!("{}", x)` / `format!("{:?}", x)` |
| `write!` / `writeln!` | Into any `Write` |
| Custom format | impl `fmt::Display` / `fmt::Debug` |
| Width / precision / hex / binary | `{}` format specs |
| Ad-hoc lists | `format!("{:?}", vec)` |

## Iterators

| Need | Use | See |
|------|-----|-----|
| Borrow / mutate / consume | `iter` / `iter_mut` / `into_iter` | `iterators.md` |
| Custom iterator | impl `Iterator` | `iterators.md` |
| Infinite / finite constructors | `iter::{once, empty, repeat, from_fn, successors}` | `iterators.md` |
| Collect to collection | `Iterator::collect` | `iterators.md` |

## Macros (built into std prelude)

| Macro | Use |
|-------|-----|
| `vec![a, b, c]` | Build `Vec` |
| `format!(...)` | Build `String` |
| `println!` / `eprintln!` | Print line to stdout / stderr |
| `print!` / `eprint!` | Print without newline |
| `write!` / `writeln!` | Into any `Write` |
| `panic!` / `unreachable!` / `todo!` / `unimplemented!` | Abort-equivalent |
| `assert!` / `assert_eq!` / `assert_ne!` / `debug_assert!*` | Tests |
| `cfg!` / `env!` / `include!` / `include_str!` / `include_bytes!` | Compile-time |

## Hashing

| Need | Use |
|------|-----|
| Default hasher | `std::collections::hash_map::DefaultHasher` (SipHash, deterministic) |
| Randomized hasher | `std::collections::hash_map::RandomState` (default for `HashMap`) |
| 64-bit digest | `DefaultHasher::new()` then `.finish()` |
| Cryptographic | `sha2`, `blake3` crates |

## FFI

| Need | Type | Notes |
|------|------|-------|
| C string (owned) | `ffi::CString` | Nul-terminated, owned |
| C string (borrowed) | `ffi::CStr` | From raw pointer |
| OS-native | `ffi::OsString` / `OsStr` | |
| Raw pointer | `*const T` / `*mut T` | Not `Send`/`Sync` |
| `extern "C"` | function declarations | `unsafe` to call |
| Detailed unsafe / FFI | `rust-unsafe-ffi` skill | |

## Process and env

| Need | Use | See |
|------|-----|-----|
| Run a command | `process::Command` | `process-and-fs.md` |
| Stream stdin/stdout | `Stdio::piped` + `Child` | `process-and-fs.md` |
| Exit code | `process::ExitStatus` | `process-and-fs.md` |
| Current process exit | `process::exit(code)` | |
| Env vars / args | `env::var`, `env::args`, `env::current_dir` | `process-and-fs.md` |

## Markers for recent stable and nightly

| API | Stabilized |
|-----|-----------|
| `thread::scope` | Rust 1.63+ |
| `OnceLock<T>` | Rust 1.70+ |
| `LazyLock<T>` | Rust 1.80+ |
| `OnceCell<T>` (in std) | Rust 1.70+ |
| `impl Trait` in associated types | Rust 1.79+ |
| `let ... else` | Rust 1.65+ |
| `core::array::from_fn` | Rust 1.63+ |
| Exit status `.signal()` on Unix | nightly (use `ExitStatusExt`) |

If an API is not in this list, assume it is long-stable. For nightly-only behavior, check the [`unstable book`](https://doc.rust-lang.org/nightly/unstable-book/) before relying on it.

## Reference

- [Rust Standard Library](https://doc.rust-lang.org/std/)
- [std::collections](https://doc.rust-lang.org/std/collections/index.html) / [std::sync](https://doc.rust-lang.org/std/sync/index.html) / [std::cell](https://doc.rust-lang.org/std/cell/index.html)
- [std::io](https://doc.rust-lang.org/std/io/index.html) / [std::fs](https://doc.rust-lang.org/std/fs/index.html) / [std::process](https://doc.rust-lang.org/std/process/index.html)
- [std::net](https://doc.rust-lang.org/std/net/index.html) / [std::path](https://doc.rust-lang.org/std/path/index.html) / [std::time](https://doc.rust-lang.org/std/time/index.html)
- [std::env](https://doc.rust-lang.org/std/env/index.html) / [std::ffi](https://doc.rust-lang.org/std/ffi/index.html) / [std::mem](https://doc.rust-lang.org/std/mem/index.html)
