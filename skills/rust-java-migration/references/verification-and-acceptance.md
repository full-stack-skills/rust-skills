# Verification and Acceptance

## Evidence levels

| Level | Evidence | What it proves |
|---|---|---|
| E0 | file/type/signature inventory | structural disposition only |
| E1 | Rust check/tests/lints | Rust implementation builds and local tests pass |
| E2 | Java/Rust golden differential | selected observable contracts match |
| E3 | real script/example replay | caller-shaped workflows match |
| E4 | concurrency/model tests | specified interleavings and lifecycle properties hold |
| E5 | load/soak and profiling | measured performance and stability under stated profile |
| E6 | fuzz/property/security tests | malformed and broad input classes are exercised |
| E7 | real host integration | actual framework/database/network/filesystem boundary works |
| E8 | gray rollout/rollback drill | operational recovery path is exercised |

Never report a higher level from lower-level evidence.

## Differential tests

Pin the Java source SHA and Rust source SHA in the fixture metadata. Prefer a Java golden exporter that emits deterministic JSON, binary fixtures, or line protocol. Compare:

- defaults and configuration normalization;
- successful outputs and wire representation;
- error categories and boundary inputs;
- ordering, deduplication, rounding, time zones, and locale;
- mutation and idempotency;
- non-deterministic outputs by observable properties rather than exact values.

Do not make the Rust test invoke an unpinned remote Java artifact.

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
- structural, implementation, behavioral, test, integration, and production percentages with denominators;
- exact commands and outcomes;
- approved exemptions and blocked placeholders;
- failed/flaky/skipped tests;
- unverified external dependencies;
- next evidence required for completion.
