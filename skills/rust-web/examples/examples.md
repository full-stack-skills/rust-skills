# HTTP Service Scenario Examples

## Scenario: Adding a Query Endpoint

User Request:
Add the `GET /users/{id}` endpoint to an existing Axum service, with unified error formatting and timeout support.

First confirm success responses, syntax errors for invalid IDs, user not found status codes, database timeouts, and internal failures along with their corresponding response bodies. Then:

```text
Path extractor
  -> GetUser use case
  -> UserRepository port
  -> UserResponse / AppError
  -> centralized IntoResponse mapping
```

The handler should not directly write SQL queries; the router must test at least for status codes 200, invalid ID (400), missing user (404), downstream timeout, and response sanitization. Middleware tests confirm that the `timeout` middleware covers all target routes.

## Scenario: Integrating Transaction Scenarios

User Request:
The `POST /orders` endpoint requires both order creation and inventory updates; any failure must result in rollback.

Place transactions at the boundary of application/data adapters, where only request parsing and invocation of `CreateOrder` occur via handlers. Test cases include:

1. **Use Case Testing**: Ensure that a partial commit does not occur if the second write fails during transaction execution.
2. **Database Integration Testing**: Verify in real-world scenarios that transactions are properly rolled back on failure.
3. **Router Testing**: Map conflicts, insufficient inventory, and database unavailability to agreed-upon responses.
4. **Idempotency Testing**: Confirm that client retries do not result in duplicate order creation.

## Scenario: Graceful Shutdown

User Request:
During rolling deployments, ensure no requests are dropped while processing is active.

First confirm platform termination signals and grace periods. Stop accepting new incoming requests, propagate cancellation to background tasks, exhaust pending work within budget limits using controlled slow handlers; verify both the exhaustion path and timeout behavior without relying solely on process signal reception.
