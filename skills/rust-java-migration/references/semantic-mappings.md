# Java-to-Rust Semantic Mappings

Use these mappings as decision prompts, not mechanical substitutions.

For third-party discovery, consult [Component candidate catalog](component-candidate-catalog.md), then apply the [Component replacement decision SOP](component-replacement-sop.md). A catalog entry is never an approved dependency.

## Types and ownership

| Java | Rust questions and common mapping |
|---|---|
| nullable reference | Is absence valid? Use `Option<T>` and preserve null/default distinctions. |
| immutable DTO | owned struct with private fields, derives, and validated constructor |
| mutable bean | explicit mutation methods; do not generate setters that bypass invariants |
| interface | trait; decide object safety and generic versus `dyn Trait` use |
| abstract class | trait defaults plus composed state, not inheritance emulation |
| record | struct with value semantics |
| enum with fields/methods | Rust enum with data and `impl` |
| `Class<T>` / reflection | type parameter, `TypeId`, registry, serializer metadata, or factory |
| weak/soft reference | `Weak`; cache policy must be redesigned because JVM soft references differ |

## Errors

- Map recoverable checked exceptions to typed `Result<T, E>`.
- Preserve error categories, causality, retryability, and partial side effects.
- Use `thiserror` for library errors; add context at boundaries without exposing secrets.
- Do not convert Java exceptions to panics.
- Record exception-message compatibility only when callers depend on it.

## Collections and ordering

Select `Vec`, `VecDeque`, `HashMap`, `BTreeMap`, `IndexMap`, `HashSet`, or `BTreeSet` from actual ordering, duplication, lookup, and serialization contracts. Java `HashMap` iteration must not be accidentally promoted to a stable order unless the public behavior requires it.

## Serialization

- Map Jackson field names, aliases, ignored/default fields, flattening, polymorphism, and custom modules explicitly.
- Use `serde` attributes or custom serializers/deserializers.
- Golden-test wire bytes/JSON, missing fields, unknown fields, nulls, numbers, timestamps, and enum spellings.
- Do not treat successful round-trip as compatibility with Java input/output.

## Async and concurrency

| Java | Rust mapping considerations |
|---|---|
| `synchronized` method | minimize critical section; `Mutex` only if exclusive state is real |
| `ConcurrentHashMap` | `DashMap` or `RwLock<HashMap>` after checking compound atomic operations |
| atomic classes | corresponding atomics with documented ordering |
| `CompletableFuture` | future; spawn only when independent task ownership is intended |
| executor pool | Tokio for async I/O; Rayon for CPU work; dedicated threads for blocking ownership |
| Reactor `Mono` | lazy `Future<Output = Result<T, E>>` |
| Reactor `Flux` | bounded stream with cancellation and backpressure contract |
| `ThreadLocal` | task-local only if async task propagation semantics match |

Test interleavings, cancellation, timeout, queue bounds, slow consumers, shutdown, and resource cleanup. Do not put a blocking Java-style critical section across `.await`.

## Frameworks and extension points

- Keep the domain core framework-neutral.
- Map Spring Boot, Quarkus, or other Java host entry points to framework-neutral Rust contracts plus separate approved adapter crates.
- Select Axum, Actix Web, Poem, Salvo, Tonic, or another host from target constraints and contract evidence; never infer the Rust framework from the Java framework name.
- Replace classpath scanning with explicit module registration, generated registration, or `inventory`.
- Replace lifecycle annotations with explicit start/stop ownership and cancellation-safe cleanup.
- Preserve interceptor order and before/after/error semantics through middleware tests.

## Templates

| Java engine | Rust candidate | Use when |
|---|---|---|
| FreeMarker | Tera | dynamic feature-rich templates |
| Velocity | Handlebars | constrained logic and portable templates |
| JSP/Thymeleaf-like compile-time views | Askama | compiled, typed templates |
| Twirl/JSX-like construction | maud | Rust-native markup composition |

## Annotations and macros

Classify each Java annotation:

1. Metadata consumed at runtime → explicit config, registry, middleware, or derive metadata.
2. Mechanical implementation generation → derive procedural macro.
3. Item transformation → attribute procedural macro.
4. Framework scanning marker → explicit registration or generated inventory.
5. Validation/security policy → typed wrapper or middleware unless compile-time transformation is essential.

Keep macro entry points thin. Put reusable runtime contracts in the core crate and optionally parsing/generation logic in a normal `macro-core` crate for unit testing.

## Java APIs with no direct Rust equivalent

Do not silently omit bytecode generation, dynamic proxies, serialization hooks, class loaders, GC reference semantics, thread interruption, or reflection. Classify each as:

- equivalent Rust behavior through another mechanism;
- intentionally unsupported with impact analysis;
- host/framework responsibility;
- explicit Rust extension.

Document observable differences and add contract tests for the replacement.
