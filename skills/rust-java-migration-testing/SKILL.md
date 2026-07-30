---
name: rust-java-migration-testing
description: Design, implement, audit, and report valuable tests for Java-to-Rust migrations without promoting green tests into false completion claims. Use when porting JUnit tests to Rust, checking every Java test disposition, validating an object migration ledger, proving exact dependency reuse, deciding Rust-specific obligations, comparing coverage without gaming, or building differential, golden, property, fuzz, mutation, concurrency, cancellation, lifecycle, adapter-conformance, real-dependency, host, load, security, and rollback evidence. Keeps MISSING, MISPLACED, STUB, PARTIAL, and UNVERIFIED objects incomplete even when Cargo tests pass.
---

# Java-to-Rust Migration Testing

Prove observable compatibility and Rust safety properties, not test volume. Build three explicit test ledgers in this order:

1. `SOURCE_PARITY` — disposition every in-scope source test.
2. `RUST_OBLIGATION` — test risks introduced by the Rust implementation and replacement components.
3. `VALUE_ADD` — add tests justified by uncovered behavior, plausible defects, incidents, mutation survivors, or hostile inputs.

Coverage should rise because meaningful contracts are exercised. A percentage is not the design input and 100% is not migration proof.

## Scope and routing

Use this skill for migration-specific test planning, implementation, audit, and acceptance.

Route:

- module/object/component migration planning to `rust-java-migration`;
- general Rust unit, integration, doctest, and fixture mechanics to `rust-testing`;
- async model checking to `rust-concurrency`;
- profiling and benchmark construction to `rust-performance`;
- unsafe and FFI validation to `rust-unsafe-ffi`;
- web threat modeling to `rust-web-security`.

An audit-only request does not authorize deleting or rewriting tests. Preserve existing behavior and unrelated dirty work. Treat heuristic findings as review candidates.

## Required inputs

Resolve or mark unknown:

- pinned Java and Rust SHAs, dirty state, toolchains, profiles, features, targets, and generated-code boundaries;
- in-scope modules, public contracts, test roots, fixtures, examples, scripts, and test-support code;
- Java test runner and Rust test runner, including parameterized and dynamic test behavior;
- source coverage scope/tool/report and comparable Rust coverage scope/tool/report;
- available oracle: source only, executable Java tests, golden exporter, packaged artifact, live service, or standards suite;
- the current authoritative object ledger generated from the same Java/Rust
  baselines; ignore historical-design appendices when reading current states;
- required hosts, real dependencies, concurrency/load model, security boundary, and rollback mechanism;
- deterministic normalization rules for time, identifiers, paths, map order, locale, float precision, and scheduling.

Never use an unpinned remote artifact as the compatibility oracle.

## Evidence labels

Use these labels without promotion:

| Level | Evidence | Claim allowed |
|---|---|---|
| `V0_STATIC` | source/test inventory, call trace, no-stub scan | structural disposition only |
| `V1_RUST_LOCAL` | Rust unit/integration/doc/compile tests | Rust-local behavior passes |
| `V2_MIRRORED` | Rust test preserves a named Java test's inputs and assertions | source test represented; not differential |
| `V3_GOLDEN_DIFF` | pinned Java-generated fixtures compared by Rust | selected outputs match |
| `V4_LIVE_DIFF` | pinned Java and Rust execute identical cases | selected live behavior matches |
| `V5_HOST` | real framework/process/database/network/filesystem | named integration boundary works |
| `V6_NONFUNCTIONAL` | model, mutation, property, fuzz, load, soak, security | named non-functional claim holds |
| `V7_ROLLBACK` | gray rollout and rollback rehearsal | stated recovery path works |

A copied test name, green Rust suite, or 100% line report does not prove `V3_GOLDEN_DIFF`.

Evidence levels never replace object states. A green `V1_RUST_LOCAL` suite does
not turn `MISSING`, `MISPLACED`, `STUB`, `PARTIAL`, or `UNVERIFIED` into
`IMPLEMENTED`. `DEPENDENCY_REUSED` additionally requires an exact pinned
upstream symbol and local integration test; `PLATFORM_NA` requires platform
evidence rather than a passing test that skips the behavior.

