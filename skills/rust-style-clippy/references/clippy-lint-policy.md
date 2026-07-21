# Clippy Lint Policy — Production Configurations

Companion to `SKILL.md` §II. Covers all 10 lint groups in depth, the full `clippy.toml` reference, `#[expect]` patterns, `priority` layering, and ready-to-paste CI configurations by project type.

## The 10 lint groups (full breakdown)

### `correctness` (default: deny)
Code that is **wrong** — broken semantics that compile but are bugs. Always enabled.

| Lint | Triggers on |
|------|------------|
| `almost_swap` | `a = b; b = a;` (no-op due to evaluation order) |
| `drop_non_drop` | Calling `Drop` on a non-`Drop` type |
| `if_same_then_else` | `if x { ... } else if y { /* same body */ }` |
| `logic_bug` | `a && b || a` (always-true predicate) |
| `out_of_bounds_looping` | Loop range exceeds container |
| `ptr_offset_with_cast` | `isize`-cast pointer arithmetic that's likely wrong |
| `while_let_loop` | `while let Some(_) = x.next()` that should be `for` |

### `suspicious` (default: warn)
Code that's likely buggy but plausible. Always enabled as warnings.

| Lint | Triggers on |
|------|------------|
| `mutable_key_type` | `HashMap<K, _>` where `K`'s hash can change via `&K` |
| `assign_op_pattern` | `a = a + b` (use `a += b`) |
| `blacklisted_name` | `foo`, `bar`, `baz`, `qux`, `toto`, `tutu` |
| `blanket_clippy_restriction_lints` | `#![warn(clippy::restriction)]` (usually too aggressive) |
| `cast_lossless` | `x as u64` where `u64::from(x)` is lossless |
| `clone_on_ref_ptr` | `.clone()` on `Rc`/`Arc` (use `Clone::clone` explicitly or restructure) |
| `dbg_macro` | `dbg!()` left in code |
| `print_stdout` | `println!()` in library code |

### `style` (default: warn)
Idiomatic style preferences. The biggest group. Examples:

- `new_without_default` — `new()` exists but no `Default`
- `new_ret_no_self` — `new()` returns non-`Self`
- `wrong_self_convention` — `as_X(self)`, `to_X(&mut self)`, `into_X(&self)`
- `needless_return` — `return foo;` at end of function
- `module_inception` — `use foo::foo;`
- `enum_variant_names` — `FooBar`, `FooBaz`, `FooQux` (redundant prefix)
- `len_without_is_empty` — has `len()` but no `is_empty()`

### `complexity` (default: warn)
Code that could be simpler. Examples:

- `too_many_arguments` — fn with 7+ args (configurable)
- `cognitive-complexity` — function exceeds 25 cognitive complexity (configurable)
- `manual_flatten` — hand-rolled `.flatten()`
- `option_option` — `Option<Option<T>>` (rarely what you want)
- `double_neg` — `--x` (no-op, often typo)
- `while_let_on_iterator` — `while let Some(x) = iter.next()` (use `for`)

### `perf` (default: warn)
Performance hints — allocations, copies, missed inlining. Examples:

- `large_enum_variant` — enum variant > 200 bytes (blows up size of all variants)
- `single_char_pattern` — `.contains("a")` → `.contains('a')`
- `manual_memcpy` — hand-rolled loop that should be `.copy_from_slice()`
- `vec_box` — `Box<Vec<T>>` (redundant indirection)
- `derivable_impls` — manual impl that could be derived
- `to_string_in_format_args` — `format!("{}", x.to_string())` → `format!("{}", x)`

### `pedantic` (default: allow — opt-in)
Opinionated, stricter style. Enable with `-W clippy::pedantic` or `#![warn(clippy::pedantic)]`.

- `cast_possible_truncation` — `as u8` from `u32`
- `cast_sign_loss` — `i32 as u32`
- `fn_params_excessive_bools` — fn with ≥3 bool params
- `must_use_candidate` — fn returns non-trivial value without `#[must_use]`
- `missing_errors_doc` — public fn returning `Result` without `# Errors` doc
- `missing_panics_doc` — public fn documented as panicking without `# Panics` doc
- `module_name_repetitions` — `network::NetworkClient` (redundant)
- `needless_pass_by_value` — param could be `&T` instead of `T`

### `restriction` (default: allow — opt-in)
Forbid patterns that **may be intentional** but are often mistakes. Enable selectively.

