---
name: rust-java-migration
description: Plan, execute, audit, and verify behavior-preserving migrations from Java Maven or Gradle projects to Rust Cargo workspaces. Use when comparing Java and Rust repositories at module, package, object, file, method, parameter, documentation, example, test, concurrency, or runtime-behavior level; selecting Rust replacements for Java frameworks and components; searching crates.io and evaluating unfamiliar alternatives; producing per-module migration roadmaps and parity tables; or continuing an incomplete port without deleting existing work. Enforces a complete upfront inventory, one continuous module-level semantic implementation batch, one consolidated post-implementation parity audit, and final unified build, differential, replay, concurrency, load, fuzz, host-integration, and rollback verification. Forbids inefficient object-by-object migrate-compare-test loops.
---

# Java to Rust Migration

Migrate contracts and observable behavior, not Java syntax. Preserve the Java project's public concepts and source traceability while selecting Rust-native ownership, error, concurrency, async, serialization, and framework mechanisms.

## Scope and Routing

Use this skill for full-project migrations, one Maven/Gradle module, parity audits, migration planning, or continuation of an existing Rust port.

Route detailed Rust choices to:

- `rust-workspace` and `rust-module-layout` for crate and module boundaries.
- `rust-api-design` for public Rust API quality.
- `rust-crate-discovery` for crates.io search and pre-adoption ecosystem-health evidence; migration contract fitness remains owned here.
- `rust-dependencies` for resolved graph, feature, license, advisory, update, and post-adoption governance.
- `rust-macros` for annotation-to-procedural-macro work.
- `rust-concurrency`, `rust-database`, `rust-http-client`, or `rust-web` for domain implementation.
- `rust-java-migration-testing` for source-test disposition, Rust-specific test obligations, differential evidence, and test-value review.
- `rust-testing`, `rust-performance`, and `rust-web-security` for Rust test mechanics and non-functional verification.

Do not modify migration code when the user requested only an audit, plan, or documentation. A plan-only or read-only request does not authorize running a write-producing document scaffolder: return the proposed four-document content in the response, use `--dry-run`, or write only to a user-approved destination. Do not broaden a module migration into a repository rewrite without authorization.

## Required Inputs

Resolve or explicitly mark unknown:

- Java repository path, baseline commit/tag, build tool, JDK, and module scope.
- Rust repository path, baseline commit, toolchain/MSRV, workspace, and target platforms.
- Compatibility goal: source-shape parity, public API parity, behavior parity, or production replacement.
- Dependency policy: license, MSRV, supported targets, unsafe policy, advisory policy, maintenance horizon, and acceptable transitive cost.
- Component-candidate sources and their observation date; distinguish team policy, researched candidates, declared dependencies, and verified adoption.
- Explicit exceptions, blocked external projects, unsupported JVM-only features, and completion deadline.
- Required host applications, real scripts, test data, concurrency model, load profile, and rollback mechanism.

Never silently infer that the newest branch, a generated manifest, or an API registration list is the behavioral baseline.

## Workflow

Treat one declared Java source module and its Rust target crate/module as the
default migration batch. A user-authorized multi-module scope may be one batch,
but its complete boundary must be frozen before implementation. Follow this
execution invariant:

```text
freeze full scope and contracts
    -> implement the complete batch once
    -> freeze implementation
    -> audit the complete batch once
    -> run unified verification
```

Dependency-ordered editing inside the implementation batch is allowed. Per-object
completion loops are not.

### 1. Freeze baselines and inspect repository state

Record both repository SHAs, dirty worktrees, Java/Rust toolchains, module manifests, enabled features, and generated-code boundaries. Preserve existing Rust work and unrelated changes.

If a repository contains `.codegraph/`, use CodeGraph before text search or file-by-file reading:

1. Survey module/package/crate architecture.
2. Query representative public types and overloaded methods.
3. Trace high-value call chains across factories, registries, interceptors, serializers, persistence, networking, and concurrency.
4. Query the Rust counterparts and their callers/tests.
5. Refresh or re-query the module inventory once before implementation if the
   index reports staleness.

If no index exists, do not initialize one without authorization. Use language-aware tooling or targeted source inspection and disclose the weaker evidence.

Read [CodeGraph parity audit](references/codegraph-parity-audit.md) for query patterns and inventory rules.
Read [Case-study lessons](references/case-study-lessons.md) when designing a large utility-library migration or an annotation/macro split.

### 2. Build inventories before implementation

Create separate machine-readable or tabular inventories for:

