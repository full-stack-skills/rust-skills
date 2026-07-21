# Module Resolution — How `mod foo;` Finds Files

How the Rust compiler resolves a `mod foo;` declaration to a file on disk. Covers the default rules and the `#[path]` attribute for non-standard layouts.

> Authority: [The Rust Reference — Modules](https://doc.rust-lang.org/reference/items/modules.html)

---

## The Resolution Algorithm

When the compiler sees `mod foo;` in a module whose file is `src/<path>.rs`, it looks for `foo` in this order:

1. `src/<path>/foo.rs`
2. `src/<path>/foo/mod.rs`
3. `src/<path>/foo` directory with **both** `foo.rs` and `foo/mod.rs` → error E0761

If both `foo.rs` and `foo/mod.rs` exist, the compiler errors out. Pick one.

### Modern layout (Edition 2018+)

```text
src/
├── lib.rs              // mod foo;  →  looks for src/foo.rs
├── foo.rs              // mod bar;  →  looks for src/foo/bar.rs
└── foo/
    └── bar.rs
```

### Legacy layout (Edition 2015, still works)

```text
src/
├── lib.rs              // mod foo;  →  looks for src/foo/mod.rs
└── foo/
    ├── mod.rs          // mod bar;  →  looks for src/foo/bar.rs
    └── bar.rs
```

---

## The `#[path]` Attribute

For non-standard layouts, use `#[path = "..."]` to override the default resolution:

```rust
// src/lib.rs
#[path = "generated/code.rs"]
mod generated;
```

The path is relative to the directory of the file containing the `mod` declaration.

### Common uses

**Generated code**:

```rust
// src/lib.rs
#[path = "generated/protos.rs"]
mod protos;
```

**Code that lives outside `src/`**:

```rust
// src/lib.rs
#[path = "../shared/types.rs"]
mod shared_types;
```

**Multiple files combined into one module** (rare):

```rust
// src/lib.rs
#[path = "parser/combined.rs"]
mod parser;
```

Where `parser/combined.rs` does:

```rust
include!("lexer.rs");
include!("grammar.rs");
```

This is unusual — prefer proper submodules over `include!`.

---

## Edge Cases

### Edge case 1 — `mod.rs` in 2018+

`mod.rs` still works in Edition 2018+. It's not deprecated. It's just redundant when `foo.rs + foo/` is available. Both layouts compile.

### Edge case 2 — Empty module

```rust
// src/lib.rs
mod empty;              // looks for src/empty.rs or src/empty/mod.rs
```

If `src/empty.rs` doesn't exist:

```
error[E0583]: file not found for module `empty`
```

To declare a module with no body:

```rust
mod empty {}            // inline — no file needed
```

### Edge case 3 — Module-only file (`mod.rs` with only declarations)

```rust
// src/foo/mod.rs
pub mod bar;
pub mod baz;
```

This works in both layouts. In modern layout, the equivalent is:

```rust
// src/foo.rs
pub mod bar;
pub mod baz;
```

### Edge case 4 — Modules with the same name as keywords

If you want a module named `type` or `match` (keywords), use raw identifiers:

```rust
// src/lib.rs
pub mod r#type;
```

```text
src/
└── type.rs            // file is named normally
```

### Edge case 5 — `crate::` vs `self::` vs `super::`

```rust
// src/parser/lexer.rs

// crate:: — refers to the crate root (src/lib.rs)
use crate::ast::Expr;

// self:: — refers to the current module (src/parser/lexer.rs)
use self::token::Token;

// super:: — refers to the parent module (src/parser.rs or src/parser/mod.rs)
use super::Parser;
```

`crate::` is unambiguous and preferred for absolute paths. `self::` and `super::` are useful for relative paths.

### Edge case 6 — `extern crate` in 2018+

In Edition 2015:

```rust
// src/lib.rs
extern crate serde;
use serde::Serialize;
```

In Edition 2018+:

```rust
// src/lib.rs
use serde::Serialize;      // serde is auto-imported from Cargo.toml deps
```

`extern crate` is unnecessary for most crates. Keep it only for:
- Pre-2018 code
- Crates that need `#[macro_use]` (rare)
- Renaming on import: `extern crate foo as bar;` (use `use foo as bar;` instead in 2018+)

---

## File Discovery Table

For `mod foo;` declared in `src/<parent>.rs`:

| Layout | Files searched |
|--------|----------------|
| Modern | `src/<parent>/foo.rs` |
| Legacy | `src/<parent>/foo/mod.rs` |
| `#[path = "x.rs"]` | `src/<parent>/x.rs` (or wherever the path points) |

If `<parent>` is the crate root (`lib.rs`), drop `<parent>/` from the path:

| Layout | `mod foo;` in `src/lib.rs` searches |
|--------|--------------------------------------|
| Modern | `src/foo.rs` |
| Legacy | `src/foo/mod.rs` |

---

## `mod.rs` ↔ `foo.rs` Quick Conversion

| In `src/lib.rs` | File that becomes the module body |
|-----------------|-----------------------------------|
| `mod foo;` | `src/foo.rs` (modern) or `src/foo/mod.rs` (legacy) |

| In `src/foo.rs` (modern) or `src/foo/mod.rs` (legacy) | File that becomes the submodule body |
|------------------------------------------------------|---------------------------------------|
| `mod bar;` | `src/foo/bar.rs` |

| In `src/foo/bar.rs` | File that becomes the sub-submodule body |
|---------------------|-------------------------------------------|
| `mod baz;` | `src/foo/bar/baz.rs` |

The pattern recurs. Each level of `mod` adds one directory.

---

## Common Errors

### E0583 — file not found for module

```
error[E0583]: file not found for module `foo`
```

Cause: `mod foo;` is declared but neither `src/foo.rs` nor `src/foo/mod.rs` exists.

Fix: create the file, or remove the declaration.

### E0761 — file for module found at both

```
error[E0761]: file for module `foo` found at both `foo.rs` and `foo/mod.rs`
```

Cause: both layouts exist simultaneously.

Fix: delete one. The modern layout uses `foo.rs + foo/` (where `foo/` does NOT contain `mod.rs`).

### E0432 — unresolved import

```
error[E0432]: unresolved import `foo::bar`
```

Cause: `use foo::bar;` but `bar` is not declared as `pub mod bar;` in `foo`, or `bar` is private and you're outside its visibility scope.

Fix: add `pub mod bar;` in `foo`, or widen visibility, or import via a re-export.

---

## How `cargo` discovers binaries

Binaries follow a separate resolution:

| File | Binary name |
|------|-------------|
| `src/main.rs` | The package's main binary (named after the package) |
| `src/bin/<name>.rs` | Binary named `<name>` |
| `src/bin/<name>/main.rs` | Binary named `<name>` (multi-file binary) |
| `examples/<name>.rs` | Example named `<name>` |
| `tests/<name>.rs` | Integration test target named `<name>` |
| `benches/<name>.rs` | Benchmark target named `<name>` |

Each binary is a separate compilation unit. They share `src/lib.rs` if it exists, via the `use my_crate::...` path.

---

## Summary

- `mod foo;` resolves to `foo.rs` (modern) or `foo/mod.rs` (legacy) — pick one per crate.
- `#[path]` overrides the default for generated or unusual layouts.
- Privacy is **parent-bound** — `pub` items are only reachable if every module on the path is `pub`.
- Binaries live in `src/bin/` and are separate compilation units.
