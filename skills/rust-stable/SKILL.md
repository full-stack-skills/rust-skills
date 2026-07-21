---
name: rust-stable
description: Implement and explain stable Rust language and standard-library code with explicit toolchain and MSRV checks, covering ownership, borrowing, lifetimes, traits, generics, conversions, collections, errors, paths, files, interior mutability, and stable API selection. Use as the core Rust language skill when users ask for Rust syntax, compiler-error fixes, standard-library choices, or version-sensitive stable code; hand specialized domains to their dedicated skills.
---

# Rust Stable Language and Standard Library

Use this skill as the primary entry point for stable Rust language features and standard-library APIs. First verify the project's actual toolchain and Minimum Supported Rust Version (MSRV), then select general language resources or hand the task to a specialized skill; do not infer the user's version from the skill name.

## Prerequisites Before Starting

1. Run `rustc --version --verbose` and `cargo --version`.
2. Inspect the `rust-version` field in `rust-toolchain.toml`, `rust-toolchain`, and `Cargo.toml`.
3. Distinguish between three versions: local toolchain, project MSRV, and current official stable release.
4. When encountering version-sensitive APIs, consult [Current Stable Baseline](references/release-current.md) and rely on official release notes and API documentation as the final authority.
5. If a project is locked to an old version, strictly adhere only to syntaxes and APIs that are already stabilized for that specific version.

**Current Offline Baseline:** Rust 1.97.1 (released July 16, 2026). This is a dated repository baseline and does not update automatically.

## Capability Boundaries

### Suitable For Handling
- Ownership, borrowing, lifetimes, and move semantics.
- `struct`, `enum`, pattern matching, traits, generics, and associated types.
- `Option`, `Result` error propagation, and custom errors.
- `Vec`, `String`, `HashMap`, iterators, closures.
- `Box`, `Rc`, `Arc`, `Cell`, `RefCell`, `OnceLock`, `LazyLock`.
- Modules, visibility modifiers, attributes, formatting, and common standard library I/O.
- Common compilation errors, borrowing check failures, and stable migration judgments.

### Transfer to Specialized Skills

| User Intent | Preferred Skill | Jointly Load If Necessary |
|---|---|---|
| Project layout, module trees, workspace structure | `rust-workspace` | `rust-cargo-build` |
| Cargo.toml dependencies, features, profiles, publishing | `rust-cargo-build` | `rust-testing` |
| Threads, locks, atomics, channels, Tokio | `rust-concurrency` | `rust-stable` |
| Unit tests, integration tests, doctests, coverage | `rust-testing` | `rust-workspace` |
| Raw pointers, memory layout, FFI, Miri | `rust-unsafe-ffi` | `rust-code-review` |
| macro_rules, derive, procedural macros | `rust-macros` | `rust-stable` |
| Command contracts, standard streams, exit codes, CLI process behavior | `rust-cli` | `rust-testing`, `rust-cargo-build` |
| Server-side HTTP APIs, handlers, middleware, lifetimes | `rust-web` | `rust-concurrency`, `rust-testing` |
| SQL/ORMs, schemas, migrations, transactions, connection pools | `rust-database` | `rust-testing`, `rust-concurrency` |
| Web authentication, authorization, sessions, tokens, browser security | `rust-web-security` | `rust-web`, `rust-database` |
| Bare-metal firmware, portable no_std drivers, hardware acceptance testing | `rust-embedded` | `rust-unsafe-ffi`, `rust-cargo-build` |
| Risk, correctness, API and safety review | `rust-code-review` | `rust-style-clippy` |

Do not replace the complete workflow of domain-specific skills with this skill.

## Workflow

1. **Determine Version Boundaries** — Record toolchain version, edition, MSRV, and target platform(s).
2. **Narrow Problem Scope** — Determine whether the issue belongs to ownership/type system/standard library/compiler errors or a specialized domain.
3. **Read Minimal Resources** — Open only references directly relevant to the problem; do not load entire documentation sets at once.
4. **Implement Minimum Correct Solution** — Prioritize stable standard library usage, clear ownership semantics, and explicit error propagation.
5. **Run Quality Gate Checks** — Execute `cargo fmt --check`, `cargo check` (with all targets/features), and relevant tests.
6. **Handle Version Differences** — If an API is not supported by MSRV, choose the old compatible API or implement a compatibility shim; otherwise explicitly raise the MSRV.
7. **Transfer to Specialized Skills** — Load corresponding skills for async, unsafe macros, Web, embedded domains after entering those areas.

