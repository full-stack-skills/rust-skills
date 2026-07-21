# Cargo Version Requirements — Full Reference

Companion to `SKILL.md` §1. Comprehensive version requirement syntax with examples and edge cases.

## Semver requirement grammar

A Cargo "version requirement" is a constraint, not an exact version. Cargo matches against the requirement when resolving which version to download.

```
requirement = [op] version_part
op          = "^" | "~" | "=" | ">" | ">=" | "<" | "<=" | "*"
version_part = major ["." minor ["." patch]]
```

If no op is specified, it defaults to `^` (caret).

## Caret (`^`) — the default

Allows changes that do not modify the leftmost non-zero element.

| Requirement | Means |
|-------------|-------|
| `"^1.2.3"` | `>=1.2.3, <2.0.0` |
| `"^1.2"` | `>=1.2.0, <2.0.0` |
| `"^1"` | `>=1.0.0, <2.0.0` |
| `"^0.2.3"` | `>=0.2.3, <0.3.0` |
| `"^0.0.3"` | `>=0.0.3, <0.0.4` |
| `"^0.0"` | `>=0.0.0, <0.1.0` |
| `"^0"` | `>=0.0.0, <1.0.0` |

Caret is the default; the `^` is optional.

## Tilde (`~`) — within minor

| Requirement | Means |
|-------------|-------|
| `"~1.2.3"` | `>=1.2.3, <1.3.0` |
| `"~1.2"` | `>=1.2.0, <1.3.0` |
| `"~1"` | `>=1.0.0, <2.0.0` (same as caret) |

Tilde is more conservative than caret for full versions: it pins the minor.

## Equal (`=`) — exact pin

| Requirement | Means |
|-------------|-------|
| `"=1.2.3"` | exactly 1.2.3 |
| `"=1.2"` | `>=1.2.0, <1.3.0` (same as `~1.2`) |
| `"=1"` | `>=1.0.0, <2.0.0` (same as `^1`) |

Use `=` for reproducibility — but be aware you'll need to manually bump for security patches.

## Comparison (`<`, `<=`, `>`, `>=`)

```toml
[dependencies]
foo = ">=1.0, <2.0"        # range
bar = ">=1.2.3"            # unbounded upper
baz = "<2.0"               # bounded upper
```

Multiple bounds can be combined with commas:

```toml
[dependencies]
foo = ">=1.0, <1.5, !=1.3.0"   # 1.3.0 was broken
```

## Wildcard (`*`)

```toml
foo = "*"    # any version
foo = "1.*"  # any 1.x.y
foo = "1.2.*" # any 1.2.z
```

`*` is rejected by crates.io publishing. Use only for local development.

## Pre-release and build metadata

```toml
foo = "1.0.0-beta.1"        # matches 1.0.0-beta.1 only
foo = "1.0.0-alpha"         # matches 1.0.0-alpha
foo = ">=1.0.0-alpha, <2.0.0"
```

SemVer rules: pre-release versions are *less than* the release. So `1.0.0-beta.1 < 1.0.0`. Pre-releases only match if they share the same `[major, minor, patch]` tuple unless explicitly requested.

## Worked examples

```toml
[dependencies]
serde = "1"                        # latest 1.x.y
serde = { version = "1.0.200" }    # latest >=1.0.200, <2.0.0
serde = { version = "=1.0.200" }   # exactly 1.0.200
serde = { version = "~1.0" }       # latest 1.0.x
serde = { version = "1.*" }        # any 1.x.y (same as ^1)
serde = { version = "1.0.*" }      # any 1.0.x (same as ~1.0)
```

## Pre-1.0 special behavior

The Cargo team's convention: pre-1.0 minor bumps are breaking. This is encoded in the caret rule:

| Requirement | Means |
|-------------|-------|
| `"0.7.3"` | `>=0.7.3, <0.8.0` |
| `"0.7"` | `>=0.7.0, <0.8.0` |
| `"0.0.4"` | `>=0.0.4, <0.0.5` (almost a pin) |

So if you have a dep at `0.7.3`, the next breaking change is `0.8.0` (major-minor position).

## Updating behavior

When you run `cargo update`:

```bash
cargo update                          # bump within reqs
cargo update -p serde                 # just serde
cargo update -p serde --precise 1.0.201   # exact
cargo update --dry-run                # see what would change
```

Updates only happen within the version requirement you declared. To go beyond:

- Edit Cargo.toml requirement, then `cargo update`
- Or `cargo update --precise X.Y.Z` to bypass

## Lockfile and reproducibility

When `Cargo.lock` exists and matches your requirements, `cargo build` uses the locked versions. `cargo update` rewrites the lock.

For CI reproducibility:

```bash
cargo build --locked     # fail if Cargo.lock is stale
cargo build --frozen     # --locked + --offline
```

## Source

- [Cargo — Specifying Dependencies](https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html)
- [SemVer 2.0 spec](https://semver.org/)
- [Cargo SemVer compatibility](https://doc.rust-lang.org/cargo/reference/semver.html)
