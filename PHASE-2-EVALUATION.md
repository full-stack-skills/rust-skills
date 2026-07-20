# Rust Skill Tree Phase 2 Evaluation

Evaluation date: 2026-07-20

This document evaluates the next five candidate skills after the 19-skill baseline. The decision is based on stable Rust engineering boundaries and current upstream documentation. Crate versions below are evidence snapshots, not defaults that a future skill may apply without inspecting `Cargo.lock`, MSRV, target, and compatibility requirements.

## Decision Summary

| Priority | Candidate | Decision | Skill boundary | Representative components | Required golden example |
|---:|---|---|---|---|---|
| 1 | `rust-rpc` | Approve | Typed RPC contracts, gRPC clients/servers, streaming, deadlines, cancellation, health, reflection, TLS, and message limits | tonic, prost, Tower | A local tonic service with unary and streaming calls, deadline propagation, health, and bounded messages |
| 2 | `rust-data-formats` | Approve | Serialization contracts, schema evolution, trusted versus untrusted decoding, compatibility, no_std, and zero-copy tradeoffs | serde, serde_json, TOML/YAML crates, postcard, bincode, rkyv, prost | Versioned records with backward-compatible tests, explicit decode limits, and one compact-format comparison |
| 3 | `rust-messaging` | Approve | Delivery semantics, acknowledgements, offsets, ordering, idempotency, retries, dead letters, backpressure, and schema governance | async-nats, rdkafka, lapin, Redis Streams | A broker-backed producer/consumer contract test with duplicate delivery, retry, and graceful shutdown |
| 4 | `rust-wasm` | Approve | Browser JavaScript interop and WASI/component targets, with explicit boundary selection, ownership, async, size, and target testing | wasm-bindgen, web-sys, wasm-pack, WASI component tooling | A browser module tested with wasm-bindgen plus a documented WASI handoff boundary |
| 5 | `rust-network-protocols` | Conditional approval | Raw TCP/UDP framing, WebSocket, DNS, TLS, and QUIC; excludes HTTP clients/servers and RPC | Tokio net, tokio-tungstenite, Hickory Resolver, rustls, Quinn | A length-bounded framed protocol with timeouts, malformed-input tests, TLS policy, and slow-peer handling |

## Candidate Boundaries

### `rust-rpc`

Create this as an independent skill. RPC work has a distinct contract lifecycle: schema design, generated code, wire compatibility, status mapping, deadlines, streaming flow control, and service discovery metadata. It should route generic outbound HTTP to `rust-http-client`, executor and cancellation mechanics to `rust-concurrency`, and authentication policy to `rust-web-security`.

The skill must require explicit request and response size limits. Current tonic documentation describes HTTP/2 gRPC on Tokio, Hyper, and Tower, supports unary and streaming calls, and exposes configurable decode/encode limits. Health and reflection belong here because they expose RPC service metadata rather than generic application telemetry.

### `rust-data-formats`

Create this as an independent skill because wire and storage compatibility outlive individual request handlers. It should cover Serde attributes and custom implementations, human-readable formats, compact formats, Protobuf, schema evolution, unknown fields, deterministic output where required, decode budgets, no_std constraints, and zero-copy safety.

The skill must never imply that bincode, postcard, rkyv, and Protobuf are interchangeable. Format version, crate version, endianness, validation, and trust boundary must be explicit. The observed bincode release line shows active version churn, reinforcing the need to pin persistent or network formats and test old fixtures against new readers.

### `rust-messaging`

Create one semantics-first skill, not one skill per broker. Provider-specific details should live in references for NATS/JetStream, Kafka, AMQP/RabbitMQ, and Redis Streams. The main workflow should begin with delivery and failure semantics, then choose a client library.

The skill must define producer confirmation, consumer acknowledgement or offset commit, ordering scope, idempotency key, retry budget, dead-letter policy, rebalance behavior, schema ownership, and overload behavior. It must reject unqualified “exactly once” claims unless the complete broker, database, external side-effect, and retry boundary proves the claim.

### `rust-wasm`

Create this as an independent target-domain skill. Browser WebAssembly through wasm-bindgen/web-sys and WASI/component workloads have different hosts and capabilities; the workflow must choose one before selecting APIs. It should cover JavaScript value conversion, ownership across the boundary, async interop, panic/error transport, browser or Node tests, size profiling, and feature isolation.

The first golden example should focus on browser interop because wasm-bindgen and wasm-pack provide a coherent compile/test path. WASI components can be a routed reference until a stable repository-wide runtime baseline is chosen.

### `rust-network-protocols`

Defer implementation until the four approved skills above are stable. This candidate is useful but broad and security-sensitive. Its boundary must be protocol mechanics below HTTP and RPC: TCP/UDP, framing, WebSocket, DNS, TLS, and QUIC. Generic HTTP belongs to `rust-http-client` or `rust-web`; gRPC belongs to `rust-rpc`.

Approval is conditional on a security-first workflow covering maximum frame size, incremental parsing, read/write/idle deadlines, connection budgets, slow peers, cancellation, half-close behavior, certificate and hostname verification, malformed input, fuzzing, and observability. Protocol-specific references are preferable to a shallow list of networking crates.

## Go/No-Go Gates

A phase-2 skill is ready to add only when it has:

1. A trigger description that distinguishes it from all 19 existing skills.
2. A workflow organized around engineering decisions rather than crate APIs.
3. Provider- or protocol-specific material routed to references.
4. At least one compilable golden project with pinned dependencies and an offline lockfile.
5. Failure-path tests for limits, cancellation, malformed data, duplicate delivery, or compatibility as appropriate.
6. At least two forward-test scenarios, including one handoff or refusal case.
7. No claim that a current crate version, runtime maturity level, or compatibility behavior is timeless.

Do not add one skill per crate. A crate belongs in an existing skill when it implements the same engineering decision and validation contract; create a new skill only when it owns a distinct task boundary.

## Upstream Evidence

- [tonic](https://docs.rs/tonic/) and [prost](https://docs.rs/prost/)
- [tonic-health](https://docs.rs/tonic-health/) and [tonic-reflection](https://docs.rs/tonic-reflection/)
- [async-nats](https://docs.rs/async-nats/), [rust-rdkafka](https://docs.rs/rdkafka/), [lapin](https://docs.rs/lapin/), and [redis](https://docs.rs/redis/)
- [The wasm-bindgen Guide](https://rustwasm.github.io/docs/wasm-bindgen/) and [The wasm-pack Guide](https://rustwasm.github.io/docs/wasm-pack/)
- [Serde](https://serde.rs/), [postcard](https://docs.rs/postcard/), [bincode](https://docs.rs/bincode/), and [rkyv](https://docs.rs/rkyv/)
- [Tokio networking](https://docs.rs/tokio/latest/tokio/net/), [tokio-tungstenite](https://docs.rs/tokio-tungstenite/), [Hickory Resolver](https://docs.rs/hickory-resolver/), [rustls](https://docs.rs/rustls/), and [Quinn](https://docs.rs/quinn/)
