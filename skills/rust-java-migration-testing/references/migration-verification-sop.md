# Migration Verification SOP and Templates

Use these templates to turn a Java-to-Rust compatibility claim into reproducible evidence.

## 1. Three-ledger record

Create the source inventory before the generic contract matrix:

| Ledger | Required row |
|---|---|
| `SOURCE_PARITY` | one per Java test and distinct parameterized/dynamic case, with source production trace and disposition |
| `RUST_OBLIGATION` | one per applicable ownership, async, error, serialization, feature, macro, adapter, unsafe, or replacement-component risk |
| `VALUE_ADD` | one per uncovered branch, meaningful mutant, property, fuzz finding, incident, load, security, or rollback risk |

Do not substitute Rust test counts for source-test disposition.

## 2. Slice verification record

```markdown
# Verification: <module / vertical slice>

- Java SHA/artifact:
- Rust SHA:
- Java command/toolchain:
- Rust command/toolchain/features/target:
- Compatibility claim:
- Source call path:
- Rust call path:
- Available oracle:
- Required hosts/dependencies:
- Evidence level achieved:
- Unverified boundaries:
```

## 3. Contract-to-evidence matrix

Create one row per observable contract:

| ID | Java source/test | Contract | Risk | Rust target | Oracle | Planned level | Result/artifact |
|---|---|---|---|---|---|---|---|
| CFG-01 | `EnvironmentTests#higherPrioritySourceWins` | first configured precedence rule wins | high | `Environment::get` | live Java/Rust | `V4_LIVE_DIFF` | pending |
| LIFE-03 | `LifecycleProcessor#stop` | initialized components stop in reverse dependency order | critical | `ApplicationContext::close` | mirrored + deterministic probe | `V2_MIRRORED` | command/log |

If a row has only a mirrored test, keep the planned differential level open.

## 4. Differential case format

Prefer an append-only JSONL corpus:

```json
{"schema":1,"case_id":"cfg-empty","seed":null,"input":{"sources":[]},"expected":{"kind":"ok","value":null}}
{"schema":1,"case_id":"cfg-cycle","seed":null,"input":{"value":"${a}","a":"${b}","b":"${a}"},"expected":{"kind":"error","code":"CYCLE"}}
```

Store metadata beside it:

```json
{
  "java_sha": "<sha>",
  "java_toolchain": "<jdk/build>",
  "exporter_sha": "<sha>",
  "schema": 1,
  "normalizer": "normalizer-v1",
  "generated_at": "<timestamp>"
}
```

Keep raw Java output, raw Rust output, normalized output, and comparison report as separate artifacts.

## 5. Normalizer checklist

Normalize only documented nondeterminism:

- generated identifiers;
- timestamps/time zones;
- temporary absolute paths;
- map/set order when the contract is unordered;
- locale-specific messages when callers do not consume them;
- scheduling order only when the API explicitly leaves it unspecified.

Do not normalize:

- error category;
- omitted/extra fields;
- numeric precision;
- stable ordering;
- retry/side-effect count;
- state transitions;
- security-relevant text.

Version and test the normalizer. A normalizer change requires reviewing prior fixtures.

## 6. Harness outcome taxonomy

Report one of:

| Outcome | Meaning |
|---|---|
| `MATCH` | both executions completed and normalized contracts match |
| `SEMANTIC_MISMATCH` | executions completed but observable behavior differs |
| `JAVA_HARNESS_FAILURE` | Java oracle/exporter did not produce valid evidence |
| `RUST_HARNESS_FAILURE` | Rust runner did not produce valid evidence |
| `NORMALIZER_FAILURE` | raw artifacts exist but cannot be normalized safely |
| `BLOCKED` | a named dependency or decision prevents execution |

Never turn harness failures into product mismatches or silently skip them.

## 7. Lifecycle failure matrix

Adapt this table to the framework:

| Phase | Success | Error | Panic | Timeout | Caller cancel | Dependency loss |
|---|---|---|---|---|---|---|
| Build | final state/no context | typed error | isolated if user code runs | bounded | no partial context | N/A |
| Refresh/init | next state | rollback/closed | isolated + rollback | abort + rollback | operation contract explicit | cleanup |
| Start | ready | reverse cleanup | isolated + cleanup | abort + cleanup | orphan policy explicit | cleanup |
| Ready | serves work | structured failure | supervisor policy | bounded | shutdown begins | degrade/close |
| Pause/reload | stable paused/reloaded state | rollback policy | isolated | bounded | state remains legal | recover/close |
| Close | closed | first + supplemental errors | continue cleanup | bounded abort | idempotent | best effort + evidence |

For each applicable cell assert:

- exact state sequence;
- target/body invoked or short-circuited;
- cleanup order and count;
- cancellation propagation;
- task/connection/handle count returns to baseline;
- primary error remains primary;
- public error/log/report surfaces follow redaction policy.

## 8. Public error-surface matrix

| Surface | Audience | Typical policy | Test |
|---|---|---|---|
| `Display` | user/operator | stable, low-cardinality, redacted | inject secret and assert absence |
| `Debug` | developer | may contain structure; define secret policy explicitly | snapshot/property |
| `Error::source()` | programmatic diagnostics | preserve causal chain | walk chain and assert type/root cause |
| serialized report | API/artifact consumer | schema-stable and redacted | golden wire fixture |
| tracing/log fields | operators/log store | no secrets/high-cardinality payloads | captured subscriber |
| HTTP/RPC error | remote caller | stable public code/message | real adapter request |

Testing one row does not prove the others.

## 9. Shared adapter conformance template

Define one testkit interface:

```rust
pub trait AdapterProbe {
    type NativeRequest;
    type NativeResponse;

    fn observe_context(&self) -> ContextObservation;
    fn observe_scope(&self) -> ScopeObservation;
    fn observe_error(&self) -> ErrorObservation;
}
```

Run common assertions for:

- same application/context identity;
- request scope remains open while native body/stream is alive;
- scope closes on completion, error, cancellation, and drop;
- request-scoped component identity is stable;
- missing route/plan fails closed when required;
- native error/status/source semantics are preserved;
- slow consumer respects queue/body bounds;
- shutdown releases framework resources.

Keep framework-specific tests for native extractors, middleware/service composition, routing templates, body frames/trailers, local non-`Send` futures, and packaging.

## 10. Test-value review record

For every test proposed for deletion or rewrite:

| Field | Value |
|---|---|
| Test | file and function |
| Protected contract | specific behavior or `NONE_IDENTIFIED` |
| Source trace | Java source/test/doc |
| Bug caught | concrete mutation/regression |
| Current evidence level | V0-V7 |
| Action | `KEEP` / `IMPROVE` / `MERGE` / `REMOVE_PROPOSED` |
| Proof | mutation result, overlap trace, or reviewer rationale |

Never delete solely because a heuristic labels the test low value.

## 11. Gate sequence

Prefer fast feedback first:

1. no-stub/source invariant scan;
2. format/check/targeted unit tests;
3. compile-fail and feature matrix;
4. full Rust-local suite and Clippy/docs;
5. mirrored source contracts;
6. golden/live differential corpus;
7. shared adapter conformance and real host;
8. deterministic concurrency/model tests;
9. mutation/property/fuzz/security;
10. load/soak and rollout/rollback.

Parallelize independent crates, platforms, and external-service jobs, but isolate ports, temp directories, databases, and process state.

## 12. Acceptance summary

```markdown
## Acceptance summary

| Dimension | Denominator | Passed | Evidence | Gaps |
|---|---:|---:|---|---|
| Structural disposition | | | V0 | |
| Source-test disposition | | | V0–V4 | |
| Rust obligations | | | V1–V6 | |
| Value-add risks | | | V1–V7 | |
| Real implementation | | | V1+ | |
| Mirrored contracts | | | V2 | |
| Golden/live differential | | | V3/V4 | |
| Host integration | | | V5 | |
| Non-functional | | | V6 | |
| Rollback | | | V7 | |

- Exact commands:
- Failed/flaky/skipped:
- Stubs/placeholders:
- Warnings/lints:
- Simulated dependencies:
- Unsupported targets:
- Next promotion gate:
```
