# cargo-semver-checks Lint Catalog

Reference for the most common lints emitted by [`cargo-semver-checks`](https://github.com/obi1kenobi/cargo-semver-checks). 270+ total; the high-value ones are listed here.

## How it works

`cargo-semver-checks` parses your crate's public API via `trustfall_rustdoc` (queries rustdoc JSON). It compares the current API against a baseline (a published version, git tag, or git rev) and reports each semver-relevant change.

## Run

```bash
cargo semver-checks check-release                            # vs latest crates.io
cargo semver-checks check-release --baseline-version 1.2.0   # vs specific version
cargo semver-checks check-release --baseline-tag v1.2.0      # vs git tag
cargo semver-checks check-release --baseline-rev <sha>       # vs git rev
```

Output format:

```
Loaded 109 SemVer checks.
Checking golden-semver v0.2.0 -> v0.3.0
   Checking golden-semver v0.2.0 (currently checked out)
   Checking golden-semver v0.3.0 (published on crates.io)
error: breaking change detected
   --- failure enum_variant_added ---
   Description: An enum variant was added without #[non_exhaustive]
```

## Common Lints (categorized)

### Major-version triggers (breaking)

| Lint | Trigger |
|------|---------|
| `function_missing` | Removed or renamed public fn |
| `method_missing` | Removed inherent method |
| `enum_variant_missing` | Removed enum variant |
| `enum_repr_changed` | Changed `#[repr(...)]` |
| `enum_struct_variant_field_missing` | Removed field from struct variant |
| `struct_field_missing` | Removed pub field |
| `struct_missing` | Removed struct |
| `trait_missing` | Removed trait |
| `module_missing` | Removed module |
| `type_alias_missing` | Removed type alias |
| `trait_method_missing` | Removed trait method |
| `function_parameter_count_changed` | Changed number of params |
| `method_parameter_count_changed` | Changed method param count |
| `function_parameter_type_changed` | Param type changed |
| `inherent_method_unsafe_added` | Added `unsafe` to method |
| `enum_marked_non_exhaustive` | Added `#[non_exhaustive]` |
| `struct_marked_non_exhaustive` | Added `#[non_exhaustive]` |
| `struct_field_added` | Added pub field to plain struct |
| `enum_variant_added` | Added variant to plain enum |
| `trait_method_added` | Added method to unsealed trait without default |
| `trait_unsafe_added` | Added `unsafe` to trait |
| `trait_removed_supertrait` | Removed supertrait |
| `trait_removed_associated_constant` | Removed assoc const |
| `trait_removed_associated_type` | Removed assoc type |
| `pub_module_level_const_removed` | Removed `pub const` |
| `pub_static_missing` | Removed `pub static` |
| `macro_missing` | Removed declarative macro |

### Minor-version triggers (additive)

| Lint | Trigger |
|--------|---------|
| `function_added` | New public fn |
| `method_added` | New inherent method |
| `enum_variant_added_non_exhaustive` | New variant on `#[non_exhaustive]` enum |
| `trait_added` | New trait |
| `module_added` | New module |
| `type_alias_added` | New type alias |
| `struct_field_added_private` | New private field on existing struct |
| `constructible_struct_added` | New struct that can be constructed by downstream |
| `derive_trait_added` | New `#[derive(...)]` |
| `trait_default_impl_added` | New trait method with default |
| `pub_static_added` | New `pub static` |

### Patch / informational

| Lint | Trigger |
|--------|---------|
| `type_marked_deprecated` | Added `#[deprecated]` |
| `function_marked_deprecated` | Function deprecated |
| `method_marked_deprecated` | Method deprecated |

## Suppressing a lint

If you intentionally make a breaking change and want to acknowledge it (bumping major), the lints are informational. To silence false positives:

```rust
// Add a #[doc] hidden note that cargo-semver-checks recognizes:
// (not currently supported — file an issue if you hit a false positive)
```

Or filter by version:

```bash
cargo semver-checks check-release --release-type major  # acknowledge breaking
```

## CI integration

```yaml
# .github/workflows/semver.yml
name: Semver
on:
  pull_request:
    branches: [main]
jobs:
  semver-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: obi1kenobi/cargo-semver-checks-action@v2
        with:
          baseline-version: ${{ github.event.pull_request.base.ref }}
```

PRs with breaking changes will fail unless the PR explicitly bumps the version.

## Common false positives

- Feature-gated items: cargo-semver-checks may not respect features in all cases
- `#[doc(hidden)]` items: still considered public API (correct behavior)
- Build-tag-specific code: rare

If you get a false positive, [file an issue](https://github.com/obi1kenobi/cargo-semver-checks/issues).

## Source

- [cargo-semver-checks](https://github.com/obi1kenobi/cargo-semver-checks)
- [All lints (filterable)](https://obi1kenobi.github.io/cargo-semver-checks/)