## SOP

### 1. Freeze the verification baseline

Record exact SHAs, commands, tools, profiles, features, targets, test counts, ignored/flaky tests, coverage exclusions, and existing evidence artifacts. Record Java and Rust coverage separately before comparing them.

Read the current fact region of the authoritative object table before designing
tests. Stop at `historical-design-appendix-start`; old appendix statuses are
context only. Record counts for all strict object states. If any incomplete
state remains, the acceptance report must say “module migration incomplete”
regardless of test results.

Use CodeGraph when indexed to trace each source test through its production entry, collaborators, side effects, and Rust counterpart. Text similarity is insufficient for overloaded methods, registries, interceptors, dynamic dispatch, cleanup, and async paths.

### 2. Inventory source and target tests

Create one row per Java test method and per parameterized/dynamic case when cases have distinct contracts. Include disabled tests and fixtures that encode behavior.

Use dispositions:

| Disposition | Meaning |
|---|---|
| `MIRRORED` | same contract represented in one Rust test |
| `ADAPTED` | same observable contract using a Rust-native fixture/oracle |
| `SPLIT` | one Java test becomes several focused Rust tests |
| `MERGED_APPROVED` | several Java tests share one parameterized Rust test without losing cases/assertions |
| `NOT_APPLICABLE` | approved JVM-only behavior with impact and replacement recorded |
| `BLOCKED` | named dependency or oracle prevents the test |
| `MISSING` | no Rust disposition; migration gap |

Do not map by test name alone. Preserve inputs, assertions, exception/error category, ordering, side effects, fixture state, and cleanup.

Resolve `SKILL_DIR` to this skill directory and run from the migration repository:

```bash
python3 "$SKILL_DIR/scripts/audit_migration_tests.py" \
  --java-root ../java-project/source-module \
  --rust-root crates/source_module \
  --object-ledger docs/source-module/对象级对照表.md \
  --fail-on-incomplete
```

The report inventories tests, flags weak signals, and refuses a completion gate
while the current ledger contains strict incomplete rows. It cannot infer
semantic mappings or authorize deletion.

### 3. Implement the `SOURCE_PARITY` ledger

For every source row:

1. Trace the protected Java contract and production call path.
2. Port the fixture and assertions, not merely the method name.
3. Preserve valid, boundary, failure, state-transition, and side-effect cases.
4. Use the strongest feasible oracle: live diff, golden diff, standards suite, or honestly labeled mirror.
5. Record the Rust test, evidence level, command, and divergence.

Missing or blocked source tests remain visible. Source tests are a compatibility floor, not the complete Rust plan.

Do not use one test per object as a substitute for one real file per source
object. A test that reaches a re-export, compatibility facade, or merged type
does not cure `MISPLACED`/`MISSING`. Tests validate semantics only after the
layout and object boundary are factually present.

### 4. Implement the `RUST_OBLIGATION` ledger

Add applicable tests created by the target design:

| Rust mechanism | Mandatory questions |
|---|---|
| Ownership / `Drop` | exactly-once cleanup, partial initialization, early return, panic/cancel boundary |
| Async / Tokio | cancellation, timeout ownership, orphan tasks, shutdown, bounded queues, slow consumers |
| Shared state | atomicity, poison/recovery policy, no lock held across `.await`, deadlock/interleaving risks |
| `Send` / `Sync` | intended compile contract and supported executor/thread boundary |
| Typed errors | exact variant, context, retryability, `Error::source`, public redaction surfaces |
| serde / wire/storage | rename/default/unknown fields, round trip, bytes, compatibility window |
| Traits / registries | selection, duplicate registration, missing provider, dynamic dispatch |
| Procedural macros | compile-pass/fail, generics, visibility, renamed dependencies, diagnostics |
| Feature/platform/MSRV | supported combinations compile and behave as promised |
| Unsafe / FFI | invariants, Miri/sanitizer where applicable, ownership across boundary |
| Replacement crate | risky semantic path, lifecycle, real dependency, upgrade/rollback boundary |
| Framework adapters | one shared contract suite plus adapter-native routing/body/service behavior |

