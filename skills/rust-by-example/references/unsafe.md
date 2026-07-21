# Unsafe

> Patterns for the four unsafe superpowers: dereferencing raw pointers, calling `unsafe fn`, implementing `unsafe trait`, and accessing union fields. Covers FFI, safe wrappers, and common pitfalls. For deep FFI / ABI / cross-language binding work, route to `rust-unsafe-ffi`.

## The four unsafe superpowers

`unsafe { ... }` unlocks exactly four things:

1. Dereference a raw pointer (`*const T` / `*mut T`).
2. Call an `unsafe fn` (including FFI).
3. Implement an `unsafe trait`.
4. Read or write a field of a `union`.

That's it. `unsafe` does NOT turn off the borrow checker, does NOT make data races defined, and does NOT free you from aliasing rules.

## 1. Raw pointers

```rust
fn main() {
    let x: i32 = 42;
    let ptr: *const i32 = &x;       // creating a raw pointer is safe
    let val = unsafe { *ptr };      // dereferencing requires unsafe
    assert_eq!(val, 42);

    let mut v = vec![1, 2, 3];
    let p: *mut i32 = v.as_mut_ptr();
    unsafe { *p = 99; }
    assert_eq!(v[0], 99);
}
```

Raw pointers are not tracked by the borrow checker; you must manually uphold: validity, alignment, no aliasing of `&mut`, and lifetime.

## 2. `unsafe fn` and `unsafe impl`

```rust
// Function whose body relies on a caller-provided invariant.
unsafe fn read_at(buf: *const u8, idx: usize) -> u8 {
    unsafe { *buf.add(idx) }        // inner unsafe is optional but explicit
}

// Implementing a trait that requires us to promise some invariant.
unsafe impl Send for MyHandle {}     // "MyHandle is safe to move across threads"

struct MyHandle(*mut u8);

fn main() {
    let buf = [10u8, 20, 30];
    let p = buf.as_ptr();
    let v = unsafe { read_at(p, 1) };
    assert_eq!(v, 20);
}
```

`unsafe fn` advertises a contract callers must satisfy; `unsafe impl` is the implementor promising a property the compiler cannot verify (e.g. `Send`, `Sync`).

## 3. FFI — `extern "C"`

```rust
extern "C" {
    fn abs(input: i32) -> i32;       // C standard library
}

fn main() {
    let v = unsafe { abs(-5) };
    assert_eq!(v, 5);
}
```

Exporting Rust to C:

```rust
#[no_mangle]
pub extern "C" fn add(a: i32, b: i32) -> i32 { a + b }
```

`#[no_mangle]` keeps the symbol name. Use `#[repr(C)]` on structs passed across the boundary. For anything beyond a few symbols, route to `rust-unsafe-ffi`.

## 4. Unions

```rust
#[repr(C)]
union Value {
    i: i32,
    f: f32,
}

fn main() {
    let mut v = Value { i: 0x4048_F5C3 };
    let bits = unsafe { v.i };          // read is unsafe (which field?)
    println!("bits = {bits:#x}");

    v.f = 3.14;                         // write the active field
    let f = unsafe { v.f };
    assert_eq!(f, 3.14);
}
```

Unions share storage across fields; reading the wrong field is UB. Mostly relevant for C interop (`#[repr(C)]` is required for FFI layout).

## 5. Writing a safe wrapper

The golden rule: keep `unsafe` confined to one module, expose a safe API.

```rust
mod raw_buf {
    pub struct Buf {
        ptr: *mut u8,
        len: usize,
    }

    impl Buf {
        pub fn new(v: &mut [u8]) -> &mut Self {
            // SAFETY: we borrow `v` for `'a` and never hand outliving refs.
            unsafe { std::mem::transmute::<&mut [u8], &mut Self>(v) }
        }
        pub fn at(&self, idx: usize) -> Option<u8> {
            if idx >= self.len { return None; }
            // SAFETY: idx < self.len and ptr is valid for `len` bytes.
            Some(unsafe { *self.ptr.add(idx) })
        }
    }
}
```

Every `unsafe` block must carry a `// SAFETY:` comment explaining why it is sound.

## Common pitfalls

| Pitfall | What goes wrong | Fix |
|---------|-----------------|-----|
| Aliasing `&mut T` | UB; miscompiles | One `&mut` at a time; use `UnsafeCell` for interior mutation |
| Calling `free` twice (double free) | UB | Use `Drop`, or wrap raw allocation in a RAII type |
| Sending `Rc` across threads | UB (non-atomic refcount) | Use `Arc`, or audit and `unsafe impl Send` |
| Returning a reference to a stack local | Dangling pointer | Tie lifetime to the input via `&'a` |
| Writing through `*const T` | UB | Use `*mut T` |
| `Send`/`Sync` on a non-thread-safe type | UB | Read the [Rustonomicon](https://doc.rust-lang.org/nomicon/) before deriving |

## When to reach for unsafe

| Situation | Reach for unsafe? |
|-----------|-------------------|
| Bit reinterpret (`[u8; 4]` → `i32`) | No — use `i32::from_le_bytes` |
| OS / kernel call, FFI | Yes — wrap in safe API |
| Performance hotspot provable faster | Benchmark first; usually no |
| Custom allocator | Yes |
| Inline assembly | Yes (see `inline-asm.md`) |
| Interior mutability without `Cell`/`RefCell` | Almost never — use those |

## Reference

- [Rust by Example — Unsafe](https://doc.rust-lang.org/rust-by-example/unsafe.html)
- [Rust by Example — Raw pointers](https://doc.rust-lang.org/rust-by-example/unsafe/ptr.html)
- [The Rustonomicon](https://doc.rust-lang.org/nomicon/)
- [The Rust Reference — Unsafe](https://doc.rust-lang.org/reference/unsafe-keyword.html)
- [std::ptr](https://doc.rust-lang.org/std/ptr/index.html)
