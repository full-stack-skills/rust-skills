---
name: rust-java-migration-testing
license: Apache-2.0
description: Design, implement, audit, and report lossless Java-to-Rust migration tests without promoting green tests into false completion claims. Use when porting 100% of JUnit tests and concrete parameterized/dynamic cases, SHA-256-verifying source fixtures/resources/scripts/data, requiring complete per-case golden or live differential MATCH results, validating object/test ledgers, reviewing oversized Rust test files, organizing inline unit versus integration tests, adding Rust-specific obligations, comparing coverage, or building property, fuzz, mutation, concurrency, lifecycle, adapter, host, load, security, and rollback evidence. Enforces a 500-line cohesion-review threshold, an 800-line authored-file blocker, and idiomatic Rust test placement.
---

# Java-to-Rust Migration Testing

Prove observable compatibility and Rust safety properties, not test volume. Treat
the complete source test suite as a non-negotiable compatibility floor: migrate
100% of its test cases without weakening inputs or assertions, copy every test
fixture/data/script byte-for-byte into the target repository, and make both
implementations produce the same per-case observable result. Build three explicit
test ledgers in this order:

## Mandatory verification structure

- Require exact Java/Rust path parity; every `MISPLACED` or missing `file-map.csv` target blocks completion.
- Treat E0583/E0761/E0405/E0425/E0659 and broken fixture paths as structural failures after file moves.
- Treat up to 500 physical lines as normal, review authored `.rs` files from 501–800 lines for cohesion, and block files above 800 lines; split suites by contract or behavior family rather than arbitrary ranges.
- Allow focused unit tests in `#[cfg(test)]` modules beside their implementation. Put public-boundary, cross-module, differential, host, load, and whole-project tests in `tests/` or a non-published test/testkit crate.
- Run path audit, fmt, default/all-feature check, Clippy, complete tests, golden/live differential, migration audit, and the project coverage gate without using any one result as parity proof.

Read [Directory parity verification](references/directory-parity-verification.md) and [Migration verification SOP](references/migration-verification-sop.md).

1. `SOURCE_PARITY` — map every source test/case and every source test asset; no
   missing, blocked, or not-applicable row permits a completion claim.
2. `RUST_OBLIGATION` — test risks introduced by the Rust implementation and replacement components.
3. `VALUE_ADD` — add tests justified by uncovered behavior, plausible defects, incidents, mutation survivors, or hostile inputs.

`SOURCE_PARITY` has two mandatory sections: `TEST_CASE` and `TEST_ASSET`.
`TEST_CASE` preserves the source inputs, assertions, exception/error category,
ordering, state, side effects, and cleanup. `TEST_ASSET` preserves the source
relative path, target path, and SHA-256 of every copied fixture, script, corpus,
golden file, and data file. Coverage should rise because meaningful contracts are
exercised. A percentage is not the design input and 100% is not migration proof.

## Scope and routing

Use this skill for migration-specific test planning, implementation, audit, and acceptance.

This is the Rust testing adapter of the shared target-language migration
profile. Keep source-test dispositions, exact-asset rules, full differential
outcomes, and completion semantics equivalent to `zig-java-migration-testing`
and future Kotlin/Swift adapters; vary only Rust test/build syntax and Rust risks.

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
- the authoritative workspace-topology decision and actual paths of the target
  production and `<project>-test` packages; do not assume a `crates/` directory;
- the complete source test roots and runner configuration, including fixtures,
  examples, scripts, test resources, parameter sources, dynamic factories, and
  test-support code; the source repository defines the denominator and exclusions
  cannot be introduced merely to make parity reach 100%;
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
| `V3_GOLDEN_DIFF` | pinned Java-generated fixtures compared by Rust | recorded outputs match; completion requires the full source denominator |
| `V4_LIVE_DIFF` | pinned Java and Rust execute identical cases | recorded live behavior matches; completion requires every source case |
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