## Design Rules

- Prefer `&T` / `&mut T`; clone only when ownership transfer is required or independent lifetimes are needed.
- Use types to express invariants; prefer enums/newtypes over boolean parameters and unconstrained strings.
- Library code should return structured errors; application boundaries may add context before deciding how to display them.
- Prefer iterators and standard collections, but do not sacrifice readability for chain-of-call syntax.
- Do not use `unsafe` as a bypass for borrowing checks first prove that safe abstractions cannot express the requirement.
- Do not default third-party crate imports; compare against stable std, MSRV, maintenance cost, and supply chain risk.
- Never claim an API is stabilized in a specific version unless official release notes or an API page marked with `since` confirm it.

## Validation Gateways

Run validation gates from lowest to highest risk:

```bash
cargo fmt --all --check
cargo check --all-targets --all-features
cargo test --all-targets --all-features
cargo clippy --all-targets --all-features -- -D warnings
```

If the project does not support `--all-features` or contains platform-specific targets, record reasons and use a defined feature/target matrix. For unsafe code, add `cargo miri test`; for MSRV issues, repeat `cargo check` and tests on the declared minimum toolchain.

## Required Documentation to Read On-Demand

### Version & Language
- [Current Stable Baseline](references/release-current.md): Latest version, compatibility notes, update steps.
- [Ownership & Lifetimes](references/ownership-lifetimes.md): Borrowing design, return values and lifetime judgment rules.
- [Traits & Generics](references/traits-generics.md): Bounds, associated types, trait objects, API trade-offs.
- [Patterns & Idiomatic Style](references/patterns.md): Builder patterns, newtypes, RAII, typestate management.
- [Style Guide](references/style-guide.md): Naming conventions, module organization, documentation style, and API design principles.

### Standard Library Modules
- [Standard Library Index](references/std-index.md): Select modules based on task requirements.
- `Vec`, `String`, `HashMap`: Core collection types with usage patterns.
- Iterators & Formatting (`fmt`): Iterator-based iteration strategies and output formatting rules.
- I/O, Filesystem, Path: Standard library file system operations.
- Error Handling, Smart Pointers, Interior Mutability, Conversions: Advanced runtime behavior and type manipulation.

### Reproducible Examples
- [Quick Start Workflows](examples/quickstart-workflows.md)
- Ownership Patterns (`examples/ownership-patterns.md`)
- Collection Patterns (`examples/collections-patterns.md`)
- Trait Design Patterns (`examples/trait-design-patterns.md`)
- Error Handling Patterns (`examples/error-handling-patterns.md`)
- `examples/golden-basic/`: Minimal golden examples compiled by repository CI.

## Common Pitfalls to Avoid

1. Confusing "current stable" with project MSRV.
2. Running only `cargo check`, omitting tests, examples, benchmarks, or feature combinations.
3. Blindly using `clone`, wrapping in `Arc<Mutex<_>>`, or invoking `unsafe` solely to avoid borrowing errors.
4. Holding synchronous locks across `.await` calls in async code.
5. Describing versioned historical documentation as continuously updated resources.
6. Copying code snippets without including dependencies, features, error types, and platform constraints.

## Official Sources

- [Rust Release Notes](https://doc.rust-lang.org/stable/releases.html)
- [The Rust Programming Language (Book)](https://doc.rust-lang.org/book/)
- [Standard Library Reference](https://doc.rust-lang.org/std/)
- [Reference Manual](https://doc.rust-lang.org/reference/)
- [Rust by Example](https://doc.rust-lang.org/rust-by-example/)
- [Edition Guide](https://doc.rust-lang.org/edition-guide/)

## Data Privacy Policy

This skill provides local knowledge, examples, and validation workflows only. It does not collect, store, or transmit user data. Access to official documentation must comply with the user's network access requirements prior to accessing public resources.
