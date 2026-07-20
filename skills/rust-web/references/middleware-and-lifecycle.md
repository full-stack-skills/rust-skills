## Middleware and Lifecycle Ordering

The declaration order of the middleware layer must be validated against locked versions of `ServiceBuilder`/axum documentation. Test-driven approaches are required to verify critical ordering; intuition is insufficient for this purpose.

Common Considerations:

1. Establish or propagate request IDs as early as possible;
2. Ensure trace coverage across downstream layers while masking sensitive headers and bodies;
3. Apply body size limits before large amounts of data are read;
4. Authenticate prior to business logic requiring identity verification;
5. Configure timeouts and load shedding within expected operational ranges;
6. Enable error handling visibility into middleware-induced failures;
7. Handle CORS preflight requests alongside actual responses simultaneously.

## Timeout Budgets

The outer request budget must be greater than or equal to the sum of internal step budgets, with additional reserves for response generation and cleanup:

```text
Total Request Budget
  >= Queueing + Database + Outbound HTTP + Computation + Response/Cleanup
```

After timeout expiration, cancel any work that can still be cancelled. For non-cancelable background side effects, implement idempotency keys, state tracking mechanisms, or compensation strategies to ensure data consistency and recoverability.

## Access and Overload Budgets

Resource costs differ between connection establishment and teardown; therefore, layered restrictions are necessary:

1. On accept failures, retry based on error type with short backoff delays where appropriate, avoiding tight loops of repeated errors;
2. Before TLS/HTTP/WebSocket authentication, use isolated, smaller concurrent slots and shorter timeouts to prevent resource exhaustion from unauthenticated connections;
3. Enforce hard limits for headers, frames, bodies, message queues, and subscription counts;
4. When bounded queues fill up, explicitly return overload status, discard reconstructible events, or disconnect slow consumers—never allow silent indefinite growth;
5. For broadcast consumers handling lag: send new snapshots if state can be reconstructed; otherwise use persistent logs per consumer queue to prevent event loss;
6. In cases of overload and authentication failures, ensure consistent latency behavior and error details across responses to avoid creating side channels through enum differentiation.

## Graceful Shutdown

1. Listen for SIGTERM/CTRL-C signals or platform-provided shutdown events;
2. Stop accepting new connections and requests;
3. Wait in-flight requests within defined budgets before terminating them;
4. Terminate background tasks or notify them of termination;
5. Flush necessary logs, metrics, and release resources;
6. Exit according to deployment platform policies when budget limits are exceeded.

Do not merely add shutdown signals for server futures while leaving `spawn`-ed background tasks running without proper cleanup coordination.

## Security Defaults

- Use precise origin/method/header allowlists for CORS configuration;
- Do not trust any arbitrary `X-Forwarded-*` headers;
- Enforce limits on body size, header fields, connection counts, concurrency levels, and request durations;
- Conduct risk assessments regarding compressed payloads, slow requests, and high-cost endpoints;
- Exclude cookies, tokens, and Authorization headers from general logging streams;
- Avoid exposing source code paths, SQL queries, internal hostnames, or backtrace information in external error responses.

## Primary References

- [axum middleware](https://docs.rs/axum/latest/axum/middleware/)
- [tower ServiceBuilder](https://docs.rs/tower/latest/tower/builder/struct.ServiceBuilder.html)
- [tower-http](https://docs.rs/tower-http/)
- [axum graceful shutdown](https://docs.rs/axum/latest/axum/serve/struct.Serve.html#method.with_graceful_shutdown)
- [Tokio graceful shutdown topic](https://tokio.rs/tokio/topics/shutdown)
