# Rust Component Candidate Catalog for Java Migrations

This catalog turns collected component notes into structured discovery input. It does not mandate a crate or prove production readiness. Versions, maintenance, license, MSRV, targets, advisories, unsafe/build scripts, and protocol compatibility must be re-verified from primary sources when making a decision. When no row fits, follow [crate replacement discovery and evaluation](crate-replacement-discovery.md) rather than guessing from a Java product name.

Observation baseline for the initial catalog: 2026-07-29.

## How to use the catalog

For each Java responsibility:

1. write the observable contract before opening this catalog;
2. choose a replacement shape: standard library, direct crate, wrapper, trait plus adapters, registry, macro/codegen, host responsibility, redesign, or exclusion;
3. shortlist candidates from relevant rows;
4. verify official docs/repository/crate metadata and resolved dependency graph;
5. hard-filter license, MSRV, targets, advisories, unsafe, runtime, blocking, maintenance, and wire/storage incompatibility;
6. spike the riskiest behavior and record an adoption state.

Do not compare a niche protocol client with a foundational crate by raw
downloads. Use same-responsibility evidence, separate ecosystem health from
semantic fitness, and retain the search queries and rejected candidates.

`Research status` is not the migration adoption state defined in the component SOP.

## Web, HTTP, runtime, and validation

| Responsibility | Candidates/patterns | Research status | Decision notes |
|---|---|---|---|
| Async runtime | Tokio | `PRIMARY_SOURCE_CHECKED` | Verify runtime ownership, blocking boundaries, cancellation, time, I/O, features, and target support. |
| HTTP types/protocol | `http`, Hyper | `PRIMARY_SOURCE_CHECKED` | Usually infrastructure below an application framework; do not expose implementation types from the core facade without intent. |
| Web framework/adapter | Axum, Actix Web, Poem, Salvo, Rocket, Warp, Tide, Gotham, Ntex | `PRIMARY_SOURCE_CHECKED` for ecosystem identity | Select from host requirements. Keep core contracts framework-neutral and run one shared adapter conformance suite. |
| Middleware/service abstraction | Tower | `PRIMARY_SOURCE_CHECKED` | Useful when readiness, backpressure, layers, and reusable services match the contract. |
| Validation integration | `validator`, `axum-valid` | `DISCOVERED` | Separate validation rules from framework extraction. Verify derive/runtime behavior and error shape. |
| WebSocket | `tokio-websockets`; framework-native support | `DISCOVERED` | Verify protocol features, fragmentation, control frames, limits, backpressure, shutdown, and TLS integration. |
| STOMP | `wstomp` | `NEEDS_SPIKE` | Verify protocol coverage, maintenance, runtime, heartbeat, reconnect, acknowledgement, and broker compatibility. |
| MIME | `mime` and ecosystem parsers | `DISCOVERED` | Pick exact parsing/serialization requirement; test invalid and ambiguous inputs. |
| “Topcoat” framework | Topcoat | `DISCOVERED` | Identity, maintenance, scope, and primary-source evidence need verification before comparison. Do not treat as a default web replacement. |

Primary starting points:

- Axum: <https://github.com/tokio-rs/axum>
- Tokio: <https://tokio.rs/>
- Tower: <https://github.com/tower-rs/tower>

## Data, ORM, SQL, and cache