Create one row per Java test method and one row per concrete parameterized,
repeated, template, or dynamic case. Include disabled tests; a disabled source
test remains a required migrated test and its disabled reason is preserved
separately. Create one `TEST_ASSET` row per file in every source test resource,
fixture, script, corpus, and data root. Copy source assets without editing them;
place target-generated or normalized derivatives beside the immutable copy.

Use dispositions:

| Disposition | Meaning |
|---|---|
| `MIRRORED` | same contract represented in one Rust test |
| `ADAPTED` | same observable contract using a Rust-native fixture/oracle |
| `SPLIT` | one Java test becomes several focused Rust tests |
| `MERGED_APPROVED` | several Java tests share one parameterized Rust test without losing cases/assertions |
| `NOT_APPLICABLE` | JVM-only claim recorded for analysis; blocks 100% lossless source-test completion |
| `BLOCKED` | named dependency or oracle prevents the test; blocks completion |
| `MISSING` | no Rust implementation; blocks completion |

`MIRRORED`, `ADAPTED`, `SPLIT`, and `MERGED_APPROVED` are complete only when
every source case remains identifiable, all preservation flags are true, every
target test exists, and golden/live comparison records `MATCH`. `ADAPTED` permits
Rust-native harness mechanics, not a weaker contract. `SPLIT` and
`MERGED_APPROVED` may reorganize tests but may not remove a case or assertion.
Do not map by test name alone.

Resolve `SKILL_DIR` to this skill directory and run from the migration repository:

```bash
python3 "$SKILL_DIR/scripts/audit_migration_tests.py" \
  --java-root ../java-project/source-module \
  --rust-root <selected-target-crate-or-workspace> \
  --object-ledger docs/source-module/对象级对照表.md \
  --parity-manifest docs/source-module/source-test-parity.json \
  --java-test-assets-root src/test/resources \
  --fail-on-incomplete
```

The report inventories tests, flags weak signals, verifies every source-test
manifest row, checks target test files, hashes exact asset copies, and refuses a
completion gate for any object, test, asset, run, or differential gap. Additional
non-standard asset roots must be passed with repeated
`--java-test-assets-root`. The script validates recorded preservation evidence;
it cannot infer semantic mappings or authorize deletion. It warns on authored
files above 500 physical lines and blocks those above 800; inline unit tests are
valid Rust organization and are not reported as structural violations.

### 3. Implement the `SOURCE_PARITY` ledger

For every source row:

1. Trace the protected Java contract and production call path.
2. Port the fixture and assertions, not merely the method name.
3. Preserve valid, boundary, failure, state-transition, and side-effect cases.
4. Run the source and target suites from pinned baselines and retain raw per-case
   results. A mirror without Java output is useful during implementation but does
   not satisfy the final source-parity gate.
5. Compare each source case through a pinned golden or live differential oracle;
   require `MATCH`, zero harness failures, and zero not-run cases.
6. Record the Rust test, preservation flags, evidence, commands, artifacts, and
   any divergence.

Missing, blocked, or not-applicable source tests remain visible and block a
migration-complete conclusion. Source tests are a compatibility floor, not the
complete Rust plan.

#### Whole-project migration test module

For every repository/product-level migration completion claim, create one
non-published workspace package as the whole-project acceptance authority. It
is especially important for multiple crates, bindings/adapters, or a source
system/templatesuite. Name it
`<project>-test` by default; keep the final directory name and Cargo package name
identical, set `publish = false`, and run it explicitly in CI. Its parent path
follows the recorded workspace topology: a small root-flat workspace uses
`<project>-test/`; a hybrid may keep it at root or in a real test family; a
contained workspace may use `crates/<project>-test/` or
`crates/tests/<project>-test/`. Local tests inside production
crates prove their own parser/type/API/binding behavior; they do not replace the
whole-project module's source-suite replay, cross-crate workflows, real copied
assets, golden/live differential comparison, or aggregate result artifact.

For FreeMarker use this boundary:

