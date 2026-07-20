# Migration and Schema Evolution

## Change Log

Each migration record must include: target database version, estimated data volume, lock risk, backward/forward application compatibility, backfill strategy, validation steps, recovery procedures, and responsible owner. Once a migration file is executed in the shared environment, do not modify its content locally; instead, create new correction migrations as needed.

## Expand / Contract

1. **Expand**: Add nullable columns, new tables, or compatible indexes without breaking existing applications.
2. **Deploy compatible code**: New code must handle both old and new data formats effectively.
3. **Backfill**: Execute in bounded batches with retry logic, pause capability, progress tracking, and error logging.
4. **Switch**: Transition read paths or constraints while monitoring relevant metrics.
5. **Contract**: Confirm all downstream consumers have completed their migrations before removing deprecated columns, indexes, or query paths.

Double-writes can introduce partial successes and ordering issues; unless a clear consistency protocol is defined in advance, do not treat double-write as the default approach.

## DDL Risks

- `ALTER`, index construction, and constraint validation operations exhibit varying lock semantics across databases and versions.
- Large tables with defaults, type conversions, or table rewrites may generate long locks or substantial WAL/binlog activity.
- Down migrations cannot recover data that has already been lost; "executable down" does not equate to safe rollback.
- Before performing deletion, truncate, reconstruction, or irreversible cleaning operations, ensure backups/snapshots exist and restore procedures are verified.
- Production-grade migrations should utilize dedicated permissions and audit logging rather than application superuser credentials.

## Data Backfill

- Use stable primary keys or cursor-based batching to avoid reliance on unstable offsets.
- Each batch must include timeout limits, rate limiting, idempotency keys, and progress tracking.
- Both old and new applications running concurrently must observe consistent intermediate states during backfill.
- After completion, validate counts, NULL values, constraints, and sampled content via independent queries.
- Separate the backfill process from DDL operations to prevent single long-running transactions.

## Validation

- Execute migrations on an empty database to verify full execution integrity.
- Run validation at each supported upgrade point.
- Verify migration checksums and ordering consistency.
- Compare expected schema against actual schema output.
- Measure lock contention, latency, and additional memory usage under representative data volumes.
- Simulate rollback procedures in case of failure during backfill or deployment.

## Key Resources

- [SQLx Migrations](https://docs.rs/sqlx/latest/sqlx/migrate/)
- [Diesel CLI Configuration](https://diesel.rs/guides/configuring-diesel-cli)
- [SeaORM Migrations](https://www.sea-ql.org/SeaORM/docs/migration/setting-up-migration/)
- [PostgreSQL ALTER TABLE Documentation](https://www.postgresql.org/docs/current/sql-altertable.html)
