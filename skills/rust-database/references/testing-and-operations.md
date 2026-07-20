## Testing and Execution

### Test Layers

| Layer | Target | Dependencies |
|---|---|---|
| Domain/Application | Business rules and transaction orchestration | fake repository / unit of work |
| Query mapping | Parameter, column, and type mappings | Real database |
| Migration | Empty schema, upgrades, and failure recovery | Target database version |
| Concurrency | Locks, isolation levels, and unique constraints | Multi-connection real databases |
| Operations | pool management, restarts, timeouts, scheduling | Controlled integration environment |

SQLite mock/ in-memory databases cannot validate SQL behavior, locking mechanisms, data types, timezones, or indexing logic of PostgreSQL/MySQL. They should only be considered as "real dialect" tests if the production target itself is SQLite-based.

### Isolation Test Data

- Each test uses an independent database/schema/container with reliable transaction strategies;
- Parallel testing must not share fixed IDs, sequence assumptions, or global cleanup mechanisms;
- Transaction rollback fixtures cannot override commit behavior, DDL operations, or cross-database visibility;
- Fixed timezone/locale/extension settings should be avoided to prevent reliance on default values from development machines;
- Save migration logs, SQLSTATE codes, and minimal diagnostics upon failure without recording sensitive bind parameters.

### Queries & Performance

- Use `EXPLAIN` execution statistics for the target database; avoid destructive explain queries during write operations;
- Validate under representative distributions and data volumes—not just using ten-row fixtures;
- Inspect scan rows returned, result row counts, index usage, sorting behavior, temporary space consumption, and lock waits;
- Create normalized fingerprints for slow queries to prevent overfitting on complete sensitive SQL/bindings as labels;
- Prove N+1 query patterns via `query count` or trace data rather than inferring solely from code structure.

### Fault Testing

- Pool acquire timeout scenarios;
- Database connection refusals and restarts;
- Statement/lock timeouts;
- Serialization/deadlock retry mechanisms;
- Commit failures or disconnections near commit points;
- Migration mid-flight failure and recovery procedures;
- Credential rotation and TLS certificate updates (when applicable).

### Release Observability

- Migration duration, lock waits, replication lag metrics;
- Pool active/idle/waiter counts and acquire latency measurements;
- Aggregate query latency/error/timeout statistics by low-cardinality labels;
- Constraint violation detection, deadlock occurrences, serialization retry events;
- Rollback progress rates and remaining quantities;
- Error rates and compatibility analysis between old and new application versions.

### Key Resources

- [SQLx testing attribute](https://docs.rs/sqlx/latest/sqlx/attr.test.html)
- [Diesel test transaction](https://docs.rs/diesel/latest/diesel/connection/trait.Connection.html#method.test_transaction)
- [PostgreSQL EXPLAIN documentation](https://www.postgresql.org/docs/current/sql-explain.html)
- [RustSec guidelines](https://rustsec.org/)
