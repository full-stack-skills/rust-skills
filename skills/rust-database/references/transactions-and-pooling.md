## Transactions and Connection Pools

### Transaction Boundaries

Transactions must encapsulate a business case that requires atomic completion. Ensure callers obtain `Transaction-scoped` repositories or wrap transactions within the application service to prevent accidental use of connections from another pool during any step.

Handle:
- Failure on begin;
- Failures in intermediate queries;
- Explicit rollback failures;
- Commit failures;
- Task cancellation/drop;
- Repeated side effects after retries.

When using `SQLx` transactions without explicit commit/rollback, a drop will trigger an implicit rollback afterward. Treat their asynchronous cleanup and connection reuse behavior as if they were operating under lock versions.

### Isolation and Concurrency

Do not assume safety merely by stating "use transactions." Identify isolation requirements based on the use case:
- **Lost update**: Use atomic conditional updates, locks, or version columns;
- **Write skew**: Require stronger isolation with explicit locks or constraints;
- **Phantom queries**: Rely on database-level isolation and locking semantics to maintain invariant ranges;
- **Duplicate creation**: Apply unique constraints correctly while mapping conflicts appropriately;
- **Work queues**: Use lock/skip semantics supported by the database, preventing starvation.

Isolation levels and lock semantics must be verified against the target database documentation.

### Retry Strategy

- Retries are limited to explicitly recoverable serialization errors, deadlocks, or transient connection issues;
- Retry entire transaction closures rather than continuing from failed SQL statements;
- Configure maximum retry count, exponential backoff, jitter, and total deadline;
- Side effects outside the transaction must have idempotency keys, outbox mechanisms, or compensating actions;
- Permanent constraint errors, validation failures, and authentication failures cannot be retried.

### Connection Budgets

```text
Database available connections
  >= application instances × max pool per instance
     + migration/worker/admin connection overhead
     + buffer for faults and rolling deployments
```

- `acquire_timeout` prevents indefinite queuing;
- `max_lifetime` aligns with database/proxy lifecycle policies while incorporating jitter;
- Idle settings balance cold start performance against resource consumption;
- Statement, lock, and transaction timeouts must be configured on the database side as well;
- Upon process shutdown: stop new work, wait for active transactions to complete, and close the pool.

Monitor metrics such as `active`, `idle`, `waiter`, `acquire_latency`, and `timeout`.