| Lint | Triggers on |
|------|------------|
| `unwrap_used` | `.unwrap()` calls |
| `expect_used` | `.expect()` calls |
| `panic` | `panic!()` |
| `indexing_slicing` | `[i]` indexing (use `.get()` instead) |
| `dbg_macro` | `dbg!()` (also in suspicious by default in newer Clippy) |
| `print_stdout` | `println!()` / `print!()` |
| `print_stderr` | `eprintln!()` / `eprint!()` |
| `float_arithmetic` | `+`/`-`/`*`/`/` on floats |
| `arithmetic` | All arithmetic (overflow concern) |
| `default_numeric_fallback` | `let x = 0;` (type inferred from usage) |
| `default_trait_access` | `Default::default()` instead of `T::default()` |
| `exhaustive_structs` | External crates doing `Foo { ... }` struct literal |
| `exhaustive_enums` | External `match` without wildcard |
| `impl_trait_in_parameters` | `fn f(x: impl Trait)` (prefer generic `<T: Trait>`) |
| `missing_docs_in_private_items` | Even private items need docs |
| `mod_module_files` | Using `foo/mod.rs` (modern: `foo.rs` + `foo/`) |
| `panic_in_result_fn` | `panic!()` inside a fn returning `Result` |
| `self_named_module_files` | Using `foo.rs` (modern is `foo/mod.rs` if you've enabled the opposite) |
| `string_slice` | `&s[..]` slicing on UTF-8 (panics on non-boundary) |

### `cargo` (default: warn)
Cargo.toml quality checks.

| Lint | Triggers on |
|------|------------|
| `cargo_common_metadata` | Missing `description`, `license`, `repository`, `readme`, `keywords`, `categories` |
| `negative_feature_names` | Feature named `no-foo` (should be positive `foo`) |
| `redundant_feature_names` | Feature named `with-foo` or `use-foo` (just `foo`) |
| `wildcard_dependencies` | `*` version requirement |

### `nursery` (default: allow — experimental)
Lints under development. Enable cautiously; may have false positives.

- `use_self` — `Foo` inside `impl Foo` should be `Self`
- `fallible_impl_from` — `impl From` that may panic
- `missing_const_for_fn` — fn could be `const fn`
- `option_if_let_else` — `match opt { Some(x) => f(x), None => default }` should be `opt.map_or(default, f)`

### `internal` (rare)
Used by Clippy's own development. Not relevant for users.

## `#[expect]` patterns (Rust 1.81+)

```rust
// ✅ Single lint with reason
#[expect(
    clippy::too_many_arguments,
    reason = "Builder methods are intentionally granular"
)]
fn build(name: &str, retries: u32, timeout: u32, limit: u32, retries_on_5xx: u32) -> Client { /* */ }

// ✅ Multiple lints
#[expect(clippy::cast_possible_truncation, clippy::cast_sign_loss)]
fn convert(x: i64) -> u8 { x as u8 }

// ✅ Crate-wide expectation
#![expect(clippy::module_name_repetitions, reason = "module names are domain-relevant")]

// ❌ Don't use #[allow] for permanent suppressions — it can silently become dead
```

CI behavior: if the lint **stops firing**, the build fails with `unsatisfied expectation`. This keeps your policy honest.

## Lint `priority` for layered policy

```rust
// At crate root (lib.rs or main.rs):
#![warn(clippy::pedantic)]                           // priority 0
#![warn(priority = 1, clippy::module_name_repetitions)]   // override for one lint
#![deny(priority = 2, clippy::unwrap_used)]               // deny a single restriction lint
```

Higher priority wins. Useful when:
- You want pedantic generally but `allow` specific lints
- You want one restriction lint `deny` while keeping the rest `allow`

## `clippy.toml` — full reference

```toml
# Root-level config (workspace root for multi-crate projects)

# Toolchain-aware linting
msrv = "1.85"                                  # Don't suggest APIs newer than MSRV

# API breaking
avoid-breaking-exported-api = false            # Suggest fixes that change public API

# Thresholds
arithmetic-side = "checked"                    # "checked" (suggest checked_*) or "none"
cognitive-complexity-threshold = 25            # Function complexity
too-many-arguments-threshold = 7               # Max fn args
too-many-lines-threshold = 100                 # Max fn lines
type-complexity-threshold = 250                # Type complexity
enum-variant-name-threshold = 1                # Trigger variant_name lint
single-char-binding-names-threshold = 3        # Allow `_a`, `_b`, but not 4+
max-fn-params-bools = 1                        # Max bool params per fn
max-struct-bools = 1                           # Max bool fields per struct
max-trait-bounds = 3                           # Max trait bounds
# array-size-threshold = 16384                  # Max array literal size
# large-error-threshold = 128                   # Max error enum size
# verbose-bit-mask-threshold = 1                # Bitmask complexity

# Disallowed
disallowed-methods = [
    { path = "std::env::var", reason = "use config::get" },
    { path = "std::print", reason = "library must not write stdout" },
]
disallowed-types = [
    { path = "std::collections::LinkedList", reason = "almost never right" },
    { path = "std::sync::Mutex", reason = "use parking_lot::Mutex" },
]
disallowed-macros = [
    { path = "std::println", reason = "use tracing::info!" },
    { path = "std::dbg", reason = "remove before commit" },
]
disallowed-names = ["foo", "bar", "baz", "toto", "tutu", "titi"]

#doc-valid-idents = [
#    "KiB", "MiB", "GiB", "TiB", "PiB", "EiB",
#    "DirectX", "ECMAScript", "GPLv2", "GPLv3", "GitHub", "GitLab",
#    "IPv4", "IPv6", "ClojureScript", "CoffeeScript", "JavaScript", "PureScript",
#    "TypeScript", "WebAssembly", "NaN", "NaNs", "OAuth", "GraphQL", "OCaml",
#    "OpenGL", "OpenMP", "OpenSSH", "OpenSSL", "OpenStreetMap", "OpenDNS",
#    "TensorFlow", "TrueType", "iOS", "macOS", "FreeBSD", "NaN", "NaNs",
#    "OAuth", "gRPC", "GPLv2", "GPLv3",
#]

# conditional configs
# excessive-nesting-threshold = 12
# future-size-threshold = 16 * 1024
# literal-representation-threshold = 12
# pass-by-value-size-limit = 256
# semicolon-inside-block-ignore-singleline = true
# semicolon-outside-block-ignore-multiline = true
```

See [Clippy's clippy.toml reference](https://doc.rust-lang.org/clippy/clippy_configuration.html) for the canonical list.

## Production CI policies

### Library (published to crates.io)

```rust
// lib.rs
#![warn(clippy::pedantic)]
#![warn(clippy::cargo)]
#![deny(clippy::cargo_common_metadata)]   // force description/license/repository
#![expect(clippy::module_name_repetitions, reason = "domain prefixes intentional")]
#![expect(clippy::must_use_candidate, reason = "most public APIs are builder-style")]
```

```yaml
# .github/workflows/clippy.yml
- run: cargo clippy --workspace --all-targets --all-features -- -D warnings
```

### Application / binary

```rust
// main.rs or lib.rs
#![warn(clippy::pedantic)]
#![warn(clippy::restriction::unwrap_used)]
#![warn(clippy::restriction::expect_used)]
#![deny(clippy::restriction::panic)]
#![deny(clippy::restriction::indexing_slicing)]
```

Use `deny` for things you never want in application code.

### Embedded / safety-critical

```rust
#![warn(clippy::pedantic)]
#![deny(clippy::restriction::unwrap_used)]
#![deny(clippy::restriction::expect_used)]
#![deny(clippy::restriction::panic)]
#![deny(clippy::restriction::indexing_slicing)]
#![deny(clippy::restriction::string_slice)]
#![deny(clippy::restriction::arithmetic)]
#![deny(clippy::restriction::float_arithmetic)]
#![deny(clippy::restriction::default_numeric_fallback)]
```

All restriction lints `deny`. Use `core::num::*` and `checked_*` arithmetic exclusively.

### Internal tool (lightweight)

```rust
// lib.rs — just defaults
#![warn(clippy::all)]   // correctness, suspicious, style, complexity, perf
```

No pedantic, no restriction. Don't add friction to throwaway tools.

## CI integration

```yaml
# .github/workflows/clippy.yml
name: Clippy
on: [push, pull_request]
jobs:
  clippy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: clippy
      - run: cargo clippy --workspace --all-targets --all-features -- -D warnings
```

For MSRV-aware linting, run twice: once on stable, once on MSRV (Clippy's suggestions should not require newer APIs — enforced by `msrv = "..."` in `clippy.toml`).

## Common false positives

| Lint | False positive cause | Mitigation |
|------|---------------------|------------|
| `module_name_repetitions` | Intentional domain prefix | `#[expect(clippy::module_name_repetitions)]` |
| `too_many_arguments` | Builder pattern by design | `#[expect]` with reason |
| `cast_possible_truncation` | Intentional narrowing | `#[expect]` or use `try_from` |
| `must_use_candidate` | Builder methods return `Self` | `#[expect]` or `#[must_use]` on the type |
| `needless_pass_by_value` | Function takes ownership on purpose | `#[expect]` |

Prefer `#[expect]` over `#[allow]` — surface dead expectations in CI.

## Source

- [Clippy Book](https://doc.rust-lang.org/clippy/)
- [Clippy Lint List (filterable)](https://rust-lang.github.io/rust-clippy/master/)
- [Clippy Configuration Reference](https://doc.rust-lang.org/clippy/clippy_configuration.html)
- [`#[expect]` RFC](https://rust-lang.github.io/rfcs/2383-lint-reasons.html)
- [Your Clippy Config Should Be Stricter (Evan Schwartz)](https://emschwartz.me/your-clippy-config-should-be-stricter/)
