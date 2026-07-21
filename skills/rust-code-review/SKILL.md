---
name: rust-code-review
description: Review Rust changes for correctness, memory and thread safety, error semantics, unnecessary allocation or cloning, lock scope, API compatibility, test gaps, documentation, and dependency risk, applying the Rust API Guidelines checklist (C-PANIC, C-UNWRAP, C-TRANSMUTE, C-BOOL, C-NEWTYPE, C-COMMON-TRAITS, C-CONVERT, C-SEALED, C-NON-EXHAUSTIVE). Use when reviewing Rust diffs, pull requests, libraries, unsafe boundaries, or production incidents; report actionable findings by severity before summaries, route automated formatting or lint policy to rust-style-clippy, and route API shape decisions (trait sealing, error taxonomy, newtype design, builder patterns) to rust-api-design.
---

# Rust Code Review

Review the actual diff and its callers, not an isolated snippet or a generic checklist. Prioritize defects that can change behavior, violate invariants, expose data, deadlock, panic unexpectedly, or break public APIs.

## Scope and Routing

Use this skill to review:

- ownership, borrowing, lifetime, and drop behavior;
- `unsafe` preconditions and safe-wrapper soundness;
- error propagation, panic paths, partial updates, and rollback;
- concurrency, cancellation, lock ordering, and task lifecycle;
- public API, semver, feature, target, and MSRV compatibility;
- allocation, cloning, blocking, serialization, and hot-path costs;
- tests, documentation, dependencies, and operational failure paths.

Route format and lint configuration to `rust-style-clippy`, deep unsafe or ABI analysis to `rust-unsafe-ffi`, concurrency design to `rust-concurrency`, dependency resolution to `rust-cargo-build`, test implementation to `rust-testing`, and API shape decisions (trait sealing, newtype design, error taxonomy, builder patterns) to `rust-api-design`.

## Workflow

### 1. Establish the review contract

Inspect the repository instructions, changed files, surrounding symbols, callers, tests, manifests, lockfile, declared MSRV, enabled features, and supported targets. Determine whether the change affects a private implementation, public library API, persistent data, wire format, database schema, or security boundary.

Use the narrowest relevant commands:

```bash
git diff --check
cargo metadata --format-version 1
cargo check --workspace --all-targets --all-features
cargo test --workspace --all-targets --all-features
cargo clippy --workspace --all-targets --all-features -- -D warnings
```

Do not claim a command passed unless it ran. Do not treat successful compilation as proof of behavioral correctness.

### 2. Trace behavior through boundaries

For each changed path, follow input, state transitions, side effects, errors, cleanup, and observable output. Check:

- whether references outlive their owners or guards;
- whether moves, clones, or allocations change cost or semantics;
- whether `Option` and `Result` preserve absence and failure information;
- whether resources are released on early return, cancellation, panic, and shutdown;
- whether transactions and multi-step mutations are atomic where required;
- whether retries are bounded and safe for the operation;
- whether logs, Debug output, metrics, or errors expose secrets.

### 3. Review Rust-specific hazards

#### Unsafe and FFI

- Require a documented safety invariant for every unsafe API and implementation.
- Keep unsafe blocks minimal and enable `unsafe_op_in_unsafe_fn` explicitly.
- Verify provenance, validity, alignment, initialization, aliasing, layout, unwinding, ownership transfer, and deallocation symmetry.
- Treat manual `Send` or `Sync` implementations as unsafe contracts, not marker boilerplate.

#### Concurrency

- Check lock ordering and whether guards cross `.await`, callbacks, blocking I/O, or user code.
- Require bounded queues, overload behavior, cancellation ownership, supervised tasks, and deterministic shutdown.
- Distinguish I/O concurrency from CPU parallelism; adding tasks or workers is not automatically a performance fix.

#### Error handling

