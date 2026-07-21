---
name: rust-semver
description: Manage Rust crate semantic versioning — what counts as a public API (visible items + reachable through re-exports), pre-1.0 rules (0.x.y compatibility), breaking change detection via cargo-semver-checks (270+ lints), workspace lockstep publishing with cargo-workspaces, yank/deprecate workflows, RustSec advisories, and the semver implications of `#[non_exhaustive]`, sealed traits, hidden modules, feature flags, and trait impl additions. Use when users ask whether a change is breaking, want to publish a new version safely, run cargo-semver-checks, coordinate multi-crate workspace releases, or handle a yanked/advisory situation; hand Cargo manifest mechanics to rust-cargo-build, API design choices to rust-api-design, and CI config to rust-style-clippy.
---

# Rust Semver and Release Workflow

> Authority: [Cargo Semver Reference](https://doc.rust-lang.org/cargo/reference/semver.html), [RFC 1105 (Semver)](https://rust-lang.github.io/rfcs/1105-api-evolution.html), [cargo-semver-checks](https://github.com/obi1kenobi/cargo-semver-checks), [RustSec Advisory Database](https://rustsec.org/).

This skill owns **what is and isn't a breaking change** in Rust, the **publishing workflow** for crates.io, and **workspace-wide release coordination**. It does not own API *design* (`rust-api-design`), Cargo manifest mechanics (`rust-cargo-build`), or lint config (`rust-style-clippy`).

## Capability Boundaries

### ✅ Strengths
1. Determining whether a specific code change is a major, minor, or patch bump
2. Understanding pre-1.0 (`0.x.y`) special rules
3. Running and interpreting `cargo-semver-checks` (270+ lints)
4. Coordinating multi-crate workspace releases via `cargo-workspaces`
5. Handling yank, deprecate, and RustSec advisory workflows
6. Knowing the semver implications of `#[non_exhaustive]`, sealed traits, feature flags, hidden modules
7. Writing release notes that match the change type

### ⚠️ Prerequisites
1. A Rust crate with a clear public API surface — see `rust-api-design`
2. Cargo manifest and `cargo publish` basics — see `rust-cargo-build`

### ❌ Out of Scope
1. Designing the API itself → `rust-api-design`
2. Cargo manifest format and build configuration → `rust-cargo-build`
3. Clippy lint rules → `rust-style-clippy`
4. Test design for verifying behavior → `rust-testing`

## Data Privacy

This skill does not collect, store, or transmit user data. Publishing to crates.io is a public action — confirm with the user before running `cargo publish`.

---

# Part 1: What Is the Public API?

Semver applies to **public API surface**. In Rust, the public API is everything visible to downstream — but the definition is subtle.

## Visible items

```rust
// src/lib.rs
pub fn hello() {}                    // public API
pub struct User { pub name: String } // public API
pub mod network {                    // public API
    pub fn connect() {}              // public API
}

mod internal {                       // private — NOT public API
    pub fn helper() {}               // pub, but module is private → not reachable
}
```

Rule: an item is public API if and only if **a downstream crate can name it without `unsafe`**. A `pub` item inside a `pub(crate)` module is **not** public API.

## Reachability through re-exports

```rust
// src/lib.rs
mod hidden;
pub use hidden::Config;   // Config IS public API (reachable via crate root)
```

Even though `hidden` is private, `Config` is reachable via the re-export — it's public API.

## Hidden modules

```rust
#[doc(hidden)]
pub mod unstable { /* */ }
```

**`#[doc(hidden)]` does NOT remove items from the public API for semver purposes.** Downstream can still `use crate::unstable::Foo`. If you intend them to be unstable, gate behind a feature flag or move to a private module.

## Feature-gated items

```rust
#[cfg(feature = "json")]
pub mod json;   // public API only when feature enabled
```

The semver contract is **per feature combination**. Adding items under `json` is a minor bump for users with `json` enabled, and invisible to users without.

---

# Part 2: Breaking vs Non-Breaking Changes

The Cargo Book [lists the canonical changes](https://doc.rust-lang.org/cargo/reference/semver.html). Summary:

## Always breaking (major bump, except pre-1.0)

| Change | Why |
|--------|-----|
| Remove a public item | Downstream code referencing it breaks |
| Rename a public item | Same as remove + add |
| Change a function signature (param/return type) | Callers fail to compile |
| Add a new variant to a non-`#[non_exhaustive]` enum | `match` lacks wildcard |
| Add a field to a public struct literal | `Foo { x: 1 }` breaks if `Foo` gains a field |
| Implement a trait for an external type (or vice versa) | Conflicts with downstream orphan impls |
| Tighten trait bounds | Downstream impls may no longer satisfy |
| Change `pub` item to `pub(crate)` | Removes from API |
| Remove `Copy`/`Clone`/`Debug` derive | Downstream may rely on them |
| Change semver of a public dependency | May transitively break |

## Non-breaking (minor or patch bump)

| Change | Why |
|--------|-----|
| Add a new public function | Additive |
| Add a new trait impl for your own type | Additive |
| Add a variant to a `#[non_exhaustive]` enum | Caller has wildcard |
| Add a field to a private-field struct | Caller can't struct-literal it |
| Add a new feature flag | Invisible to non-users |
| Loosen trait bounds | More permissive |
| Add default method to a sealed trait | Sealed = you control impls |
| Deprecate with `#[deprecated]` | Soft removal |

## Subtle cases

### Adding a method to a public trait

```rust
// Before
pub trait Foo { fn a(&self); }
// After
pub trait Foo { fn a(&self); fn b(&self); }   // ❌ BREAKING
```

Downstream impls of `Foo` will fail to compile (missing `b`). **Fix**: either (a) bump major, (b) seal the trait before adding methods, or (c) add `b` as a default method (`fn b(&self) {}`).

### Adding a default method to an unsealed trait

```rust
pub trait Foo { fn a(&self); fn b(&self) {} }  // ✅ non-breaking
```

Default methods are non-breaking. But you cannot later remove the default without breaking.

### Generic param with default

```rust
// Before
pub fn parse<T>(input: &str) -> T { /* */ }
// After
pub fn parse<T = String>(input: &str) -> T { /* */ }   // ✅ non-breaking
```

Adding a default to a generic is non-breaking. Removing the default IS breaking.

### Trait object safety

If `Foo` is currently object-safe (`Box<dyn Foo>` works), making it object-unsafe (adding `Self: Sized` bound, adding generic method) is breaking.

### Lifetime additions

```rust
// Before
pub fn parse(input: &str) -> &str { /* */ }
// After
pub fn parse<'a>(input: &'a str) -> &'a str { /* */ }   // ✅ usually non-breaking
```

Lifetime elision makes most lifetime changes transparent.

---

# Part 3: Pre-1.0 (`0.x.y`) Rules

Crates at version `0.x` follow **modified** semver:

| Version | Compatible with | What increments on breaking |
|---------|----------------|----------------------------|
| `0.0.x` | Nothing — experimental, any change OK | `0.0.x` |
| `0.x.y` where x > 0 | Same `0.x.*` only | The **minor** (x) position = "major" |

So `0.1.0` → `0.2.0` is a major bump. `0.1.0` → `0.1.1` is a patch (bug fix).

```toml
# Allowed in Cargo.toml:
[dependencies]
my-crate = "0.1"     # means >=0.1.0, <0.2.0
```

Once you hit `1.0.0`, normal semver resumes.

## When to go 1.0

- API is stable (no planned breaking changes for ~6 months)
- Used by other crates (signal of usefulness)
- All fundamental design decisions are settled

Don't fear 1.0. Many crates live too long at 0.x because they're afraid of the commitment. The cost of 1.0 is "I commit to breaking changes requiring major bumps," which is usually fine.

---

# Part 4: `cargo-semver-checks`

[`cargo-semver-checks`](https://github.com/obi1kenobi/cargo-semver-checks) is a tool that compares your crate's current public API against a published version and flags breaking changes. 270+ lints cover most cases.

## Install and run

```bash
cargo install cargo-semver-checks --locked

# Before publishing a new version:
cargo semver-checks check-release

# Compare against a specific baseline:
cargo semver-checks check-release --baseline-version 1.2.0

# Compare against a git tag:
cargo semver-checks check-release --baseline-tag v1.2.0
```

## Output interpretation

```
--- failure function_missing ---
Description: Function removed or renamed, or return type changed.
Error: the function `parse` was removed from the API
```

Each failure is a semver violation. Fix by either:
1. **Restore the item** (don't actually remove it)
2. **Bump the major version** (acknowledge the breaking change)
3. **Use a compatibility shim** (re-add under the old name, delegating to new)

## CI integration

```yaml
# .github/workflows/semver.yml
name: Semver Check
on: [pull_request]
jobs:
  semver:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: obi1kenobi/cargo-semver-checks-action@v2
```

PRs that introduce breaking changes will fail CI unless the version is bumped accordingly.

## Common lint hits

| Lint | Meaning | Fix |
|------|---------|-----|
| `function_missing` | Removed or renamed function | Restore or bump major |
| `enum_variant_added` | Added variant to non-`#[non_exhaustive]` enum | Mark `#[non_exhaustive]` |
| `struct_field_added` | Added field to public struct | Make private or `#[non_exhaustive]` |
| `trait_method_added` | Added method to unsealed trait | Add default or seal |
| `inherent_method_missing` | Removed impl block method | Restore or bump major |
| `type_marked_deprecated` | `#[deprecated]` added | Acceptable, bump minor |

---

# Part 5: Publishing Workflow

## Single-crate publish

```bash
# 1. Bump version in Cargo.toml
# 2. Update CHANGELOG.md
# 3. Run quality gates
cargo fmt --all --check
cargo test --workspace --all-targets --all-features
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo semver-checks check-release

# 4. Verify package contents
cargo package --list    # show files included
cargo package           # build the .crate in target/package/
cargo publish --dry-run # full simulation

# 5. Publish
cargo publish           # 🚨 public action — confirm with user first
```

## Workspace lockstep publish via `cargo-workspaces`

For multi-crate workspaces, [`cargo-workspaces`](https://crates.io/crates/cargo-workspaces) automates the version bump + publish dance:

```bash
cargo install cargo-workspaces

# Bump all members together:
cargo workspaces version minor      # 0.1.0 → 0.2.0 across all members

# Bump with custom prerelease:
cargo workspaces version prerelease --pre-id beta

# Publish all members in topological order:
cargo workspaces publish
```

`cargo-workspaces`:
1. Edits each member's `Cargo.toml` version
2. Updates internal `path = ""` dependencies to the new version
3. Commits + tags if you pass `--no-individual-tags` or `--individual-tags`
4. Publishes in dependency order (deps before dependents)

## Yank a published version

If a version has a critical bug, **yank** it (prevents new dependencies on it, doesn't remove existing):

```bash
cargo yank --vers 1.2.3
# To undo:
cargo yank --vers 1.2.3 --undo
```

Yanked versions remain in the registry for projects with `Cargo.lock` pinning them.

## Deprecate a crate

Mark the crate as deprecated on crates.io via the maintainer's page. Downstream will see a deprecation notice when they run `cargo add`.

---

# Part 6: RustSec Advisories

[RustSec Advisory Database](https://rustsec.org/) tracks known vulnerabilities in published crates.

## `cargo-audit`

```bash
cargo install cargo-audit --locked
cargo audit               # scan Cargo.lock against advisory DB
cargo audit --deny warnings   # fail CI on any advisory
```

## `cargo-deny` (more comprehensive)

[`cargo-deny`](https://embarkstudios.github.io/cargo-deny/) covers:
- **advisories** — RustSec
- **licenses** — deny unauthorized licenses
- **bans** — deny specific crates
- **sources** — deny specific git/registry sources

```toml
# deny.toml
[advisories]
db-urls = ["https://github.com/rustsec/advisory-db"]
yanked = "deny"

[licenses]
allow = ["MIT", "Apache-2.0", "BSD-3-Clause"]
confidence-threshold = 0.8
```

```bash
cargo install cargo-deny --locked
cargo deny check
```

## Responding to an advisory in your crate

1. Acknowledge in the issue tracker
2. Patch and publish a new version
3. File an advisory with RustSec (if applicable): https://github.com/rustsec/advisory-db/
4. Yank the vulnerable version (after the fix is published)
5. Communicate to users via CHANGELOG + release notes

---

# Part 7: Release Notes

For every publish, write a `CHANGELOG.md` entry. Suggested format:

```markdown
## [1.2.0] - 2026-07-21

### Added
- `Client::builder()` for ergonomic construction (#45)
- `Visibility::IncludeHidden` variant

### Changed
- `parse()` now accepts `impl AsRef<str>` instead of `&str`

### Deprecated
- `Client::new()` — use `Client::builder()` instead

### Fixed
- Panic on empty input in `parse()` — now returns `Err`
```

Tools:
- [`cargo-release`](https://crates.io/crates/cargo-release) — automates version bump + tag + publish
- [`release-plz`](https://release-plz.io/) — generates CHANGELOG from conventional commits
- [setuptools-changelog](https://github.com/orhun/setuptools-changelog) — manual

---

## Workflow

1. **Inventory the diff** — what changed in `pub` items since the last release?
2. **Classify each change** — breaking, additive, or fix (see Part 2)
3. **Decide version bump** — major/minor/patch; remember pre-1.0 rules
4. **Run cargo-semver-checks** — confirm your classification matches the tool
5. **Update CHANGELOG** — what changed, why, with migration notes
6. **Run quality gates** — fmt, test, clippy, doc
7. **Publish** — single (`cargo publish`) or workspace (`cargo workspaces publish`)
8. **Handle post-publish** — yank if broken, file advisory if security

## Decision Shortcuts

| Change | Bump | Notes |
|--------|------|-------|
| Added a `pub fn` | minor | Additive |
| Fixed a bug | patch | Behavior change, no API change |
| Removed a `pub fn` | major | Or restore + deprecate |
| Added a sealed trait method | minor | Sealed = you control impls |
| Added an unsealed trait method | major | Or add default |
| Added enum variant | major (or minor if `#[non_exhaustive]`) | |
| Added pub struct field | major (or minor if `#[non_exhaustive]` or private) | |
| Bumped MSRV | minor (if min = 1.0+) | Document policy |
| Bumped dependency semver-major | major | Transitive break |

## Resources

- [Semver Reference (full)](references/semver-reference.md) — full change catalog
- [cargo-semver-checks Lint Catalog](references/cargo-semver-checks-lints.md)
- [Workspace Publishing Cookbook](examples/workspace-publishing.md) — `cargo-workspaces` recipes
- `examples/golden-semver/` — a crate demonstrating a non-breaking version bump

## Upstream Sources

- [Cargo Semver Reference](https://doc.rust-lang.org/cargo/reference/semver.html)
- [Cargo Publishing Guide](https://doc.rust-lang.org/cargo/reference/publishing.html)
- [RFC 1105 — API Evolution](https://rust-lang.github.io/rfcs/1105-api-evolution.html)
- [cargo-semver-checks](https://github.com/obi1kenobi/cargo-semver-checks)
- [cargo-workspaces](https://crates.io/crates/cargo-workspaces)
- [cargo-release](https://crates.io/crates/cargo-release)
- [release-plz](https://release-plz.io/)
- [RustSec Advisory Database](https://rustsec.org/)
