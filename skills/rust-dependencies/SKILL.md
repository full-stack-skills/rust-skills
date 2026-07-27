---
name: rust-dependencies
description: Manage Rust dependency governance at scale — version requirement strategy, crate and source selection, feature minimization, transitive dependency analysis, cargo-deny license/ban/advisory/source policy, cargo-audit, cargo-outdated, Renovate/Dependabot automation, dependency update cadence, cycle diagnosis, and supply-chain security. Use for dependency strategy, crate approval, license compliance, advisories, allowed sources, automated updates, or dependency-graph governance; hand Cargo manifest and registry configuration, lockfile mechanics, resolvers, and Cargo command behavior to rust-cargo-build, semver compatibility decisions to rust-semver, and lint policy to rust-style-clippy.
---

# Rust Dependency Management and Governance

> Authority: [Cargo — Specifying Dependencies](https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html), [Cargo — Dependency Resolution](https://doc.rust-lang.org/cargo/reference/resolver.html), [Cargo — Source Replacement](https://doc.rust-lang.org/cargo/reference/source-replacement.html), [Cargo — Credentials](https://doc.rust-lang.org/cargo/reference/registry-authentication.html), [cargo-deny](https://embarkstudios.github.io/cargo-deny/), [cargo-audit](https://crates.io/crates/cargo-audit), [RustSec](https://rustsec.org/).

This skill owns the **governance of dependencies**: how to declare them safely, what they pull in, who is allowed in, and what to do when one goes wrong. It does not own the Cargo.toml field reference (`rust-cargo-build`), semver (`rust-semver`), or workspace topology (`rust-workspace`).

## Capability Boundaries

### ✅ Strengths
1. Choosing the right version requirement (`"1"` vs `"1.2"` vs `"=1.2.3"`)
2. Evaluating dependency sources (crates.io / git / path / private registry)
3. Setting up source replacement for vendored or mirrored registries
4. Configuring `cargo-deny` (4 tables: advisories, licenses, bans, sources)
5. Running `cargo-audit` and responding to RustSec advisories
6. Diagnosing dependency cycles and duplicate-version problems via `cargo tree`
7. Setting MSRV-aware resolver behavior
8. Automating dependency updates with Renovate / Dependabot
9. Establishing supply-chain policy for an organization

### ⚠️ Prerequisites
1. Cargo manifest basics — see `rust-cargo-build`
2. Semver vocabulary — see `rust-semver`

### ❌ Out of Scope
1. Cargo.toml field-by-field reference → `rust-cargo-build`
2. Workspace layout → `rust-workspace`
3. Clippy / lint policy → `rust-style-clippy`
4. Testing dependency injection → `rust-testing`

## Data Privacy

This skill does not collect, store, or transmit user data. Private registry access and credential use are user-authorized actions; never log credentials or expose tokens in build artifacts.

---

# Part 1: Version Requirement Syntax

Cargo uses SemVer version **requirements** (not exact versions) by default.

| Syntax | Meaning | Compatibility |
|--------|---------|--------------|
| `"1"` or `"^1"` | `>=1.0.0, <2.0.0` | Default — auto-update within major |
| `"1.2"` or `"^1.2"` | `>=1.2.0, <2.0.0` | At least 1.2.x |
| `"1.2.3"` or `"^1.2.3"` | `>=1.2.3, <2.0.0` | At least 1.2.3, may pull 1.5.0 |
| `"=1.2.3"` | Exactly 1.2.3 | Pin — for reproducibility |
| `"~1.2"` | `>=1.2.0, <1.3.0` | Within minor only |
| `"~1.2.3"` | `>=1.2.3, <1.3.0` | Within minor only |
| `">=1.0, <2.0"` | Range | Explicit bounds |
| `"*"` | Any | Forbidden on crates.io — too loose |
| `"0.1"` or `"^0.1"` | `>=0.1.0, <0.2.0` | Pre-1.0: minor treated as major |
| `"0.0.1"` | `>=0.0.1, <0.0.2` | Pre-0.1: patch treated as major |

## The default is caret (`^`)

```toml
[dependencies]
serde = "1"              # caret by default
serde = { version = "1" }   # same
```

This is usually right. You get bug fixes and non-breaking features automatically.

## When to deviate

| Need | Use | Example |
|------|-----|---------|
| Pin for reproducibility | `=` | `"=1.2.3"` |
| Restrict to minor only | `~` | `"~1.2"` (no 1.3.x) |
| Bounded range | `>=, <` | `">=1.0, <1.5"` |
| Pre-1.0 with breaking minors | minor pin | `"0.7.3"` (Cargo treats as <0.8) |
| Git head | git | `{ git = "..." }` |

## Caret rule for pre-1.0

```toml
# These are equivalent and both mean <0.2:
my-crate = "0.1"
my-crate = "^0.1"

# 0.0.x is even more restrictive:
my-crate = "0.0.3"      # means >=0.0.3, <0.0.4 — almost a pin
```

The pre-1.0 rules exist because the SemVer spec treats `0.x` as "anything goes." Cargo encodes community convention: minor bump in `0.x` = breaking.

---

# Part 2: Dependency Sources

## crates.io (default)

```toml
[dependencies]
serde = "1"
```

Public, immutable, audited via [crates.io](https://crates.io). This is what 99% of dependencies should use.

## Git

```toml
[dependencies]
# Branch / tag / rev / default
my-crate = { git = "https://github.com/user/repo", branch = "dev" }
my-crate = { git = "https://github.com/user/repo", tag = "v1.0.0" }
my-crate = { git = "https://github.com/user/repo", rev = "abc1234" }
my-crate = { git = "https://github.com/user/repo" }
```

**Use sparingly**: git deps make `Cargo.lock` non-portable, slow down CI, and cannot be published to crates.io unless the git dep is also published. Prefer crates.io, a fork published under a different name, or `cargo vendor`.

## Path (local / workspace)

```toml
[dependencies]
my-core = { path = "../core", version = "0.1" }
```

Required for workspace internal deps. Always pair with a `version` for publishing (otherwise `cargo publish` fails).

## Private registry

```toml
# .cargo/config.toml
[registries.my-registry]
index = "sparse+https://my-registry.example.com/index/"

[registry]
default = "my-registry"   # optional: make this the default
```

```toml
# Cargo.toml
[dependencies]
my-private-crate = { version = "1.0", registry = "my-registry" }
```

## Source replacement (transparent)

[Cargo Source Replacement](https://doc.rust-lang.org/cargo/reference/source-replacement.html) lets you replace crates.io with a mirror — without editing each `Cargo.toml`:

```toml
# .cargo/config.toml
[source.my-mirror]
registry = "sparse+https://mirrors.example.com/crates.io-index"

[source.crates-io]
replace-with = "my-mirror"
```

Use cases: enterprise proxy, China mirrors (`RsProxy`, `tuna`), vendored offline builds.

## Vendored

```bash
cargo vendor vendor/   # downloads all deps to vendor/
```

```toml
# .cargo/config.toml
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
```

For air-gapped / reproducible builds. Check `vendor/` into git (it's large but stable).

---

# Part 3: Dependency Tree Analysis

## `cargo tree`

```bash
cargo tree                        # full tree
cargo tree --depth 2              # limit
cargo tree --invert --package X   # what depends on X?
cargo tree -e features            # show feature unification
cargo tree -e no-dev              # exclude dev-deps
cargo tree -e no-build            # exclude build-deps
```

## Finding duplicates

```bash
cargo tree --duplicates           # show crates with multiple versions
```

If you see `serde` at both 1.0.180 and 1.0.195, that's two versions in the tree. Common causes:
- An old transitive dep requires an old version
- A git dep pulled in a specific version
- Your own version requirement is too tight

## Resolving duplicates

```bash
cargo update -p serde             # bump to latest matching req
cargo update -p serde --precise 1.0.200
```

If a transitive dep pins an old version, you can either:
1. Update the transitive dep (`cargo update -p that-crate`)
2. Live with the duplicate (usually fine)
3. Replace the transitive with a fork

## Detecting cycles

Cargo forbids cycles in the dependency graph. If you see:

```
error: cyclic package dependency: package `a` depends on `b`. package `b` depends on `a`.
```

You have a real design bug — restructure (often by extracting a shared crate `c` that both depend on).

---

# Part 4: Dependency Update Governance

Use `rust-cargo-build` for current Cargo.lock version-control guidance and the exact behavior of `--locked`, `--offline`, and `--frozen`. The current Cargo Guide recommends committing `Cargo.lock` when in doubt; do not apply an application-versus-library prohibition here.

This skill owns how resolved dependency changes are proposed, reviewed, and approved:

```bash
cargo update                      # bump all to latest within reqs
cargo update --precise 1.0.200 -p serde   # pin a specific version
cargo update --dry-run            # see what would change
```

- Prefer package-scoped updates over unrelated graph churn.
- Review lockfile source, checksum, version, feature, and duplicate-version changes.
- Run advisories, licenses, bans, and source-policy checks on the proposed graph.
- Keep automated update pull requests bounded and observable.
- Use a separate scheduled compatibility lane when libraries need to test newly resolved dependency ranges.
- Never add an unconditional `cargo update` to required CI merely to make a stale lockfile pass.

---

# Part 5: cargo-deny (Supply-Chain Governance)

[`cargo-deny`](https://embarkstudios.github.io/cargo-deny/) is the de-facto tool for dependency policy. Four checks:

## 5.1 advisories — RustSec

```toml
# deny.toml
[advisories]
db-urls = ["https://github.com/rustsec/advisory-db"]
yanked = "deny"
ignore = [
    # "RUSTSEC-2024-0001",  # ignore specific advisory with justification
]
```

```bash
cargo deny check advisories
```

## 5.2 licenses — policy

```toml
# deny.toml
[licenses]
allow = [
    "MIT",
    "Apache-2.0",
    "BSD-3-Clause",
    "ISC",
    "Unicode-DFS-2016",
]
confidence-threshold = 0.93

[[licenses.exceptions]]
allow = ["Zlib"]
name = "some-zlib-crate"
version = "1.0"
```

```bash
cargo deny check licenses
```

Default is permissive; tighten to your org's policy.

## 5.3 bans — forbidden crates

```toml
# deny.toml
[bans]
multiple-versions = "warn"
wildcards = "deny"        # don't allow "2.*" requirements

[[bans.deny]]
name = "openssl"          # prefer rustls
version = "*"

[[bans.deny]]
name = "chrono"
version = "<0.5"          # only old versions

[bans.workspace-dependencies]
duplicates = "deny"       # require [workspace.dependencies]
```

```bash
cargo deny check bans
```

## 5.4 sources — where deps come from

```toml
# deny.toml
[sources]
unknown-registry = "deny"   # disallow non-crates.io registries
unknown-git = "deny"        # disallow non-allowlisted git sources
allow-registry = ["crates-io"]
allow-git = []
```

```bash
cargo deny check sources
```

## All-in-one

```bash
cargo deny check               # runs all four
```

CI integration:

```yaml
- uses: EmbarkStudios/cargo-deny-action@v2
  with:
    command: check
```

---

# Part 6: cargo-audit

[`cargo-audit`](https://crates.io/crates/cargo-audit) scans `Cargo.lock` against the RustSec advisory database.

```bash
cargo install cargo-audit --locked
cargo audit                           # scan
cargo audit --deny warnings           # fail CI on warnings
cargo audit --ignore RUSTSEC-XXXX     # ignore specific advisory
```

Difference from `cargo-deny`:
- `cargo-audit` is **advisory-only** (security focus)
- `cargo-deny` covers advisories + licenses + bans + sources

Most projects use `cargo-deny` as a superset. Some use both (defense in depth).

## Responding to an advisory

1. Run `cargo audit` to identify the vulnerable crate + version
2. Check [RustSec](https://rustsec.org/advisories/) for the fixed version
3. `cargo update -p vulnerable-crate --precise X.Y.Z`
4. If no fix exists: switch to a maintained fork, remove the dependency, or disable the affected feature
5. File an issue upstream if it's a new vulnerability

---

# Part 7: Automation

## Renovate

[Renovate](https://docs.renovatebot.com/) auto-opens PRs when deps update. Supports Cargo out of the box:

```json
// .renovaterc.json
{
  "extends": ["config:recommended", ":semanticCommits"],
  "schedule": ["before 6am on Monday"]
}
```

## Dependabot

[Dependabot](https://docs.github.com/en/code-security/dependabot) is GitHub-native:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "cargo"
    directory: "/"
    schedule:
      interval: "weekly"
```

## Cargo's own auto-update

There's no built-in "cargo update PR" tool, but you can script it:

```bash
cargo update
git diff Cargo.lock
# Commit + push to a branch
```

---

# Part 8: Feature Minimization

```toml
[dependencies]
serde = { version = "1", features = ["derive"] }     # only what you use
tokio = { version = "1", features = ["rt-multi-thread", "macros"] }
```

Each enabled feature increases compile time, binary size, and attack surface. Disable defaults when you only need a subset:

```toml
[dependencies]
tokio = { version = "1", default-features = false, features = ["rt", "net"] }
```

## Inspecting features

```bash
cargo tree -e features              # which features are enabled, where
cargo tree -e features -p tokio     # just tokio's features
```

If `tokio` shows up with `[full]` from a transitive dep, you're paying for more than you use.

## Workspace dep governance

```toml
# root Cargo.toml
[workspace.dependencies]
serde = { version = "1", features = ["derive"] }   # pin features once

# crates/abc/Cargo.toml
[dependencies]
serde.workspace = true    # inherits feature set
```

Prevents feature drift across members.

---

## Workflow

1. **Inventory** — `cargo tree -e features`, `cargo tree --duplicates`
2. **Audit** — `cargo audit` (advisories) + `cargo deny check` (full policy)
3. **Tighten versions** — replace `"*"` with `"1"`; pin exact only when reproducible
4. **Minimize features** — `default-features = false`, list only what you use
5. **Decide sources** — prefer crates.io; reserve git/path for legitimate cases
6. **Configure CI** — `cargo build --locked`, `cargo deny check`, scheduled `cargo audit`
7. **Automate updates** — Renovate or Dependabot with semantic commits

## Decision Shortcuts

| Question | Answer |
|---------|--------|
| Pin or caret? | Caret (`"1"`) by default; pin (`"=1.2.3"`) for reproducibility only |
| crates.io or git? | crates.io unless you have a specific reason |
| Use latest or wait? | Wait 1-2 weeks for new majors; auto-patch for patches |
| Allow `"*"` requirements? | No — crates.io rejects them, and they hide upgrades |
| How many versions of `serde`? | One. If duplicates, trace via `cargo tree --duplicates` |
| Commit Cargo.lock for a library? | No — downstream owns the lock |
| CI: `--locked` or `--frozen`? | `--locked` for normal CI; `--frozen` for air-gapped |

## Resources

- [Cargo — Specifying Dependencies](references/version-requirements.md) — full syntax reference
- [cargo-deny Configuration Cookbook](references/cargo-deny-cookbook.md) — 4-table policies
- [Private Registry Setup](examples/private-registry.md) — credentials, source replacement
- `examples/golden-deps/` — a small crate with a minimal, audited dep set

## Upstream Sources

- [Cargo — Specifying Dependencies](https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html)
- [Cargo — Dependency Resolution](https://doc.rust-lang.org/cargo/reference/resolver.html)
- [Cargo — Source Replacement](https://doc.rust-lang.org/cargo/reference/source-replacement.html)
- [Cargo — Registries](https://doc.rust-lang.org/cargo/reference/registries.html)
- [cargo-deny Book](https://embarkstudios.github.io/cargo-deny/)
- [cargo-audit](https://crates.io/crates/cargo-audit)
- [RustSec Advisory Database](https://rustsec.org/)
- [cargo-outdated](https://crates.io/crates/cargo-outdated)
