# Visibility and Privacy — Complete Reference

Rust's privacy model is module-based, not class-based. This reference covers the full model with edge cases.

> Authority: [The Rust Reference — Visibility and Privacy](https://doc.rust-lang.org/reference/visibility-privacy.html)

---

## The Five Visibility Levels

| Level | Syntax | Visible to |
|-------|--------|-----------|
| Private (default) | *(nothing)* | Current module and its descendant modules |
| Module-restricted | `pub(in path)` | The ancestor module `path` and its descendants |
| Parent-restricted | `pub(super)` | Parent module (and its descendants) — shorthand for `pub(in <parent>)` |
| Self-restricted | `pub(self)` | Same as private — rarely written |
| Crate-visible | `pub(crate)` | All modules in the current crate |
| Public | `pub` | All modules — but see "parent-bound reachability" below |

---

## Parent-Bound Reachability (Critical Concept)

`pub` on an item makes it visible to the world **only if every module on the path from the crate root to the item is also `pub`**.

```rust
// src/lib.rs
pub mod outer {                    // outer is pub → reachable externally
    pub mod inner {                // inner is pub → reachable externally
        pub struct Item;           // pub → reachable externally
    }
}

// Users CAN reach: my_crate::outer::inner::Item
```

```rust
// src/lib.rs
mod outer {                        // outer is PRIVATE → unreachable externally
    pub mod inner {                // inner is pub, but parent is private
        pub struct Item;           // pub, but path is blocked
    }
}

// Users CANNOT reach: my_crate::outer::inner::Item (outer blocks)
// Only crate-internal code can reach it.
```

This is why the facade pattern works: declare the internal tree as `mod foo;` (private), and re-export selected items at the crate root with `pub use`. The deep tree is invisible externally even if every item inside is `pub`.

---

## Privacy Includes Descendants

A private item is visible to:
1. The module that declares it
2. **All descendant modules** of that module

```rust
// src/parser.rs
fn internal_helper() {}          // private — visible here

mod lexer {                       // child of parser
    fn use_parent_helper() {
        super::internal_helper();  // OK — descendant can see parent's privacy
    }
}

mod grammar {                     // another child of parser
    fn also_use() {
        super::internal_helper();  // OK — sibling can also see (via parent)
    }
}
```

Wait — let me restate this precisely. Privacy in Rust is:
- An item with visibility V is visible to the set of modules defined by V
- For private (default) visibility, the set is "the current module and its descendants"

So:
- `parser::internal_helper` (private) is visible in `parser` and in `parser::lexer`, `parser::grammar`, `parser::lexer::token`, etc.
- `parser::lexer::token` is **not** visible in `parser` (token is private to `lexer`); but `parser` is visible in `lexer` (parent).

This is the source of much confusion. Internal helpers go in the parent and are visible to children. Child-specific helpers go in the child and are private to that child.

---

## Choosing Visibility — Decision Tree

```
Is this item part of the public API that external users will use?
├── Yes
│   ├── Is it a top-level concept (Connection, Pool, Error)?
│   │   └── pub use at crate root (via facade)
│   └── Is it a subdomain (parser::Lexer, ast::Expr)?
│       └── pub mod + pub use inside the module
└── No
    ├── Is it used by multiple modules within the crate?
    │   ├── Yes, by modules that share a common ancestor
    │   │   └── pub(in path) where path is the common ancestor
    │   ├── Yes, by any module in the crate
    │   │   └── pub(crate)
    │   └── Yes, by the parent module only
    │       └── pub(super)
    └── Used only in this module
        └── private (default)
```

---

## Edge Cases

### Edge case 1 — `pub` field in a `pub` struct

```rust
pub struct Connection {
    pub host: String,          // public field — users can read and write
    port: u16,                 // private field — users cannot access
}
```

A `pub` field means users can construct the struct with literal syntax and mutate the field freely. This is rarely what you want for fields that should be encapsulated.

```rust
// ❌ Dangerous — users can construct invalid state
pub struct Connection {
    pub host: String,
    pub port: u16,
    pub socket: TcpStream,
}

let conn = Connection {
    host: "localhost".to_string(),
    port: 0,                   // invalid port
    socket: /* how do users get this? */,
};
```

```rust
// ✅ Encapsulated — constructor validates
pub struct Connection {
    host: String,
    port: u16,
    socket: TcpStream,
}

impl Connection {
    pub fn new(host: &str, port: u16) -> std::io::Result<Self> {
        if port == 0 { return Err(/* ... */); }
        let socket = TcpStream::connect((host, port))?;
        Ok(Self { host: host.to_string(), port, socket })
    }

    pub fn host(&self) -> &str { &self.host }
    pub fn port(&self) -> u16 { self.port }
}
```

### Edge case 2 — `pub` trait vs `pub(crate)` trait

```rust
// pub trait — external users can implement it
pub trait Driver {
    fn connect(&self) -> Result<(), Error>;
}

// pub(crate) trait — only this crate can implement it
// (This is the "sealed trait" pattern lite — prevents external impls)
pub(crate) trait Internal {
    fn internal_op(&self);
}
```

For traits you don't want users to implement, use the [sealed trait pattern](https://rust-lang.github.io/api-guidelines/future-proofing.html) — combine `pub(crate)` or private supertrait with `pub`:

```rust
mod private {
    pub trait Sealed {}
}

pub trait Public: private::Sealed {
    fn method(&self);
}

// Only types in this crate can implement Sealed, so only this crate
// can implement Public.
```

### Edge case 3 — Re-exporting with visibility modifiers

```rust
mod parser;
mod lexer;

// pub use — exposes to external users
pub use parser::Parser;

// pub(crate) use — exposes only within this crate
pub(crate) use lexer::Lexer;

// private use — same as no modifier
use parser::Parser;        // crate-internal alias, not exposed
```

### Edge case 4 — Enums and variant privacy

Enum variants inherit the enum's visibility. You cannot have a `pub` enum with private variants, or vice versa.

```rust
pub enum Color {
    Red,                // pub (because Color is pub)
    Green,
    Blue,
}

// Users: my_crate::Color::Red — reachable
```

```rust
pub(crate) enum Internal {
    Variant1,            // pub(crate) (because Internal is pub(crate))
}
```

### Edge case 5 — `pub use foo::*;` visibility

The re-export inherits the visibility of the `use` statement:

```rust
mod internal_module {
    pub struct Hidden;
}

pub use internal_module::*;     // Hidden becomes externally reachable as my_crate::Hidden
```

This is how facade re-exports work — the `internal_module` is private, but `pub use` lifts its items to the crate root.

### Edge case 6 — `impl` blocks and visibility

Methods inside an `impl` block have their own visibility. The struct's visibility doesn't affect method visibility.

```rust
pub struct Foo;

impl Foo {
    pub fn public_method(&self) {}
    fn private_method(&self) {}     // module-private
    pub(crate) fn crate_method(&self) {}
}
```

External users can call `Foo::public_method` but not `Foo::private_method` or `Foo::crate_method`.

### Edge case 7 — Privacy and testing

Child modules can access parent privacy. Use this for unit tests:

```rust
pub struct Foo {
    internal_field: i32,        // private
}

impl Foo {
    pub fn new() -> Self { Self { internal_field: 42 } }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_internal() {
        let foo = Foo::new();
        assert_eq!(foo.internal_field, 42);    // OK — child sees parent privacy
    }
}
```

---

## Visibility Audit

When reviewing a crate's privacy, run this checklist:

1. **Every `pub` item**: do you have a concrete reason for it to be public? "I might need it someday" is not a reason.
2. **Every `pub` field**: would users constructing the struct with literal syntax produce valid state? If not, make it private + provide a constructor.
3. **Every `pub use`**: is the re-exported item actually used by callers? Dead re-exports pollute the namespace.
4. **Every `pub mod`**: is the entire subtree meant to be public? If not, declare it `mod foo;` (private) and re-export selected items.
5. **Every glob `pub use foo::*;`**: can you list every item being re-exported? If not, replace with an explicit list.

Tools:
- `cargo doc --no-deps --open` — your crate's docs are the public API. Anything visible here is a semver promise.
- [`cargo-public-api`](https://github.com/Enselic/cargo-public-api) — lists every public item, diffs between versions.
