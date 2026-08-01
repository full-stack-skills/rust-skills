# Migration Test-Value Rubric

Use this rubric after source-test inventory and before deleting, merging, or adding tests. It is a decision aid, not an automated score gate.

This rubric evaluates test quality only. It never promotes object status and
never overrides `MISSING`, `MISPLACED`, `STUB`, `PARTIAL`, or `UNVERIFIED` in
the current authoritative object ledger. A perfect test score against a facade
or substitute is irrelevant if the source object's expected file or semantics
are absent.

Do not use this rubric to remove or weaken a `SOURCE_PARITY` case. Every source
test remains in the 100% compatibility floor even when it is redundant or low
value by target-language standards. `REMOVE_PROPOSED` applies only to
Rust-authored duplicate/value-add tests after confirming no source mapping is
lost.

## Required metadata

Every retained or proposed test should answer:

| Field | Required content |
|---|---|
| Ledger | `SOURCE_PARITY`, `RUST_OBLIGATION`, or `VALUE_ADD` |
| Trace | Java test/signature, Rust mechanism, contract, bug, incident, or risk |
| Observable | exact value, error, side effect, state, bytes, order, or resource behavior |
| Failure model | concrete plausible mutation/defect that makes the test fail |
| Boundary | unit, integration, real dependency, host, differential, load, or rollout |
| Evidence | `V0_STATIC` through `V7_ROLLBACK` |
| Determinism | seed, clock, scheduler, timeout, normalization, and environment controls |
| Distinction | branch/case/platform/failure/invariant not already protected |

## Manual review score

Give one point for each “yes”:

1. Is the protected behavior traceable to a source test, documented contract, Rust mechanism, bug, or risk?
2. Does the assertion observe meaningful behavior instead of type existence or compilation alone?
3. Would a plausible implementation defect make it fail?
4. Does it exercise the real production path at the correct boundary?
5. Is it deterministic without relying on an arbitrary sleep?
6. Does it add a distinct input, branch, failure, platform, or invariant?
7. Does it assert the exact value/error/state when that contract is observable?
8. Is its evidence label honest?

Interpretation:

| Score | Review action |
|---:|---|
| 7–8 | `KEEP`; consider elevating to shared conformance if reused |
| 5–6 | `KEEP` or `IMPROVE`; identify the missing signal |
| 3–4 | `IMPROVE` or `MERGE`; inspect source trace and mutation sensitivity |
| 0–2 | `REMOVE_PROPOSED` or replace; require human approval |

Never remove a test from this score alone. A low-scoring test may be a compile contract, platform guard, or regression whose context is outside the body.

## Assertion-strength ladder

From weakest to strongest:

1. code compiles or a type can be constructed;
2. operation returns `Ok`/`Err`;
3. exact value or error variant is asserted;
4. value plus state/side effect/order/resource behavior is asserted;
5. the same contract is checked against Java golden/live output or an approved standards oracle;
6. property, mutation, fuzz, interleaving, real-host, or rollback evidence tests a broader failure model.

Use the weakest level that fully proves the named contract, but no weaker.

## Common improvements

| Weak test | Improvement |
|---|---|
| `assert!(result.is_err())` | assert typed variant, error code, position/context, source, and redacted public surface as applicable |
| parse-only check for evaluator feature | evaluate representative true/false/boundary/failure cases |
| `let _ = result` | assert outcome and observable effects, or mark the missing implementation |
| cache test checks only returned values | instrument loader/backend calls, hit/miss/eviction, concurrency, and invalidation |
| async test sleeps then inspects | coordinate with barriers/notifies/channels and use a bounded timeout |
| duplicate coverage tests | parameterize distinct cases or merge only after contract mapping |
| snapshot regenerated on mismatch | review semantic diff and version normalizer/schema |
| fixture `Clone`/`Debug` test | remove unless the trait output/behavior is a public contract |

## Coverage and mutation

Coverage locates code that tests did not execute. Mutation asks whether assertions detect behavior changes. Neither proves Java/Rust parity.

- Compare coverage only with documented, comparable scope.
- Review branch and condition gaps before chasing lines.
- Treat generated code and approved exclusions explicitly.
- Review surviving mutants individually; equivalent mutants do not require artificial tests.
- Do not keep meaningless tests merely because deleting them lowers coverage.
