# API Guidelines ↔ Clippy Lints Crosswalk

> Maps each Rust API Guidelines `C-*` rule that Clippy can mechanically enforce to the specific lint that enforces it.
>
> Companion to [`SKILL.md` Section V](../SKILL.md). Used during review to find the lint that catches a violation, or during CI setup to enforce a guideline automatically.
>
> Sources: [Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html), [Clippy lint list](https://rust-lang.github.io/rust-clippy/master/index.html).

## How to read this document

- **C-\* Rule** — the identifier from the API Guidelines checklist (e.g. `C-UNWRAP`).
- **Clippy Lint** — the `clippy::...` name to enable in `#![warn(...)]` / `clippy.toml`.
- **Group** — the Clippy lint group: `correctness`, `suspicious`, `style`, `complexity`, `perf`, `pedantic`, `restriction`, or `nursery`.
- **Effect** — what the lint actually flags and the typical fix.
- **Default level** — whether the lint is on by default (`warn`/`deny`) or must be opted in. Most `pedantic` and all `restriction` lints are **off by default**; enable them explicitly when you want to enforce the guideline.

## Quick recipe: enforcing a guideline in CI

```toml
# clippy.toml — example workspace policy enforcing several C-* rules
cognitive-complexity-threshold = 25
disallowed-macros = ["dbg", "println!"]
```

```rust
// src/lib.rs — opt into the restriction/pedantic lints that map to C-* rules
#![warn(
    clippy::unwrap_used,          // C-UNWRAP
    clippy::expect_used,          // C-UNWRAP
    clippy::panic,                // C-PANIC
    clippy::indexing_slicing,     // C-INDEXING
    clippy::dbg_macro,            // C-DEBUG (debug leftovers)
    clippy::print_stdout,         // C-PRINT (no println! in lib)
    clippy::clone_on_ref_ptr,     // C-CLONE-ON-REF
    clippy::missing_const_for_fn, // C-CONST / C-DEBUG
    clippy::fn_params_excessive_bools, // C-BOOL-ARG
)]
```

```bash
cargo clippy -- -D warnings        # CI: treat every fired lint as an error
cargo clippy --fix                 # Local: auto-apply MachineApplicable fixes
```

## Coverage at a glance

The Rust API Guidelines checklist contains roughly **100 `C-*` rules**. Clippy covers approximately **25** of them mechanically. The remaining ~75 fall into three buckets:

| Bucket | Where to review |
|--------|-----------------|
| API shape / naming / type & trait design | `rust-api-design` skill |
| Manual review (readability, ergonomics, documentation tone) | `rust-code-review` skill |
| Breaking-change / semver | `cargo-semver-checks` (crate, runs in CI) |

This file lists every C-* rule Clippy can help with, then calls out notable gaps.

## Full mapping table

### Reliability and panics

| C-* Rule | Clippy Lint | Group | Default | Effect |
|----------|-------------|-------|---------|--------|
| C-UNWRAP | `clippy::unwrap_used` | restriction | off | Flags `unwrap()` calls; use `?`, `ok_or`, or `expect` with context. |
| C-UNWRAP | `clippy::expect_used` | restriction | off | Flags `expect()` calls; prefer typed errors with context. |
| C-PANIC | `clippy::panic` | restriction | off | Flags `panic!()`; replace with `Result` propagation. |
| C-PANIC | `clippy::panic_in_result_fn` | restriction | off | Flags `panic!()` inside functions returning `Result`. |
| C-INDEXING | `clippy::indexing_slicing` | restriction | off | Flags `[i]` indexing that can panic; use `get(i)` or iterators. |
| C-EXPECT-DEBUG | `clippy::expect_fun_call` | style | warn | `.expect(format!(...))` — allocate-and-panic; use `expect("static")` or `unwrap_or_else`. |
| C-DBG | `clippy::dbg_macro` | restriction | off | `dbg!()` left in committed code. |

### Type design and traits

| C-* Rule | Clippy Lint | Group | Default | Effect |
|----------|-------------|-------|---------|--------|
| C-COMMON-TRAITS | `clippy::derivable_impls` | perf | warn | Manual `impl` that could be `#[derive(...)]`. |
| C-NEWTYPE | `clippy::new_without_default` | style | warn | `new()` exists but no `Default` impl. |
| C-NEWTYPE | `clippy::new_ret_no_self` | style | warn | `new()` returns non-`Self` — confuses readers. |
| C-NEWTYPE | `clippy::new_without_default_derive` | style | warn | Suggests deriving `Default` when `new` has no args. |
| C-WRONG-SELF / C-CONV | `clippy::wrong_self_convention` | style | warn | `as_X(self)` taking `&self`, or `to_X(&self)` consuming self, or `into_X(&self)`. |
| C-UNNECESSARY-BOX | `clippy::box_collection` | perf | warn | `Box<Vec<T>>`, `Box<HashMap<..>>` — the inner heap alloc makes the `Box` redundant. |
| C-MUTABLE-KEY | `clippy::mutable_key_type` | suspicious | warn | `HashMap`/`HashSet` key type whose `Hash`/`Ord` can observably change. |
| C-CONST | `clippy::missing_const_for_fn` | pedantic | off | Function body is const-evaluable; should be `const fn`. |

### Function signatures and arguments

| C-* Rule | Clippy Lint | Group | Default | Effect |
|----------|-------------|-------|---------|--------|
| C-BOOL-ARG | `clippy::fn_params_excessive_bools` | pedantic | off | Function takes ≥3 `bool` params; use a config struct or two-variant enum. |
| C-BOOL-ARG | `clippy::bool_assert_comparison` | style | warn | `assert_eq!(x, true)` → `assert!(x)`. |
| C-MANY-ARGS | `clippy::too_many_arguments` | complexity | warn | Function takes more than 7 args; bundle into a struct. |

### Iterators and conversions

| C-* Rule | Clippy Lint | Group | Default | Effect |
|----------|-------------|-------|---------|--------|
| C-ITER | `clippy::iter_nth_zero` | style | warn | `.nth(0)` should be `.next()`. |
| C-ITER | `clippy::manual_flatten` | complexity | warn | Hand-rolled flatten via `for { for {} }`; use `.flatten()`. |
| C-ITER | `clippy::useless_conversion` | complexity | warn | Unnecessary `.into()` / `.iter()` that the compiler can elide. |
| C-ITER | `clippy::iter_cloned_collect` | style | warn | `vec.iter().cloned().collect()` — use `vec.clone()` or `Vec::from_iter`. |
| C-STRING-PATTERNS | `clippy::single_char_pattern` | perf | warn | `.contains("a")` → `.contains('a')` (avoids a `&str` search). |
| C-STRING-PATTERNS | `clippy::into_iter_on_ref` | style | warn | `&vec.into_iter()` should be `&vec.iter()` (or `into_iter()` on the owned value). |
| C-STRING | `clippy::string_lit_as_bytes` | style | warn | `"...".as_bytes()` — use `b"..."` where possible. |

### Numeric literals and readability

| C-* Rule | Clippy Lint | Group | Default | Effect |
|----------|-------------|-------|---------|--------|
| C-LARGE-NUMERIC | `clippy::unreadable_literal` | style | warn | `1000000` should be `1_000_000`. |
| C-LARGE-NUMERIC | `clippy::inconsistent_digit_grouping` | style | warn | Mixing group sizes (`0x12_345_678`). |
| C-LARGE-NUMERIC | `clippy::large_digit_groups` | pedantic | off | Digit groups larger than 5. |

### Smart pointers and cloning

| C-* Rule | Clippy Lint | Group | Default | Effect |
|----------|-------------|-------|---------|--------|
| C-CLONE-ON-REF | `clippy::clone_on_ref_ptr` | restriction | off | `.clone()` on `Rc`/`Arc` — usually meant to be a borrow. |
| C-CLONE-ON-REF | `clippy::rc_buffer` | restriction | off | `Rc<String>`/`Rc<Vec<T>>` — use `Arc<str>` / `Arc<[T]>`. |
| C-EXPECT-DEBUG | `clippy::redundant_clone` | perf | warn | `.clone()` of a value that is moved immediately afterwards. |

### Debug, printing, and documentation

| C-* Rule | Clippy Lint | Group | Default | Effect |
|----------|-------------|-------|---------|--------|
| C-PRINT | `clippy::print_stdout` | restriction | off | `println!()` in library code; use a logging facade. |
| C-PRINT | `clippy::print_stderr` | restriction | off | `eprintln!()` in library code. |
| C-DEBUG | `clippy::dbg_macro` | restriction | off | `dbg!()` left in committed code. |
| C-DOCUMENTED | `clippy::missing_docs_in_private_items` | restriction | off | Even private items require doc comments (stricter than rustc's `missing_docs`). |
| C-LINK | `clippy::doc_markdown` | pedantic | off | Unquoted items in doc comments that look like identifiers should be backticked. |

## Notable rules Clippy does NOT cover

The following commonly cited `C-*` rules have **no mechanical Clippy lint** and require manual review (see the `rust-api-design` and `rust-code-review` skills) or `cargo-semver-checks`:

| C-* Rule | Why Clippy can't help | Where to enforce |
|----------|------------------------|------------------|
| C-NAME / C-CASE | Naming conventions (`snake_case`, `CamelCase`, `SCREAMING_SNAKE`) are largely rustc/style-enforced, but semantic naming (does this verb match the action?) is a design judgment. | `rust-api-design` |
| C-CUSTOMER-FACING | Stability of public API surface — Clippy does not know which items are part of the public contract vs. internal. | `cargo-semver-checks` |
| C-SEMVER | Breaking changes between releases. | `cargo-semver-checks` |
| C-FAILURE | Error types should implement `std::error::Error`, `Debug`, `Display`, `Send` + `Sync`. Clippy cannot verify semantic contracts. | `rust-api-design` + manual review |
| C-PREDICATE / C-INTERPOLATE | Predicate naming (`is_*`, `has_*`) and format-string interpolation are partial. Clippy covers some idioms (e.g. `clippy::is_digit_ascii_radix`) but not the guideline as a whole. | `rust-api-design` |
| C-BUILDER | Builder pattern ergonomics — Clippy has `clippy::builder_return_self` but cannot verify the overall builder API shape. | `rust-api-design` |
| C-FEATURE | Feature flags should compose, be additive, and have sane defaults. Clippy cannot reason about feature matrices. | `rust-api-design` + manual review |
| C-MSRV | Minimum Supported Rust Version — only `cargo-semver-checks` and `cargo-msrv` can verify this. | `cargo-msrv` |
| C-DOC-LOC | Documentation tone, examples in rustdoc, and cross-linking. Clippy's `doc_markdown` is syntactic only. | `rust-code-review` |
| C-INTO-ITER-REF | `IntoIterator for &Collection` ergonomics — Clippy covers specific cases (`into_iter_on_ref`) but not the full guideline. | `rust-api-design` |

When a `C-*` rule has no Clippy coverage, route the question:

- Design / naming / type / trait shape → **`rust-api-design` skill**.
- Readability / ergonomics / documentation tone → **`rust-code-review` skill**.
- Release-to-release breaking changes → **`cargo-semver-checks`** in CI.

## Worked examples

### Example 1 — enforcing C-UNWRAP across a library

```rust
// src/lib.rs
#![warn(clippy::unwrap_used, clippy::expect_used, clippy::panic)]

pub fn parse_port(s: &str) -> u16 {
    // Before: s.parse().unwrap()  — would fire clippy::unwrap_used
    s.parse().unwrap_or(8080)        // OK: bounded fallback, no panic
}
```

```bash
$ cargo clippy -- -D warnings
warning: used `unwrap_or` — but the unsafe `unwrap()` path is gone. ✓
```

### Example 2 — C-NEWTYPE in review

```rust
// Reviewer sees:
struct Port(u16);
impl Port {
    fn new(p: u16) -> Port { Port(p) }
}
```

`cargo clippy` fires `clippy::new_without_default`:

```rust
// Fixed:
#[derive(Default)]
struct Port(u16);
impl Port {
    fn new(p: u16) -> Port { Port(p) }
}
```

### Example 3 — C-INDEXING without panicking

```rust
// Before: fires clippy::indexing_slicing
let first = items[0];

// After: safe access via get
let first = items.get(0).ok_or("empty slice")?;
```

## Gotchas

1. **Restriction lints are off by default.** Enabling `clippy::restriction` as a group enables everything (including opinionated lints unrelated to the guidelines). Enable individual lints by name.
2. **Pedantic lints have false positives.** `clippy::missing_const_for_fn` often fires on functions that *can* be const but where doing so locks in implementation details. Use `#[allow]` locally rather than disabling globally.
3. **`clippy::unwrap_used` is noisy in tests.** Tests legitimately use `unwrap()`. Scope the lint to non-test code with a crate-level `#![warn(...)]` and per-module `#[allow(clippy::unwrap_used)]` in `#[cfg(test)]` modules, or use `#![cfg_attr(test, allow(clippy::unwrap_used))]`.
4. **`clippy::doc_markdown` requires the `Pedantic` feature group** and may need `clippy.toml`'s `doc-valid-idents` to whitelist project-specific words (crate names, URLs).
5. **Edition changes can re-enable lints.** Moving to edition 2024 turns on `unsafe_op_in_unsafe_fn` by default; review your lint policy whenever you bump editions.

## Verifying your policy

```bash
# Print every C-* lint that fires in the workspace
cargo clippy --workspace --all-targets -- \
    -W clippy::unwrap_used \
    -W clippy::expect_used \
    -W clippy::panic \
    -W clippy::indexing_slicing \
    -W clippy::missing_const_for_fn \
    -W clippy::fn_params_excessive_bools \
    -W clippy::clone_on_ref_ptr \
    -W clippy::dbg_macro \
    -W clippy::print_stdout \
    2>&1 | tee clippy-c-guidelines.log
```

Treat the log as the audit artifact for a release readiness review; cross-reference each warning against the table above.

## See also

- [Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) — the authoritative `C-*` list.
- [Clippy lint index](https://rust-lang.github.io/rust-clippy/master/index.html) — every lint with examples.
- [`cargo-semver-checks`](https://github.com/obi1kenobi/cargo-semver-checks) — lints for C-SEMVER / C-CUSTOMER-FACING rules.
- [`rust-api-design` skill](../../rust-api-design/SKILL.md) — the ~75 C-* rules requiring design judgment.
- [`rust-code-review` skill](../../rust-code-review/SKILL.md) — manual review lens for readability and ergonomics.