- Java Maven/Gradle modules and Rust crates.
- Java packages and Rust module directories.
- Classes, interfaces, enums, records, annotations, exceptions, and relevant inner types.
- Public/protected constructors and methods, including every overload.
- Parameter names, order, generic bounds, nullability, defaults, varargs, checked exceptions, and return contracts.
- Examples, tests, fixtures, scripts, configuration, resources, service descriptors, and docs.
- Call paths and externally observable side effects.

Exclude `package-info`, generated sources, BOMs, aggregators, test support, facades, and Rust-only infrastructure only through explicit categories. Do not hide them by changing the denominator.

Freeze the inventory as the batch manifest before editing production code. It
must cover the complete denominator, dependency order, shared mechanisms,
component decisions, test disposition, and approved exceptions. Do not start
with one object and discover the rest while implementing.

Resolve `SKILL_DIR` to the directory containing this `SKILL.md`; never assume a
fixed installation or mount path. Run the following commands from the Rust
migration repository root and prefer repository-relative paths for project
inputs and generated artifacts.

Run the static Rust layout audit as an early signal:

```bash
python3 "$SKILL_DIR/scripts/audit_migration_layout.py" \
  --rust-root .
```

The script detects structural red flags; it does not prove Java/Rust semantic parity.

### 3. Create four documents for every source module

When documentation writes are authorized, generate a documentation directory for each Java module before implementation:

```bash
python3 "$SKILL_DIR/scripts/scaffold_migration_docs.py" \
  --module source-module \
  --java-root ../java-project/source-module \
  --rust-root crates/source_module \
  --output-dir docs/source-module \
  --java-baseline <sha-or-tag> \
  --rust-baseline <sha>
```

The command creates:

1. `迁移路线图.md` — scope, baselines, phases, dependencies, risks, and evidence gates.
2. `对象级对照表.md` — every Java object and its Rust file/type/status.
3. `语义迁移对照表.md` — every behavior family and its Rust-native implementation.
4. `对象名称一致性检查.md` — counts, missing/extra/merged objects, names, methods, parameters, and logic gaps.

Populate every placeholder from source evidence. Keep documents synchronized with code in the same change. Templates:

- [Migration roadmap](assets/templates/迁移路线图.md)
- [Object mapping](assets/templates/对象级对照表.md)
- [Semantic mapping](assets/templates/语义迁移对照表.md)
- [Name consistency audit](assets/templates/对象名称一致性检查.md)

Every document must show separate Java and Rust baselines, its last-audited date,
and a document status. Every migrated/verified row needs an evidence anchor:
source file or symbol, target file or symbol, test/oracle, exact command, and
artifact where applicable. During implementation, do not upgrade rows one at a
time. After the batch freeze, cross-check all four documents against the current
Rust SHA and update statuses in one consolidated pass. A later count table must
not silently contradict a technical-requirements document or an earlier semantic
gap.

### 4. Classify every object honestly

Use these states consistently:

| State | Meaning |
|---|---|
| `NOT_STARTED` | No Rust counterpart exists |
| `SKELETON` | Shape exists but behavior is absent or deliberately blocked |
| `IMPLEMENTED_UNVERIFIED` | Real logic exists but behavioral parity is not proven |
| `BEHAVIOR_VERIFIED` | Live/golden differential evidence passes, or an approved equivalent contract oracle proves the behavior |
| `JAVA_ONLY_EXEMPT` | JVM-specific behavior has an approved Rust replacement or exclusion |
| `PLANNED_BLOCKED` | Explicit external dependency blocks implementation |
| `RUST_EXTENSION` | Intentional Rust-only capability, excluded from Java parity numerator |

`SKELETON` and `PLANNED_BLOCKED` count as incomplete. API registration, compilation, file presence, or an empty method never upgrades them.

Allow a planned placeholder only when the user explicitly approves it. Isolate it by module/feature, name the dependency and owner, record exit criteria, keep it out of default facades, and exclude it from implemented/verified coverage.

For a blocked module, record the module-level exception as `PLANNED_BLOCKED`. Individual signature-only object rows inside it may be `SKELETON`; both states remain outside implementation and behavior numerators.

### 5. Decide component replacements from contracts

Do not map framework names directly. For every external Java component or framework subsystem:

1. Extract the behavior contract: API shape, wire/storage format, ordering, failure taxonomy, lifecycle, transactions, concurrency, cancellation, backpressure, security, observability, and deployment assumptions.
2. Choose a replacement shape: standard library, direct crate, wrapped crate, trait plus adapters, explicit registry/SPI, compile-time macro/code generation, application-host responsibility, or approved non-migration.
3. Check the common mapping table and candidate catalog as discovery starting points, never as automatic approval.
4. When no verified mapping fits, generate several English capability/protocol/constraint queries, search crates.io and companion primary sources, and shortlist five to ten candidates across std, direct crate, wrapper, trait/adapters, code generation, host responsibility, and exclusion shapes.
5. Route crates.io metadata collection and ecosystem-health comparison to `rust-crate-discovery` when available. Apply migration-specific contract and compatibility gates here; its numeric health score does not select the replacement.
6. Reject candidates that fail a required contract, license, MSRV/target, runtime/blocking, protocol, security, maintenance/ownership, or dependency-graph constraint before scoring.
7. Compare viable candidates using semantic fit, maintenance, adoption, docs/tests, project compatibility, security/supply chain, maturity, cost, and exit strategy. Interpret downloads, reverse dependencies, stars, release recency, and commits as contextual signals, not proof.
8. Spike the highest-risk semantic path for the top candidates before committing the architecture.
9. Record search queries and date, ownership, version/features, per-dimension evidence/confidence, rejected alternatives, escape hatch, and rollback plan.
10. Promote the decision only through explicit evidence states; a manifest entry or highest score is not semantic verification.

For multiple target frameworks, define a framework-neutral contract and thin adapters, then run one shared conformance suite against every adapter. Keep runtime traits/types separate from thin procedural macros and generated code.

Read [Component replacement decision SOP](references/component-replacement-sop.md), [crate replacement discovery and evaluation](references/crate-replacement-discovery.md), and [Component candidate catalog](references/component-candidate-catalog.md) before choosing or approving a third-party replacement. The catalog is discovery input, never an approval list; re-verify release, maintenance, license, MSRV, targets, advisories, unsafe/build-script surface, and required contracts at decision time.

### 6. Complete the declared batch in one semantic implementation pass

Read [Layout and migration rules](references/layout-and-governance.md) and
[Semantic mappings](references/semantic-mappings.md) before changing code. Then
execute the entire frozen batch without object-level acceptance pauses:

1. Establish the target module tree, shared errors, traits, registries, adapters,
   serialization rules, concurrency model, and dependency boundaries once.
2. Implement every mapped Java object and operation in dependency order. Keep
   exactly one primary `.rs` file per Java object and real logic in the
   corresponding object or explicit collaborator files.
3. Copy and translate JavaDoc semantics into Chinese Rust doc comments across
   the batch. Preserve parameter, default, nullability, error, side-effect,
   ordering, lifecycle, and concurrency intent.
4. Implement all mapped overload variants, examples, fixtures, source-test
   counterparts, Rust-specific obligations, and risk-driven tests as batch
   artifacts, but do not execute validation yet.
5. Maintain one deferred-issues ledger. Continue through local uncertainties;
   pause only for a blocker that changes the frozen public contract,
   architecture, dependency policy, or authorized scope.
6. When every non-exempt manifest row has real implementation, freeze the Rust
   batch. Only then update the four documents in bulk and enter audit.

During this pass, do **not** run `cargo check`, tests, Clippy, coverage,
differential comparison, per-object CodeGraph re-queries, or per-object
completion reviews. Do not report an object as accepted merely because its file
was edited. Recovery commits are allowed, but they are not verification gates.

### 7. Preserve naming and overload intent

- Use `snake_case` for Rust directories, files, methods, and parameters.
- Use `PascalCase` for Rust types.
- Map `loadOrCreateAgentState(slotKey)` to `load_or_create_agent_state(slot_key)`.
- Preserve the last meaningful Java package level as the Rust subdirectory.
- Keep `lib.rs` and `mod.rs` as declarations and re-exports only.
- Keep one Java class/interface/enum/record per Rust file; an inner builder tightly owned by the primary type may remain with it.
- Record every intentional rename in both object and name-consistency documents.

Rust has no method overloading. Keep one canonical snake_case name only when the signatures have one semantic operation. Give additional variants stable semantic suffixes such as `_with_charset`, `_into`, or `_from_reader`; record the exact Java signature mapped to each Rust function. Never collapse overloads that differ in defaults, validation, side effects, or error behavior.

### 8. Translate mechanisms, not frameworks literally

Use this table as a common starting point, then verify the exact contract and
current crate evidence:

