---
name: rust-java-migration
license: Apache-2.0
description: Plan, execute, audit, and verify behavior-preserving migrations from Java Maven or Gradle projects to project-shaped Rust Cargo workspaces, including derived crate boundaries, scale-appropriate topology, 100% lossless source-test/case migration, byte-identical test assets, and complete per-case differential parity. Use when comparing repositories at module, package, object, file, method, parameter, documentation, example, test, fixture/data, dependency-reuse, JavaBean/script-property, concurrency, runtime-behavior, oversized Rust-file, or test-organization level; producing migration documents; continuing an incomplete port; or repairing workspace drift. Enforces source-authoritative inventories, Rust-native APIs, a 500-line cohesion-review threshold and 800-line authored-file blocker, idiomatic unit/integration test placement, strict non-completion states, frozen baselines, and unified verification.
---

# Java to Rust Migration

Migrate contracts and observable behavior, not Java syntax. Preserve the Java project's public concepts and source traceability while selecting Rust-native ownership, error, concurrency, async, serialization, and framework mechanisms.

## Mandatory migration layout

- Derive the Rust directory from the Java package after the declared package root; preserve meaningful nested packages and never flatten, cross-place, or double-nest them.
- Convert the Java object name to acronym-aware `snake_case.rs`; keep the Rust type in `PascalCase` and do not add suffixes such as `_trait`.
- Keep one Java object as one Rust object boundary. Rust defines no universal file-length limit: treat up to 500 physical lines as normal, review 501–800 lines for cohesion, and block authored `.rs` files above 800 lines.
- Split only when a file mixes responsibilities. Retain one primary object file and use subordinate files for coherent implementation families without introducing a second migrated object; record every split or reviewed exception.
- Keep `lib.rs` and `mod.rs` to declarations and re-exports. Update parent modules after moves and qualify ambiguous external re-exports with `::`.
- Keep focused private-behavior unit tests in `#[cfg(test)]` modules when useful. Put public-boundary, cross-module, differential, host, and whole-project tests under `tests/` or a non-published `<project>-test` package; keep source fixtures under `<project>-test/tests/fixtures/`.

Read [Directory path alignment](references/directory-path-alignment.md) and [Layout and governance](references/layout-and-governance.md), then run the layout audit after moves.

## Scope and Routing

Use this skill for full-project migrations, one Maven/Gradle module, parity audits, migration planning, or continuation of an existing Rust port.

This is the Rust adapter of the [cross-language migration profile](references/cross-language-migration-profile.md). Route crate/layout/API, dependency, macro, and domain mechanics to the corresponding Rust skills. Route verification to `rust-java-migration-testing` plus relevant test skills.

Do not modify migration code when the user requested only an audit, plan, or documentation. A plan-only or read-only request does not authorize running a write-producing document scaffolder: return the proposed four-document content in the response, use `--dry-run`, or write only to a user-approved destination. Do not broaden a module migration into a repository rewrite without authorization.

## Required Inputs

Resolve or explicitly mark unknown:

- Java repository path, baseline commit/tag, build tool, JDK, and module scope.
- Exact Java module package root used for path mapping; do not pass only a repository or `src/main/java` root and guess which segments to strip.
- Rust repository path, baseline commit, toolchain/MSRV, workspace, and target platforms.
- Target-product topology inputs: independently published Rust units, dependency/feature/target/proc-macro/FFI boundaries, expected crate count, package families, root noise, other languages, and established paths.
- Compatibility goal: source-shape parity, public API parity, behavior parity, or production replacement.
- Dependency policy: license, MSRV, supported targets, unsafe policy, advisory policy, maintenance horizon, and acceptable transitive cost.
- Component-candidate sources and their observation date; distinguish team policy, researched candidates, declared dependencies, and verified adoption.
- Explicit exceptions, blocked external projects, unsupported JVM-only features, and completion deadline.
- Required host applications, real scripts, test data, concurrency model, load profile, and rollback mechanism.
- Existing migration documents and their authority; identify the single current four-document set before merging historical material.
- Complete source test roots/runner configuration, including every concrete test case, disabled test, fixture, script, corpus, golden file, resource, and data file. The source repository defines the denominator; do not narrow it to fit Rust.

Never silently infer that the newest branch, a generated manifest, or an API registration list is the behavioral baseline.

## Workflow

