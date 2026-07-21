# Closures

> Concrete patterns for closure syntax, `move`, capture modes (`Fn`/`FnMut`/`FnOnce`), returning and storing closures. For async blocks (related but distinct), see `rust-concurrency`.

## 1. Closure syntax

```rust
fn main() {
    let add = |a: i32, b: i32| a + b;             // explicit params
    let double = |x| x * 2;                       // types inferred from use
    let greet = || println!("hi");                // no params
    let block = |x| {                             // block body
        let y = x + 1;
        y * y
    };
    assert_eq!(add(2, 3), 5);
    assert_eq!(double(4), 8);
    greet();
    assert_eq!(block(3), 16);
}
```

Parameter types and return type can be elided at the call site; the compiler infers them. Annotate them only when ambiguous or when storing in a typed field.

## 2. `move` keyword — force capture by value

```rust
fn main() {
    let name = String::from("alice");
    let print = move || println!("{name}");       // moves `name` in
    print();
    // println!("{name}");                         // ERROR: borrowed after move
}
```

Without `move`, closures capture by the least-restrictive form needed (shared ref, then mutable ref, then by value). With `move`, they always capture by value — required when the closure outlives the local scope (threads, returned closures).

## 3. `Fn` vs `FnMut` vs `FnOnce` — capture modes

| Trait | Capture | Call count |
|-------|---------|-----------|
| `FnOnce` | by value (may consume) | once |
| `FnMut` | by mutable reference | multiple, mutating |
| `Fn` | by shared reference | multiple, immutable |

```rust
fn run_fn(f: impl Fn())               { f(); f(); }
fn run_fn_mut(mut f: impl FnMut())    { f(); f(); }
fn run_fn_once(f: impl FnOnce() -> i32) { let _ = f(); }

fn main() {
    let v = vec![1, 2, 3];
    let len = || println!("{}", v.len());         // Fn: shared ref
    run_fn(len);

    let mut counter = 0;
    let mut inc = || { counter += 1; };           // FnMut: mut ref
    run_fn_mut(inc);

    let owned = String::from("x");
    let consume = move || owned.into_bytes();     // FnOnce: consumes
    let _ = run_fn_once(consume);
}
```

`Fn` ⊆ `FnMut` ⊆ `FnOnce`: anything that is `Fn` is also `FnMut`/`FnOnce`. Use the weakest bound the caller needs (e.g. `FnOnce` if you call only once) to accept more closures.

## 4. Returning closures — `-> impl Fn()`

Closures have anonymous types; return them via `impl Trait`.

```rust
fn make_adder(delta: i32) -> impl Fn(i32) -> i32 {
    move |x| x + delta
}

fn make_counter() -> impl FnMut() -> i32 {
    let mut count = 0;
    move || { count += 1; count }
}

fn main() {
    let add5 = make_adder(5);
    assert_eq!(add5(10), 15);

    let mut next = make_counter();
    assert_eq!([next(), next(), next()], [1, 2, 3]);
}
```

Returning `dyn Fn()` requires boxing (see §5). Returning `impl Fn` is zero-cost and monomorphized.

## 5. Storing closures — `Box<dyn Fn()>`

For heterogeneous closures (different types in one collection), use trait objects.

```rust
fn main() {
    let callbacks: Vec<Box<dyn Fn(i32) -> i32>> = vec![
        Box::new(|x| x + 1),
        Box::new(|x| x * 2),
        Box::new(move |x| x * x),
    ];
    for cb in &callbacks {
        println!("{}", cb(5));
    }
}
```

`Box<dyn Fn(...)>` works for shared captures; `Box<dyn FnMut(...)>` needs `&mut` to call; `Box<dyn FnOnce(...)>` can be called once via `Box::call_once` (or `Option<Box<dyn FnOnce>>`).

## 6. Closure as struct field

```rust
struct OnClick<F: Fn() + 'static>(F);

struct Handler {
    on_click: Box<dyn Fn(&str)>,
}

fn main() {
    let h = Handler { on_click: Box::new(|s| println!("clicked {s}")) };
    (h.on_click)("button");
}
```

For generic fields, parameterize the struct; for heterogeneous storage, use `Box<dyn Fn(...)>`.

## 7. Closures in iterators

```rust
fn main() {
    let nums = vec![1, 2, 3, 4, 5, 6];
    let doubled: Vec<i32> = nums.iter().map(|&x| x * 2).collect();
    let evens: Vec<&i32> = nums.iter().filter(|x| *x % 2 == 0).collect();
    let sum: i32 = nums.iter().filter(|x| **x > 2).map(|x| x * 2).sum();
    assert_eq!(doubled, vec![2, 4, 6, 8, 10, 12]);
    assert_eq!(evens.len(), 3);
    assert_eq!(sum, 20);
}
```

`.map(|x| ...)` transforms; `.filter(|x| ...)` keeps (note: takes `&T`, returns `bool`); `.for_each(|x| ...)` runs for side effects.

## Common pitfalls

| Symptom | Fix |
|--------|-----|
| "cannot borrow X as mutable" | Capture needs `mut`; switch bound to `FnMut`, or `move` |
| Closure outlives data | Add `move`, or extend lifetime of captured data |
| Want different closures in a `Vec` | `Vec<Box<dyn Fn()>>` |
| Returning closure won't compile | Add `move` and use `impl Fn` return |
| `Fn` needed but only `FnMut` satisfied | Reduce mutation, capture by value where possible |

## Reference

- [Rust by Example — Closures](https://doc.rust-lang.org/rust-by-example/fn/closures.html)
- [Rust by Example — Capturing](https://doc.rust-lang.org/rust-by-example/fn/closures/capture.html)
- [Rust by Example — Input functions](https://doc.rust-lang.org/rust-by-example/fn/closures/input_functions.html)
- [Rust by Example — As output parameters](https://doc.rust-lang.org/rust-by-example/fn/closures/output_parameters.html)
- [The Rust Book — Closures](https://doc.rust-lang.org/book/ch13-01-closures.html)