| Java responsibility | Rust starting point |
|---|---|
| Jackson JSON annotations/modules | `serde`, `serde_json`, project-owned custom serializers |
| Jackson XML / JAXB-style XML | `quick-xml` plus explicit namespace, attribute, mixed-content, and ordering logic |
| `null`, checked exceptions | `Option<T>`; typed `thiserror` enums and `Result` |
| SLF4J/Logback/MDC | `tracing`, `tracing-subscriber`, explicit field/context propagation and redaction |
| `synchronized` / `ConcurrentHashMap` | ownership first; then std `Mutex`/`RwLock` or `DashMap` when the access pattern warrants it |
| `CompletableFuture`, scheduled executors | async futures, supervised Tokio tasks, cancellation tokens, timers/intervals; select a scheduler crate only for richer contracts |
| Reactor `Mono<T>` / `Flux<T>` | `async fn -> Result<T, E>`; bounded `Stream<Item = Result<T, E>>` |
| OkHttp / Apache HttpClient | `reqwest` for high-level clients; Hyper for protocol-level control; verify TLS, proxy, pool, redirect, retry, and streaming semantics |
| Spring MVC/WebFlux / JAX-RS | framework-neutral core plus approved Axum, Actix Web, Poem, or other thin host adapters |
| JDBC/JPA/MyBatis | SQLx, Diesel, SeaORM, RBatis, or another verified data layer selected by query, mapping, transaction, migration, and runtime contracts |
| Caffeine/Guava cache | Moka or a project-owned cache; verify eviction, TTL/TTI, loading, invalidation, and concurrency |
| Jedis/Lettuce | `redis`; verify cluster/sentinel, reconnect, pipeline/transaction, TLS, and async behavior |
| Kafka/RabbitMQ/Pulsar/NATS/MQTT | protocol-specific client such as `rdkafka`, Lapin, `pulsar`, `async-nats`, or `rumqttc`; require real-broker semantics and recovery tests |
| Protobuf / gRPC | Prost; Tonic plus Prost for gRPC |
| Bean Validation | `validator` or project-owned validation, kept separate from framework extractors |
| `java.time`, UUID/ULID, `BigDecimal`, regex | `time`/`chrono`, `uuid`/`ulid`, `rust_decimal`/`bigdecimal`, `regex`; choose representations and compatibility before crate preference |
| `.properties`, YAML, TOML, configuration binding | `java-properties`, `serde_yaml_ng`, `toml`, or a verified configuration crate plus project-owned precedence/profile rules |
| Apache Commons/Hutool general utilities | std first, then focused crates such as `url`, `bytes`, `regex`, `base64`, or `hex`; do not seek one umbrella crate by name |
| Micrometer/OpenTelemetry/Prometheus | `metrics`, OpenTelemetry ecosystem, Prometheus exporters, and `tracing` integration; preserve names, labels, cardinality, context, and shutdown |
| JavaMail | `lettre`; verify MIME, attachment, TLS/authentication, retry, and delivery reporting |
| JWT/passwords/general crypto | `jsonwebtoken`, `argon2`, and focused RustCrypto crates; select algorithms/formats from the security contract, never from convenience alone |
| Groovy/Nashorn/embedded scripts | `rhai`, `boa_engine`, `mlua`, PyO3, or Wasmtime according to language, sandbox, resource-limit, threading, and packaging requirements |
| Apache POI/document formats | format-specific crates such as `rust_xlsxwriter`, `calamine`, `docx-rs`, `printpdf`, or `lopdf`; validate actual Office/PDF fixtures and unsupported features |
| ServiceLoader/SPI | explicit registry first; `inventory` only when link-time registration is required |
| Spring IoC/AOP/runtime annotations | constructors/builders, traits, middleware, registries, wrappers; use macros only for compile-time behavior |
| FreeMarker / Velocity / compile-time views | Tera / Handlebars; Askama for compile-time templates; maud for Rust-native markup |
| Lombok data boilerplate | standard derives plus invariant-preserving APIs/builders; evaluate `lombok-macros` only against the generated API contract |
| JUnit/Testcontainers | Rust unit/integration tests; `testcontainers` for disposable real dependencies |
| JNI/manual Swift/Kotlin/Python bindings | UniFFI when its supported type/error/async model fits; shipping and packaging remain separate work |

Prefer composition of mature Rust crates over recreating a Java all-in-one implementation, but retain the source project's observable facade when compatibility requires it.

### 9. Extract annotation behavior behind a stable macro boundary

Do not place procedural macro entry points in a normal runtime crate. Use:

```text
project-core      # runtime traits, types, errors, and generated-code contract
project-macros    # thin proc-macro entry points and syntax parsing
project-web-*     # framework adapters that may re-export approved macros
```

Use `-derive` only for a derive-only public surface; use `-macros` for attribute/function-like or mixed macros, unless the existing crate family has a deliberate established spelling. Keep generated code dependent on public runtime APIs, not proc-macro internals. Test expansion success, compile failures, generics, visibility, renamed dependencies, and each framework re-export.