These tests need not exist in Java because they protect the Rust implementation's correctness.

For a `DEPENDENCY_REUSED` row, execute the local adapter against the exact
declared upstream symbol/version or commit. The dependency's own unit tests,
documentation examples, or a similar capability name are not local integration
evidence. Assert the source contract's ordering, errors, lifecycle, cancellation,
and metadata that cross the adapter.

### 5. Implement the `VALUE_ADD` ledger

Add a test only when it has a reason such as:

- missing boundary or branch revealed by coverage;
- surviving meaningful mutant;
- property/invariant over a broad input space;
- malformed or hostile input found by fuzzing;
- production incident or bug regression;
- concurrency interleaving, load, resource leak, or long-soak risk;
- compatibility behavior absent from the Java suite but required by docs/protocol;
- real-host or rollback behavior that mocks cannot prove.

For each test, record the concrete bug it should catch. Prefer a small parameter/branch matrix over “one test per type/token/method” count targets.

### 6. Use observable assertions

Strong tests observe exact public behavior:

- value, bytes, order, state transition, call count, side effect, resource release, or typed error;
- `Display`, `Debug`, serialized error report, logs/tracing fields, transport body, and `Error::source()` independently where exposed;
- cache hit/miss/eviction metrics or backend-call counts when claiming cache behavior;
- body/trailer/backpressure and disconnect cleanup when claiming streaming lifecycle.

Weak patterns requiring review:

- `let _ = result`, unused parsed AST, or a test that accepts success and failure;
- parse-only checks named as semantic/evaluation tests;
- only `is_ok()` or `is_err()` when value/error category matters;
- a cache test that observes only final values;
- tests of fixture `Clone`, `Debug`, constants, constructors, or type existence without a public contract;
- duplicate “coverage burst” tests with no distinct risk;
- tests that merely prove `todo!()` or `unimplemented!()` panics.

Read [Vernal case study](references/vernal-testing-case-study.md) and [test-value rubric](references/test-value-rubric.md) before cleanup.

### 7. Build differential fixtures

Use a versioned case format such as JSON Lines:

```json
{"schema":1,"case_id":"empty-name","input":{"name":""},"expected":{"kind":"error","code":"INVALID_NAME"}}
```

Retain Java and Rust raw outputs separately. Pin exporter and implementation SHAs, seeds, environment, and normalizer version. Compare success values, error categories, side effects, order, and wire bytes as applicable. Do not normalize unexpected fields away.

### 8. Reuse conformance suites for adapters

Put shared assertions and failure fixtures in a testkit. Each adapter must provide real native observations. Run the same identity, scope, lifecycle, error, cancellation, streaming, and cleanup contracts for every implementation, then add adapter-native tests.

Prefer event-driven synchronization and bounded timeouts over fixed sleeps. Assert the resource is open while a stream is active and closed after completion, disconnect, timeout, cancellation, or panic.

### 9. Compare coverage without gaming it

Coverage comparison is valid only when scopes are documented and reasonably comparable:

- production files/modules included;
- generated code and approved exclusions;
- line/region/branch semantics of each tool;
- features, targets, test types, and profile;
- source and target baselines.

Acceptance order:

1. every source test has an approved disposition;
2. every high-risk source contract has adequate evidence;
3. every applicable Rust obligation is tested;
4. meaningful mutants and uncovered branches are reviewed;
5. comparable Rust coverage exceeds the Java baseline if the project requires it.

Do not weaken assertions, duplicate tests, exclude difficult files, or add trivial getters to reach a number. A user-mandated 100% gate may be enforced, but report what it proves and what it does not.

### 10. Audit test value before removing or merging

Score each test manually:

