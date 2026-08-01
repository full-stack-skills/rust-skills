# Migration Test Categories

Classify tests by the behavior they protect, not by file location or coverage effect. A test may belong to more than one category; record its primary risk.

Location still defines ownership: production and binding crates keep focused
local tests, while a non-published `<project>-test` workspace package owns the
complete source suite, cross-component workflows, and aggregate differential
gate for a repository/product-level migration claim.

## 1. Parity tests

Protect a source-side observable contract and cite the Java source, test, or documentation.

```rust
/// Java source contract: explicit configuration overrides a default.
#[test]
fn explicit_value_overrides_default() {
    let mut config = Config::with_default("timeout", "30");
    config.set("timeout", "60");
    assert_eq!(config.get("timeout"), Some("60"));
}
```

Use parity tests for:

- precedence and fallback;
- accepted spellings and defaults;
- ordering and deduplication;
- serialization and protocol values;
- mutation/idempotency;
- exception category and partial side effects.

A Rust test copied from a Java test is `V2_MIRRORED`. It becomes differential only when pinned Java output participates.

The final parity gate includes every source test and concrete case. Preserve
source tests even when a target-language reviewer considers them redundant;
Rust-specific cleanup may reorganize them only with a lossless case/assertion
mapping and per-case differential `MATCH`.

## 2. Boundary tests

Exercise input boundaries with behavior-specific assertions.

```rust
#[test]
fn numeric_parser_rejects_surrounding_whitespace_when_contract_is_strict() {
    assert!(" 42".parse::<i32>().is_err());
    assert!("42 ".parse::<i32>().is_err());
}

#[test]
fn numeric_parser_reports_overflow() {
    assert!("999999999999999999999".parse::<i64>().is_err());
}

#[test]
fn utf8_text_can_contain_a_nul_code_point() {
    let text = std::str::from_utf8(b"hello\0world").expect("valid UTF-8");
    assert_eq!(text.as_bytes()[5], 0);
}
```

Choose expected behavior from the migrated contract. Do not invent a restriction because an input looks unusual.

Typical boundaries:

- empty versus absent;
- zero, min/max, overflow, precision, signedness;
- Unicode normalization, invalid UTF-8 bytes, embedded NUL where applicable;
- maximum depth/size/count;
- time zone, locale, leap/daylight transitions;
- duplicate keys and stable/unstable order.

## 3. Failure and security tests

Assert error type, causal chain, side effects, and each public surface.

```rust
#[test]
fn public_display_is_redacted_while_source_is_preserved() {
    use std::error::Error;

    let error = load_secret_fixture().expect_err("fixture must fail");
    assert!(!error.to_string().contains("credential-value"));

    let source = error.source().expect("causal source");
    assert_eq!(source.to_string(), "credential-value");
}
```

Test separately:

- `Display`;
- `Debug`;
- serialized diagnostics;
- logs/tracing fields;
- HTTP/RPC error body;
- `Error::source()`.

Also assert whether the target body ran, what state changed before failure, and whether retry is safe.

## 4. Lifecycle and concurrency tests

Use deterministic probes, barriers, notifications, channels, paused time, or model checking rather than fixed sleeps.

```rust
#[tokio::test]
async fn cancelling_waiter_does_not_leave_an_orphan_resource() {
    let probe = Probe::new();
    let mut operation = Box::pin(start_with_probe(probe.clone()));

    tokio::select! {
        _ = &mut operation => panic!("operation completed before the injected boundary"),
        () = probe.wait_until_started() => {}
    }

    drop(operation);
    probe.release();
    probe.wait_until_closed().await;
    assert_eq!(probe.open_resource_count(), 0);
}
```

Protect:

- state transitions;
- before/after and cleanup order;
- exactly-once release;
- cancellation and timeout ownership;
- bounded queues/backpressure;
- concurrent registration/shutdown;
- retry/idempotency and transaction atomicity.

## 5. Compile-contract tests

Use normal compilation, doctests, feature-matrix jobs, and `trybuild`/equivalent UI tests for:

- public imports and re-exports;
- macro success and diagnostic failures;
- generics, visibility, renamed dependencies;
- `Send`/`Sync` or deliberately local APIs;
- MSRV and target-specific feature combinations.

```rust
#[test]
fn macro_diagnostics_are_stable() {
    let cases = trybuild::TestCases::new();
    cases.pass("tests/ui/component-pass.rs");
    cases.compile_fail("tests/ui/component-missing-field.rs");
}
```

Do not add a runtime “type exists” test when the compiler already exercises the same surface. Keep a compile test when the public path/feature combination itself is the contract.

## 6. Adapter conformance tests

Put shared semantic assertions in a testkit and execute them for every framework adapter:

```rust
pub fn assert_scope_contract(observation: &ScopeObservation) {
    assert!(observation.open_during_body);
    assert!(observation.cancelled_after_drop);
    assert_eq!(observation.close_count, 1);
}
```

Each adapter should provide native observations. Keep adapter-specific routing, extractor, middleware/service, stream/body, error mapping, and shutdown tests beside the adapter.

## 7. Non-functional tests

Choose tools from the claim:

- mutation testing for whether tests detect behavior changes;
- property testing for broad invariants and generated differential cases;
- fuzzing for untrusted parsers/codecs/formats;
- benchmarks for latency/throughput regression;
- load/soak tests for resource growth and recovery;
- real-host tests for deployment boundaries;
- rollout/rollback rehearsals for operational recovery.

Do not infer one claim from another. A benchmark is not a correctness test; line coverage is not mutation evidence; a mock is not a real-host test.

## 8. Review candidates, not automatic deletions

Review these patterns:

- constructor/getter/setter round trips with no domain invariant;
- constants compared only to their literal definition;
- tests named for coverage lines or parts;
- `#[should_panic]` that preserves a `todo!()`/`unimplemented!()` stub;
- broad snapshots with no stable contract;
- duplicated adapter tests that should share a conformance assertion.

Keep or rewrite a candidate when it protects a public compatibility rule, invariant, feature combination, or known regression. Delete only after source trace, overlap, and mutation/reviewer evidence show no lost protection.