Treat one declared Java source module and its Rust target crate/module as the default migration batch. A user-authorized multi-module scope may be one batch, but freeze its boundary before implementation. Apply: freeze scope/contracts → implement the batch → freeze → audit → unified verification.

Dependency-ordered editing inside the implementation batch is allowed. Per-object completion loops are not.

### 1. Freeze baselines and inspect repository state

Record both repository SHAs, dirty worktrees, Java/Rust toolchains, module manifests, enabled features, and generated-code boundaries. Preserve existing Rust work and unrelated changes.

Verify the Rust toolchain satisfies the workspace MSRV: an older default rustc fails with `rustc X is not supported by the following packages` — run gates via `rustup run <ver> cargo ...`, never silently lower `rust-version`.

If a repository contains `.codegraph/`, use CodeGraph before text search or file-by-file reading:

1. Survey module/package/crate architecture.
2. Query representative public types and overloaded methods.
3. Trace high-value call chains across factories, registries, interceptors, serializers, persistence, networking, and concurrency.
4. Query the Rust counterparts and their callers/tests.
5. Refresh or re-query the module inventory before implementation if the index reports staleness.

If no index exists, do not initialize one without authorization. Use language-aware tooling or targeted source inspection and disclose the weaker evidence.

Read [CodeGraph parity audit](references/codegraph-parity-audit.md) for query patterns and inventory rules.
Read [Case-study lessons](references/case-study-lessons.md) when designing a large utility-library migration or an annotation/macro split.

### 1.5. Derive Rust crate boundaries and workspace topology

Do not map Maven/Gradle modules one-to-one to Cargo packages. Derive Rust packages from independent publishing/reuse, dependency/feature/target isolation, proc-macro or FFI constraints, and distinct lifecycles; source modules remain traceability scopes.

Select placement with `rust-workspace`: small cohesive results are normally root-flat; real adapter/binding/example/test families support a hybrid; large, root-heavy, or multi-language repositories may use `crates/`. Counts are review triggers, not laws. Record the source-module-to-crate mapping, chosen topology, rejected alternatives, and compatibility plan in the roadmap. See [Layout and governance](references/layout-and-governance.md).

### 2. Build inventories before implementation

Create separate machine-readable or tabular inventories for:

- Java Maven/Gradle modules and Rust crates.
- The source-module-to-crate mapping and why root-flat, hybrid, or contained/grouped paths fit this project.
- Java packages and Rust module directories.
- Classes, interfaces, enums, records, annotations, exceptions, and relevant inner types.
- For every object, the deterministic Rust path after removing the organization/module package root and retaining the final two remaining segments (or one/zero when fewer remain).
- Public/protected constructors and methods, including every overload.
- Parameter names, order, generic bounds, nullability, defaults, varargs, checked exceptions, and return contracts.
- Existing object, constructor, method, generic/value parameter, return, exception, metadata-tag, and semantic inline comments, with source anchors.
- Examples, tests, fixtures, scripts, configuration, resources, service descriptors, and docs.
- A source-test case manifest and asset manifest; record every concrete case and asset path/hash before copying resources byte-for-byte into Rust.
- A non-published `<project>-test` package owning project-level source replay, cross-component paths, and differential acceptance.
- Call paths and externally observable side effects.

Exclude `package-info`, generated sources, BOMs, aggregators, test support, facades, and Rust-only infrastructure only through explicit categories. Do not hide them by changing the denominator.

Freeze the inventory as the batch manifest before production edits. Cover the complete denominator, dependency order, shared mechanisms, component decisions, test disposition, and approved exceptions; do not discover scope object-by-object.

Resolve `SKILL_DIR` from this `SKILL.md`; never assume a fixed install path. Run commands from the Rust migration root and prefer repository-relative inputs/artifacts.

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
missing Chinese source comments. Record an approved 501–800-line cohesion review
with repeated `--reviewed-large-file path/to/file.rs`; this never exempts a file
above 800 lines. Any strict blocker keeps migration completion blocked; a clean
scan still does not prove Java/Rust semantic parity.

### 3. Create four documents for every source module

When documentation writes are authorized, generate a documentation directory for each Java module before implementation:

