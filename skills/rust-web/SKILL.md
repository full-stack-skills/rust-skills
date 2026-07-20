---
name: rust-web
description: Design, implement, test, and operate production Rust server-side HTTP services, including axum, Actix Web, routing, extractors, application state, error mapping, middleware order, timeouts, body limits, observability, graceful shutdown, and database boundaries. Use when users ask for Rust REST APIs, web handlers, middleware, server lifecycle, HTTP contracts, or production web-service architecture; hand security controls to rust-web-security.
---

# Rust HTTP Service Delivery

Deliver server-side HTTP APIs based on HTTP contracts and runtime lifecycles. The framework handles transport adaptation; domain logic and data access remain independently testable without embedding all backend issues into handlers.

## Confirming the Service Contract

Before modification, verify from OpenAPI specs, existing routes, clients, tests, configuration, and run environments:

- Methods, paths, status codes, request/response schemas, and compatibility strategies;
- Authentication context origin (authentication system design is outside this skill scope);
- Request bodies, concurrency limits, timeouts, upload sizes, and response size constraints;
- Dependencies on external HTTP services, databases, caches, or queues, including failure semantics;
- Listening addresses, proxies, TLS termination, health checks, graceful shutdown budgets;
- Rust/MSRV versions of axum, Tokio, Tower, and related crates with locked dependencies;
- Logging levels, tracing configuration, metrics exposure, sensitive field handling, data retention policies.

Response fields from existing client libraries constitute compatibility constraints. When contracts are missing, declare minimal assumptions first.

## Workflow

### 1. Establish Current Baseline

```bash
rustc --version --verbose
cargo metadata --format-version 1
cargo tree -e features
cargo test --all-targets
```

Verify service entry points, router composition, state management, error types, middleware ordering, shutdown signals, and testing tools. Adhere strictly to `Cargo.lock` versions and official documentation; do not mix axum/Tower APIs based on memory rather than versioned specifications.

### 2. Define Transport Boundaries

Recommended call flow:

```text
HTTP request
  -> router / extractor / transport validation
  -> application service / use case
  -> repository or outbound HTTP port
  -> domain result/error
  -> centralized HTTP response mapping
```

- Handlers perform extraction, transport-layer validation, invoke use cases, and map responses;
- Domain logic does not depend on axum request/response types;
- Database connection pools and HTTP clients serve as stateful dependencies within the service layer; do not store business data in global locks.
- Transactions belong to use case/data access boundaries and are not scatteredly controlled by handlers.
- DTOs, domain models, and persistence models should be separated based on change reasons to avoid unintended reuse of structures without control.

Refer to [Service Boundaries](references/service-boundaries.md) when determining specific layering or adapter requirements.

### 3. Implement Routing and Input Boundaries

- Route paths, extractors, and response types must align with locked axum versions;
- Explicitly validate path parameters, query strings, headers, and request bodies to distinguish syntax errors from domain conflicts;
- Enforce limits on request body size, uploads, pagination, and batch sizes;
- Avoid `.await` operations across lock-held states; prefer delegating shared mutable state to dedicated services or storage mechanisms.
- Do not use `unwrap()`/`expect()` for handling failures in requests, network access, database queries, or serialization; instead, convert unexpressible preconditions into type-level checks and centralized validation that avoids duplication across multiple handlers.

### 4. Unified Error Response Mapping

Define a single mapping from application errors to HTTP responses:

- Validation failures → client-fixable 4xx status codes;
- Not found, conflicts, and permission denials → stable client-error statuses such as `404`, `409`, and `403`;
- Downstream unavailability, timeouts, internal defects → 5xx status codes that do not leak internal details.

Each error response must include a stable machine code and request/tracing identifiers for correlation. Full error chains enter controlled logging; responses should not expose SQL queries, tokens, file paths, or backtraces. Avoid mapping all errors to `500` or hiding failures by returning `200`.

### 5. Middleware Composition and Security Boundaries

Review the Tower middleware layer in accordance with actual call order:

- Redact sensitive headers while retaining request IDs and trace identifiers;
- Configure global and downstream timeouts;
- Enforce request body limits and concurrency/load protection measures;
- Integrate authentication contexts and authorization checks at appropriate points.
- Maintain precise CORS allowlists; do not default to permissive policies when credentials are present in the service chain.
- Account for CPU costs associated with compression and risks of exposing sensitive responses under compressed headers.
- Trust proxy headers only from explicitly controlled sources.

Middleware ordering, timeout configurations, and graceful shutdown strategies are documented in [Middleware and Lifecycle](references/middleware-and-lifecycle.md).

### 6. Managing Async Lifecycles

