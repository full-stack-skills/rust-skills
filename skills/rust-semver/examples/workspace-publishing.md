# Workspace Publishing Cookbook

Recipes for publishing multi-crate workspaces with `cargo-workspaces` and `cargo-release`.

## Scenario A: Lockstep versioning (simplest)

All member crates share one version. Bump together, publish together.

### Setup

```toml
# root Cargo.toml — virtual manifest
[workspace]
resolver = "3"
members = ["crates/*"]

[workspace.package]
version = "0.1.0"           # shared
edition = "2024"
license = "Apache-2.0"

[workspace.dependencies]
my-core = { path = "crates/core", version = "0.1.0" }
my-net = { path = "crates/net", version = "0.1.0" }
```

```toml
# crates/net/Cargo.toml
[package]
name = "my-net"
version.workspace = true      # inherits 0.1.0
edition.workspace = true
license.workspace = true

[dependencies]
my-core.workspace = true      # internal dep uses version from [workspace.dependencies]
```

### Bump and publish

```bash
# Install once
cargo install cargo-workspaces --locked

# 1. Run all quality gates
cargo fmt --all --check
cargo test --workspace --all-targets --all-features
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo semver-checks check-release  # if baseline available

# 2. Bump all members together
cargo workspaces version minor            # 0.1.0 → 0.2.0
# This command:
#   - Updates version.workspace in each member's Cargo.toml
#   - Updates [workspace.dependencies] version for internal crates
#   - Updates Cargo.lock
#   - Commits + tags if you pass --no-individual-tags

# 3. Publish all in topological order
cargo workspaces publish
```

### Cleanup

The bump command creates a commit + tag. Push:

```bash
git push --follow-tags
```

## Scenario B: Independent versioning

Member crates have their own version trajectories.

### Setup

```toml
# crates/net/Cargo.toml — explicit version, not inherited
[package]
name = "my-net"
version = "1.5.0"           # not .workspace = true

[dependencies]
my-core = { path = "../core", version = "0.3" }  # allows 0.3.x of core
```

### Bump and publish

```bash
# Bump only one crate:
cd crates/net
cargo workspaces version minor      # only bumps crates/net

# Or use cargo-release:
cargo install cargo-release --locked
cargo release minor --package my-net --execute
```

## Scenario C: cargo-release (full automation)

[`cargo-release`](https://crates.io/crates/cargo-release) handles version bump, CHANGELOG, commit, tag, push, and publish in one command.

### Setup — `release.toml` at workspace root

```toml
consolidate-commits = true       # single commit per release
pre-release-commit-message = "release: {{version}}"
pre-release-replacements = [
    { file = "CHANGELOG.md", search = "Unreleased", replace = "{{version}}" },
]
```

### One-shot release

```bash
# Dry run first:
cargo release minor --dry-run

# Real release:
cargo release minor --execute
```

This:
1. Bumps version in Cargo.toml(s)
2. Updates CHANGELOG.md
3. Commits with a `release: x.y.z` message
4. Tags `v1.2.3` (or `my-crate-v1.2.3` for workspace)
5. Pushes commit + tag
6. Runs `cargo publish` for each member in topological order

## Scenario D: release-plz (conventional commits)

[`release-plz`](https://release-plz.io/) generates CHANGELOG from [Conventional Commits](https://www.conventionalcommits.org/) and auto-versions based on commit prefixes.

- `feat: add X` → minor
- `fix: handle Y` → patch
- `feat!: breaking change` → major (or `BREAKING CHANGE:` in body)

### Setup

```bash
# Install
cargo install release-plz --locked

# Initialize (creates release-plz.toml)
release-plz init

# Generate a release PR
release-plz update
```

### CI

release-plz has a GitHub Action that opens a PR whenever conventional commits land on main. Merge the PR → release-plz publishes. See [release-plz.ci](https://release-plz.io/docs/ci).

## Scenario E: Hotfix an already-published version

You published 1.2.0 with a critical bug. Workflow:

```bash
# 1. Branch from the v1.2.0 tag
git checkout -b hotfix-1.2.1 v1.2.0

# 2. Fix the bug
git commit -m "fix: critical bug in 1.2.0"

# 3. Bump patch version
# Edit Cargo.toml: version = "1.2.1"
# Edit CHANGELOG.md

# 4. Publish
cargo publish

# 5. Yank the broken version (prevents new deps on it)
cargo yank --vers 1.2.0

# 6. Merge hotfix into main
git checkout main
git merge hotfix-1.2.1
git push
```

## Scenario F: Pre-release workflow (beta/rc)

```bash
# Publish a beta:
cargo workspaces version prerelease --pre-id beta --force  # 0.1.0 → 0.2.0-beta.1

# Publish next beta:
cargo workspaces version prerelease --pre-id beta          # → 0.2.0-beta.2

# Release the stable:
cargo workspaces version release                           # → 0.2.0
```

Downstream opts into beta:

```toml
[dependencies]
my-crate = "=0.2.0-beta.1"
```

## Common pitfalls

### `cargo publish` fails: "no token found"

You need a crates.io token. Generate at https://crates.io/settings/tokens, then:

```bash
cargo login <token>
```

Token is stored in `~/.cargo/credentials`.

### Internal path deps with version

```toml
# Wrong — version mismatch
[dependencies]
my-core = { path = "../core" }   # no version → publish will fail

# Right
[dependencies]
my-core = { path = "../core", version = "0.1" }   # version for downstream
```

### Owner / publish permission

A crate name is owned by the first publisher. To add collaborators:

```bash
cargo owner --add githubuser:username
```

### `publish = false` in a binary crate

```toml
[package]
name = "my-app"
publish = false   # app, not a library — never publish
```

## Tools

| Tool | Purpose |
|------|---------|
| [cargo-workspaces](https://crates.io/crates/cargo-workspaces) | Workspace version + publish |
| [cargo-release](https://crates.io/crates/cargo-release) | Single-command release |
| [release-plz](https://release-plz.io/) | Conventional-commits-driven |
| [cargo-semver-checks](https://github.com/obi1kenobi/cargo-semver-checks) | Verify semver before publish |
| [cargo-deny](https://embarkstudios.github.io/cargo-deny/) | License/advisory/ban checks |
| [cargo-audit](https://crates.io/crates/cargo-audit) | RustSec advisory scan |