```bash
python3 "$SKILL_DIR/scripts/scaffold_migration_docs.py" \
  --module source-module \
  --java-root ../java-project/source-module \
  --java-package-root ../java-project/source-module/src/main/java/org/example/module \
  --rust-root <selected-target-crate-or-workspace> \
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

Read [Layout and migration rules](references/layout-and-governance.md),
[Directory path alignment patterns and error catalog](references/directory-path-alignment.md),
and [Semantic mappings](references/semantic-mappings.md) before changing code. Then
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
   artifacts, but do not execute validation yet. Preserve 100% of source test
   inputs, assertions, error expectations, state, side effects, and cleanup.
   Copy source test files/data/resources without editing them; put any
   Rust-specific derivatives in separate files.
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
- Treat 500 physical lines as a cohesion-review threshold and 800 as the authored-file blocker. Split by responsibility rather than line ranges; no subordinate file may introduce another migrated object.
- Enable `clippy::too_many_lines` as a function/method review signal at its 100-line default; refactor long routines when they combine distinct responsibilities.
- Use Rust's idiomatic test organization: colocate focused unit tests in `#[cfg(test)]` modules, and place public-boundary, cross-module, differential, host, and whole-project tests in `tests/` or a test/testkit package.
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
4. Run the complete pinned Java suite and the complete Rust lossless-port suite,
   then run the complete Java golden exporter or live Java/Rust differential
   suite over every concrete source case. Require both suites to pass and every
   case to report `MATCH`; zero mismatches, harness failures, and not-run cases.
   Execute this from the dedicated `<project>-test` package; local
   production-crate tests remain subsystem evidence only.
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

Read [Verification and acceptance](references/verification-and-acceptance.md) for evidence design and use `rust-java-migration-testing` for the three-ledger testing SOP. Before repairing a non-compiling or warning-heavy workspace, read [Compile drift and migration cleanup](references/compile-drift-and-cleanup.md): dependency/version drift, MSRV, crate-root re-export chain breaks, duplicate cross-crate types, Java-mirror naming/scaffolding norms, and the zero-warning check workflow (default + `--all-features`, `--keep-going` layered errors, per-crate attribution, tests after cleanup).

### 11. Report completion without inflating coverage

Report structural, implementation, behavioral, test, integration, and production
readiness separately. For behavior, distinguish mirrored contracts, golden
differential, live differential, and approved equivalent oracles; for tests,
separate losslessly migrated source tests from Rust-native additions.

Include exact commands, SHAs, test counts, failures, exceptions, and unverified boundaries. Never call a migration complete because code compiles or a parity manifest reaches 100%.

## Red Lines

