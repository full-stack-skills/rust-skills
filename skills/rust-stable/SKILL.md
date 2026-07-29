---
name: rust-stable
description: Implement and explain stable Rust language semantics with explicit toolchain and MSRV checks — ownership, borrowing, lifetimes, move semantics, traits, generics, associated types, pattern matching, closures, error propagation, and Edition differences. Use as the core Rust language skill when users ask for Rust syntax, compiler-error fixes, ownership/borrowing diagnoses, or version-sensitive stable code; hand std API selection (which collection, which smart pointer, which string type) to rust-stdlib, "how do I write X" pattern questions to rust-by-example, and specialized domains to their dedicated skills.
---

# Rust Stable Language Semantics

Use this skill for **language semantics**: ownership, borrowing, lifetimes, traits, generics, pattern matching, error propagation, and Edition differences. First verify the project's actual toolchain and Minimum Supported Rust Version (MSRV).

For **standard-library API selection** (which collection, which smart pointer, which string type, which I/O trait), use `rust-stdlib`. For **concrete pattern examples** ("how do I write X"), use `rust-by-example`.

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
- `Option`, `Result` error propagation, and custom errors (the *language mechanism*).
- Closures (`Fn`/`FnMut`/`FnOnce`), attribute syntax, format strings (the *language mechanism*).
- Modules, visibility modifiers, `pub`/`pub(crate)`/`pub(super)`.
- Edition differences (language-level — `unsafe extern`, RPIT capture, match ergonomics).
- Common compilation errors, borrowing check failures, and stable migration judgments.

### Hand Off to Specialized Skills

| User Intent | Preferred Skill |
|---|---|
| **"Which std collection / smart pointer / string type should I use?"** | `rust-stdlib` |
| **"How do I write X in Rust?"** (concrete pattern) | `rust-by-example` |
| API design (naming, traits, future-proofing, ~100 C-* rules) | `rust-api-design` |
| Project layout, module trees, workspace structure | `rust-workspace`, `rust-module-layout` |
| Cargo.toml dependencies, features, profiles, publishing | `rust-cargo-build` |
| Dependency governance, supply chain, cargo-deny | `rust-dependencies` |
| Semver, breaking-change classification, publish workflow | `rust-semver` |
| Java Maven/Gradle project migration and component replacement | `rust-java-migration` |
| Java-to-Rust source-test parity, Rust obligations, and migration test audit | `rust-java-migration-testing` |
| Threads, locks, atomics, channels, Tokio | `rust-concurrency` |
| Unit tests, integration tests, doctests, coverage | `rust-testing` |
| Raw pointers, memory layout, FFI, Miri | `rust-unsafe-ffi` |
| UniFFI-generated Kotlin, Swift, Python, Ruby, or WASM bindings | `rust-uniffi-building` |
| macro_rules, derive, procedural macros | `rust-macros` |
| Command contracts, standard streams, exit codes, CLI | `rust-cli` |
| Server-side HTTP APIs, handlers, middleware | `rust-web` |
| SQL/ORMs, schemas, migrations, transactions, pools | `rust-database` |
| Web authentication, authorization, sessions, tokens | `rust-web-security` |
| Bare-metal firmware, no_std drivers, hardware validation | `rust-embedded` |
| Risk, correctness, API and safety review | `rust-code-review` |
| rustfmt, Clippy, Edition migration, lint policy | `rust-style-clippy` |

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

### Version & Language Semantics
- [Current Stable Baseline](references/release-current.md): Latest version, compatibility notes, update steps.
- [Ownership & Lifetimes](references/ownership-lifetimes.md): Borrowing design, return values and lifetime judgment rules.
- [Traits & Generics](references/traits-generics.md): Bounds, associated types, trait objects, API trade-offs.
- [Patterns & Idiomatic Style](references/patterns.md): Builder patterns, newtypes, RAII, typestate management.
- [Style Guide](references/style-guide.md): Naming conventions, module organization, documentation style, and API design principles.

### Cross-references (load the right skill instead)
- **"Which std collection / smart pointer / string type?"** → `rust-stdlib` (its `references/` covers collections, smart-pointers, string-types, iterators, I/O, interior-mutability, combinators, std-concurrency, process-and-fs, std-module-index)
- **"How do I write X?"** → `rust-by-example` (its `references/` covers conversions, flow-control, closures, modules, generics-traits, error-handling, attributes, unsafe, procedural-macros-overview, inline-asm, migrating-from-other-languages)
- **API design** → `rust-api-design`; **Cargo manifest** → `rust-cargo-build`; **dependency governance** → `rust-dependencies`

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
