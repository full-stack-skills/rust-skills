# HTTP Service Boundary

## Component Responsibilities

| Component | Should Handle | Should Not Handle |
|---|---|---|
| Router | Path, method, nesting, and layer combinations | Domain decisions |
| Extractor | Reading transport data and early transmission validation | Database transactions |
| Handler | Calling use cases and mapping results | Large-scale business logic |
| Application service | Orchestrating complete use cases | axum response details |
| Repository/outbound port | Data or external protocol services | HTTP inbound status codes |
| Error mapper | Stable status codes and response schemas | Swallowing raw error chains |

## State

State is suitable for saving cloneable, thread-safe dependency handles such as connection pools, configuration snapshots, clients, and application services. Avoid:

- Using `Arc<Mutex<Vec<_>>>` to act as a production database;
- Executing network or database `.await` operations on data protected by locks;
- Piling every request's data into global state;
- Recreating connection pools or HTTP clients within handlers;
- Bypassing dependency injection with global mutable singletons.

## DTOs and Domain Models

- Request DTOs express transport formats and optionality;
- Domain types express business invariants after validation;
- Persistence models express tables, columns, and query requirements;
- Response DTOs expose only fields promised by the protocol.

Reusing a structure across layers is reasonable only when changes are driven by identical reasons.

## Database Boundary

- Handlers should not directly concatenate SQL statements;
- Transactions determine commit/rollback scope for complete use cases;
- Do not wait on unbounded external HTTP calls within database transactions;
- Error mapping distinguishes missing, conflict, timeout, and internal errors;
- `sqlx::query!` compilation-time checks require preparing databases or offline metadata according to project configuration conditions that cannot be ignored in CI.

## Outbound HTTP Boundary

- Reuse clients centrally with default headers, TLS, proxies, and timeouts configured once;
- Handle status codes, body size limits, and deserialization errors separately;
- Retry only calls that are idempotent and within budget constraints;
- Log target services and trace associations without recording credentials or complete sensitive bodies;
- Use fake servers or adapter mocks to test failure paths.

## Main Resources

- [axum extract module](https://docs.rs/axum/latest/axum/extract/)
- [axum State](https://docs.rs/axum/latest/axum/extract/struct.State.html)
- [axum IntoResponse](https://docs.rs/axum/latest/axum/response/trait.IntoResponse.html)
- [reqwest Client](https://docs.rs/reqwest/latest/reqwest/struct.Client.html)
- [SQLx](https://docs.rs/sqlx/)