- Configure layered timeouts for servers, external requests, and database operations;
- Ensure cancellation propagates downward to clean up subtasks without creating leaked tasks detached from request lifetimes;
- Gracefully shut down by stopping new incoming requests while exhausting in-flight ones within budget limits before releasing resources.
- Distinguish between non-retryable and retryable errors; retries require budgets, backoff strategies, and idempotency guarantees.
- Route deep design of Tokio tasks, channels, `Send`/`Sync`, cancellation safety, and lock scopes to `$rust-concurrency`.

### 7. Bounded External Adapter Access

This skill can integrate with services requiring databases or outbound HTTP clients but focuses solely on the server-side boundary:

- Reuse connection pools/client instances rather than creating new ones per request;
- Configure timeouts, connection limits, and observable error reporting for downstream components;
- Ensure transaction coverage across complete use cases without unnecessary external network waits.
- Route schema migrations, indexes, transactions, SQL tuning, and ORM modeling to `$rust-database`.
- Independent SDKs, crawlers, or bulk HTTP clients are not part of the server-side main flow; they belong to separate tooling domains.
- Route JWT/OAuth flows, sessions, tokens, CORS/CSRF policies, and secret management to `$rust-web-security`; this skill only consumes principal identities and authorization outcomes from verified sources.
- WebSocket upgrades, message protocols, heartbeat mechanisms, and backpressure handling are processed as independent sub-flows when explicitly requested.

### 8. Layered Service Testing

Ensure coverage of:

1. Domain/use case pure tests;
2. Router-level request testing without binding to real ports per use case;
3. Extractor failures, error mapping logic, body limits, timeouts, and authentication boundaries;
4. External adapter contract validation and fault injection scenarios;
5. Database migration isolation, commits, rollbacks when requiring real databases;
6. Limited socket tests verifying listening behavior, proxy configurations, or graceful shutdown dynamics.

Detailed test matrices are provided in [HTTP Service Testing](references/testing.md). Test organization, coverage targets, CI gate policies, and performance baselines fall under the purview of [rust-testing](references/testing.md).

## Common Gates

```bash
cargo fmt --all -- --check
cargo check --all-targets
cargo test --all-targets
cargo clippy --all-targets -- -D warnings
```

Add OpenAPI/schema compatibility checks, integration environment tests, and security scans per project. Do not silently skip failing dependency-based tests to claim overall pass status.

## Completion Criteria

- HTTP contracts, versioning assumptions, and compatibility guarantees are explicit;
- Handlers remain thin with domain logic and external adapters testable independently;
- Error handling, status codes, timeouts, middleware ordering, and graceful shutdown behaviors have corresponding tests;
- Logs and responses do not leak secrets or internal details.
- `cargo fmt`, `cargo check`, `cargo test`, and `clippy` pass successfully;
- When real databases, networks, TLS connections, or deployments are unverified, remaining boundaries must be explicitly marked.

## Handoff Boundaries

| Primary Issue | Assigned Responsibility |
|---|---|
| Schema definitions, migrations, transactions, connection pools, SQL/ORM modeling | `rust-database` |
| Authentication, authorization, sessions/tokens, CORS/CSRF policies, SSRF protection | `rust-web-security` |
| Tokio tasks, locks, channels, cancellation safety, graceful shutdown implementation | `rust-concurrency` |
| Test layering strategies, coverage targets, attribute tests, performance baselines | `rust-testing` |
| Ownership semantics, serde type contracts, generic error design patterns | `rust-stable` |
| Features, workspace configurations, build scripts, release pipelines | `rust-cargo-build` |
| Unsafe network libraries, C ABI interfaces, raw buffer handling | `rust-unsafe-ffi` |

## On-Demand Resources

- [Service Boundaries](references/service-boundaries.md): Consult when designing handlers, state management, data structures, or outbound HTTP adapters.
- [Middleware and Lifecycle](references/middleware-and-lifecycle.md): Review Tower configuration, timeout policies, CORS rules, load balancing strategies, or graceful shutdown logic.
- [HTTP Service Testing](references/testing.md): Refer to design patterns for router integration, end-to-end testing, fault injection scenarios.
- [Examples](examples/examples.md): Use templates for end-to-end task decomposition when needed.
- `examples/golden-handler/`: Offline compilation and verification of transport boundary behavior and error mapping logic.

## References

- [Rust Networking](https://www.rust-lang.org/what/networking)
- [axum documentation](https://docs.rs/axum/)
- [Tokio documentation](https://docs.rs/tokio/)
- [Tower documentation](https://docs.rs/tower/)
- [Serde](https://serde.rs/)
