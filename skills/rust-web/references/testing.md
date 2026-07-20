# HTTP Service Testing

## Test Matrix

| Layer | Objective | Typical Dependencies |
|---|---|---|
| Domain/use case | Business rules and error handling | fake ports |
| Handler/router | Routing, extraction, status codes, body parsing | in-process service |
| Adapter contract | SQL/HTTP serialization and failure modes | isolated database/fake server |
| Socket lifecycle | Listening, proxying, streaming, closing behavior | ephemeral port |
| System | Cross-service critical paths | controlled integration environment |

## Router-Level Checks

- Correct method and path;
- Failure to extract `path`, `query`, `header`, or `body`;
- Content type and serialization format compliance;
- Status codes for each application error class, plus machine-level errors;
- Body limits, timeouts, CORS policies, and authentication boundaries;
- Request ID and trace header presence/validity;
- Response must not contain secrets or internal error chains.

Prioritize direct calls to `Tower::Service` for router testing. Bind ports only when verifying real socket behavior, connection handling, TLS negotiation, streaming bodies, or graceful shutdowns.

## Database and Transactions

- Each test uses an isolated schema, database instance, transaction scope, or container strategy;
- Covers commit operations, explicit rollbacks, and mid-flight failures;
- Tests conflict resolution strategies: not found, duplicate key errors, connection failures, timeout mappings;
- Ensures tests do not depend on existing data from the development machine;
- Avoids shared fixed records or ports during parallel execution;
- Validates offline metadata queries (`query!`) have no expiration issues.

## External HTTP Integration

- fake server assertions over method, path, headers, and body content;
- Coverage of non-2xx responses, malformed bodies, slow response times, connection failures, and oversized payloads;
- Retry tests must assert retry count limits, budget constraints, and that retries only apply to permitted operations;
- Do not invoke uncontrolled public services in standard CI pipelines.

## Lifecycle Management

- Stop accepting new requests after sending a shutdown signal;
- In-flight requests complete within the allocated budget or are explicitly cancelled;
- Background tasks receive shutdown notifications and exit gracefully;
- Include overall timeout limits to prevent indefinite hangs on test failures.

## Key References

- [axum testing example](https://github.com/tokio-rs/axum/tree/main/examples/testing)
- `Tower::ServiceExt` trait documentation: https://docs.rs/tower/latest/tower/trait.ServiceExt.html
- Tokio testing guide: https://tokio.rs/tokio/topics/testing