| Question | Pass signal |
|---|---|
| Traceable? | source test, contract, risk, bug, or incident is named |
| Observable? | assertion checks externally meaningful behavior |
| Mutation-sensitive? | a plausible defect would make it fail |
| Production path? | exercises real production logic at the right boundary |
| Deterministic? | synchronization/seed/environment are controlled |
| Distinct? | adds a branch, case, platform, failure, or invariant |
| Right level? | unit/integration/host/load test matches the boundary |

Classify `KEEP`, `IMPROVE`, `MERGE`, or `REMOVE_PROPOSED`; require review before deletion. Coverage loss alone may justify replacement but not retention of a meaningless assertion.

### 11. Run layered gates

Run applicable gates from cheapest to most diagnostic:

```bash
cargo fmt --all -- --check
cargo check --workspace --all-targets --all-features
cargo test --workspace --all-features
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo test --doc --workspace
```

Then run targeted compile-fail, platform/MSRV, differential, real-dependency, real-host, model/Loom, Miri/sanitizer, mutation, property/fuzz, load/soak, security, and rollback gates. Record exact command, environment, result, and artifact.

Use the project-specific coverage command. For mutation candidates:

```bash
"$SKILL_DIR/scripts/run_mutation_test.sh" crates/source_module
```

Interpret survivors individually; do not impose one universal mutation score.

### 12. Report acceptance honestly

Report separately:

- source-test disposition coverage;
- source behavior evidence by `V0`–`V4`;
- Rust-obligation completion;
- value-add tests and defect/risk rationale;
- line/branch/region coverage with comparable scope;
- mutation, property, fuzz, concurrency, load, security, host, and rollback evidence;
- failures, flaky/ignored tests, stubs, exclusions, missing targets, and external boundaries.
- current object-state counts and the explicit list of all
  `MISSING`/`MISPLACED`/`STUB`/`PARTIAL`/`UNVERIFIED` blockers;
- compiler and Clippy warnings, ignored/doctests, feature/target gaps, and tests
  that were not executed;

## Red lines

- Do not call mirrored tests differential.
- Do not replace source-test disposition with raw test-count parity.
- Do not write tests solely to increase coverage or file count.
- Do not call parse success semantic equivalence.
- Do not accept generic `is_err()` when the error contract is observable.
- Do not auto-delete tests from names, body length, or heuristics.
- Do not hide mismatches through broad normalization or snapshot regeneration.
- Do not replace real dependency/host tests with mocks when the contract crosses that boundary.
- Do not use fixed sleeps as the only async coordination mechanism.
- Do not count production stubs as implemented because their tests compile.
- Do not mark a module complete from Cargo/JUnit test totals, coverage, or a
  green CI job while the authoritative object ledger has any incomplete state.
- Do not read completion states from a historical appendix or stale duplicate
  migration document.
- Do not call dependency reuse verified from upstream tests or semantic
  similarity; require the exact dependency symbol and a local integration test.

## On-demand resources

- [Migration verification SOP](references/migration-verification-sop.md)
- [Test categories](references/test-categories.md)
- [Test-value rubric](references/test-value-rubric.md)
- [Vernal positive and negative examples](references/vernal-testing-case-study.md)
- [Migration test ledger template](assets/templates/迁移测试对照表.md)
- [Worked audit report](examples/audit-report.md)
- `scripts/audit_migration_tests.py` — Java/Rust test inventory and weak-signal audit
- `scripts/run_mutation_test.sh` — mutation-test wrapper

## Completion criteria

- Every in-scope Java test/case has an approved disposition and source trace.
- The authoritative current object ledger was checked, its baselines match the
  test run, and no incomplete object state was hidden by the test summary.
- Every high-risk contract has an oracle, evidence label, and result.
- Applicable Rust ownership, async, error, serialization, feature, adapter, and unsafe obligations are tested.
- Added tests name a distinct risk or plausible defect.
- Coverage scopes are comparable and any numeric gate is reported as a signal, not parity proof.
- Stubs, warnings, flaky/skipped tests, missing platforms, real-host gaps, and unverified boundaries remain visible.
- A module completion claim is emitted only when its object ledger, source-test
  ledger, Rust obligations, and required host/non-functional gates all permit it.
