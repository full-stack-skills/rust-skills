# Modernizing `foo/mod.rs` → `foo.rs + foo/`

A mechanical migration from the legacy `mod.rs` layout to the modern Edition 2018+ layout. Zero behavior change; purely a file move.

---

## Background

In Rust 2015, a directory module required a `mod.rs` file:

```text
src/
└── foo/
    ├── mod.rs          ← required — declares submodules
    ├── bar.rs
    └── baz.rs
```

Edition 2018+ allows an alternative without `mod.rs`:

```text
src/
├── foo.rs             ← replaces foo/mod.rs
└── foo/
    ├── bar.rs
    └── baz.rs
```

Both layouts compile. The modern layout is preferred because:
1. One fewer file per directory
2. The module's top-level content lives alongside its submodule declarations
3. Avoids confusion when both `foo.rs` and `foo/mod.rs` accidentally exist (the compiler errors out)

---

## Mechanical Migration

### Step 1 — Check edition

Confirm the crate is on Edition 2018 or later:

```toml
# Cargo.toml
[package]
edition = "2021"     # or "2018"
```

If `edition = "2015"`, you cannot use the modern layout. Upgrade the edition first.

### Step 2 — Move the file

```bash
git mv src/foo/mod.rs src/foo.rs
```

The compiler now resolves `mod foo;` (declared in `lib.rs`) to `src/foo.rs` instead of `src/foo/mod.rs`.

### Step 3 — Check for `#[path]` attributes

If your `mod` declarations use `#[path]` to point at non-standard paths, the migration doesn't affect them. But verify:

```rust
// In some file
#[path = "foo/custom.rs"]
mod custom;
```

This still works after the migration.

### Step 4 — Verify

```bash
cargo check
cargo test
cargo doc --no-deps
```

All should pass with zero code changes.

---

## Edge Cases

### Edge case 1 — Both `foo.rs` and `foo/mod.rs` exist

If you accidentally have both:

```
src/foo.rs
src/foo/mod.rs
```

The compiler errors:

```
error[E0761]: file for module `foo` found at both `foo.rs` and `foo/mod.rs`
```

Fix: delete one. The modern layout uses `foo.rs + foo/` (where `foo/` contains submodules but **no** `mod.rs`).

### Edge case 2 — `foo/mod.rs` contains only `mod` declarations

If your `mod.rs` is just a list of submodule declarations, the migration is trivial — the content moves verbatim to `foo.rs`:

```rust
// src/foo/mod.rs (before)
pub mod bar;
pub mod baz;
```

```rust
// src/foo.rs (after)
pub mod bar;
pub mod baz;
```

### Edge case 3 — `foo/mod.rs` contains substantial code

If `mod.rs` has both `mod` declarations *and* implementation:

```rust
// src/foo/mod.rs (before)
pub mod bar;
pub mod baz;

pub struct Foo { /* ... */ }

impl Foo {
    pub fn new() -> Self { /* ... */ }
}
```

You have two choices:

**Choice A — Keep everything in `foo.rs`**:

```rust
// src/foo.rs (after)
pub mod bar;
pub mod baz;

pub struct Foo { /* ... */ }

impl Foo {
    pub fn new() -> Self { /* ... */ }
}
```

**Choice B — Promote `Foo` to its own file**:

```text
src/
├── foo.rs                 ← just mod decls + re-exports
└── foo/
    ├── bar.rs
    ├── baz.rs
    └── foo_struct.rs      ← the struct + impl
```

```rust
// src/foo.rs
mod foo_struct;
pub mod bar;
pub mod baz;

pub use foo_struct::Foo;
```

Choice B is cleaner for large `mod.rs` files. See `splitting-files.md` for the full procedure.

### Edge case 4 — Tests in `mod.rs`

If `mod.rs` has `#[cfg(test)] mod tests { ... }`, the tests move with the file:

```rust
// src/foo.rs (after)
pub mod bar;

pub struct Foo { /* ... */ }

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn foo_works() { /* ... */ }
}
```

Tests continue to work because `super::` refers to `foo`, which is still the module containing the `tests` submodule.

---

## Mixed Layouts (Don't)

If your crate has some modules using `mod.rs` and others using the modern layout, readers have to check each directory. Pick one per crate.

The validator script enforces consistency — see `scripts/validate_skills.py` in the rust-skills repo.

---

## Automation

For a crate with many `mod.rs` files, automate the migration:

```bash
# Find all mod.rs files and move them
find src -name "mod.rs" -type f | while read modrs; do
    dir=$(dirname "$modrs")
    parent=$(dirname "$dir")
    name=$(basename "$dir")
    git mv "$modrs" "$parent/$name.rs"
done
```

⚠️ Run `cargo check` after to catch any `#[path]` attributes that need updating.

---

## Should I Migrate at All?

If your crate is on Edition 2018+ and you're starting new modules, use the modern layout. For existing crates:

- **New code** — use modern layout (`foo.rs + foo/`)
- **Existing `mod.rs` crates** — migrate opportunistically (when you're already touching the file)
- **Mixed crates** — pick one and apply consistently

`mod.rs` is **not deprecated**. It's not wrong. The modern layout is just preferred for new code. Don't do a giant PR that migrates 100 files at once — do it incrementally as part of other refactors.
