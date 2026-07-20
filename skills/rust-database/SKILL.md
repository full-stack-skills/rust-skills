---
name: rust-database
description: Design, implement, migrate, test, and operate Rust database access, including SQLx, Diesel, SeaORM, schema evolution, transaction boundaries, connection pools, retries, type mapping, concurrency control, and real-database verification. Use when users ask about Rust SQL or ORM code, migrations, transactions, PostgreSQL or MySQL integration, connection pools, query safety, or database production readiness.
---

# Rust Database Layer Delivery

Deliver a migration-compatible, rollback-capable, and observable data access layer based on the actual dialects, schemas, and transaction semantics of databases. Do not treat HTTP handlers as repositories; do not use mocks to validate real database behavior.

## Confirming Database Contracts

Before modifications:
- Collect information about the database product, exact version, extensions, deployment topology, read/write nodes;
- Gather current schema constraints, indexes, triggers, views, and migration history;
- Identify locked versions of SQLx, Diesel, SeaORM (or other access stacks) along with their features;
- Determine Rust toolchain/MSRV, synchronous or asynchronous execution models;
- Establish connection limits, instance counts, timeouts, transaction isolation levels, and consistency requirements;
- Define data volume profiles, hot query patterns, pagination strategies, retention policies, and archival needs;
- Document credential sources, TLS configurations, tenant boundaries, row-level permissions, and audit requirements;
- Clarify whether deployments allow downtime, double writes, backfills, or destructive DDL operations.

When real database access is unavailable, distinguish between "code/offline metadata validation" and "real dialect validation." Do not conflate these two approaches in reporting.

## Workflow

### 1. Establish Current Baseline
```bash
rustc --version --verbose
cargo metadata --format-version 1
cargo tree -e features
cargo test --all-targets
```
Locate connection initialization, pool configuration, repository implementations, queries, migrations, test fixtures, and CI database connections. Execute existing migration status/check commands; do not run operations that modify shared databases without explicit authorization.

### 2. Preserve Existing Access Stacks
Avoid rewriting solely based on preference among SQLx, Diesel, or SeaORM. Select the appropriate stack according to current codebase and task requirements:
- **SQLx**: Requires direct SQL access, asynchronous querying, and optional compile-time query validation;
- **Diesel**: Utilizes typed DSL queries, synchronous connections, or existing Diesel schemas;
- **SeaORM**: Leverages async ORM/entity models with corresponding migration systems;
- **Native database drivers**: Reserved for cases where protocol or functionality does not support a generic layer, though expanding maintenance and security review scope.

Specific selection criteria and type boundaries are documented in [Access Stack and Types](references/access-stack-and-types.md). All APIs must align with the versioned documentation from `Cargo.lock`, avoiding direct application of latest examples to legacy projects.

### 3. Let Schema Constraints Enforce Facts
- Define primary keys, uniqueness constraints, foreign keys, non-null checks, and check constraints as immutable invariants guaranteed by the database;
- Rust types express domain semantics but cannot replace cross-process concurrency guarantees provided by databases;
- Explicitly specify integer widths, decimal precision, timezones, UUIDs, JSON formats, nullability mappings;
- Bind parameters to all queries. Use dynamic identifiers or sort fields only via allowlists and type mapping—not as regular bind values pretending to be safe;
- Restrict column selection to necessary columns to avoid reliance on unstable `SELECT *` layouts;
- Prioritize stable sorting strategies and keyset-based pagination over unbounded offset operations under high data volumes.

### 4. Design Migrations Before Code Changes
For each schema change, document:
1. Forward DDL statements;
2. Compatibility windows between old and new versions for applications;
3. Data backfill methods, batch sizes, and rollback points;
4. Index construction risks and lock contention implications;
5. Rollback or forward recovery strategies;
6. Validation queries, monitoring metrics, and termination conditions.

Adopt the sequence: expand → backfill → switch → contract. Destructive operations—column deletion, type changes, large table reconstruction, data clearing, irreversible backfills—require explicit target parsing and authorization details found in [Migrations and Schema Evolution](references/migrations-and-schema.md).

### 5. Place Transactions Within Complete Use Cases
- Initiate transactions via application services or repository unit-of-work units; do not commit transactionally across HTTP handlers indiscriminately;
- Ensure atomic success of writes within a single shared transaction and connection set;
- Avoid unbounded user interactions outside the transaction scope, including unnecessary external HTTP waits inside transactions;
- Select isolation levels per database documentation to identify risks such as lost updates, write skew, phantom reads;
- Retry only transient errors explicitly identified by the database. Set retry counts, backoff strategies, and idempotency boundaries;
- Commit failures are possible; do not treat "last SQL statement success" as transactional completion;
- Drop/rollback serves as a safety net but does not replace explicit control flow design or testing practices.

