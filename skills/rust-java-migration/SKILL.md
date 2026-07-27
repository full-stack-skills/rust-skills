---
name: rust-java-migration
description: Plan, execute, audit, and verify behavior-preserving migrations from Java Maven or Gradle projects to Rust Cargo workspaces. Use when comparing Java and Rust repositories at module, package, object, file, method, parameter, documentation, example, test, concurrency, or runtime-behavior level; when producing per-module migration roadmaps and parity tables; or when continuing an incomplete port without deleting existing work. Enforces one-Java-object-per-Rust-file layout, explicit Java-to-Rust semantic mappings, evidence-based completion states, CodeGraph-guided call-chain analysis, differential tests, replay, fuzzing, load tests, host integration, and rollback drills.
---

# Java to Rust Migration

Migrate contracts and observable behavior, not Java syntax. Preserve the Java project's public concepts and source traceability while selecting Rust-native ownership, error, concurrency, async, serialization, and framework mechanisms.

## Scope and Routing

Use this skill for full-project migrations, one Maven/Gradle module, parity audits, migration planning, or continuation of an existing Rust port.

Route detailed Rust choices to:

- `rust-workspace` and `rust-module-layout` for crate and module boundaries.
- `rust-api-design` for public Rust API quality.
- `rust-macros` for annotation-to-procedural-macro work.
- `rust-concurrency`, `rust-database`, `rust-http-client`, or `rust-web` for domain implementation.
- `rust-testing`, `rust-performance`, and `rust-web-security` for verification.

Do not modify migration code when the user requested only an audit, plan, or documentation. A plan-only or read-only request does not authorize running a write-producing document scaffolder: return the proposed four-document content in the response, use `--dry-run`, or write only to a user-approved destination. Do not broaden a module migration into a repository rewrite without authorization.

## Required Inputs

Resolve or explicitly mark unknown:

- Java repository path, baseline commit/tag, build tool, JDK, and module scope.
- Rust repository path, baseline commit, toolchain/MSRV, workspace, and target platforms.
- Compatibility goal: source-shape parity, public API parity, behavior parity, or production replacement.
- Explicit exceptions, blocked external projects, unsupported JVM-only features, and completion deadline.
- Required host applications, real scripts, test data, concurrency model, load profile, and rollback mechanism.

Never silently infer that the newest branch, a generated manifest, or an API registration list is the behavioral baseline.

## Workflow

### 1. Freeze baselines and inspect repository state

Record both repository SHAs, dirty worktrees, Java/Rust toolchains, module manifests, enabled features, and generated-code boundaries. Preserve existing Rust work and unrelated changes.

If a repository contains `.codegraph/`, use CodeGraph before text search or file-by-file reading:

1. Survey module/package/crate architecture.
2. Query representative public types and overloaded methods.
3. Trace high-value call chains across factories, registries, interceptors, serializers, persistence, networking, and concurrency.
4. Query the Rust counterparts and their callers/tests.
5. Re-query the exact symbols before changing them if the index reports staleness.

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
  --baseline "java=<sha-or-tag>; rust=<sha>"
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

### 4. Classify every object honestly

Use these states consistently:

| State | Meaning |
|---|---|
| `NOT_STARTED` | No Rust counterpart exists |
| `SKELETON` | Shape exists but behavior is absent or deliberately blocked |
| `IMPLEMENTED_UNVERIFIED` | Real logic exists but behavioral parity is not proven |
| `BEHAVIOR_VERIFIED` | Differential or equivalent contract tests pass |
| `JAVA_ONLY_EXEMPT` | JVM-specific behavior has an approved Rust replacement or exclusion |
| `PLANNED_BLOCKED` | Explicit external dependency blocks implementation |
| `RUST_EXTENSION` | Intentional Rust-only capability, excluded from Java parity numerator |

`SKELETON` and `PLANNED_BLOCKED` count as incomplete. API registration, compilation, file presence, or an empty method never upgrades them.

Allow a planned placeholder only when the user explicitly approves it. Isolate it by module/feature, name the dependency and owner, record exit criteria, keep it out of default facades, and exclude it from implemented/verified coverage.

For a blocked module, record the module-level exception as `PLANNED_BLOCKED`. Individual signature-only object rows inside it may be `SKELETON`; both states remain outside implementation and behavior numerators.

### 5. Migrate one vertical slice at a time

Choose a coherent slice containing source object, collaborators, tests, examples, and documentation. For each Java object:

1. Create exactly one primary `.rs` file.
2. Copy and translate the JavaDoc semantics into Chinese Rust doc comments.
3. Map all constructors/methods/overloads and parameters before coding.
4. Trace the Java method body and collaborators with CodeGraph.
5. Select Rust-native types and crates without deleting observable behavior.
6. Implement real logic in the object's file or explicit collaborator files.
7. Add unit and differential evidence.
8. Update all four documents.

