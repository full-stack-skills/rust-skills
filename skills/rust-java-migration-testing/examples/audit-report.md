# Migration Test Audit Example

This hypothetical report demonstrates evidence labels and review decisions. The audit script provides hints only; a reviewer confirms every classification from source and executable evidence.

## Baseline

- Java SHA: `java-sha`
- Rust SHA: `rust-sha`
- Module: `configuration`
- Java oracle: source tests plus a pinned golden exporter
- Rust command: `cargo test -p configuration --all-features`
- Current result: 84 passed, 0 failed, 0 ignored
- Line coverage: 92% (gap-finding signal only)

## `SOURCE_PARITY`

| ID | Java source test/case | Contract | Rust test | Disposition | Evidence | Result |
|---|---|---|---|---|---|---|
| CFG-01 | `EnvironmentTests#explicitOverridesDefault` | explicit value overrides default | `explicit_value_overrides_default` | `ADAPTED` | `V3_GOLDEN_DIFF` | match |
| CFG-02 | `PlaceholderTests#cycle` | cyclic placeholder returns a typed error | `cycle_returns_typed_error` | `MIRRORED` | `V2_MIRRORED` | pass; live diff pending |
| CFG-03 | `EnvironmentTests#profiles(String)` row `empty` | empty profile is rejected | — | `MISSING` | `V0_STATIC` | add target case |

The suite is green, but CFG-02 remains below differential evidence because only the Rust implementation executed.

## `RUST_OBLIGATION`

| ID | Rust mechanism | Risk | Test | Status |
|---|---|---|---|---|
| RUST-01 | `Arc<RwLock<...>>` replacement cache | lock held across `.await` or lost atomicity | deterministic concurrent update test | planned |
| RUST-02 | typed `thiserror` error | public display leaks a value while source chain is lost | `display_redacts_value_and_preserves_source` | passing |
| RUST-03 | Tokio background refresh | cancelled caller leaves orphan task | cancellation/cleanup probe | missing |

## `VALUE_ADD`

| ID | Source | Plausible defect | Test | Status |
|---|---|---|---|---|
| ADD-01 | surviving mutant | precedence comparison reversed | three-source precedence matrix | passing |
| ADD-02 | branch coverage | Unicode key normalization branch untested | normalization property test | planned |

## Heuristic review candidates

### Candidate 1: constant comparison

```rust
#[test]
fn max_depth_is_correct() {
    assert_eq!(MAX_DEPTH, 32);
}
```

Review:

- Protected behavior: no direct behavior identified.
- Source trace: Java documentation states only “bounded depth,” not the value 32.
- Overlap: `depth_33_is_rejected` and `depth_32_is_accepted` protect the boundary.
- Action: `REMOVE_PROPOSED` after confirming mutation/overlap evidence and reviewer approval; retain the value explanation in rustdoc.

### Candidate 2: public feature path

```rust
#[cfg(feature = "yaml")]
#[test]
fn yaml_parser_is_publicly_constructible() {
    let _ = configuration::YamlParser::new();
}
```

Review:

- Protected behavior: the `yaml` feature must expose the documented public path.
- Bug caught: accidental removal of the re-export.
- Action: keep as a compile contract or move to a feature-specific doctest. Do not delete merely because the body is short.

### Candidate 3: redacted report only

```rust
#[test]
fn report_is_redacted() {
    let error = failing_load("credential-value").unwrap_err();
    let json = serde_json::to_string(error.report()).unwrap();
    assert!(!json.contains("credential-value"));
}
```

Review:

- Protected behavior: serialized report redaction.
- Missing evidence: `Display`, `Debug`, tracing fields, and HTTP error body are separate surfaces.
- Action: keep and add surface-specific tests. Do not claim global secret safety from this test.

## Stub and warning gate

The source scan found one production `unimplemented!()` in a default feature
path. That object remains `STUB` even though all current tests pass, so the
module is not migration-complete. The test command also emitted warnings, so
the Clippy `-D warnings` gate remains open.

## Acceptance summary

| Dimension | Status |
|---|---|
| Structural disposition | complete for the module |
| Real implementation | incomplete: one production stub |
| Source-test disposition | 18 represented, 1 missing |
| Golden differential | 7 matching |
| Live differential | not run |
| Rust obligations | 1 passing, 2 open |
| Value-add | 1 passing, 1 planned |
| Real host | not run |
| Concurrency/non-functional | not applicable to this slice |
| Production readiness | not claimed |

Next actions:

1. Replace the production stub and add its source-linked contract tests.
2. Run the pinned Java/Rust corpus for CFG-02.
3. Add `Display` and captured-tracing secret tests.
4. Run Clippy with warnings denied.
