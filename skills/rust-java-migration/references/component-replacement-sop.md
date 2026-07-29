# Component Replacement Decision SOP

Use this SOP when a Java library, framework subsystem, annotation mechanism, runtime service, or infrastructure client needs a Rust replacement. Select against observable contracts and deployment constraints, not name similarity.

Research notes, copied component lists, and organization conventions are candidate sources only. Record their provenance and observation date, then re-verify candidates against primary project documentation, the resolved dependency graph, advisories, license, MSRV, targets, and executable contracts. Consult [crate replacement discovery and evaluation](crate-replacement-discovery.md) when the common mapping does not fit, and use the [Component candidate catalog](component-candidate-catalog.md) for discovery, not approval.

## 1. Define the decision unit

Split an all-in-one Java framework into responsibilities before evaluating crates:

- domain/API contract;
- serialization and wire format;
- configuration and discovery;
- lifecycle and resource ownership;
- async execution, cancellation, and backpressure;
- persistence or transaction boundary;
- framework/transport adapter;
- code generation or annotation processing;
- diagnostics, security, and operational hooks.

Make one decision per responsibility. Do not choose a single Rust crate merely because one Java dependency covered all of them.

## 2. Capture the compatibility contract

Record:

| Dimension | Required evidence |
|---|---|
| API | required types, operations, overload intent, defaults, nullability |
| Data | wire/storage schema, ordering, precision, time zone, locale, compatibility window |
| Errors | categories, retryability, source chain, redacted public message, partial effects |
| Lifecycle | create/start/ready/pause/close order, idempotency, rollback, `Drop` boundary |
| Concurrency | thread/task safety, atomic operations, ordering, queue bounds |
| Async | laziness, cancellation, timeout ownership, backpressure, blocking boundary |
| Transactions | isolation, propagation, commit/rollback, retry ownership |
| Security | secrets, authentication/authorization hooks, unsafe surface, advisories |
| Operations | tracing/metrics, config reload, shutdown, health, deployment targets |

Mark unknown items explicitly. An unknown high-risk contract blocks a final selection.

## 3. Choose a replacement shape

Prefer the smallest shape that preserves the contract:

| Shape | Use when |
|---|---|
| Standard library | Rust already provides the required semantics |
| Direct crate | one maintained crate closely matches the contract |
| Wrapped crate | the crate is suitable but its API/failure model must be hidden behind a stable port facade |
| Trait + adapters | several runtimes/frameworks must share one semantic contract |
| Registry/SPI | link-time or explicit plugin discovery is an actual requirement |
| Macro/codegen + runtime contract | Java annotation processing/reflection becomes compile-time generation |
| Rust-native redesign | the Java mechanism is JVM-specific but observable behavior can be preserved differently |
| Host responsibility | deployment/framework code belongs outside the reusable core |
| Approved exclusion | the capability is JVM-only or intentionally unsupported, with documented impact |

Keep IoC, AOP, application lifecycle, transport contracts, adapters, and procedural macros in separate layers when they can evolve independently. Avoid process-global service locators and framework-specific types in the core.

## 4. Discover candidates when the mapping is unknown

Search by responsibility, capability, protocol, and constraints rather than the
Java product name alone. Generate several English query families, inspect
crates.io, docs.rs, source repositories, reverse dependencies, and RustSec, and
record the observation date. Include std/project-owned implementations,
wrappers, traits plus adapters, code generation, host responsibility, and
approved exclusion in addition to direct crates.

Use `rust-crate-discovery` for registry search and ecosystem-health evidence
when available. Its score is only one input: migration selection still requires
manual contract fitness, target/runtime compatibility, and a risk-focused
spike. Follow the complete [discovery workflow and scorecard](crate-replacement-discovery.md).

## 5. Apply hard filters before scoring

Reject or block a candidate when any required constraint fails:

- incompatible license or distribution obligations;
- MSRV/edition or target-platform mismatch;
- unresolved security advisory or unacceptable unsafe boundary;
- missing required protocol/wire compatibility;
- incompatible async runtime or unavoidable blocking on executor threads;
- no viable cancellation, timeout, shutdown, or resource-cleanup story;
- abandoned maintenance with no ownership/fork plan;
- feature unification or transitive dependency conflict that cannot be isolated.

Document the rejected candidate and reason so the same evaluation is not repeated.

## 6. Compare viable candidates

Score only after hard filters. Weight dimensions for the project:

| Dimension | Questions |
|---|---|
| Semantic fidelity | Which required contracts are exact, adapted, or missing? |
| Boundary quality | Can the crate stay behind a port-owned trait/facade? |
| Lifecycle correctness | Can startup failure, cancellation, and shutdown clean up deterministically? |
| Concurrency model | Are `Send`/`Sync`, local tasks, queue bounds, and ordering explicit? |
| Testability | Can failures be injected and real dependencies be exercised? |
| Compatibility | Are formats and public behavior stable across the migration window? |
| Ecosystem health | Maintenance, releases, docs, downstream production use, bus factor |
| Supply chain | License, advisories, unsafe, build scripts, native dependencies |
| Cost | compile time, binary size, runtime overhead, memory, operational complexity |
| Exit strategy | Can the implementation be replaced without breaking the migrated facade? |

Downloads and stars are weak ecosystem signals, not acceptance evidence.
Compare usage and activity within the same category, combine recent/all-time
downloads with reverse dependencies and credible downstreams, and distinguish a
quiet stable crate from an abandoned one using ownership, issue/PR response,
release intent, and source history.

## 7. Spike the riskiest behavior

Build a narrow POC around the highest-risk semantic path, not a hello-world path. Examples:

- cancel during startup and prove exactly-once cleanup;
- fail an interceptor before target invocation and prove ordering/error mapping;
- round-trip Java-produced data with edge precision and unknown fields;
- stream with a slow consumer and prove bounded memory/backpressure;
- roll back a transaction after a partial operation;
- load the adapter inside the real target framework and exercise shutdown.

Record the exact candidate version, features, target, commands, outputs, and unresolved gaps.

## 8. Use evidence-gated adoption states

Keep component adoption separate from object migration state:

| State | Meaning |
|---|---|
| `CANDIDATE` | identified but not hard-filtered |
| `ELIGIBLE` | hard constraints pass on paper |
| `DEPENDENCY_DECLARED` | present in the manifest/lockfile only |
| `SPIKE_VERIFIED` | a named risky path passed a bounded POC |
| `CONTRACT_VERIFIED` | the required semantic contract suite passes |
| `HOST_VERIFIED` | a real supported application/runtime integration passes |
| `PRODUCTION_READY` | operational, security, load, upgrade, and rollback gates pass |
| `REJECTED` | failed constraint or comparison, with reason |
| `BLOCKED` | evidence cannot proceed until a named dependency/decision is available |

Never collapse `DEPENDENCY_DECLARED`, `SPIKE_VERIFIED`, and `CONTRACT_VERIFIED` into one “confirmed” label.

Keep research maturity separate from adoption:

| Research status | Meaning |
|---|---|
| `DISCOVERED` | appeared in a source list; identity and current status may be unverified |
| `PRIMARY_SOURCE_CHECKED` | official repository/docs/crate metadata were checked on a recorded date |
| `NEEDS_SPIKE` | plausible candidate with a named semantic or operational uncertainty |
| `NOT_SUITABLE` | unsuitable for the stated contract, with reason |

A crate can be `PRIMARY_SOURCE_CHECKED` yet remain only an adoption `CANDIDATE`. Conversely, a manifest dependency without recorded research is only `DEPENDENCY_DECLARED`, not an endorsed choice.

## 9. Build shared conformance suites

When several adapters implement one contract:

1. Put common assertions and failure fixtures in a dedicated testkit crate/module.
2. Make each adapter produce its native observations.
3. Run the same contract assertions for identity, scope/lifecycle, error mapping, cancellation, body/stream completion, and cleanup.
4. Add adapter-specific tests only for native behavior not expressible in the shared contract.
5. Gate every supported adapter/feature combination in CI.

This prevents ten adapters from carrying ten drifting interpretations of the same contract.

## 10. Record an ADR

Use this minimum record:

```markdown
# Replacement: <Java responsibility> -> <Rust shape/candidate>

- Java baseline:
- Rust baseline:
- Owner:
- Required targets/MSRV/license policy:
- Compatibility contract:
- Search queries, observation date, and canonical sources:
- Hard filters and project-specific scorecard:
- Selected shape and crate/version/features:
- Dependency owner crate/module:
- Alternatives and rejection reasons:
- Highest-risk spike:
- Evidence state:
- Exact test/host evidence:
- Known semantic differences:
- Security/unsafe/advisory review:
- Upgrade and rollback plan:
- Exit criteria for the next state:
```

Verify the ADR against actual `Cargo.toml`, resolved metadata/lockfile, source ownership, and executable tests. Documentation that names a crate not owned by the stated module is drift, not confirmation.

## 11. Re-evaluate on change

Re-open the decision when:

- the source Java contract changes;
- target/MSRV or deployment topology changes;
- a crate changes major version, ownership, license, runtime, or maintenance status;
- advisories or unsafe findings appear;
- load/host evidence contradicts the POC;
- the facade begins leaking implementation-specific types.
- the candidate catalog, local convention, and actual manifest disagree.

Keep the port-owned contract stable where possible and replace the adapter behind it.
