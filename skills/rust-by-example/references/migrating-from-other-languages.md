# Migrating From Other Languages

> Concept mapping for engineers coming from Java, Python, Go, C++, or JavaScript. Each pair shows a 3-line before/after. For deep semantics, see `rust-stable`; for std API selection, see `rust-stdlib`.

## Quick index

| From | Top 3 shocks |
|------|--------------|
| Java | traits vs interfaces, no `null`, ownership instead of GC |
| Python | static types everywhere, RAII replaces `with`, no decorators-as-syntax |
| Go | `Result` instead of multi-return, traits instead of `interface{}`, borrow checker |
| C++ | ownership built-in, `dyn Trait` vs `virtual`, no default move ctor |
| JavaScript | `Future` is lazy, no `undefined`, `Option<T>` replaces nullishness |

---

## Java

| Java | Rust | Note |
|------|------|------|
| `interface` / `abstract class` | `trait` (with default methods) | same mechanism |
| `implements` | `impl Trait for Type` | impl is separate from the type |
| `Optional<T>` | `Option<T>` | Rust's is a value, not boxed |
| `try / catch` / `throws` | `?` + `Result<T, E>` | errors are values, no checked exceptions |
| `null` | `Option::None` / no null | compiler-enforced handling |
| `<T extends X>` | `<T: X>` or `where T: X` | bounds on type params |
| `instanceof` | `Any::downcast_ref` | only for `dyn Any` |
| `synchronized` | `Mutex` / `RwLock` | std lib, not keyword |

```java
// Java
interface Shape { double area(); }
class Circle implements Shape {
    public double area() { return Math.PI * r * r; }
}
```

```rust
// Rust
trait Shape { fn area(&self) -> f64; }
struct Circle { r: f64 }
impl Shape for Circle {
    fn area(&self) -> f64 { std::f64::consts::PI * self.r * self.r }
}
```

## Python

| Python | Rust | Note |
|--------|------|------|
| `with open(...)` | RAII + `Drop` | scope-exit cleanup is automatic |
| decorator `@x` | attribute macro `#[x]` | similar idea, different syntax |
| duck typing | trait objects or generics | static checks |
| `list` | `Vec<T>` | homogeneous |
| `dict` | `HashMap<K, V>` | needs `Hash` |
| `None` | `Option<T>` | explicit |
| `try / except` | `?` + `Result` | errors are values |

```python
# Python
class Conn:
    def __enter__(self): return self
    def __exit__(self, *_): self.close()
```

```rust
// Rust — Drop runs on scope exit, no need for `with`
struct Conn;
impl Drop for Conn { fn drop(&mut self) { /* close() */ } }
```

## Go

| Go | Rust | Note |
|----|------|------|
| `goroutine` | `std::thread::spawn` or async task | OS threads by default |
| `interface{}` / `any` | `dyn Trait` or generics | type-erased or generic |
| `interface { Foo() }` | `trait Foo { fn foo(&self); }` | via trait bound |
| `func() (T, error)` | `Result<T, E>` | single value |
| `if err != nil { return err }` | `?` | shorthand |
| `defer cleanup()` | `Drop` trait | scope-bound, deterministic |
| `sync.Mutex` | `std::sync::Mutex` | similar |
| `map[K]V` | `HashMap<K, V>` | heap-allocated |
| `chan T` | `std::sync::mpsc` / `tokio::sync::mpsc` | channels |
| slices | `&[T]` / `Vec<T>` | borrow vs owned |

```go
// Go
func read(path string) (int, error) {
    b, err := os.ReadFile(path)
    if err != nil { return 0, err }
    n, err := strconv.Atoi(strings.TrimSpace(string(b)))
    return n, err
}
```

```rust
// Rust
fn read(path: &str) -> Result<i32, Box<dyn std::error::Error>> {
    let b: String = std::fs::read_to_string(path)?;
    let n: i32 = b.trim().parse()?;
    Ok(n)
}
```

## C++

| C++ | Rust | Note |
|-----|------|------|
| RAII destructor | `Drop` trait | one per type |
| `template<typename T>` | generics `<T>` | monomorphized like templates |
| `virtual` / vtable | `dyn Trait` | explicit `dyn` keyword |
| `std::move(x)` | ownership transfer by value or `move` closure | moves are typed |
| `reinterpret_cast<T>` | `unsafe { transmute }` | avoid; prefer `from_le_bytes` |
| `std::optional<T>` | `Option<T>` | |
| `try / catch` | `Result<T, E>` + `?` | no exceptions |
| `new` / `delete` | RAII / `Drop` | no manual `delete` |
| `shared_ptr<T>` / `unique_ptr<T>` | `Arc<T>` / `Box<T>` | refcount or owned |
| `const T&` / `T&` | `&T` / `&mut T` | shared vs exclusive borrow |

```cpp
// C++
class File { public: ~File() { close(); } };
```

```rust
// Rust
struct File;
impl Drop for File { fn drop(&mut self) { /* close() */ } }
```

## JavaScript / TypeScript

| JS / TS | Rust | Note |
|---------|------|------|
| `Promise<T>` | `Future<Output = T>` | Rust futures are lazy (poll-driven) |
| `async / await` | `async / await` | syntax similar |
| `undefined` / `null` | `Option<T>` | one type for "missing" |
| `Array` | `Vec<T>` | homogeneous |
| `Map` | `HashMap<K, V>` | |
| `try / catch` | `Result<T, E>` + `?` | |
| `class` | `struct` + `impl` | data and behavior separated |
| `interface` | `trait` | with default methods |
| `extends` | trait inheritance (supertrait) | |
| `\|\|` / `??` | `unwrap_or` / `unwrap_or_else` | |
| `any` | `dyn Trait` or generics | |

```javascript
// JavaScript
async function getUser(id) {
  const r = await fetch(`/users/${id}`);
  if (!r.ok) throw new Error('not found');
  return r.json();
}
```

```rust
// Rust — async runtime lives in tokio/async-std, not std. See rust-concurrency.
async fn get_user(id: u64) -> Result<User, reqwest::Error> {
    let r = reqwest::get(format!("https://x/users/{id}")).await?;
    r.json().await
}
```

## Shared idioms across all migrations

- **No `null`.** Use `Option<T>`; the compiler makes you handle both arms.
- **No exceptions.** Use `Result<T, E>` and propagate with `?`.
- **Ownership, not GC.** Values move or borrow; no shared mutable state by default.
- **No inheritance.** Composition + traits replace class hierarchies.
- **Errors are values.** `Result` flows through the type system like any other data.

## Reference

- [Rust by Example](https://doc.rust-lang.org/rust-by-example/)
- [The Rust Book — Glossary for C++/Java/Python/JS](https://doc.rust-lang.org/book/foreword.html)
- [Rust for Rubyists / polyglot comparisons](https://doc.rust-lang.org/book/)
- [JNI / interop with JVM](https://docs.rs/jni/)
- [PyO3 — Python bindings](https://pyo3.rs/)
- [pyo3, cxx, wasm-bindgen — language interop crates](https://crates.io/)