```text
freemarker/          # Rust engine local unit/integration tests
freemarker-pyo3/     # Python binding local/packaging tests
freemarker-test/     # complete Java templatesuite + cross-component acceptance
```

The `freemarker-test` package must be a workspace member, depend on public
surfaces under test, and remain outside crates.io publication. Its complete gate
is every source case `MATCH`, with no threshold pass count, skipped capability,
or ignored case. Read [Migration verification SOP](references/migration-verification-sop.md)
for naming, ownership, layout, and CI rules.

The test package's semantic role is mandatory; one physical parent directory
is not. Never relocate it solely to imitate the Java test-module tree or a
generic Rust example.

Do not use one test per object as a substitute for one real file per source
object. A test that reaches a re-export, compatibility facade, or merged type
does not cure `MISPLACED`/`MISSING`. Tests validate semantics only after the
layout and object boundary are factually present.

Treat 500 physical lines as the suite-cohesion review threshold and 800 as the
authored-file blocker. Split by contract, behavior family, fixture family,
adapter, or verification layer while preserving every source case ID and
assertion. Keep compact private-behavior unit tests in `#[cfg(test)]` modules;
put reusable integration support in `tests/common/` or a dedicated testkit crate.
Enable `clippy::too_many_lines` to review functions over its 100-line default.

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
  note that during cleanup, converting a genuinely dropped `Result` to
  `let _ = expr;` preserves semantics and is not itself weak evidence — it only
  becomes weak when `let _ =` is the sole observation of the behavior under test;
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

Differential comparison is a full source-suite gate, not a representative
sample. The final manifest must record one `MATCH` per concrete source case and
suite-level Java, Rust, and differential runs with `PASS`, zero mismatches, zero
harness failures, and zero not-run cases. A temporary subset may guide
development but must be labeled partial and cannot satisfy completion.

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

1. every source test and concrete case has a lossless target implementation;
2. every source test asset has a byte-identical target copy verified by SHA-256;
3. both complete suites pass and every source case has differential `MATCH`;
4. every high-risk source contract has adequate evidence;
5. every applicable Rust obligation is tested;
6. meaningful mutants and uncovered branches are reviewed;
7. comparable Rust coverage exceeds the Java baseline if the project requires it.

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

Run every gate at the workspace MSRV: a default rustc older than the workspace
`rust-version` fails with `rustc X is not supported by the following packages`
rather than testing your code — use `rustup run <ver> cargo ...` and never
silently lower the manifest. Use `--keep-going` so one failing crate does not
hide the remaining errors (errors surface in layers; fix the first layer and
re-run). Require **both** default and `--all-features` check runs to reach zero
warnings: feature-gated crates and code paths only compile under
`--all-features`, and a check gate with warnings must be reported as a gap, not
a pass.

Use the project-specific coverage command. For mutation candidates:

```bash
"$SKILL_DIR/scripts/run_mutation_test.sh" <selected-target-crate>
```

Interpret survivors individually; do not impose one universal mutation score.

### 12. Report acceptance honestly

Report separately:

- source-test lossless implementation and per-case differential coverage;
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
- Do not exclude, disable, weaken, merge away, or mark a source test not
  applicable to manufacture 100% parity.
- Do not rewrite copied source fixtures or data in place; retain a byte-identical
  copy and generate target-specific derivatives separately.
- Do not accept two independently green suites as result parity; require
  per-case Java/Rust golden or live comparison.
- Do not substitute local tests in production or binding crates for the
  non-published `<project>-test` whole-project acceptance package, and do not
  use pass thresholds, skips, or ignored cases as its completion gate.
- Do not hardcode `<project>-test` under `crates/` or at repository root without
  checking the migration roadmap's project-driven workspace topology.