Connection pooling, isolation levels, and retry mechanisms are detailed in [Transactions and Pooling](references/transactions-and-pooling.md).

### 6. Design Stable Data Access Interfaces
```text
application use case
  -> repository / unit of work port
  -> SQL/ORM adapter
  -> database
```
- Repository methods should accept domain parameters and results without leaking Web DTOs;
- Classify errors into categories: not found, uniqueness conflicts, foreign key violations, serialization failures, timeouts, unavailability;
- Preserve full error chains for logging and diagnostics while preventing sensitive SQL parameter exposure in user responses;
- Batch interfaces must define ordering semantics, partial failure handling, idempotency guarantees, and return row counts;
- Avoid N+1 queries. Validate performance under realistic data scales when pre-fetching joins or batching is required.

### 7. Configure Limited Connection Budgets
Validate total connection budgets using the formula: `(per-instance pool limit × maximum instance count) + operational connections`. Set acquire, connect, statement, and transaction timeouts; define idle/max lifetimes, health checks, and graceful shutdown procedures. Do not instantiate a new pool per request nor let indefinite waits mask resource exhaustion issues.

### 8. Validate with Real Engines
Conduct at least the following validations:
1. Execute all migrations from an empty database;
2. Upgrade schema versions supported by existing databases;
3. Verify repository success, missing records, constraint conflicts, and type boundaries;
4. Test transaction commits, rollbacks, commit failures, and retryable concurrency issues;
5. Ensure invariants hold under concurrent writes;
6. Confirm query plans, index hits, and representative data volumes;
7. Assess pool exhaustion scenarios, database restarts/disconnections, and graceful shutdown behaviors;
8. Verify logs, metrics, and traces do not leak bound values or credentials.

Test execution and operation lists are provided in [Testing and Operations](references/testing-and-operations.md).

## Common Gates (Gateways)

```bash
cargo fmt --all -- --check
cargo check --all-targets
cargo test --all-targets
cargo clippy --all-targets -- -D warnings
```
Run repository-specific migration validation, SQLx offline metadata checks, Diesel schema audits, or real database integration tests. Commands and features may vary by version; consult project configuration first.

## Completion Criteria
- Database versions, schemas, access stacks, and consistency assumptions are clearly defined;
- All queries use parameterization with dynamic identifiers filtered via allowlists;
- Migration compatibility windows, backfill strategies, recovery procedures, and destructive boundaries are documented;
- Transaction coverage spans complete use cases with justified connection budgets and timeouts;
- Real database testing validates migrations, constraints, rollbacks, and concurrency risks;
- fmt, check, test, Clippy pass; unvalidated real-database tests must be explicitly marked.

## Handoff Boundaries

| Primary Responsibility | Assigned To |
|---|---|
| HTTP routing, handlers, status codes, middleware | `rust-web` |
| Credentials, tenant authorization, audit logs, sensitive field exposure | `rust-web-security` |
| Async cancellation, locks, tasks, blocking isolation | `rust-concurrency` |
| Test layering, coverage metrics, performance baselines | `rust-testing` |
| Features, build scripts, offline metadata, release pipelines | `rust-cargo-build` |
| Types, ownership semantics, error traits, standard library behavior | `rust-stable` |

## On-Demand Resources
- [Access Stack and Types](references/access-stack-and-types.md): Consult when selecting or adapting SQLx, Diesel, SeaORM, or type mappings.
- [Migrations and Schema Evolution](references/migrations-and-schema.md): Review DDL design, compatibility backfills, and recovery strategies.
- [Transactions and Pooling](references/transactions-and-pooling.md): Refer for atomicity guarantees, isolation levels, retry logic, and capacity management.
- [Testing and Operations](references/testing-and-operations.md): Access real-database test setups, query plans, observability practices.
- [Scenario Examples](examples/examples.md): Use this template when end-to-end task decomposition is required.
- `examples/golden-transaction/`: Offline compilation and validation of transaction boundary examples available here.

## References
- [`std::error`](https://doc.rust-lang.org/stable/std/error/) (Rust Standard Library)
- [SQLx documentation](https://docs.rs/sqlx/)
- [Diesel guides](https://diesel.rs/guides/)
- [SeaORM documentation](https://www.sea-ql.org/SeaORM/)