| Responsibility | Candidates/patterns | Research status | Decision notes |
|---|---|---|---|
| Async SQL toolkit | SQLx | `PRIMARY_SOURCE_CHECKED` | Verify database features, compile/offline query mode, pool lifecycle, transactions, migrations, and runtime/TLS choices. |
| Data/ORM facade | RBatis | `DISCOVERED` | Verify query semantics, transactions, macros, drivers, runtime, maintenance, and facade leakage. |
| ORM/data mapper | Toasty family | `PRIMARY_SOURCE_CHECKED`, `NEEDS_SPIKE` | Upstream describes Toasty as preview with unstable API. Never call it “locked” or production-ready solely from selection notes. Wrap it and prove required database/transaction behavior if considered. |
| SQL parsing | `sqlparser` | `DISCOVERED` | Parser support is not database execution compatibility. Verify dialect, AST round trip, positions, and unsupported syntax. |
| Redis | `redis` | `DISCOVERED` | Verify async connection manager, cluster/sentinel, pipeline/transaction, reconnect, TLS, cancellation, and error mapping. |
| Memcached | `memcache` | `DISCOVERED` | Verify protocol, pooling, timeouts, expiration semantics, and maintenance. |
| In-process cache | Moka | `PRIMARY_SOURCE_CHECKED` for identity | Test hit/miss/loading, invalidation, eviction, TTL/TTI, concurrency, and shutdown; final-value tests alone do not prove caching. |

Primary starting point for Toasty: <https://github.com/tokio-rs/toasty>.

## Serialization, protocols, and RPC

| Responsibility | Candidates/patterns | Research status | Decision notes |
|---|---|---|---|
| Jackson-like data mapping | serde, `serde_json` | `PRIMARY_SOURCE_CHECKED` | Map rename/alias/default/skip/flatten/polymorphism/custom modules explicitly. Golden-test Java and Rust wire output. |
| XML | `quick-xml` plus serde integration/custom mapping | `DISCOVERED` | Verify namespaces, attributes, mixed content, entities, ordering, encoding, and streaming. |
| Protobuf | Prost | `PRIMARY_SOURCE_CHECKED` | Verify schema/source ownership, unknown fields, optional/presence semantics, generated API, compatibility, and build tooling. |
| gRPC | Tonic + Prost | `PRIMARY_SOURCE_CHECKED` | Verify streaming, deadlines, cancellation, status mapping, interceptors, TLS, reflection, health, and graceful shutdown. |
| Foreign-language bindings | UniFFI | `PRIMARY_SOURCE_CHECKED` | Binding generation for a Rust library, not a general Java component replacement or shipping system. Verify supported target language/type/error/async model and packaging separately. |

Primary starting points:

- serde: <https://serde.rs/>
- Prost: <https://github.com/tokio-rs/prost>
- Tonic: <https://github.com/hyperium/tonic>
- UniFFI: <https://mozilla.github.io/uniffi-rs/latest/>

## Messaging and event systems

| Responsibility | Candidates | Research status | Required spike |
|---|---|---|---|
| Kafka | `rdkafka` | `DISCOVERED` | delivery semantics, rebalance, transactions, backpressure, native dependency, shutdown, observability |
| RabbitMQ/AMQP | Lapin or another verified AMQP client | `DISCOVERED` | confirms/returns, acknowledgements, reconnect, channel lifecycle, TLS, broker compatibility |
| Pulsar | `pulsar` | `DISCOVERED` | subscriptions, acknowledgement, redelivery, batching, schema, auth, reconnect |
| RocketMQ | `rocketmq-rust` | `NEEDS_SPIKE` | protocol/feature completeness, broker compatibility, maintenance, failure recovery |
| NATS | `async-nats` | `DISCOVERED` | core/JetStream semantics, ordering, dedupe, ack, reconnect, drain/shutdown |
| MQTT | `rumqttc` or another verified client | `DISCOVERED` | QoS, session persistence, reconnect, keepalive, backpressure, TLS |
| Redis messaging | `redis` pub/sub/streams | `DISCOVERED` | delivery and consumer-group semantics; do not equate with a general message broker |
| ActiveMQ | protocol-compatible AMQP/STOMP client | `NEEDS_SPIKE` | select by broker protocol/configuration, not product-name similarity |
| In-process disruptor/ring buffer | `disruptor` or bounded channels | `NEEDS_SPIKE` | ordering, wait strategy, overwrite policy, affinity, latency, shutdown |

