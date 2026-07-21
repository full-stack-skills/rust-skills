# Semver Reference (Full Change Catalog)

Authoritative reference for what counts as a major, minor, or patch bump in Rust. Condensed from [Cargo's Semver chapter](https://doc.rust-lang.org/cargo/reference/semver.html) and [RFC 1105](https://rust-lang.github.io/rfcs/1105-api-evolution.html).

## Legend

- 🔴 **MAJOR** — breaking change, requires `x+1.0.0`
- 🟢 **MINOR** — additive or backward-compatible, requires `x.y+1.0`
- 🔵 **PATCH** — bug fix, requires `x.y.z+1`

## Items and Modules

| Change | Severity |
|--------|---------|
| Add a new public item | 🟢 minor |
| Remove a public item | 🔴 major |
| Rename a public item | 🔴 major (same as remove + add) |
| Add a `pub` to a previously private item | 🟢 minor |
| Remove `pub` from an item (make private) | 🔴 major |
| Mark item `#[doc(hidden)]` | 🟢 minor (but it's still semver-relevant!) |
| Move a public item to a different module path | 🔴 major (unless re-exported at old path) |

## Structs

| Change | Severity |
|--------|---------|
| Add a field to a struct with public fields | 🔴 major |
| Add a field to a struct with private fields only | 🟢 minor |
| Add a field to a `#[non_exhaustive]` struct | 🟢 minor |
| Remove a field | 🔴 major |
| Change field type | 🔴 major |
| Reorder tuple struct fields | 🔴 major (positional) |
| Add `#[non_exhaustive]` to existing struct | 🔴 major (downstream can no longer struct-literal) |
| Derive new trait (e.g., `Copy`) | 🟢 minor (but removing it later is 🔴) |
| Remove derived trait | 🔴 major |

## Enums

| Change | Severity |
|--------|---------|
| Add a variant to a plain enum | 🔴 major |
| Add a variant to a `#[non_exhaustive]` enum | 🟢 minor |
| Remove a variant | 🔴 major |
| Add `#[non_exhaustive]` to existing enum | 🔴 major |
| Change variant field type | 🔴 major |

## Traits

| Change | Severity |
|--------|---------|
| Add a method to an **unsealed** trait without default | 🔴 major |
| Add a method to a **sealed** trait | 🟢 minor |
| Add a method with a default impl to unsealed trait | 🟢 minor |
| Remove a method | 🔴 major |
| Change method signature | 🔴 major |
| Add a supertrait bound | 🔴 major |
| Add a provided item (assoc const with value) | 🟢 minor |
| Seal an unsealed trait | 🔴 major (downstream impls break) |
| Add new trait impl for your type | 🟢 minor |
| Add new trait impl for external type (orphan rule issues) | 🔴 major |

## Functions

| Change | Severity |
|--------|---------|
| Add a function | 🟢 minor |
| Remove a function | 🔴 major |
| Change parameter type | 🔴 major |
| Add a parameter with default | 🟢 minor |
| Add a parameter without default | 🔴 major |
| Change return type | 🔴 major |
| Loosen parameter bound (e.g., `T: Clone` → `T: ?Sized`) | 🟢 minor |
| Tighten parameter bound | 🔴 major |
| Add a generic param with default | 🟢 minor |
| Add a generic param without default | 🔴 major |

## Type aliases and consts

| Change | Severity |
|--------|---------|
| Change type alias to a different type | 🔴 major |
| Change const value | 🟢 minor (but downstream may depend on the value) |
| Change const type | 🔴 major |

## Macros

| Change | Severity |
|--------|---------|
| Add a new rule to declarative macro | 🟢 minor |
| Change macro syntax accepted | 🔴 major |
| Remove a rule | 🔴 major |

## Features and Cargo.toml

| Change | Severity |
|--------|---------|
| Add a new feature | 🟢 minor |
| Remove a feature | 🔴 major |
| Add a feature that defaults on | 🔴 major (changes default build) |
| Remove `default` feature | 🔴 major |
| Add `default = ["x"]` | 🟢 minor (or 🔴 if it changes default build) |
| Add a dependency | 🟢 minor |
| Remove a dependency | 🔴 major (if it was public) |
| Bump dependency minor | 🟢 minor |
| Bump dependency major | 🔴 major (if it's public) |

## MSRV (Minimum Supported Rust Version)

| Policy | Severity |
|--------|---------|
| Bump MSRV from `1.70` to `1.75` | 🟢 minor (under semver) — but **controversial**; some treat as 🔴 |
| Lower MSRV | 🟢 minor |

The Cargo team's official stance is that MSRV bumps are minor. But many crates treat MSRV bumps as major out of courtesy. State your policy in the README.

## Pre-1.0 special rules

| Version pattern | Breaking = ? |
|----------------|--------------|
| `0.0.x` | Any change. The crate is experimental. |
| `0.x.y` (x ≥ 1) | Breaking = bump the **x** (minor position) |
| `1.x.y` and beyond | Standard semver |

A version `0.1.0` is *implicitly* `0.1.*`-compatible with downstream. So `0.1.0` → `0.1.1` is patch; `0.1.0` → `0.2.0` is "major" (requires downstream to opt in via `=0.1.0` or `"0.2"` update).

## Non-semver but relevant

These aren't semver-relevant but matter for downstream:

- Performance regression (slower by 20%) — usually patch, sometimes minor
- Memory usage change — patch
- Compile time change — not semver-relevant
- Error message text change — patch (downstream may parse, but that's their bug)

## Verification Commands

```bash
# Mechanically check breaking changes
cargo semver-checks check-release

# Diff the public API against a baseline
cargo public-api diff 1.2.0..HEAD

# Show the public API
cargo public-api
```
