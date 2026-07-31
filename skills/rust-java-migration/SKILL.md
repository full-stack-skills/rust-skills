---
name: rust-java-migration
description: Plan, execute, audit, and verify behavior-preserving migrations from Java Maven or Gradle projects to Rust Cargo workspaces. Use when comparing Java and Rust repositories at module, package, object, file, method, parameter, documentation, example, test, dependency-reuse, JavaBean getter/setter or script-property compatibility, concurrency, or runtime-behavior level; preserving Java semantics in Chinese Rust documentation; selecting exact Rust dependency replacements; producing one detailed four-document set per source module; or continuing an incomplete port without deleting existing work. Enforces source-authoritative object boundaries, idiomatic Rust APIs with explicit ADAPTED compatibility layers, one Java object per real Rust file, strict non-completion states, evidence-backed dependency reuse/platform exclusions, a frozen full inventory, consolidated audit, and unified verification.
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
- Exact Java module package root used for path mapping; do not pass only a
  repository or `src/main/java` root and then guess which package segments to strip.
- Rust repository path, baseline commit, toolchain/MSRV, workspace, and target platforms.
- Compatibility goal: source-shape parity, public API parity, behavior parity, or production replacement.
- Dependency policy: license, MSRV, supported targets, unsafe policy, advisory policy, maintenance horizon, and acceptable transitive cost.
- Component-candidate sources and their observation date; distinguish team policy, researched candidates, declared dependencies, and verified adoption.
- Explicit exceptions, blocked external projects, unsupported JVM-only features, and completion deadline.
- Required host applications, real scripts, test data, concurrency model, load profile, and rollback mechanism.
- Existing migration documents and their authority; identify the single current
  four-document set before creating or merging historical material.

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
- For every object, the deterministic expected Rust path after removing the
  organization/module package root and retaining the final two remaining package
  segments (or one/zero when fewer remain).
- Public/protected constructors and methods, including every overload.
- Parameter names, order, generic bounds, nullability, defaults, varargs, checked exceptions, and return contracts.
- Existing object, constructor, method, generic/value parameter, return,
  exception, metadata-tag, and semantic inline comments, with source anchors.
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
  --java-package-root ../java-project/source-module/src/main/java/org/example/module \
  --rust-root . \
  --retain-segments 2 \
  --require-source-comments \
  --fail-on-warning
```

The script calculates expected paths and distinguishes missing from misplaced
objects. It also detects non-snake-case paths, multi-object files, facade
definitions, wildcard imports, stub macros/panics, empty function bodies, and
missing Chinese source comments. Any strict blocker keeps migration completion
blocked; a clean scan still does not prove Java/Rust semantic parity.

### 3. Create four documents for every source module

When documentation writes are authorized, generate a documentation directory for each Java module before implementation:

```bash
python3 "$SKILL_DIR/scripts/scaffold_migration_docs.py" \
  --module source-module \
  --java-root ../java-project/source-module \
  --java-package-root ../java-project/source-module/src/main/java/org/example/module \
  --rust-root crates/source_module \
  --output-dir docs/source-module \
  --java-baseline <sha-or-tag> \
  --rust-baseline <sha> \
  --retain-segments 2
