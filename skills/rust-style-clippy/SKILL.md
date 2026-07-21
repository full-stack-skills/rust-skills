---
name: rust-style-clippy
description: Apply and diagnose Rust style, rustfmt, Clippy, compiler diagnostics, Edition migrations, lint policy, idiomatic control flow, error handling, allocation behavior, production Rust conventions, and the Rust API Guidelines ↔ Clippy lint mapping. Use when users ask to format or lint Rust, fix warning or error codes, migrate editions, review unwrap or clone usage, improve idioms, map a C-* API guideline rule to the enforcing Clippy lint, or establish CI quality gates. Route API shape decisions (naming conventions, type/trait design, module layout, full C-* guideline review) to the rust-api-design skill.
---

# Rust Style Formatting and Static Analysis

> Based on the [`rustfmt Book`](https://doc.rust-lang.org/rustfmt/), [`Clippy Book`](https://doc.rust-lang.org/clippy/index.html), [`Edition Guide`](https://doc.rust-lang.org/edition-guide/), and [`Error Code Index`](https://doc.rust-lang.org/error_codes/).

## Capability Boundaries

### ✅ Strengths
1. Stable rustfmt configuration (edition, max_width, tab_spaces, use_field_init_shorthand, etc.)
2. Clippy lint system — all 10 lint groups: correctness, suspicious, style, complexity, perf, pedantic, restriction, cargo, nursery, internal
3. `clippy.toml` configuration (msrv, arithmetic-side, cognitive-complexity-threshold, avoid-breaking-exported-api, etc.)
4. `#[expect(...)]` attribute (Rust 1.81+) for CI-enforced lint expectations
5. Lint `priority` ordering for layered policy
6. Production CI lint policy (deny/warn/allow decisions per group)
7. Edition migration (2015→2018→2021→2024, key changes per edition and cargo fix commands)
8. Compiler error code interpretation (rustc --explain, common error codes reference table)

### ⚠️ Prerequisites
1. Rust toolchain installed and configured

### ❌ Out of Scope
1. Rust syntax basics → Use `rust-stable` skill
2. Code review → Use `rust-code-review` skill
3. API shape design (naming, type/trait design, module layout) and the full ~100 C-* API Guidelines checklist → Use the `rust-api-design` skill. This skill only maps the ~25 C-* rules that Clippy can mechanically enforce; the rest are design decisions.

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
cargo clippy                              # Default: correctness, suspicious, style, complexity, perf
cargo clippy -- -W clippy::pedantic       # Enable pedantic group
cargo clippy --fix                        # Auto-fix MachineApplicable lints
cargo clippy -- -A clippy::module_inception  # Allow a specific lint
```

### All 10 lint groups

| Group | Default level | Description | High-leverage lints |
|-------|---------------|-------------|---------------------|
| `correctness` | deny (effectively) | Code that is **wrong** — broken semantics | `almost_swap`, `drop_non_drop`, `if_same_then_else`, `out_of_bounds_looping`, `ptr_offset_with_cast` |
| `suspicious` | warn | Likely-buggy code that compiles but smells off | `mutable_key_type`, `assign_op_pattern`, `blqcklisted_name`, `cast_lossless`, `clone_on_ref_ptr` |
| `style` | warn (default group) | Idiomatic Rust stylistic preferences | `enum_variant_names`, `new_without_default`, `wrong_self_convention`, `needless_return`, `module_inception` |
| `complexity` | warn | Code that could be simpler | `too_many_arguments`, `cognitive-complexity`, `manual_flatten`, `option_option` |
| `perf` | warn | Performance hints (allocations, copies) | `large_enum_variant`, `single_char_pattern`, `manual_memcpy`, `vec_box`, `derivable_impls` |
| `pedantic` | **allow** (opt-in) | Opinionated style — stricter than style | `cast_possible_truncation`, `fn_params_excessive_bools`, `must_use_candidate`, `missing_errors_doc`, `module_name_repetitions` |
| `restriction` | **allow** (opt-in) | Forbid patterns that may be intentional but risky | `unwrap_used`, `expect_used`, `panic`, `indexing_slicing`, `dbg_macro`, `print_stdout`, `float_arithmetic` |
| `cargo` | warn | `Cargo.toml` quality | `cargo_common_metadata`, `negative_feature_names`, `redundant_feature_names`, `wildcard_dependencies` |
| `nursery` | **allow** (experimental) | Lints under development | `use_self`, `fallible_impl_from`, `missing_const_for_fn` |
| `internal` | allow | For Clippy's own development | (rarely used by users) |

### `#[expect]` attribute (Rust 1.81+) — better than `#[allow]`

```rust
// ✅ #[expect] — CI fails if the lint stops firing, surfacing dead expectations
#[expect(clippy::too_many_arguments, reason = "configurable builder has many options")]
fn build(name: &str, retries: u32, timeout: u32, /* 5 more */) { /* */ }

// ❌ #[allow] — silently becomes dead code if the lint stops firing
#[allow(clippy::too_many_arguments)]
fn build(/* */) { /* */ }
```

Prefer `#[expect]` for intentional suppressions; reserve `#[allow]` for transient reasons.

### Lint `priority` — layering

```rust
// Higher priority wins. Use for layered policy.
#![warn(clippy::pedantic)]                       // enable pedantic (priority 0)
#![warn(priority = 1, clippy::module_name_repetitions)]  // re-enable a specific lint
```

### `clippy.toml` configuration

```toml
# clippy.toml at workspace root
msrv = "1.85"                                  # Don't suggest APIs newer than MSRV
avoid-breaking-exported-api = false            # Suggest fixes that change public API
cognitive-complexity-threshold = 25            # Function complexity limit
arithmetic-side = "checked"                    # Prefer checked_* arithmetic
enum-variant-name-threshold = 1                # Trigger variant_name lint
single-char-binding-names-threshold = 3        # Allow `_a`, `_b`, but not 4+
too-many-arguments-threshold = 7
type-complexity-threshold = 250
disallowed-methods = [
    { path = "std::env::var", reason = "use our config::get instead" },
]
disallowed-types = [
    { path = "std::collections::LinkedList", reason = "almost never the right choice" },
]
disallowed-macros = [
    { path = "std::println", reason = "use tracing in libraries" },
]
```

See `references/clippy-lint-policy.md` for the full `clippy.toml` reference and production policies.

### Production CI lint policy

Different projects need different strictness. See `references/clippy-lint-policy.md` for ready-to-paste configurations.

| Project type | Pedantic | Restriction | Recommended |
|--------------|----------|-------------|-------------|
| Library (published) | warn | allow | `clippy::all` + `clippy::pedantic` warn + `cargo::cargo_common_metadata` deny |
| Application / binary | warn | warn (`unwrap_used`) | Add `restriction::unwrap_used`, `panic`, `indexing_slicing` |
| Embedded / safety-critical | warn | deny | All restriction lints deny; add `float_arithmetic` deny |
| Internal tool | allow | allow | Just `clippy::all` (default groups) |

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

## V. API Guidelines ↔ Clippy Lints

The [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/) checklist uses `C-*` rules (about 100 total). Clippy mechanically enforces roughly 25 of them; the remaining ~75 are design judgments (naming, type/trait shape, module layout) that belong to the `rust-api-design` skill, or require `cargo-semver-checks` for breaking-change detection. The table below lists the 12 highest-leverage mappings reviewers ask about most. The full crosswalk, including "lints not yet covered" guidance, lives in [`references/api-guidelines-to-clippy.md`](references/api-guidelines-to-clippy.md).

| C-* Rule | Clippy Lint | Group | Effect |
|----------|-------------|-------|--------|
| C-UNWRAP | `clippy::unwrap_used` | restriction | Flags `unwrap()` calls |
| C-UNWRAP | `clippy::expect_used` | restriction | Flags `expect()` calls |
| C-PANIC | `clippy::panic` | restriction | Flags `panic!()` |
| C-INDEXING | `clippy::indexing_slicing` | restriction | Flags `[i]` indexing (panics) |
| C-BOOL-ARG | `clippy::fn_params_excessive_bools` | pedantic | Functions with ≥3 bool params |
| C-NEWTYPE | `clippy::new_without_default` | style | `new()` exists but no `Default` |
| C-NEWTYPE | `clippy::new_ret_no_self` | style | `new()` returns non-`Self` |
| C-CONV / C-WRONG-SELF | `clippy::wrong_self_convention` | style | `as_X(self)` taking `&self`, or `to_X(&self)` consuming self |
| C-STRING-PATTERNS | `clippy::single_char_pattern` | perf | `.contains("a")` → `.contains('a')` |
| C-COMMON-TRAITS | `clippy::derivable_impls` | perf | Manual impl that could be derived |
| C-LARGE-NUMERIC | `clippy::unreadable_literal` | style | `1000000` should be `1_000_000` |
| C-MUTABLE-KEY | `clippy::mutable_key_type` | suspicious | `HashMap` key type is mutable |
| C-CLONE-ON-REF | `clippy::clone_on_ref_ptr` | restriction | `.clone()` on `Rc`/`Arc` |

Many `restriction` and `pedantic` lints are off by default — enable them explicitly via `#![warn(clippy::unwrap_used)]` or in `clippy.toml` when enforcing a guideline in CI.

## Workflow

1. Format code — `cargo fmt` ensures consistent style
2. Run Clippy — `cargo clippy` runs the 5 default groups (correctness, suspicious, style, complexity, perf); add `-W clippy::pedantic` for stricter
3. Decide policy — pick pedantic/restriction level by project type (see table above); paste the matching config from `references/clippy-lint-policy.md`
4. Configure `clippy.toml` — set `msrv`, `disallowed-methods`, and any project-specific thresholds
5. Use `#[expect]` for intentional suppressions — keeps CI honest about dead expectations
6. Check Edition — Confirm edition in Cargo.toml is up-to-date
7. CI integration — `cargo fmt --check` + `cargo clippy -- -D warnings` + `cargo audit` in CI

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
- [Clippy Lint Policy](references/clippy-lint-policy.md): Full `clippy.toml` reference, all 10 lint groups in depth, `#[expect]` patterns, `priority` layering, and ready-to-paste production CI configurations by project type.
- [Production Rust Idioms](references/production-rust-idioms.md): Review let-else, Option combinators, newtype patterns, non-exhaustive APIs, lock scopes, and overflow strategies when reviewing production code.
- [API Guidelines ↔ Clippy Lints Crosswalk](references/api-guidelines-to-clippy.md): Full mapping from Rust API Guidelines `C-*` rules to the Clippy lints that enforce them, plus the ~75 rules Clippy does not cover and where to review them.
- `examples/golden-style/`: Golden examples for CI passing rustfmt and Clippy

## Official References

- [rustfmt Book](https://doc.rust-lang.org/rustfmt/)
- [Clippy Book](https://doc.rust-lang.org/clippy/)
- [Edition Guide](https://doc.rust-lang.org/edition-guide/)
- [Compiler Error Index](https://doc.rust-lang.org/error_codes/)