Read [Layout and migration rules](references/layout-and-governance.md) and [Semantic mappings](references/semantic-mappings.md) before changing code.

### 6. Preserve naming and overload intent

- Use `snake_case` for Rust directories, files, methods, and parameters.
- Use `PascalCase` for Rust types.
- Map `loadOrCreateAgentState(slotKey)` to `load_or_create_agent_state(slot_key)`.
- Preserve the last meaningful Java package level as the Rust subdirectory.
- Keep `lib.rs` and `mod.rs` as declarations and re-exports only.
- Keep one Java class/interface/enum/record per Rust file; an inner builder tightly owned by the primary type may remain with it.
- Record every intentional rename in both object and name-consistency documents.

Rust has no method overloading. Keep one canonical snake_case name only when the signatures have one semantic operation. Give additional variants stable semantic suffixes such as `_with_charset`, `_into`, or `_from_reader`; record the exact Java signature mapped to each Rust function. Never collapse overloads that differ in defaults, validation, side effects, or error behavior.

### 7. Translate mechanisms, not frameworks literally

Use the mapping table as a starting point, then verify behavior:

| Java mechanism | Rust default |
|---|---|
| Jackson annotations/modules | `serde`, `serde_json`, custom serializers |
| `null` / nullable | `Option<T>` |
| checked exception hierarchy | typed `thiserror` enums and `Result` |
| `synchronized` / `ConcurrentHashMap` | ownership first; then `Mutex`/`RwLock`/`DashMap` |
| `CompletableFuture` | async future or supervised `tokio::task::JoinHandle` |
| Reactor `Mono<T>` | `async fn -> Result<T, E>` |
| Reactor `Flux<T>` | bounded `Stream<Item = Result<T, E>>` |
| ServiceLoader | explicit registry or `inventory` when link-time registration is required |
| Spring Boot integration | an `axum` adapter crate, not framework code in core |
| Quarkus integration | an `actix-web` adapter when that is the approved target |
| FreeMarker / Velocity | Tera / Handlebars |
| compile-time templates | Askama; use maud for Rust-native markup composition |
| Lombok data boilerplate | derives plus invariant-preserving handwritten APIs/builders |

Prefer composition of mature Rust crates over recreating a Java all-in-one implementation, but retain the source project's observable facade when compatibility requires it.

### 8. Extract annotation behavior behind a stable macro boundary

Do not place procedural macro entry points in a normal runtime crate. Use:

```text
project-core      # runtime traits, types, errors, and generated-code contract
project-macros    # thin proc-macro entry points and syntax parsing
project-web-*     # framework adapters that may re-export approved macros
```

Use `-derive` only for a derive-only public surface; use `-macros` for attribute/function-like or mixed macros, unless the existing crate family has a deliberate established spelling. Keep generated code dependent on public runtime APIs, not proc-macro internals. Test expansion success, compile failures, generics, visibility, renamed dependencies, and each framework re-export.

Java runtime annotations do not automatically become Rust macros. Use middleware, traits, registries, or explicit builders when runtime state and dynamic dispatch own the behavior.

### 9. Verify in increasing evidence levels

Do not stop at compilation. Execute the applicable ladder:

1. Static object/file/method/parameter inventory.
2. Rust formatting, check, unit, doc, integration, Clippy, and platform gates.
3. Java golden exporter and Rust differential replay for deterministic behavior.
4. Real user script/example replay against both implementations.
5. Concurrency acceptance: ordering, cancellation, backpressure, races, shutdown, and Loom/model tests where useful.
6. Load/stability tests: throughput, latency percentiles, memory, handles/tasks, reconnects, and long soak.
7. Security: property tests, malformed inputs, `cargo-fuzz`, unsafe review, and dependency advisories.
8. Real business-host integration with databases, networks, files, frameworks, and deployment topology.
9. Gray rollout and rollback drill with recorded recovery time and state compatibility.

Read [Verification and acceptance](references/verification-and-acceptance.md) for evidence design.

### 10. Report completion without inflating coverage

Report separately:

- Structural coverage: objects/files/method signatures registered.
- Implementation coverage: non-stub logic present.
- Behavioral coverage: differential contracts passing.
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
- Do not claim real testing when only mocks, compilation, or static inspection ran.
- Do not edit reference source repositories while extracting patterns.

## Completion Criteria

- Four current documents exist for every in-scope source module.
- Every Java object, method, overload, and parameter has a disposition.
- Every exception and Rust extension is categorized and excluded from misleading denominators.
- Production Rust files satisfy layout, documentation, import, and no-stub rules.
- High-value call chains have source-linked semantic mappings.
- Applicable differential, replay, concurrency, load, fuzz, host, and rollback gates have evidence or explicit open gaps.
- The final report separates structural, implementation, behavioral, integration, and production-readiness claims.