Do not select a broker client from API resemblance. Real-broker tests, network fault injection, recovery, duplicate/loss semantics, load, and shutdown evidence are usually required.

## Scripting, expressions, parsing, and dynamic behavior

| Java responsibility | Candidates/patterns | Research status | Decision notes |
|---|---|---|---|
| Groovy-like embedded scripting | `mlua`, PyO3, JavaScript engine bindings, purpose-built DSL | `NEEDS_SPIKE` | No generic one-to-one Groovy replacement. Choose language, sandbox, host API, threading, cancellation, resource limits, and packaging deliberately. |
| Python embedding/extensions | PyO3 | `PRIMARY_SOURCE_CHECKED` for identity | Verify Python runtime ownership, GIL/free-threaded assumptions, packaging, errors, async bridge, and target constraints. |
| Lua embedding | `mlua` | `PRIMARY_SOURCE_CHECKED` for identity | Verify engine/features, sandbox/resource controls, Send behavior, callbacks, async, and serialization. |
| JavaScript embedding | a verified engine crate; collected `javascript` crate remains a candidate | `NEEDS_VERIFICATION` | The collected note contained inconsistent repository provenance. Verify the actual engine, maintenance, license, sandbox, and native dependencies. |
| ANTLR grammar/runtime | Rust ANTLR runtime or generated parser alternative | `NEEDS_SPIKE` | Verify grammar/tool version, generated-code ownership, runtime completeness, diagnostics, and build reproducibility. |
| QLExpress/expression engine | purpose-built parser/evaluator or verified expression crate | `NEEDS_SPIKE` | Preserve grammar, precedence, coercion, variables/functions, errors, resource limits, and sandbox. Parsing alone is not evaluation parity. |
| Spring Expression | project-owned parser/evaluator plus focused crates where suitable | contract-specific | Avoid assuming one crate replaces the full language. Build parser and evaluator matrices and live/golden differential cases. |

## Macros, annotations, and AOP

| Java responsibility | Rust shape/candidates | Research status | Decision notes |
|---|---|---|---|
| Lombok boilerplate | standard derives, invariant-preserving methods/builders, optionally `lombok-macros` | `NEEDS_SPIKE` | Verify generated public API, visibility, generics, field attributes, diagnostics, maintenance, and compatibility. Do not generate setters that violate invariants. |
| Annotation processing | derive/attribute/function-like proc macro plus runtime contract | pattern | Use `-derive` for derive-only public entry points and `-macros` for mixed macro kinds. Compile-pass/fail tests are mandatory. |
| Runtime annotations/AOP | middleware, traits, explicit registries, wrappers; `aspect-core` only after verification | `NEEDS_SPIKE` | Preserve ordering, pointcut/selection, before/after/error, panic/cancel, async, and host integration. Java annotations do not automatically become macros. |

Primary starting point for the collected Lombok candidate: <https://github.com/crates-dev/lombok-macros>.

## Observability and system information

| Responsibility | Candidates | Research status | Decision notes |
|---|---|---|---|
| Structured diagnostics | `tracing`, metrics ecosystem | `PRIMARY_SOURCE_CHECKED` for ecosystem identity | Define fields/cardinality/redaction, context propagation, sampling, exporter, and shutdown. |
| Tokio runtime metrics | `tokio-metrics` | `DISCOVERED` | Verify runtime configuration, metric stability, overhead, scrape interval, and target compatibility. |
| System information | `sysinfo` | `DISCOVERED` | Verify platform support, refresh model, units, permissions, process identity, and collection cost. |

## Configuration, utilities, security, and documents