- Do not define many migrated objects in `lib.rs`, `mod.rs`, or `compat.rs`.
- Do not delegate every object to one `compat.rs` implementation.
- Do not use empty bodies, `todo!()`, or `unimplemented!()` as completed migration.
- Do not delete or simplify working migrated behavior to make counts align.
- Do not use wildcard imports in production migration code.
- Do not silently merge several Java objects into one Rust file.
- Do not keep an authored `.rs` file above 800 physical lines; review every file above 500 and split it when cohesion is weak.
- Do not mechanically compress code, remove useful comments, or split arbitrary line ranges merely to satisfy a size gate.
- Do not embed integration, differential, host, load, or whole-project acceptance suites in production modules; inline `#[cfg(test)]` unit tests remain valid for focused module-private behavior.
- Do not replace overloaded behavior with one lossy convenience function.
- Do not create `get_*` methods solely to mirror JavaBean spelling when an idiomatic Rust method plus an explicit compatibility adapter preserves the contract.
- Do not treat an idiomatic Rust getter/setter as sufficient when scripts or dynamic member access still require Java field/getter/setter resolution.
- Do not call a declared dependency, successful compile, or isolated POC a verified component replacement.
- Do not use a replacement dependency's package/file layout as the target object inventory; source Java objects and the deterministic path rule remain authoritative.
- Do not mark a semantically similar dependency as `DEPENDENCY_REUSED` without pinned crate/commit, exact source symbol, adapter evidence, and local integration tests.
- Do not use `PLATFORM_NA` for work that is merely difficult or missing; require JVM/bytecode/class-loader/platform-specific evidence.
- Do not promote a component copied from a research list or local convention document to “selected” without current hard-filter and contract evidence.
- Do not call a Rust test copied from a Java test a differential test unless both implementations or Java-produced golden artifacts participate.
- Do not declare source-test parity from dispositions alone. Every source case needs a lossless target and golden/live `MATCH`; `MISSING`, `BLOCKED`, and `NOT_APPLICABLE` block completion.
- Do not modify copied source fixtures, scripts, corpora, golden files, or test data in place. Verify source/target SHA-256 and keep generated derivatives separate.
- Do not treat independently green suites or equal test totals as parity; compare per-case outputs, errors, state, side effects, and cleanup.
- Do not substitute production/binding-crate local tests for the non-published `<project>-test` whole-project acceptance package.
- Do not copy Maven/Gradle modules one-to-one into Cargo packages without a Rust publishing, dependency, target, macro/FFI, or lifecycle reason.
- Do not force every workspace into `crates/` or root-flat; record topology from product scale, families, repository noise, and compatibility.
- Do not mark a row behavior-verified from file counts, parser acceptance, generic `is_ok()`/`is_err()`, or “at least one test per object”.
- Do not let the four migration documents carry different baselines or contradictory completion states.
- Do not keep a current document and a `-历史详细版`/nested duplicate; merge useful history after the generated fact region.
- Do not replace the generated current-fact region or let regeneration discard the merged appendix.
- Do not claim real testing when only mocks, compilation, or static inspection ran.
- Do not edit reference source repositories while extracting patterns.
- Do not alternate migration, comparison, and testing for each object, file, or method.
- Do not run object-scoped acceptance during implementation; finish the frozen batch before consolidated audit and unified verification.
- Do not convert recovery commits or local edit milestones into completion checkpoints.
- Do not omit an existing Java object, constructor, method, parameter, return, exception, lifecycle, thread-safety, deprecation, or semantic inline comment.
- Do not replace source documentation with generic prose or claim comment parity from `cargo doc` alone.
- Do not write `对应 Java` in parameter, return, error-variant, field, or inline comments. Limit optional anchors to Rust type and constructor/method docs; keep detailed correspondence in the four documents.
- Do not rename Java-mirror SCREAMING_SNAKE enum variants or delete Java-mirror scaffolding types to silence `non_camel_case_types`/`dead_code`; use `#[allow(...)]` + comment and keep the Java inventory intact.
- Do not declare a workspace clean from the default-features gate alone; `--all-features` must also reach zero warnings, and do not silently lower `rust-version` to match an old local rustc — run the pinned toolchain via `rustup run <ver> cargo ...`.
- Do not edit a path dependency while cleaning a dependent crate; attribute each warning to its owning crate's `-->` path first.
- Do not fix "all errors" from one `--keep-going` output; errors surface in layers — fix the first layer, re-run, iterate.

## Completion Criteria

- Four current documents per source module share baselines, contract, and Rust SHA; no duplicate exists.
- The roadmap records justified source-module-to-crate boundaries and a project-driven topology; actual manifests and member paths match it.
- Every object has a deterministic final-two-segments path; `MISPLACED` remains incomplete until physically aligned.
- Every Java object, method, overload, and parameter has a disposition.
- Every source test/case has a lossless Rust implementation and every source asset has a byte-identical checked copy.
- `<project>-test` is a workspace member at the selected path with `publish = false` and owns the full source-suite/differential command and artifact.
- Complete Java/Rust suites pass and full per-case differential is 100% `MATCH`, with no harness failure or not-run case.
- Every dependency reuse, platform exclusion, blocker, exception, and Rust extension has precise evidence and honest denominator treatment.
- Every authored `.rs` file is at most 800 physical lines; files above 500 and functions above the Clippy 100-line signal have recorded cohesion reviews, and any split preserves Java object boundaries.
- Unit tests are colocated only when they exercise focused module behavior; integration, differential, host, load, and whole-project suites live under `tests/` or the non-published test package.
- Production Rust files satisfy layout, documentation, import, and no-stub rules.
- Every source-documented object, member, parameter, return, exception, metadata tag, and semantic inline comment has a traceable Rust counterpart.
- The complete declared batch was implemented before any acceptance gate ran.
- One consolidated post-implementation parity audit covers the full frozen denominator; no object-by-object verification loop was used.
- High-value call chains have source-linked semantic mappings.
- Applicable differential, replay, concurrency, load, fuzz, host, and rollback gates have evidence or explicit open gaps.
- Final reporting separates structural, implementation, behavioral, integration, and production-readiness claims.
