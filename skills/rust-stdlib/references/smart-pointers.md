# Smart Pointers — Box, Rc, Arc, Weak, Cow

> Companion to `SKILL.md` Part 2. Canonical source: [std::boxed](https://doc.rust-lang.org/std/boxed/index.html), [std::sync](https://doc.rust-lang.org/std/sync/index.html).

## Decision matrix

| Type | Ownership | Thread-safe | Cost | Use |
|------|-----------|-------------|------|-----|
| `Box<T>` | Single | Yes | 1 allocation | Heap, recursive types, trait objects |
| `Rc<T>` | Shared | **No** | Refcount inc/dec | Single-thread shared read |
| `Arc<T>` | Shared | Yes | Atomic refcount | Multi-thread shared read |
| `Weak<T>` | None | (matches owner) | Refcount, no strong hold | Break cycles, caches |
| `Cell<T>` | Single | No | Cheap | Copy types, simple state |
| `RefCell<T>` | Single | No | Runtime borrow | Mutate behind shared ref |
| `Mutex<T>` | Single | Yes | Lock + park | Multi-thread mutation |
| `RwLock<T>` | Single | Yes | Lock + park | Many readers, few writers |
| `Cow<'a, B>` | Borrowed-or-owned | Yes | Tag | Avoid copies when possible |

## Box<T>

```rust
// Recursive type needs indirection
enum List { Cons(i32, Box<List>), Nil }

// Trait object (dynamic dispatch)
let shapes: Vec<Box<dyn std::fmt::Debug>> = vec![Box::new(1), Box::new("x")];

// Move a large value onto the heap
let big = Box::new([0u64; 1_000_000]);
```

Use `Box` whenever you need heap allocation, unknown size at compile time (trait objects, recursive types), or to move a large value off the stack. It is a single-owner pointer; `Deref`/`DerefMut` make it transparent.

## Rc<T> — single-threaded shared ownership

```rust
use std::rc::Rc;

let a = Rc::new(String::from("hi"));
let b = Rc::clone(&a);                  // bump count, not a deep copy
assert_eq!(Rc::strong_count(&a), 2);
drop(b);
assert_eq!(Rc::strong_count(&a), 1);
```

`Rc` is `!Send`. To mutate through shared references on one thread, pair it with `RefCell`: `Rc<RefCell<T>>`.

## Arc<T> — atomic shared ownership

```rust
use std::sync::Arc;
use std::thread;

let buf = Arc::new(vec![1, 2, 3]);
let handles: Vec<_> = (0..4)
    .map(|_| { let b = Arc::clone(&buf); thread::spawn(move || b.len()) })
    .collect();
for h in handles { h.join().unwrap(); }
```

`Arc` uses atomics so the refcount is correct across threads. Use `Arc` (not `Rc`) the moment a value may cross a thread boundary.

## Weak<T> — breaking cycles

`Rc`/`Arc` cycles leak memory because each side keeps the other alive. `Weak` holds a non-owning reference: it does not prevent drop.

```rust
use std::rc::{Rc, Weak};
use std::cell::RefCell;

struct Node { parent: RefCell<Weak<Node>>, children: RefCell<Vec<Rc<Node>>> }

let root = Rc::new(Node { parent: RefCell::new(Weak::new()), children: RefCell::new(vec![]) });
let child = Rc::new(Node {
    parent: RefCell::new(Rc::downgrade(&root)),     // weak: avoids cycle
    children: RefCell::new(vec![]),
});
root.children.borrow_mut().push(Rc::clone(&child));

// Upgrade returns Option<Rc<T>> — None if the value was dropped
assert!(child.parent.borrow().upgrade().is_some());
```

Use `Weak` for: parent links, observer lists, caches, anything that should not keep the target alive.

## Shared mutable state patterns

| Pattern | Threads | Notes |
|---------|---------|-------|
| `Rc<RefCell<T>>` | 1 | Cheap, runtime borrow panic on misuse |
| `Arc<Mutex<T>>` | N | Exclusive lock; readers also block |
| `Arc<RwLock<T>>` | N | Many concurrent readers; one writer |

```rust
use std::sync::{Arc, Mutex};
use std::thread;

let counter = Arc::new(Mutex::new(0));
let hs: Vec<_> = (0..10).map(|_| {
    let c = Arc::clone(&counter);
    thread::spawn(move || { *c.lock().unwrap() += 1; })
}).collect();
for h in hs { h.join().unwrap(); }
assert_eq!(*counter.lock().unwrap(), 10);
```

Prefer `Mutex` by default; reach for `RwLock` only when reads dominate and the critical section is non-trivial.

## Drop order

- Local variables drop in reverse declaration order.
- Struct fields drop in declaration order.
- `Rc`/`Arc` drop when the last strong reference goes away — timing depends on control flow.
- `Weak` does not trigger drop; if only weak refs remain, the value is gone and `upgrade()` returns `None`.

## Cow — borrowed or owned

`Cow<'a, B>` defers the decision: cheaply hold a borrow, or own a modified copy.

```rust
use std::borrow::Cow;

fn shout<'a>(input: &'a str) -> Cow<'a, str> {
    if input.chars().any(|c| c.is_lowercase()) {
        Cow::Owned(input.to_uppercase())     // allocate, only if needed
    } else {
        Cow::Borrowed(input)                  // zero-copy fast path
    }
}

assert_eq!(shout("HI"), "HI");          // no allocation
assert_eq!(shout("hi"), "HI");          // allocation
```

Use `Cow` when most callers pass data that needs no transformation but a few do — you avoid forcing everyone to pay for an allocation.

## Choosing shared vs owned

| Question | Pick |
|----------|------|
| One owner, needs heap? | `Box<T>` |
| Two readers, one thread? | `Rc<T>` |
| Two readers, multi-thread? | `Arc<T>` |
| Need to mutate the shared value? | `Rc<RefCell<T>>` or `Arc<Mutex<T>>` |
| Parent/child structure? | Strong `Rc`/`Arc` for children, `Weak` for parent |
| Borrow-or-own return? | `Cow<'a, T>` |

## Gotchas

- `Rc` is not `Send`/`Sync`. Sending one to another thread is a compile error, not a runtime bug.
- `Mutex::lock` returns `Result`; on a panicked thread holding the lock, the mutex is **poisoned** and `.lock().unwrap()` panics. Use `lock().unwrap_or_else(|e| e.into_inner())` to recover the inner value.
- `Arc::clone` is cheap (one atomic increment) — do not avoid it for clarity.
- `Box::leak` turns a `Box<T>` into `&'static mut T`. Useful for statics; otherwise a memory leak.

## Reference

- [std::boxed::Box](https://doc.rust-lang.org/std/boxed/struct.Box.html)
- [std::rc::Rc](https://doc.rust-lang.org/std/rc/struct.Rc.html) / [std::rc::Weak](https://doc.rust-lang.org/std/rc/struct.Weak.html)
- [std::sync::Arc](https://doc.rust-lang.org/std/sync/struct.Arc.html) / [std::sync::Weak](https://doc.rust-lang.org/std/sync/struct.Weak.html)
- [std::borrow::Cow](https://doc.rust-lang.org/std/borrow/enum.Cow.html)
- [Rust Standard Library](https://doc.rust-lang.org/std/)
