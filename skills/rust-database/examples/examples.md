# Database Scenario Examples

## Scenario: Establishing Transaction Boundaries for Transfer Use Cases

User Request:
Implement account transfers using SQLx. Ensure that if a debit succeeds but an entry fails, no partial commit occurs.

Execution Order:

1. Confirm database version, balance type, non-negative constraints, and current isolation level;
2. Open one transaction in the application service and pass it to both repository operations within the same transaction scope;
3. Use conditional updates or locking mechanisms to prevent concurrent overdrafts, verifying affected rows count;
4. If debit entry and audit/outbox belong to the same atomic boundary, write them together into a single operation;
5. Commit only if all steps succeed; failure of any step results in rollback without reporting success;
6. Conduct real-world parallel transfer tests against two concurrent transfers to validate total balance constraints and individual account balances.

## Scenario: Adding Non-Null Columns to Large Tables

User Request:
Add a non-null `tenant_id` column to the production `orders` table, avoiding prolonged downtime.

Do not assume that an `ALTER TABLE ... ADD COLUMN` operation is safe without verification. First confirm database version, table size, and lock semantics, then plan accordingly:

```text
Add compatible columns/indexes
  -> Deploy dual-write mode for old/new compatibility
  -> Batch backfill using stable primary keys
  -> Validate NULL handling and tenant mappings
  -> Enable and verify constraints
  -> Switch read paths to new schema
  -> Clean up legacy path after windowed migration completion
```

Each step must define pause conditions, rollback triggers, and monitoring thresholds. Reversible or irreversible corrections require separate authorization approval.
