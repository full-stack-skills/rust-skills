---
name: rust-style-clippy
description: Apply and diagnose Rust style, rustfmt, Clippy, compiler diagnostics, Edition migrations, lint policy, idiomatic control flow, error handling, allocation behavior, and production Rust conventions. Use when users ask to format or lint Rust, fix warning or error codes, migrate editions, review unwrap or clone usage, improve idioms, or establish CI quality gates.
---

# Rust Style Formatting and Static Analysis

> Based on the [`rustfmt Book`](https://doc.rust-lang.org/rustfmt/), [`Clippy Book`](https://doc.rust-lang.org/clippy/index.html), [`Edition Guide`](https://doc.rust-lang.org/edition-guide/), and [`Error Code Index`](https://doc.rust-lang.org/error_codes/).

## Capability Boundaries

### ✅ Strengths
1. Stable rustfmt configuration (edition, max_width, tab_spaces, use_field_init_shorthand, etc.)
2. Clippy lint system (cargo clippy, lint levels, clippy.toml configuration)
3. Key Clippy lint groups (correctness, style, complexity, perf, pedantic, nursery, restriction)
4. Edition migration (2015→2018→2021→2024, key changes per edition and cargo fix commands)
5. Compiler error code interpretation (rustc --explain, common error codes reference table)

### ⚠️ Prerequisites
1. Rust toolchain installed and configured

### ❌ Out of Scope
1. Rust syntax basics → Use `rust-stable` skill
2. Code review → Use `rust-code-review` skill

## When to Use

- "Format Rust code"
- "Run Clippy"
- "Migrate to a new Edition"
- "What does compiler error E0xxx mean?"

---

## I. rustfmt Configuration

```toml
# .rustfmt.toml
max_width = 100                    # Line width (default: 100)
tab_spaces = 4                     # Indentation spaces
edition = "2024"                   # Rust edition
merge_derives = true               # Merge derives
use_field_init_shorthand = true    # Field initialization shorthand
use_try_shorthand = true            # Use ? shorthand
```

```bash
cargo fmt                           # Format all files
cargo fmt --check                   # Check formatting (CI usage)
cargo fmt -- --config max_width=80  # Apply specific configuration
```

Options such as `imports_granularity`, `group_imports`, and `reorder_impl_items` may still require nightly rustfmt; do not include them in default configurations that must pass stable CI.

## II. Clippy

```bash
cargo clippy                        # Run all lints
cargo clippy -- -W clippy::pedantic # Enable additional lint groups
cargo clippy --fix                  # Auto-fix issues
```

```rust
// Control lint levels
#[allow(clippy::needless_return)]
fn my_fn() { return 42; }

#[deny(clippy::unwrap_used)]
fn safe_fn() -> Result<i32, Error> {
    let v = risky()?; // Cannot use unwrap here
    Ok(v)
}

// clippy.toml (project root directory)
// disallowed-macros = ["unwrap", "expect"]
// cognitive-complexity-threshold = 25
```

Key lint groups:

| Group | Description | Common Lints |
|-------|-------------|--------------|
| correctness | Correctness of compilation (default) | `clippy::almost_swap` |
| style | Code style (default) | `clippy::enum_variant_names` |
| complexity | Complexity hints | `clippy::too_many_arguments` |
| perf | Performance hints | `clippy::large_enum_variant` |
| pedantic | Strict mode (must be enabled manually) | `clippy::cast_possible_truncation` |
| nursery | Experimental features | `clippy::use_self` |
| restriction | Most restrictive | `clippy::unwrap_used`, `clippy::expect_used` |

## III. Edition Migration

```bash
# Check current edition
cargo metadata --format-version 1 | jq '.packages[0].edition'

# Migration steps (example: 2021 → 2024)
cargo fix --edition               # Auto-migrate code
cargo build                       # Verify compilation
cargo test                        # Validate functionality

# Update Cargo.toml
# edition = "2024"
```

Key changes per edition:

| Edition | Key Changes |
|---------|-------------|
| 2015→2018 | Path and module import changes, `dyn Trait`, NLL, anonymous lifetimes and keywords changed |
| 2018→2021 | Precise closure capture, array `IntoIterator`, panic macro consistency, prelude and reserved syntax changes |
| 2021→2024 | RPIT lifetime capture, match ergonomics adjustment, temporary value scope, `unsafe extern`/unsafe attributes, `gen` keyword, etc. |

## IV. Compiler Error Code Quick Reference

```bash
# View error details
rustc --explain E0277
```

| Error Code | Meaning | Typical Scenario |
|------------|---------|------------------|
| E0277 | Trait not implemented | `T: Trait` bound is unsatisfied |
| E0308 | Type mismatch | Expected type A, but B provided |
| E0502 | Borrow conflict | Cannot have mutable borrow and immutable borrow simultaneously |
| E0597 | Insufficient lifetimes | Reference goes out of scope beyond its lifetime value |
| E0432 | Import not found | `use` path is incorrect |
| E0061 | Parameter count mismatch | Function call has wrong number of parameters |
| E0106 | Missing lifetimes | Function signature requires explicit lifetimes |
| E0382 | Use moved value | Ownership already transferred |
| E0499 | Simultaneous mutable borrow | Only one `&mut` allowed per expression |
| E0716 | Insufficient lifetime for temporary values | Reference on temporary exceeds its scope |

## Workflow

1. Format code — `cargo fmt` ensures consistent style
2. Run Clippy — `cargo clippy` discovers potential errors and improvement opportunities
3. Configure Clippy — Enable/disable specific lints per project needs (clippy.toml)
4. Check Edition — Confirm edition in Cargo.toml is up-to-date
5. Dependency safety — `cargo audit` scans for known vulnerabilities
6. CI integration — Integrate fmt --check + clippy + audit into CI pipeline

## Gotchas

1. `cargo clippy --fix` only fixes lints at MachineApplicable level
2. rustfmt config file is named `.rustfmt.toml`, not `rustfmt.toml`
3. After edition migration, new warnings may appear — especially around unsafe_op_in_unsafe_fn in 2024
4. `cargo fix --edition` does not fix all issues; manual review required after migration
5. Prefer `let ... else` for early exits and `is_some_and`/`then_some` for simple boolean mapping; avoid compressing complex control flows just to use modern syntax
6. `saturating_*`, `checked_*`, and regular arithmetic expressions have different business semantics regarding overflow strategy — decide first, then select API

## On-Demand Resources

- [Format and Clippy Examples](examples/examples.md)
- [Lint Group Quick Reference](references/references.md)
- [Production Rust Idioms](references/production-rust-idioms.md): Review let-else, Option combinators, newtype patterns, non-exhaustive APIs, lock scopes, and overflow strategies when reviewing production code.
- `examples/golden-style/`: Golden examples for CI passing rustfmt and Clippy

## Official References

- [rustfmt Book](https://doc.rust-lang.org/rustfmt/)
- [Clippy Book](https://doc.rust-lang.org/clippy/)
- [Edition Guide](https://doc.rust-lang.org/edition-guide/)
- [Compiler Error Index](https://doc.rust-lang.org/error_codes/)
