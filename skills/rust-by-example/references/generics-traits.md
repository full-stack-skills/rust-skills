# Generics and Traits

> Concrete patterns for generic functions, `where` clauses, generic structs/enums, trait definitions, default methods, associated types, trait objects, object safety, and blanket impls. For deeper type-system semantics, see `rust-stable`.

## 1. Generic functions

```rust
fn first<T>(xs: &[T]) -> Option<&T> {
    if xs.is_empty() { None } else { Some(&xs[0]) }
}

fn main() {
    let n = first(&[1, 2, 3]);
    let s = first(&["a", "b"]);
    assert_eq!(n, Some(&1));
    assert_eq!(s, Some(&"a"));
}
```

## 2. Inline bounds vs `where` clauses

```rust
// Inline — short bounds read fine inline.
fn double<T: Copy + std::ops::Add<Output = T>>(x: T) -> T { x + x }

// `where` — clearer when bounds are complex or reference the return type.
fn sum<T>(xs: &[T]) -> T
where
    T: Default + Copy + std::ops::AddAssign,
{
    let mut acc = T::default();
    for x in xs { acc += *x; }
    acc
}

fn main() {
    assert_eq!(double(5), 10);
    assert_eq!(sum(&[1.5, 2.5]), 4.0);
}
```

Use `where` when bounds span multiple lines or include associated types; inline `T: Trait` is fine for one short bound.

## 3. Generic structs and enums

```rust
struct Pair<A, B> { a: A, b: B }

impl<A: Clone, B: Clone> Pair<A, B> {
    fn swapped(&self) -> Pair<B, A> {
        Pair { a: self.b.clone(), b: self.a.clone() }
    }
}

enum Either<L, R> { Left(L), Right(R) }

fn main() {
    let p = Pair { a: 1, b: "x" };
    let s = p.swapped();
    assert_eq!(s.a, "x");
}
```

Methods can have their own generic params and bounds, independent of the struct's.

## 4. Trait definitions with default methods

```rust
pub trait Summary {
    fn summarize(&self) -> String;             // required
    fn default_summary(&self) -> String {      // default
        format!("(no summary)")
    }
}

pub struct Article { title: String }
impl Summary for Article {
    fn summarize(&self) -> String { self.title.clone() }
}

fn main() {
    let a = Article { title: "Hello".into() };
    println!("{}", a.summarize());             // "Hello"
    println!("{}", a.default_summary());       // "(no summary)"
}
```

## 5. Associated types vs generics

```rust
// Associated type — one Item per implementor.
trait Container { type Item; fn first(&self) -> Option<&Self::Item>; }
struct Ints(Vec<i32>);
impl Container for Ints {
    type Item = i32;
    fn first(&self) -> Option<&i32> { self.0.first() }
}

// Generic — multiple Item types per implementor (rare).
trait Convert<From> { fn conv(f: From) -> Self; }
```

Use **associated types** when each implementor has exactly one logical "inner type". Use **generic traits** when the same implementor supports many type pairs (e.g. `From<T>`, `Add<Rhs>`).

## 6. Trait objects vs generics — static vs dynamic dispatch

```rust
pub trait Greet { fn say(&self); }

pub fn generic<T: Greet>(g: &T) { g.say(); }       // static, monomorphized
pub fn dynamic(g: &dyn Greet) { g.say(); }         // dynamic, vtable

fn main() {
    struct English;
    impl Greet for English { fn say(&self) { println!("hi"); } }

    let e = English;
    generic(&e);                  // inlined at compile time
    let boxed: Box<dyn Greet> = Box::new(e);
    dynamic(boxed.as_ref());      // vtable call
}
```

| Aspect | Generic (`impl Trait` / `<T>`) | Trait object (`dyn Trait`) |
|--------|----------------------------------|----------------------------|
| Dispatch | Static (compile-time) | Dynamic (vtable) |
| Code size | Larger (per-type copy) | Smaller (one copy) |
| Object safety required | No | Yes |
| Heterogeneous collections | No | Yes (`Vec<Box<dyn T>>`) |
| Runtime overhead | None | One indirection |

## 7. Object safety rules

A trait is object-safe (usable as `dyn Trait`) only if:

- No `Self` in method signatures (return or args).
- All methods are dispatchable: no generic type params, `Self: Sized` not required.
- Does not have `Sized` as a supertrait.

```rust
// Object-safe.
trait Draw { fn draw(&self); }
fn render_all(xs: &[Box<dyn Draw>]) { for x in xs { x.draw(); } }

// NOT object-safe — uses Self.
// trait Clone2 { fn clone_me(&self) -> Self; }
```

## 8. Blanket impls

Implement a trait for every type that satisfies a bound.

```rust
trait PrintSize { fn size(&self) -> usize; }

impl<T> PrintSize for T where T: std::ops::Deref {
    fn size(&self) -> usize { std::mem::size_of_val(self.deref()) }
}

fn main() {
    let s = String::from("hi");
    println!("{}", s.size());      // any T: Deref qualifies
}
```

Blanket impls are powerful but can conflict; reserve for clearly general cases (this is why `From<T>` for `T` exists in std).

## Common pitfalls

| Symptom | Fix |
|--------|-----|
| `the trait bound ... is not satisfied` | Add the bound on the call site, or `impl Trait` somewhere reachable |
| `cannot be made into an object` | Trait is not object-safe — drop `Self`, or use generics |
| `conflicting implementations` | Two blanket impls overlap; specialize or restructure |
| Slow compile / large binary | Many monomorphizations — consider `dyn Trait` |

## Reference

- [Rust by Example — Generics](https://doc.rust-lang.org/rust-by-example/generics.html)
- [Rust by Example — Traits](https://doc.rust-lang.org/rust-by-example/trait.html)
- [Rust by Example — Trait Objects](https://doc.rust-lang.org/rust-by-example/trait/trait_objects.html)
- [Rust by Example — Supertraits](https://doc.rust-lang.org/rust-by-example/trait/supertraits.html)
- [The Rust Book — Traits](https://doc.rust-lang.org/book/ch10-02-traits.html)
- [Object Safety (Reference)](https://doc.rust-lang.org/reference/items/traits.html#object-safety)