```

The command creates:

1. `迁移路线图.md` — scope, baselines, phases, dependencies, risks, and evidence gates.
2. `对象级对照表.md` — every Java object and its Rust file/type/status.
3. `语义迁移对照表.md` — every behavior family and its Rust-native implementation.
4. `对象名称一致性检查.md` — counts, missing/extra/merged objects, names, methods, parameters, and logic gaps.

Populate every placeholder from source evidence. A generated template is
`DRAFT`, not evidence and never completion. Keep documents synchronized with
code in the same change. Templates:

- [Migration roadmap](assets/templates/迁移路线图.md)
- [Object mapping](assets/templates/对象级对照表.md)
- [Semantic mapping](assets/templates/语义迁移对照表.md)
- [Name consistency audit](assets/templates/对象名称一致性检查.md)

Every one of the four documents must be independently detailed and must contain
the module's current migration contract: source/Rust SHAs, exact object
denominator, target root, `retain_segments = 2`, status snapshot, strict
completion rules, and that document's responsibility. Reject a title-only,
count-only, or placeholder-only document. As an anti-summary floor, require at
least three substantive level-2 sections plus an evidence table or task matrix;
use a repository-configured size floor (45 nonblank lines by default) while
allowing a proportionally smaller generated object table for a genuinely tiny
module.

Every document must show separate Java and Rust baselines, its last-audited date,
and a document status. Every migrated/verified row needs an evidence anchor:
source file or symbol, target file or symbol, test/oracle, exact command, and
artifact where applicable. During implementation, do not upgrade rows one at a
time. After the batch freeze, cross-check all four documents against the current
Rust SHA and update statuses in one consolidated pass. A later count table must
not silently contradict a technical-requirements document or an earlier semantic
gap.

Keep exactly one current four-document set at the module root. Do not leave
`*-历史详细版.md` or a second `history/**/<current-name>.md` beside it. Merge
useful old package grouping, design context, and decision history into a clearly
delimited “历史设计附录” in the corresponding current document. The generated
current-fact region must remain first and regeneration must preserve the
appendix. Old counts, paths, statuses, tests, and completion marks never override
current facts.

Treat scaffold `--force` as destructive and use it only for a disposable,
untouched `DRAFT`; never use it to merge or refresh a populated current
document. Merge historical details into the current document in place and
preserve both its generated fact region and existing appendix.

### 4. Classify every object honestly

Use these object states consistently. Keep verification levels (`V0`–`V7`)
separate; do not invent a friendlier state or translate a test result directly
into an object state.

| State | Meaning |
|---|---|
| `MISSING` | Expected Rust object file does not exist |
| `MISPLACED` | Same-name file/type exists but not at the deterministic expected path |
| `STUB` | Shape or placeholder exists but real behavior is absent |
| `PARTIAL` | Real behavior exists but methods, callbacks, errors, ordering, lifecycle, or integration semantics are incomplete |
| `UNVERIFIED` | File/logic exists but source comments, object boundary, or semantic test evidence is insufficient |
| `IMPLEMENTED` | Expected path, one-object boundary, real complete logic, Chinese source semantics, and current semantic tests all exist |
| `DEPENDENCY_REUSED` | A pinned dependency provides the exact capability; crate/version or commit, upstream symbol, adapter, and local integration test are recorded |
| `PLATFORM_NA` | The capability is genuinely JVM/bytecode/class-loader/platform-only and explicit evidence records why no Rust object applies |
| `RUST_EXTENSION` | Intentional Rust-only capability, excluded from Java parity numerator |

Only `IMPLEMENTED`, `DEPENDENCY_REUSED`, and `PLATFORM_NA` count as handled
source objects. `MISSING`, `MISPLACED`, `STUB`, `PARTIAL`, and `UNVERIFIED` are
incomplete. `RUST_EXTENSION` never enters the Java denominator.

Allow a planned placeholder only when the user explicitly approves it. Record
the blocker in the roadmap, but keep each affected object in its factual
`MISSING` or `STUB` state. A blocker is metadata, not a completion-like object
state.

Never upgrade from `MISSING` merely because an object name appears in a manifest,
facade, `lib.rs`, `mod.rs`, re-export, generated registry, or compatibility
module. Never upgrade from `UNVERIFIED` merely because `cargo test` is green.

### 5. Decide component replacements from contracts

Do not map framework names directly. For every external Java component or framework subsystem:

The Java source module remains authoritative for object names, package
structure, and public contracts. A Rust dependency is only an implementation
reuse boundary. Do not restructure the migration around the dependency's file
tree and do not copy dependency-owned implementations into local files merely
to improve parity counts. For AOP-like work, for example, Spring defines the
Advice/Interceptor/Advisor object inventory while an aspect crate may satisfy
specific runtime symbols through `DEPENDENCY_REUSED`.

1. Extract the behavior contract: API shape, wire/storage format, ordering, failure taxonomy, lifecycle, transactions, concurrency, cancellation, backpressure, security, observability, and deployment assumptions.
2. Choose a replacement shape: standard library, direct crate, wrapped crate, trait plus adapters, explicit registry/SPI, compile-time macro/code generation, application-host responsibility, or proven `PLATFORM_NA`.
3. Check the common mapping table and candidate catalog as discovery starting points, never as automatic approval.
4. When no verified mapping fits, generate several English capability/protocol/constraint queries, search crates.io and companion primary sources, and shortlist five to ten candidates across std, direct crate, wrapper, trait/adapters, code generation, host responsibility, and exclusion shapes.
5. Route crates.io metadata collection and ecosystem-health comparison to `rust-crate-discovery` when available. Apply migration-specific contract and compatibility gates here; its numeric health score does not select the replacement.
6. Reject candidates that fail a required contract, license, MSRV/target, runtime/blocking, protocol, security, maintenance/ownership, or dependency-graph constraint before scoring.
7. Compare viable candidates using semantic fit, maintenance, adoption, docs/tests, project compatibility, security/supply chain, maturity, cost, and exit strategy. Interpret downloads, reverse dependencies, stars, release recency, and commits as contextual signals, not proof.
8. Spike the highest-risk semantic path for the top candidates before committing the architecture.
9. Record search queries and date, ownership, version/features, per-dimension evidence/confidence, rejected alternatives, escape hatch, and rollback plan.
10. Promote an object to `DEPENDENCY_REUSED` only when the exact upstream symbol,
    pinned dependency evidence, adapter boundary, and local integration test are
    all recorded. “The ecosystem has it” or “semantically similar” remains
    `UNVERIFIED`.

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
   the batch. Migrate every existing object comment, constructor/method comment,
   generic and value `@param`, `@return`, `@throws`, `@since`, `@deprecated`,
   relevant `@see`, and semantic inline comment without omission. Preserve the
   parameter-specific contracts. Keep Java-to-Rust name, signature, and exception
   mappings in the four migration documents; keep generated Rust documentation
   Rust-native.
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

Read [Comment migration contract and example](references/comment-migration.md)
before migrating documentation. Treat missing source comments as migration gaps,
not optional cleanup.

### 7. Preserve naming and overload intent

- Use `snake_case` for Rust directories, files, methods, and parameters.
- Use `PascalCase` for Rust types.
- Map `loadOrCreateAgentState(slotKey)` to `load_or_create_agent_state(slot_key)`.
- Remove the organization and declared source-module package root, then retain
  exactly the final two remaining package segments. Retain one when only one
  remains and place root-package objects at the crate root. Example:
  `factory/xml/support/Foo.java` → `xml/support/foo.rs`;
  `propertyeditors/PatternEditor.java` → `propertyeditors/pattern_editor.rs`.
- Keep `lib.rs` and `mod.rs` as declarations and re-exports only.
- Keep one Java class/interface/enum/record per Rust file; an inner builder tightly owned by the primary type may remain with it.
- Record every intentional rename in both object and name-consistency documents.

Rust has no method overloading. Keep one canonical snake_case name only when the signatures have one semantic operation. Give additional variants stable semantic suffixes such as `_with_charset`, `_into`, or `_from_reader`; record the exact Java signature mapped to each Rust function. Never collapse overloads that differ in defaults, validation, side effects, or error behavior.

Apply the local `rust-api-design` conventions to every migrated public Rust
surface. Do not mechanically translate JavaBean accessors: prefer `name()` over
`get_name()` (except genuine lookup operations), `set_name(value)` for controlled
mutation, `name_mut()` only when it cannot bypass invariants,
`into_name()`/`into_inner()` for ownership transfer, semantic boolean predicates,
and chainable builders. Use `as_`/`to_`/`into_`, `From`/`TryFrom`/`AsRef` and
`IntoIterator` by their Rust meanings; do not use `Deref` to emulate Java
inheritance. Expose fields directly only when invariants and API evolution permit
it. Preserve validation, visibility, side effects, exceptions, synchronization,
and lazy-computation behavior.

When a script, expression engine, serializer, reflection facade, or other
compatibility surface exposes Java property semantics, keep the Rust API
idiomatic and implement the old field/getter/setter behavior in an explicit
registry or member resolver. Record this relationship as mapping form
`ADAPTED`; this is orthogonal to completion status and still requires
`IMPLEMENTED`, `UNVERIFIED`, or another factual state.

Read [Rust API and JavaBean property adaptation](references/rust-api-adaptation.md)
before migrating getters, setters, builders, or script-visible properties.

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
   examples, tests, docs, and placeholders. Compare the complete Java comment
   inventory with Rust object, method, parameter, return, error, metadata, and
   inline comments. Reconcile all four documents in one pass.
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
- Do not create `get_*` methods solely to mirror JavaBean spelling when an
  idiomatic Rust method plus an explicit compatibility adapter preserves the
  contract.
- Do not treat an idiomatic Rust getter/setter as sufficient when scripts or
  dynamic member access still require Java field/getter/setter resolution.
- Do not call a declared dependency, successful compile, or isolated POC a verified component replacement.
- Do not use a replacement dependency's package/file layout as the target object
  inventory; source Java objects and the deterministic path rule remain authoritative.
- Do not mark a semantically similar dependency as `DEPENDENCY_REUSED` without
  pinned crate/commit, exact source symbol, adapter evidence, and local integration tests.
- Do not use `PLATFORM_NA` for work that is merely difficult or missing; require
  JVM/bytecode/class-loader/platform-specific evidence.
- Do not promote a component copied from a research list or local convention document to “selected” without current hard-filter and contract evidence.
- Do not call a Rust test copied from a Java test a differential test unless both implementations or Java-produced golden artifacts participate.
- Do not mark a row behavior-verified from file counts, parser acceptance, generic `is_ok()`/`is_err()`, or “at least one test per object”.
- Do not let the four migration documents carry different baselines or contradictory completion states.
- Do not keep a current document and a `-历史详细版`/nested duplicate. Merge
  useful history into the current document after the generated fact region.
- Do not replace or delete the generated current-fact region while merging old
  documentation, and do not let regeneration discard the merged appendix.
- Do not claim real testing when only mocks, compilation, or static inspection ran.
- Do not edit reference source repositories while extracting patterns.
- Do not alternate migration, comparison, and testing for each object, file, or
  method.
- Do not run object-scoped acceptance during the semantic implementation pass;
  finish the frozen batch before consolidated audit and unified verification.
- Do not convert recovery commits or local edit milestones into completion
  checkpoints.
- Do not omit an existing Java object, constructor, method, parameter, return,
  exception, lifecycle, thread-safety, deprecation, or semantic inline comment.
- Do not replace specific source documentation with generic prose such as
  “processes the request” or claim comment parity from `cargo doc` alone.
- Do not write `对应 Java` in parameter, return, error-variant, field, or inline
  comments. Limit optional source anchors to the migrated Rust type and
  constructor/method documentation; keep detailed correspondence in the four
  migration documents.

## Completion Criteria

- Four detailed current documents exist for every in-scope source module, share
  pinned baselines and one module-specific migration contract, and record their
  last audit against the current Rust SHA; no parallel historical copy exists.
- Every object has a deterministic expected path using the final-two-segments
  algorithm, and `MISPLACED` objects remain incomplete until physically aligned.
- Every Java object, method, overload, and parameter has a disposition.
- Every dependency reuse, platform exclusion, blocker, exception, and Rust
  extension has precise evidence and is excluded from misleading denominators.
- Production Rust files satisfy layout, documentation, import, and no-stub rules.
- Every source-documented Java object, constructor, method, generic/value
  parameter, return, exception, metadata tag, and semantic inline comment has a
  traceable Rust documentation counterpart.
- The complete declared batch was implemented before any acceptance gate ran.
- One consolidated post-implementation parity audit covers the full frozen
  denominator; no object-by-object verification loop was used.
- High-value call chains have source-linked semantic mappings.
- Applicable differential, replay, concurrency, load, fuzz, host, and rollback gates have evidence or explicit open gaps.
- The final report separates structural, implementation, behavioral, integration, and production-readiness claims.
