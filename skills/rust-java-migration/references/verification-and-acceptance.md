# Verification and Acceptance

## Execution timing

Verification begins only after every non-exempt row in the frozen migration
batch has a real Rust implementation and the implementation batch is frozen.
Writing the complete test suite may be part of implementation, but do not run
formatting, compilation, tests, lints, coverage, differential comparison, load,
fuzz, host, or rollback gates after each object.

Run one full static parity audit, then execute the applicable evidence ladder as
a unified batch. If failures occur, cluster them by shared root cause, repair
the implementation batch, and rerun the affected gate plus any downstream gate
whose evidence was invalidated. Do not turn failure repair into an
object-by-object migrate-compare-test loop.

Before running the evidence ladder, read the current-fact region of the
authoritative object ledger (everything before
`<!-- historical-design-appendix-start -->`). If any row is `MISSING`,
`MISPLACED`, `STUB`, `PARTIAL`, or `UNVERIFIED`, the module remains incomplete.
Evidence levels describe how strongly a handled object was verified; they do
not replace object states or repair structural gaps.

## Evidence levels

| Level | Evidence | What it proves |
|---|---|---|
| E0 | file/type/signature inventory | structural disposition only |
| E1 | Rust check/tests/lints | Rust implementation builds and local tests pass |
| E2 | mirrored/ported Java contract tests | selected source contracts are represented in Rust; no cross-implementation comparison is proven |
| E3 | Java-produced golden fixtures or live Java/Rust differential execution | selected observable contracts match across pinned implementations |
| E4 | real script/example replay | caller-shaped workflows match |
| E5 | concurrency/model/lifecycle tests | specified interleavings, cancellation, and cleanup properties hold |
| E6 | load/soak, mutation, fuzz/property, and security tests | stated non-functional and broad-input claims are exercised |
| E7 | real host integration | actual framework/database/network/filesystem boundary works |
| E8 | gray rollout/rollback drill | operational recovery path is exercised |

Never report a higher level from lower-level evidence.

Passing `cargo test`, high coverage, a clean differential subset, or a real
host smoke test cannot promote a module while the object ledger contains a
strict incomplete state. Likewise, a same-named file, facade, re-export, or
dependency with similar behavior is not E0 structural completion.

For `DEPENDENCY_REUSED`, acceptance must execute the exact declared upstream
crate symbol through the local adapter/call point using the pinned
version/commit. For `PLATFORM_NA`, acceptance checks the recorded JVM,
bytecode, class-loader, or comparable platform-only evidence rather than a
generic statement that Rust works differently.

## Whole-project migration test module

For every repository/product-level migration completion claim, create one
non-published workspace package named `<project>-test`. This is especially
important for multiple Rust crates, bindings/adapters, or a source system suite.
Make it the single owner of complete source-suite replay, immutable copied test
assets, public cross-component workflows, golden/live differential comparison,
and aggregate acceptance artifacts. Keep local tests in production crates for
focused implementation and binding behavior; never use their combined green
status as a substitute for the overall module.

For FreeMarker use `freemarker-test` alongside `freemarker` and
`freemarker-pyo3`. Set `publish = false`, include it in workspace `members`, and
run `cargo test -p freemarker-test` explicitly in CI. Use public APIs and keep
product logic out of the harness. A partial pass threshold or any skipped source
capability keeps migration incomplete.

## Evidence taxonomy

Use these labels precisely:

- **Mirrored test**: a Rust test copies a Java test name, input, or assertion. It is useful contract evidence but is not differential.
- **Golden differential**: a pinned Java exporter produces fixtures that the Rust implementation consumes and compares.
- **Live differential**: pinned Java and Rust implementations run the same generated or recorded cases and a comparator evaluates normalized outputs.
- **Equivalent oracle**: a standards suite, protocol corpus, or mathematically defined property replaces the Java runtime by explicit approval.

Do not call two independently handwritten tests “differential” merely because they describe the same behavior.

## Differential tests

Pin the Java source SHA and Rust source SHA in the fixture metadata. Prefer a Java golden exporter that emits deterministic JSON, binary fixtures, or line protocol. Compare:

- defaults and configuration normalization;
- successful outputs and wire representation;
- error categories and boundary inputs;
- ordering, deduplication, rounding, time zones, and locale;
- mutation and idempotency;
- non-deterministic outputs by observable properties rather than exact values.

Do not make the Rust test invoke an unpinned remote Java artifact.

The final migration gate covers the entire frozen source test denominator, not
a curated or high-risk subset. Before running it, copy all source fixtures,
resources, scripts, corpora, golden files, and test data into the target
repository without modification and record SHA-256 for both paths. Run the
complete pinned source suite, the complete target-language port, and the
complete per-case differential comparator. Require both suites to pass and all
cases to be `MATCH`, with zero mismatches, harness failures, and not-run cases.