- Flag `unwrap`, `expect`, indexing, assertions, integer overflow assumptions, and unreachable branches when user or external input can reach them.
- Preserve structured library errors; add context at application boundaries without leaking internals.
- Verify that cleanup or rollback failures are not silently discarded.

#### API and compatibility

- Check visibility, trait bounds, auto traits, object safety, `#[non_exhaustive]`, feature combinations, target-specific code, and MSRV.
- Treat generated methods, serialization shapes, error variants, and public feature names as API surface.
- Require explicit migration for persisted or transmitted formats.

### 3a. API Guidelines Review Lens

For every touched public item, scan the diff against the four chapters of the Rust API Guidelines checklist. Confirm each match with a concrete caller before raising it, and route design-level fixes to `rust-api-design`. The full table per chapter, severities, and suggested comments live in [API Guidelines Checklist](references/api-guidelines-checklist.md).

- **Dependability** — flag `panic!`, `unwrap`, `expect`, `unreachable!`, slice indexing, and `transmute` inside public methods that accept caller input (C-PANIC, C-UNWRAP, C-TRANSMUTE).
- **Type safety** — flag functions taking multiple `bool` parameters or interchangeable bare primitives where enums or newtypes would prevent argument-order bugs (C-BOOL, C-NEWTYPE).
- **Interoperability** — flag public types missing `Debug`/`Clone`/`PartialEq`, and non-smart-pointer types implementing `Deref` to borrow methods (C-COMMON-TRAITS, C-CONVERT).
- **Future-proofing** — flag extensible public traits that are not sealed and library error or config enums without `#[non_exhaustive]` (C-SEALED, C-NON-EXHAUSTIVE).

Do not flag `unwrap`/`expect` in `#[cfg(test)]` modules, idiomatic infallible `unsafe` in FFI shims with documented invariants, or single-purpose `bool` setters; see the false-positives list in the checklist.

### 4. Review performance with evidence

Report an allocation, clone, lock, or algorithm as a performance finding only when it is plausibly material on the changed path. Prefer measurements over aesthetic rewrites. Check blocking work on async executors, accidental quadratic behavior, repeated parsing, oversized enum variants, unnecessary buffering, and unbounded growth.

### 5. Verify tests and documentation

Require tests at the boundary where regressions are observable. Cover success, invalid input, failure after partial progress, cancellation, concurrency, feature and platform variants, and public examples. Ensure public safety requirements, errors, panics, and compatibility constraints are documented and doctests remain executable.

Read [Review Tools and Checklist](references/references.md) when choosing additional analysis tools. Read [Review Scenarios](examples/examples.md) for expected finding shape. Read [API Guidelines Checklist](references/api-guidelines-checklist.md) when applying the C-PANIC / C-UNWRAP / C-TRANSMUTE / C-BOOL / C-NEWTYPE / C-COMMON-TRAITS / C-CONVERT / C-SEALED / C-NON-EXHAUSTIVE rules to a public API surface.

## Finding Format

Return findings before any summary. Each finding must contain:

1. severity and concise title;
2. the tightest file and line range;
3. the concrete failing condition or caller path;
4. user, security, compatibility, or operational impact;
5. a minimal correction or test that proves the fix.

Do not report style-only preferences as correctness findings. If no actionable finding remains, say so and state the residual verification gaps.

## Completion Criteria

- Review the diff, callers, tests, manifests, and relevant feature or target boundaries.
- Report reproducible findings in severity order with tight locations.
- Separate confirmed defects from risks that still require evidence.
- Run or explicitly account for relevant checks.
- Avoid silently broadening the change or implementing fixes unless requested.

## Upstream Sources

- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- [Rust Style Guide](https://doc.rust-lang.org/style-guide/)
- [Rustonomicon](https://doc.rust-lang.org/nomicon/)
- [Clippy documentation](https://doc.rust-lang.org/clippy/)
- [RustSec Advisory Database](https://rustsec.org/)

## Data Privacy

This skill does not collect, store, or transmit user data. Confirm authorization before querying private registries or external review systems.