Java runtime annotations do not automatically become Rust macros. Use middleware, traits, registries, or explicit builders when runtime state and dynamic dispatch own the behavior.

### 10. Audit once, then verify the complete batch

After the implementation freeze, execute the applicable ladder for the whole
declared batch:

1. Run one consolidated CodeGraph/static parity audit over all objects, files,
   exact signatures, parameters, overloads, call paths, dynamic boundaries,
   examples, tests, docs, and placeholders. Reconcile all four documents in one
   pass.
2. Run Rust formatting, check, unit, doc, integration, Clippy, feature, target,
   and platform gates as one unified engineering suite.
3. Run every ported/mirrored Java contract test, clearly labeled as
   non-differential evidence.
4. Run the complete Java golden exporter or live Java/Rust differential suite
   over the same deterministic cases.
5. Replay the complete set of real user scripts and examples against both
   implementations.
6. Run concurrency acceptance for ordering, cancellation, backpressure, races,
   shutdown, and Loom/model properties where useful.
7. Run load/stability tests for throughput, latency percentiles, memory,
   handles/tasks, reconnects, and soak.
8. Run security property tests, malformed-input suites, `cargo-fuzz`, unsafe
   review, dependency advisories, and secret-redaction checks.
9. Run real business-host integration with databases, networks, files,
   frameworks, and deployment topology.
10. Run the gray rollout and rollback drill with recorded recovery time and
    state compatibility.

When a gate fails, group failures by shared subsystem or root cause, repair the
batch, and rerun the affected consolidated gate plus downstream invalidated
gates. Never fall back to migrate-compare-test one object at a time.

Read [Verification and acceptance](references/verification-and-acceptance.md) for evidence design and use `rust-java-migration-testing` for the three-ledger testing SOP.

### 11. Report completion without inflating coverage

Report separately:

- Structural coverage: objects/files/method signatures registered.
- Implementation coverage: non-stub logic present.
- Behavioral coverage: distinguish mirrored contracts, golden differential, live differential, and approved equivalent oracles.
- Test coverage: migrated Java tests and Rust-native tests passing.
- Integration coverage: real hosts/dependencies exercised.
- Production readiness: load, security, observability, rollout, and rollback verified.

Include exact commands, SHAs, test counts, failures, exceptions, and unverified boundaries. Never call a migration complete because code compiles or a parity manifest reaches 100%.

## Red Lines

- Do not define many migrated objects in `lib.rs`, `mod.rs`, or `compat.rs`.
- Do not delegate every object to one `compat.rs` implementation.
- Do not use empty bodies, `todo!()`, or `unimplemented!()` as completed migration.
- Do not delete or simplify working migrated behavior to make counts align.
- Do not use wildcard imports in production migration code.
- Do not silently merge several Java objects into one Rust file.
- Do not replace overloaded behavior with one lossy convenience function.
- Do not call a declared dependency, successful compile, or isolated POC a verified component replacement.
- Do not promote a component copied from a research list or local convention document to “selected” without current hard-filter and contract evidence.
- Do not call a Rust test copied from a Java test a differential test unless both implementations or Java-produced golden artifacts participate.
- Do not mark a row behavior-verified from file counts, parser acceptance, generic `is_ok()`/`is_err()`, or “at least one test per object”.
- Do not let the four migration documents carry different baselines or contradictory completion states.
- Do not claim real testing when only mocks, compilation, or static inspection ran.
- Do not edit reference source repositories while extracting patterns.
- Do not alternate migration, comparison, and testing for each object, file, or
  method.
- Do not run object-scoped acceptance during the semantic implementation pass;
  finish the frozen batch before consolidated audit and unified verification.
- Do not convert recovery commits or local edit milestones into completion
  checkpoints.

## Completion Criteria

- Four current documents exist for every in-scope source module, share pinned baselines, and record their last audit against the current Rust SHA.
- Every Java object, method, overload, and parameter has a disposition.
- Every exception and Rust extension is categorized and excluded from misleading denominators.
- Production Rust files satisfy layout, documentation, import, and no-stub rules.
- The complete declared batch was implemented before any acceptance gate ran.
- One consolidated post-implementation parity audit covers the full frozen
  denominator; no object-by-object verification loop was used.
- High-value call chains have source-linked semantic mappings.
- Applicable differential, replay, concurrency, load, fuzz, host, and rollback gates have evidence or explicit open gaps.
- The final report separates structural, implementation, behavioral, integration, and production-readiness claims.
