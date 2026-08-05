# Migration Verification SOP and Templates

Use these templates to turn a Java-to-Rust compatibility claim into reproducible evidence.

## 0. Object-state precondition

Read the authoritative `对象级对照表.md` before test inventory. Only read its
current-fact region before `<!-- historical-design-appendix-start -->`; the
appendix can explain decisions but cannot supply current completion states.

If the current region contains `MISSING`, `MISPLACED`, `STUB`, `PARTIAL`, or
`UNVERIFIED`, record the exact counts and conclude that migration completion is
blocked regardless of passing tests. Test evidence can strengthen an
`IMPLEMENTED` or `DEPENDENCY_REUSED` row; it cannot create a missing file,
move a misplaced object, or fill absent behavior.

## 1. Three-ledger record

Create the source inventory before the generic contract matrix:

| Ledger | Required row |
|---|---|
| `SOURCE_PARITY/TEST_CASE` | one per Java test and every concrete parameterized/dynamic/repeated case, with source production trace, preservation flags, target test, and golden/live result |
| `SOURCE_PARITY/TEST_ASSET` | one per source fixture/resource/script/corpus/golden/data file, with source/target path, copy mode, and SHA-256 |
| `RUST_OBLIGATION` | one per applicable ownership, async, error, serialization, feature, macro, adapter, unsafe, or replacement-component risk |
| `VALUE_ADD` | one per uncovered branch, meaningful mutant, property, fuzz finding, incident, load, security, or rollback risk |

Do not substitute Rust test counts for source-test disposition.

The completion denominator is the complete frozen source test tree, not an
agent-selected “in-scope” subset. `MISSING`, `BLOCKED`, and `NOT_APPLICABLE`
remain useful diagnostic states but all block 100% lossless completion. An
`ADAPTED`, `SPLIT`, or `MERGED_APPROVED` row passes only when it preserves every
source case and assertion and has differential `MATCH`.

All `evidence` and run `artifact` paths in the JSON manifest are relative to the
manifest file and must exist when the completion audit runs. Keep the manifest,
raw Java output, raw Rust output, normalized output, and comparison report tied
to the pinned baselines in versioned files or immutable CI artifacts.

Use the JSON manifest template bundled with the skill. Keep copied assets
immutable. Verify the manifest with:

```bash
python3 "$SKILL_DIR/scripts/audit_migration_tests.py" \
  --java-root <java-module> \
  --rust-root <rust-crate-or-workspace> \
  --object-ledger <对象级对照表.md> \
  --parity-manifest <source-test-parity.json> \
  --fail-on-incomplete
```

## 2. Whole-project migration acceptance module

Create one dedicated target-workspace package for every repository/product-level
migration completion claim. It is especially necessary when any of these hold:

- the migrated product spans multiple production crates;
- language bindings, framework adapters, or host packages must work together;
- the source has a system/templatesuite or reusable test-support module;
- the compatibility claim is about public end-to-end workflows rather than one
  crate's internal behavior.

Use `<project>-test` as the final directory and Cargo package name. Keep it
singular and consistent with the project family; do not alternate between
`-test`, `-tests`, and `-testing`. Set `publish = false`, add it to workspace
`members`, and run it explicitly in CI even when it is excluded from
`default-members` for fast local development. It is test infrastructure, not a
published production crate and not a source-object parity row.

Place that directory according to the workspace topology already recorded by
the migration roadmap:

| Workspace topology | Typical package path |
|---|---|
| small root-flat | `<project>-test/` |
| hybrid/domain-grouped | root-flat when product-wide, or `<test-family>/<project>-test/` when a real family exists |
| contained/grouped | `crates/<project>-test/` or `crates/tests/<project>-test/` |
| multi-language repository | inside the selected Rust workspace root, then apply one of the rows above |

The role and Cargo package name are mandatory; the parent directory is not.
Never infer it from Java's test-module path or hardcode `crates/` in automation.

Cargo converts hyphens to underscores only in Rust paths: the directory and
package remain `freemarker-test`, while Rust code imports an optional harness
library as `freemarker_test`.

| Product/package family | Directory | Cargo package | Rust crate identifier |
|---|---|---|---|
| FreeMarker | `freemarker-test/` | `freemarker-test` | `freemarker_test` |
| QlExpress Rust (`qlexpress`) | `qlexpress-test/` | `qlexpress-test` | `qlexpress_test` |

Keep responsibilities separate:

| Location | Owns | Does not prove |
|---|---|---|
| production crate local tests | algorithms, parser/AST nodes, internal errors, focused public APIs | complete migrated product parity |
| binding/adapter local tests | conversion, ABI/FFI, packaging, native host surface | engine plus every host workflow |
| `<project>-test` | complete source suite/assets, public cross-crate workflows, golden/live diff, aggregate artifacts | production implementation code |

## Rust file-size and test-organization gate

Rust defines no universal file-length maximum. Count physical lines in every
authored `.rs` file, including integration tests, test helpers, examples,
benches, and testkit source: up to 500 lines is normal, 501–800 requires a
cohesion review, and more than 800 blocks completion. Generated, vendored, and
build-output trees are excluded. Split weakly cohesive suites by source contract,
behavior family, fixture family, adapter, or verification layer; retain source
case IDs so splitting never loses traceability.

