# Cargo Packaging and Publishing

Use [Publishing on crates.io](https://doc.rust-lang.org/cargo/reference/publishing.html) and the command pages for [cargo package](https://doc.rust-lang.org/cargo/commands/cargo-package.html), [cargo publish](https://doc.rust-lang.org/cargo/commands/cargo-publish.html), [cargo owner](https://doc.rust-lang.org/cargo/commands/cargo-owner.html), and [cargo yank](https://doc.rust-lang.org/cargo/commands/cargo-yank.html).

## Pre-publication gate

```bash
cargo fmt --all --check
cargo test --workspace --all-targets --all-features --locked
cargo clippy --workspace --all-targets --all-features --locked -- -D warnings
cargo package --list
cargo package
```

Adapt the feature and target matrix when `--all-features` is not supported. Route SemVer classification to `rust-semver`.

Review:

- package name, version, description, documentation, repository, README, keywords, and categories;
- `package.publish` restrictions when publication must be limited to named registries;
- `license` or `license-file`;
- selected files, generated content, fixtures, secrets, and archive size;
- package-normalized manifest and lockfile behavior;
- non-dev dependencies resolvable from the target registry;
- workspace dependencies with publishable versions;
- MSRV and supported target validation;
- README and doctest behavior from the packaged crate, not only the workspace checkout.

## Dry run and registry selection

`cargo package` performs package assembly and verification without upload. Use `cargo publish --dry-run` when its installed-version behavior adds a useful final check.

Resolve explicitly:

- registry name and index;
- credential provider and account;
- package ownership;
- whether dependent workspace crates must publish first;
- publication order and propagation delay.

For a package that must never publish to crates.io, restrict the allowed registry names in `package.publish` and still pass `--registry <name>` in release commands so the external target is explicit.

## External mutations

Require explicit user authorization before:

- `cargo login` or `cargo logout`;
- adding or removing owners;
- publishing a version;
- yanking or unyanking a version.

A published crates.io version cannot be deleted. Yanking prevents new dependency resolution from selecting it by default but does not remove the archive or break existing lockfiles. Use a follow-up release for corrected code.

After publication, verify the registry version, owners, rendered documentation, and installation or dependency resolution from a clean environment.