| Java responsibility | Candidates/patterns | Research status | Decision notes |
|---|---|---|---|
| `.properties`, YAML, TOML | `java-properties`, `serde_yaml_ng`, `toml`, or a verified config crate | `DISCOVERED` | Preserve profile/source precedence, environment substitution, key normalization, defaults, reload, and error locations; a parser alone is not Spring configuration parity. |
| UUID/ULID/NanoID | `uuid`, `ulid`, `nanoid` | `DISCOVERED` | Verify version/variant, byte/string form, ordering, monotonicity, randomness, serde schema, and database mapping. |
| Java date/time | `time` or `chrono` | `DISCOVERED` | Select one domain representation deliberately; test zone, offset, precision, leap/ambiguous local time, formatting, and Java fixture compatibility. |
| `BigDecimal` / exact decimal | `bigdecimal`, `rust_decimal`, `num-bigint` combinations | `DISCOVERED` | Verify precision/scale, rounding, overflow, string/JSON/database representation, equality, and performance. |
| Commons/Hutool utility surface | std plus focused crates such as `url`, `bytes`, `regex`, `base64`, `hex`, and `aho-corasick` | pattern | Avoid replacing a Java utility umbrella with one Rust dependency. Inventory each public utility contract and use the smallest focused mechanism. |
| Metrics and telemetry | `metrics`, OpenTelemetry ecosystem, Prometheus exporters, `tracing` integration | `DISCOVERED` | Preserve instruments, units, label cardinality, trace context, sampling, exporter lifecycle, flushing, and shutdown. |
| JWT and password hashing | `jsonwebtoken`, `argon2`, `scrypt` | `DISCOVERED` | Pin algorithms and claims policy, reject algorithm confusion, validate time/key rotation, use password-specific KDFs, and test malformed/adversarial data. |
| General cryptography | focused RustCrypto crates | candidate family | Choose by standard, mode, key/nonce format, provider/compliance, side-channel and zeroization requirements. Never invent protocols or replace obsolete Java crypto without a compatibility and migration plan. |
| JavaMail | `lettre` | `DISCOVERED` | Verify MIME/charset/attachments, SMTP extensions, authentication, TLS policy, timeouts, retries, delivery reporting, and test-server behavior. |
| Excel read/write | `calamine`, `rust_xlsxwriter` | `NEEDS_SPIKE` | Select read and write responsibilities separately. Round-trip real workbooks including formulas, styles, dates, merged cells, images, and large sheets. |
| DOCX/PDF | `docx-rs`, `printpdf`, `lopdf`, or another format-specific crate | `NEEDS_SPIKE` | Separate generation, parsing, editing, rendering, and standards compliance. Validate with real consumers; file creation alone is not compatibility. |

## Test infrastructure

| Responsibility | Candidates | Research status | Decision notes |
|---|---|---|---|
| Real dependency integration | Testcontainers for Rust | `PRIMARY_SOURCE_CHECKED` | Test infrastructure for disposable Docker dependencies, not a production component replacement. Pin images, readiness, cleanup, parallelism, and CI/Docker requirements. |
| Property testing | `proptest`, `quickcheck` | `DISCOVERED` | Derive invariants from contracts; retain minimized regressions. |
| Mutation | `cargo-mutants` | `DISCOVERED` | Review meaningful survivors and equivalent mutants; no universal score. |
| Coverage | `cargo-llvm-cov` | `DISCOVERED` | Compare documented scopes; coverage is a gap signal, not semantic proof. |
| Fuzzing | `cargo-fuzz`, libFuzzer ecosystem | `DISCOVERED` | Seed from source/protocol cases; persist regressions and bound resources. |
| Async/model checks | Loom or deterministic test harnesses | `DISCOVERED` | Use for small synchronization models; retain real-runtime lifecycle tests. |

Primary starting point: <https://github.com/testcontainers/testcontainers-rs>.

## Candidate-record template

```markdown
- Responsibility:
- Source note and observation date:
- Primary source checked:
- Candidate/version/features:
- Research status:
- Required contract:
- Hard-filter result:
- Highest-risk uncertainty:
- Spike command/artifact:
- Adoption state:
- Rejected alternatives:
- Upgrade/rollback/exit strategy:
```
