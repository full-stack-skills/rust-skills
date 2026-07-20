---
name: rust-documentation
description: Design, write, build, test, and publish Rust documentation with rustdoc, cargo doc, doctests, intra-doc links, crate-level guides, examples, README synchronization, mdBook, docs.rs metadata, link checking, and documentation CI. Use when users ask for Rust API docs, a project book, runnable examples, docs.rs readiness, missing-doc policy, documentation architecture, or stale documentation repair.
---

# Rust Documentation

Treat documentation as an executable interface. Keep API reference close to code, conceptual and operational guides in an appropriate book or repository document, and examples compiled against the supported API.

## Scope and Routing

Use this skill for rustdoc comments, crate and module documentation, doctests, intra-doc links, README generation, mdBook, docs.rs configuration, link checking, spelling, and documentation release gates.

Route general test architecture to `rust-testing`, public API compatibility to `rust-code-review`, Cargo metadata and publishing to `rust-cargo-build`, and non-Rust office document formats to their dedicated document skills.

## Workflow

### 1. Identify readers and documentation surfaces

Inventory public crates, binaries, features, targets, examples, READMEs, books, generated references, and hosted output. Define the audience and owner for each surface:

| Surface | Primary purpose |
|---|---|
| Crate and module docs | Entry path, architecture, feature and platform overview |
| Item docs | Contract, errors, panics, safety, examples, complexity |
| Doctests and examples | Executable usage and compatibility proof |
| README | Discovery, installation, minimal quick start, support policy |
| mdBook | Tutorials, concepts, operations, migration, long-form guides |
| docs.rs | Versioned public API publication |

Avoid duplicating the same prose across surfaces without a declared source of truth.

### 2. Document the contract

For each public API, document only applicable sections:

- what the item does and important semantics;
- `# Examples` with assertions and realistic imports;
- `# Errors` for each meaningful failure category;
- `# Panics` for reachable panic conditions;
- `# Safety` for caller obligations on unsafe APIs;
- cancellation, blocking, allocation, complexity, platform, feature, and MSRV constraints.

Prefer intra-doc links such as ``[`Client::send`]`` over brittle hand-written URLs. Enable broken-link checking at the crate boundary:

```rust
#![deny(rustdoc::broken_intra_doc_links)]
```

Adopt `missing_docs` deliberately; do not enable it globally before deciding which public compatibility surface requires documentation.

### 3. Make examples executable

Use doctests for small public API contracts and `examples/` crates for complete workflows. Mark fences precisely:

- ordinary Rust fences compile and run;
- `no_run` compiles code that requires unavailable external effects;
- `compile_fail` proves rejected usage without locking full diagnostics;
- `ignore` is a last resort with a documented reason.

Run:

```bash
cargo test --workspace --doc --all-features
RUSTDOCFLAGS="-D warnings" cargo doc --workspace --all-features --no-deps
```

Read [rustdoc and Doctests](references/rustdoc-and-doctests.md) when authoring API documentation.

### 4. Build long-form guides with mdBook

Use mdBook for tutorials, architecture, operations, and migration material that would overload API docs. Keep `SUMMARY.md` as the explicit navigation contract. Test Rust code samples with `mdbook test`, build in CI, and check internal plus external links. Read [mdBook and Project Guides](references/mdbook-and-guides.md).

### 5. Prepare versioned publication

Inspect package metadata, docs.rs target and feature configuration, README links, repository URLs, licenses, examples, and hidden/private APIs. Verify docs using the locked dependency graph and supported MSRV/current stable rather than only the author's machine.

Do not publish, change hosted documentation, or enable external analytics without authorization. Read [Documentation Release Quality](references/documentation-release-quality.md).

## Quality Gates

```bash
cargo fmt --all --check
cargo test --workspace --doc --all-features
RUSTDOCFLAGS="-D warnings" cargo doc --workspace --all-features --no-deps
mdbook test path/to/book
mdbook build path/to/book
lychee README.md docs book/src
typos README.md docs book/src src
```

Run only tools present in the project or approved for installation. Pin non-Rust documentation tools in CI and do not silently rewrite prose during a check-only job.

## Completion Criteria

- Give each audience a clear entry point and avoid conflicting sources of truth.
- Document public errors, panics, safety, features, targets, and compatibility where applicable.
- Compile and run representative documentation examples.
- Reject broken intra-doc and repository links.
- Build the same feature and target documentation intended for publication.
- Record skipped external, platform, or hosted verification explicitly.

## Resources

- [rustdoc and Doctests](references/rustdoc-and-doctests.md)
- [mdBook and Project Guides](references/mdbook-and-guides.md)
- [Documentation Release Quality](references/documentation-release-quality.md)
- [Execution Scenarios](examples/examples.md)
- `examples/golden-docs/`: a compilable crate with enforced intra-doc links and doctests.

## Upstream Sources

- [The rustdoc Book](https://doc.rust-lang.org/rustdoc/)
- [Rustdoc documentation tests](https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html)
- [Cargo doc](https://doc.rust-lang.org/cargo/commands/cargo-doc.html)
- [mdBook](https://rust-lang.github.io/mdBook/)
- [docs.rs metadata](https://docs.rs/about/metadata)

## Data Privacy

This skill does not collect, store, or transmit user data. Review examples, generated source links, build logs, and hosted analytics for secrets or proprietary paths before publication.
