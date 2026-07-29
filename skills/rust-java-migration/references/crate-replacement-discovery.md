# Discovering and Evaluating Rust Replacement Crates

Use this workflow when the common mapping table and candidate catalog do not
contain a verified replacement, or when the project constraints make the usual
candidate unsuitable. The objective is not to find a crate with a similar
name. It is to find the smallest maintainable Rust shape that preserves the
required Java behavior.

## Contents

1. [Start from a responsibility](#1-start-from-a-responsibility)
2. [Build search queries](#2-build-search-queries)
3. [Search several evidence sources](#3-search-several-evidence-sources)
4. [Create a broad candidate set](#4-create-a-broad-candidate-set)
5. [Apply hard gates](#5-apply-hard-gates)
6. [Score fitness and health separately](#6-score-fitness-and-health-separately)
7. [Interpret ecosystem signals](#7-interpret-ecosystem-signals)
8. [Inspect integration and supply-chain cost](#8-inspect-integration-and-supply-chain-cost)
9. [Spike the riskiest contract](#9-spike-the-riskiest-contract)
10. [Record a reproducible decision](#10-record-a-reproducible-decision)

## 1. Start from a responsibility

Do not search for `Spring replacement`, `Jackson replacement`, or another Java
product name as the only query. First split the dependency into independently
testable responsibilities:

- public API and extension points;
- wire or storage format;
- parsing, validation, or transformation;
- runtime, scheduling, cancellation, and backpressure;
- persistence, pooling, transaction, or retry behavior;
- middleware, lifecycle, discovery, or dependency injection;
- code generation, reflection, or annotation processing;
- diagnostics, security, packaging, and target-platform behavior.

Write the must-have contract and the highest-risk unknown for each
responsibility. Search one responsibility at a time.

Example:

```text
Java dependency: Jackson
Responsibilities:
1. JSON data model and field naming
2. polymorphic type tags
3. streaming parser
4. custom date/time module
5. unknown-field compatibility
```

This may lead to `serde` plus `serde_json` and project-owned serializers rather
than one all-in-one replacement.

## 2. Build search queries

Generate English query families from capability, mechanism, protocol, and
constraints. Include synonyms used by the Rust ecosystem.

| Java responsibility | Query families |
|---|---|
| `ObjectMapper` behavior | `serde json custom serializer`, `json streaming deserializer`, `tagged enum json` |
| `ConcurrentHashMap` behavior | `concurrent hashmap`, `sharded map`, `async cache`; also evaluate std locking and ownership |
| JDBC/JPA responsibility | `postgres async driver`, `sql toolkit`, `rust orm`, `transaction pool` |
| scheduled executor | `tokio scheduler`, `cron async`, `delay queue`, `cancellable task scheduler` |
| ServiceLoader | `plugin registry`, `link time registration`, `inventory registry`; also evaluate explicit constructors |
| Java annotation processing | `proc macro derive`, `attribute macro codegen`, `compile time validation` |

Use protocol and environment terms where they constrain interoperability:
`AMQP 0.9.1`, `Kafka transactions`, `Redis cluster`, `WASM`, `no_std`,
`rustls`, `Android`, or `MSRV 1.xx`.

Run at least three materially different query families for an unfamiliar
responsibility. Record queries that returned no viable candidates; negative
search evidence prevents repeated work.

## 3. Search several evidence sources

Start with the official registry search:

```bash
cargo search "<capability protocol constraint>" --limit 20
```

Then inspect:

- crates.io exact crate pages, keywords, categories, versions, owners, download
  history, and reverse dependencies;
- the versioned docs.rs page, documented features/targets, examples, and build
  status;
- the source repository, releases, changelog, CI, issues, pull requests,
  contributors, security policy, and ownership;
- RustSec advisories and the resolved application dependency graph;
- official protocol or framework compatibility documentation where applicable.

If `rust-crate-discovery` is available, route the broad search and ecosystem
health comparison to it. Resolve its installed skill directory dynamically;
never copy an absolute path into the migration skill:

```bash
python3 "$CRATE_DISCOVERY_SKILL_DIR/scripts/crate_eval.py" search \
  "<capability protocol constraint>" --limit 20

python3 "$CRATE_DISCOVERY_SKILL_DIR/scripts/crate_eval.py" compare \
  candidate_a candidate_b candidate_c
```

The discovery score is an ecosystem-health input. It is not the migration
decision because it cannot prove the Java contract, runtime compatibility, or
host behavior.

Record an observation date for web metadata. Downloads, releases, owners,
advisories, and repository activity are time-dependent.

## 4. Create a broad candidate set

Collect five to ten plausible options before narrowing to two to four. Include
more than direct crates:

- standard library or a small project-owned implementation;
- a direct crate;
- a crate hidden behind a port-owned wrapper;
- a trait with multiple adapter crates;
- a lower-level protocol crate plus project-owned semantics;
- compile-time code generation or a procedural macro;
- host-application responsibility;
- an approved exclusion when the JVM-only behavior should not migrate.

Do not count aliases, abandoned forks, or several crates in the same family as
independent evidence. Record the canonical source repository and relationship
between companion crates.

## 5. Apply hard gates

Reject or block before scoring when a must-have constraint fails:

- required behavior, protocol, wire/storage compatibility, or error contract is
  absent;
- license or distribution obligations are incompatible;
- MSRV, edition, target, `no_std`, WASM, Android, iOS, or architecture support
  is incompatible;
- an unresolved advisory, unacceptable `unsafe`, unreviewable source, or
  unacceptable build script/native dependency remains;
- async runtime, blocking behavior, cancellation, backpressure, timeout, or
  shutdown semantics cannot be reconciled;
- required database/broker/server versions are unsupported;
- maintenance ownership and fork/exit strategy are unacceptable;
- feature unification or transitive conflicts cannot be isolated.

A high download count never overrides a hard gate.

## 6. Score fitness and health separately

Use a project-specific scorecard only after hard gates. The following
100-point model is a default, not a universal ranking:

| Dimension | Weight | Evidence |
|---|---:|---|
| Semantic and contract fit | 30 | contract matrix, source/API inspection, compatibility fixtures |
| Maintenance and ownership | 15 | releases, meaningful commits, issue/PR response, owners, bus factor |
| Adoption and ecosystem evidence | 15 | recent/all-time downloads, reverse dependencies, credible downstream use |
| Documentation and test quality | 10 | versioned docs, examples, CI matrix, integration/property/fuzz tests |
| Project compatibility | 10 | MSRV, targets, runtime/TLS, features, native dependencies |
| Security and supply chain | 10 | RustSec, license, unsafe/build scripts, provenance, dependency graph |
| API maturity and stability | 5 | release history, semver discipline, changelog, deprecation policy |
| Operational cost and exit strategy | 5 | compile/runtime cost, observability, upgrade/fork/wrapper strategy |

Rules:

1. Give zero for unsupported required behavior and fail the corresponding hard
   gate; do not average it away.
2. Score candidates relative to the same responsibility and project, not across
   unrelated categories.
3. Attach evidence and confidence (`HIGH`, `MEDIUM`, `LOW`) to every dimension.
4. Keep unknowns visible. Do not turn missing evidence into an optimistic score.
5. Do not automatically select the highest total. The score orders
   investigation; the contract spike and host evidence decide adoption.

## 7. Interpret ecosystem signals

### Usage

Use both recent and all-time downloads, plus reverse dependencies and credible
downstream projects. Prefer trend or download velocity over an all-time number
alone. Compare within the same category because a foundational transitive crate
and a niche protocol client naturally have different scales.

Downloads can be inflated by CI, transitive use, old versions, renamed crates,
or a widely used companion crate. Reverse-dependency counts can be inflated by
examples, abandoned projects, or one crate family. Treat both as adoption
signals, not production-quality proof.

### Activity

Inspect release recency together with meaningful commits, issue/PR response
time, contributor distribution, maintainer identity, and published maintenance
intent. A quiet small crate may be complete and stable; frequent automated
commits may indicate no human maintenance. Explain which interpretation applies.

### Documentation and maturity

Check the exact candidate version, not only `latest`. Look for feature and
target documentation, safety notes, MSRV policy, changelog, migration guides,
examples, and failure semantics. A docs.rs build proves documentation was
built in a particular environment; it does not prove API completeness or
semantic fitness. Investigate build failures before rejecting a crate because
native tools or target configuration may be the cause.

### Community and ownership

Stars and forks are weak popularity signals. Prefer accountable owners,
multiple active contributors, responsive review, a disclosed security process,
and evidence that downstream users can upgrade. A single-maintainer crate needs
an explicit bus-factor and fork/exit assessment.

## 8. Inspect integration and supply-chain cost

Evaluate the candidate in the target workspace:

```bash
cargo metadata --format-version 1
cargo tree -e features
cargo tree -d
cargo audit
```

Also inspect default features, optional features, duplicate runtime/TLS stacks,
native libraries, `build.rs`, generated code, proc macros, unsafe code, compile
time, binary size, platform toolchains, and license closure. Run `cargo deny`
when the repository policy uses it.

`cargo audit` over the resolved `Cargo.lock` is stronger evidence than a crate
name search because advisories may affect a transitive version or only a
particular version range.

## 9. Spike the riskiest contract

Spike the top two candidates when the decision is consequential or uncertain.
Use the same contract fixture and target environment for both. Test the most
likely failure:

- Java-produced wire/storage data round trip;
- cancellation during startup or an in-flight request;
- bounded memory with a slow stream consumer;
- transaction rollback after partial work;
- broker reconnect, duplicate delivery, or acknowledgement;
- macro diagnostics and generated API compatibility;
- Android/iOS/WASM/cross-compilation;
- real host startup, readiness, shutdown, and observability.

Record exact crate versions, features, target, commands, fixtures, measurements,
and failures. A hello-world compilation is only `DEPENDENCY_DECLARED` or, at
best, a narrowly named spike; it is not contract verification.

## 10. Record a reproducible decision

For every accepted or rejected candidate, record:

```markdown
- Java responsibility and source baseline:
- Required contract and hard gates:
- Search queries and observation date:
- Candidates and canonical sources:
- Candidate version/features/targets:
- Hard-filter result and rejection reasons:
- Fitness score with per-dimension evidence/confidence:
- rust-crate-discovery health result, if used:
- Resolved dependency/feature/advisory evidence:
- Highest-risk spike and artifact:
- Known differences and operational cost:
- Wrapper/adapter owner and exit strategy:
- Adoption state and next evidence gate:
```

Re-run discovery when the Java contract, Rust target/MSRV, candidate major
version, ownership, license, advisory status, or deployment topology changes.