- Do not write tests solely to increase coverage or file count.
- Do not keep an authored `.rs` file above 800 physical lines; review every file above 500 and split weakly cohesive suites.
- Do not compress code, remove useful comments, or split arbitrary line ranges to evade a size gate.
- Do not place integration, differential, host, load, or whole-project suites in production modules; focused inline unit tests remain valid.
- Do not call parse success semantic equivalence.
- Do not accept generic `is_err()` when the error contract is observable.
- Do not auto-delete tests from names, body length, or heuristics.
- Do not hide mismatches through broad normalization or snapshot regeneration.
- Do not replace real dependency/host tests with mocks when the contract crosses that boundary.
- Do not use fixed sleeps as the only async coordination mechanism.
- Do not count production stubs as implemented because their tests compile.
- Do not mark a module complete from Cargo/JUnit test totals, coverage, or a
  green CI job while the authoritative object ledger has any incomplete state.
- Do not run a completion gate without a source-test parity manifest. Missing
  test mappings, incomplete parameter expansion, false preservation flags,
  missing target files, asset hash differences, non-`MATCH` results, harness
  failures, or not-run cases all block completion.
- Do not read completion states from a historical appendix or stale duplicate
  migration document.
- Do not call dependency reuse verified from upstream tests or semantic
  similarity; require the exact dependency symbol and a local integration test.
- Do not report the check gate as passed while `cargo check` (default or
  `--all-features`) still emits warnings, or when the run used an unsupported
  toolchain instead of the workspace MSRV.

## On-demand resources

- [Migration verification SOP](references/migration-verification-sop.md)
- [Directory parity verification and post-migration checks](references/directory-parity-verification.md)
- [Cross-language migration profile](references/cross-language-migration-profile.md)
- [Test categories](references/test-categories.md)
- [Test-value rubric](references/test-value-rubric.md)
- [Vernal positive and negative examples](references/vernal-testing-case-study.md)
- [Migration test ledger template](assets/templates/迁移测试对照表.md)
- [Machine-readable source-test parity manifest](assets/templates/source-test-parity.json)
- [Worked audit report](examples/audit-report.md)
- `scripts/audit_migration_tests.py` — Java/Rust test inventory and weak-signal audit
- `scripts/run_mutation_test.sh` — mutation-test wrapper

## Completion criteria

- Every Java test and every concrete parameterized/dynamic/repeated case in the
  frozen source test roots has a target-language implementation and source trace;
  the source denominator is 100% accounted for without completion exclusions.
- Every source fixture, resource, script, corpus, golden file, and test data file
  has a byte-identical copy in the target repository with matching SHA-256.
- Every mapped case attests preservation of contract, inputs, assertions,
  fixture state, and cleanup; split/merged/adapted forms lose nothing.
- The complete pinned Java and Rust suites pass, and the complete golden/live
  differential report contains only `MATCH` with zero harness failures and zero
  not-run cases.
- The `<project>-test` package is a workspace member with `publish = false`,
  lives at the path selected by the recorded workspace topology, exercises
  public component surfaces, and owns the complete suite/differential
  command plus aggregate artifact; local crate tests remain subsystem evidence.
- The authoritative current object ledger was checked, its baselines match the
  test run, and no incomplete object state was hidden by the test summary.
- Every high-risk contract has an oracle, evidence label, and result.
- Applicable Rust ownership, async, error, serialization, feature, adapter, and unsafe obligations are tested.
- Added tests name a distinct risk or plausible defect.
- Every authored `.rs` file is at most 800 physical lines; files above 500 and functions above the Clippy 100-line signal have recorded cohesion reviews.
- Focused unit tests may be colocated in `#[cfg(test)]` modules; integration, differential, host, load, and whole-project suites live under `tests/` or a non-published test package.
- Coverage scopes are comparable and any numeric gate is reported as a signal, not parity proof.
- Stubs, warnings, flaky/skipped tests, missing platforms, real-host gaps, and unverified boundaries remain visible.
- A module completion claim is emitted only when its object ledger, source-test
  case ledger, source-asset ledger, complete differential result, Rust
  obligations, and required host/non-functional gates all permit it.