Enable `clippy::too_many_lines` and review functions/methods above its default
100-line threshold. Keep focused private-behavior unit tests in
`#[cfg(test)]` modules when that preserves encapsulation. Use
`tests/<contract>.rs`, `tests/common/mod.rs`, or a dedicated non-published
test/testkit crate for public-boundary, cross-module, differential, host, load,
and whole-project tests. A test crate may place reusable harness implementation
in its own `src/`, while executable integration entry points remain under
`tests/`.

Use public production APIs from the test package. Do not move missing product
logic into the test harness. Keep reusable runners in `src/lib.rs` or a testkit
module, integration entry points under `tests/`, immutable source assets under a
clearly named suite directory, and raw/normalized/diff artifacts under the
verification location recorded by the parity manifest.

FreeMarker naming and boundary example:

```text
freemarker-rust/
├── Cargo.toml                # members include all three packages
├── freemarker/               # engine; focused local tests
├── freemarker-pyo3/          # Python binding; focused binding/package tests
└── freemarker-test/          # whole-project migration acceptance
    ├── Cargo.toml            # name = "freemarker-test"; publish = false
    ├── src/lib.rs            # shared templatesuite/differential harness only
    └── tests/
        ├── source_parity.rs
        ├── cross_component.rs
        └── suite/source/     # byte-identical Java templates/data/expected files
```

The Java oracle may combine `freemarker-test-utils` with the Java templatesuite;
the Rust `freemarker-test` package owns replay of those assets against the public
`freemarker` API and any required `freemarker-pyo3` end-to-end workflow. Require
all cases to pass and compare. Gates such as `PASS >= 20`, “representative cases
passed”, or `SKIPPED` with a reason are progress reports, not migration
completion.

Minimum Cargo shape:

```toml
[package]
name = "freemarker-test"
publish = false

[dependencies]
freemarker = { path = "../freemarker" }
```

Record the module package, manifest path, tested components, command, artifact,
and zero failed/skipped/not-run counts in `source-test-parity.json`.

## 3. Slice verification record

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

## 4. Contract-to-evidence matrix

Create one row per observable contract:

| ID | Java source/test | Contract | Risk | Rust target | Oracle | Planned level | Result/artifact |
|---|---|---|---|---|---|---|---|
| CFG-01 | `EnvironmentTests#higherPrioritySourceWins` | first configured precedence rule wins | high | `Environment::get` | live Java/Rust | `V4_LIVE_DIFF` | pending |
| LIFE-03 | `LifecycleProcessor#stop` | initialized components stop in reverse dependency order | critical | `ApplicationContext::close` | mirrored + deterministic probe | `V2_MIRRORED` | command/log |

If a row has only a mirrored test, keep the planned differential level open.

## 5. Differential case format

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

Run the format over every concrete source case. A sampled corpus is development
evidence only. The final manifest records `result_parity: MATCH` for every row
and suite runs with zero mismatches, harness failures, and not-run cases.

## 6. Normalizer checklist

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

## 7. Harness outcome taxonomy

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

## 8. Lifecycle failure matrix

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

## 9. Public error-surface matrix

| Surface | Audience | Typical policy | Test |
|---|---|---|---|
| `Display` | user/operator | stable, low-cardinality, redacted | inject secret and assert absence |
| `Debug` | developer | may contain structure; define secret policy explicitly | snapshot/property |
| `Error::source()` | programmatic diagnostics | preserve causal chain | walk chain and assert type/root cause |
| serialized report | API/artifact consumer | schema-stable and redacted | golden wire fixture |
| tracing/log fields | operators/log store | no secrets/high-cardinality payloads | captured subscriber |
| HTTP/RPC error | remote caller | stable public code/message | real adapter request |

Testing one row does not prove the others.

## 10. Shared adapter conformance template

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

## 11. Test-value review record

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

## 12. Gate sequence

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

## 13. Acceptance summary

```markdown
## Acceptance summary

| Dimension | Denominator | Passed | Evidence | Gaps |
|---|---:|---:|---|---|
| Structural disposition | | | V0 | |
| Source-test disposition | | | V0–V4 | |
| Source-test assets | | | SHA-256 exact copy | |
| Rust obligations | | | V1–V6 | |
| Value-add risks | | | V1–V7 | |
| Real implementation | | | V1+ | |
| Mirrored contracts | | | V2 | |
| Golden/live differential | | | V3/V4 | |
| Host integration | | | V5 | |
| Non-functional | | | V6 | |
| Rollback | | | V7 | |
| Strict object blockers | | | authoritative current object ledger | |

- Exact commands:
- Failed/flaky/ignored/skipped/not-run:
- Warnings/lints:
- MISSING/MISPLACED/STUB/PARTIAL/UNVERIFIED:
- Exact DEPENDENCY_REUSED symbol/version/adapter/integration evidence:
- Simulated dependencies:
- Unsupported targets:
- Next promotion gate:
```

The final sentence must say `migration incomplete` when the strict blocker
count is non-zero. Do not phrase green executed tests as overall completion.