Normalize only documented nondeterminism: timestamps, generated identifiers, map order, locale, paths, and concurrency scheduling. Keep raw outputs as artifacts, record the normalization rules, and fail on unexpected fields rather than deleting them.

## Real script replay

Collect existing Java examples, CLI scripts, HTTP collections, database migrations, and user workflows. Run them against both implementations with equivalent configuration. Record command, environment, fixture, expected result, actual result, and artifact logs.

Mocks may isolate a unit but cannot replace a required real replay.

## Concurrency acceptance

Define invariants first:

- maximum queue/in-flight work;
- ordering and exactly/at-least/at-most-once contract;
- cancellation and timeout propagation;
- lock and transaction atomicity;
- retry ownership and idempotency;
- graceful shutdown and resource release.

Use deterministic coordination tests, Loom where state primitives warrant it, Tokio paused time for timers, and stress tests for race amplification. Report runtime/thread counts and blocking-pool use.

For application frameworks, build a lifecycle failure matrix covering build, refresh/initialize, start, ready, pause/reload, and close. At each phase inject error, panic, timeout, caller cancellation, and dependency loss where applicable. Assert final state, cleanup order, exactly-once release, preserved primary error, supplemental cleanup error, and orphan task/resource counts.

Test every public error surface separately. `Display`, `Debug`, serialized diagnostics, logs, metrics labels, HTTP/RPC bodies, and `Error::source()` have different audiences. A redacted report does not prove a redacted `Display`; preserve programmatic causality without exposing secrets on public surfaces.

## Load and stability

Specify workload, dataset, concurrency, warmup, duration, machine, network/dependency topology, and pass thresholds. Measure:

- throughput and p50/p95/p99 latency;
- error/timeout/retry rates;
- RSS/heap/allocator behavior;
- open file/socket/connection counts;
- task/thread/queue growth;
- recovery after dependency failure;
- long-running drift during soak.

Compare to the Java baseline only under comparable conditions.

## Fuzz and security

Use property tests for algebraic/data invariants and `cargo-fuzz` for parsers, codecs, protocol frames, deserializers, unsafe boundaries, and untrusted file formats. Seed corpora with Java fixtures and prior failures. Add size/depth/count/time limits and verify rejection behavior.

Run dependency/license/advisory checks and audit unsafe code. Treat authentication, authorization, path traversal, SSRF, deserialization, archive bombs, XML entities, and secret leakage according to the migrated domain.

## Business-host integration

Exercise a real supported host:

- actual framework adapter and lifecycle;
- real database/broker/cache when part of the contract;
- TLS/proxy/redirect/network failure paths;
- filesystem permissions and platform behavior;
- startup, reload, shutdown, and observability.

Record what remains simulated.

When one semantic contract has several framework adapters, place reusable assertions in a shared conformance testkit and execute them against every adapter. Keep native framework tests for routing, extractors, middleware/service boundaries, body streaming, and shutdown behavior that the shared contract cannot observe.

## Gray rollout and rollback

Define traffic selection, compatibility window, state/schema/wire backward compatibility, metrics and alerts, abort thresholds, and recovery objective. Run:

1. deploy Rust alongside Java;
2. mirror or route bounded traffic;
3. compare outputs and operational metrics;
4. trigger the documented rollback;
5. verify state remains readable and service recovers;
6. record actual recovery time and data reconciliation.

## Final acceptance report

Include:

- both SHAs and toolchains;
- module-by-module state counts;
- strict counts for `MISSING`, `MISPLACED`, `STUB`, `PARTIAL`, and `UNVERIFIED`;
- structural, implementation, behavioral, test, integration, and production percentages with denominators;
- exact commands and outcomes;
- exact dependency-reuse and platform-not-applicable evidence;
- failed/flaky/ignored/skipped/not-run tests plus warnings and lint findings;
- unverified external dependencies;
- next evidence required for completion.
- source test case mapping count, concrete parameter/dynamic case count, exact
  copied test-asset count/hash result, and full differential outcome counts;
- confirmation that implementation preceded acceptance and that the parity
  audit and verification used the complete frozen denominator.

The final conclusion must say **migration incomplete** whenever any strict
incomplete object state, source-test gap, asset mismatch, differential mismatch,
harness failure, or not-run source case remains, even if every executed test
passes.

Use `rust-java-migration-testing` to disposition every source test, add Rust-specific test obligations, design risk-driven value-add tests, and report mutation/coverage results without promoting heuristics to proof.
