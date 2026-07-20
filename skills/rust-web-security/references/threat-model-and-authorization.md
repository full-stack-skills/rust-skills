# Threat Modeling and Access Control

## Minimum Threat Model

| Item | Question |
|---|---|
| Assets | Which data, permissions, keys, and business actions require protection? |
| Attackers | Anonymous users, regular users, cross-tenant users, stolen tokens, malicious services, or internal personnel? |
| Entry Points | Routes, callbacks, webhooks, uploads, management endpoints, background tasks, message consumers? |
| Trust Boundaries | Where are CDN, LBs, sidecars, IdPs, databases, and external APIs located? |
| Abuse Scenarios | Enumeration, privilege escalation (over-privilege), replay attacks, bulk scraping, resource exhaustion, automated workflows? |
| Controls | Authentication, authorization, constraints, rate limiting, idempotency, auditing, manual confirmation? |
| Evidence | Which tests, configuration checks, or operational metrics demonstrate that controls are effective? |

## Authorization Model

Decide using the following signature:

```text
allow(principal, action, resource, tenant, context) -> allow \n\ndeny
```

- `principal`: Derived from a verified authentication boundary;
- `action`: Specific operation (avoid vague terms like "access");
- `resource`: Includes owner, tenant ID, state, and sensitive attributes;
- `context`: Uses only trusted signals; do not directly trust client-declared roles or tenants. If no matching rule exists, deny.

RBAC is suitable for coarse-grained roles; ABAC/ReBAC suits ownership-based policies and organizational relationships. In practice, systems often combine these models, but strategies must have a single decision entry point and comprehensive test matrices.

## Multi-Tenancy

- `tenant` identity should be derived from trusted identities/domains—not directly extracted from request bodies or query parameters;
- Queries first filter by tenant ID before retrieving objects. While "checking existence after retrieval" may still expose presence information, it can also introduce omissions if not handled carefully;
- Unique constraints and cache keys must include the `tenant` dimension to ensure isolation at both storage and access levels;
- Explicitly distinguish between `tenant admin` permissions versus platform-level administrative privileges;
- Batch operations (exporting data), searches, statistics queries, and background jobs must also enforce tenant isolation.

Database Row-Level Security (RLS) policies, connection roles, and application-level authorizations should align across tenants with explicit cross-tenancy negative testing to prevent unauthorized access or leakage of sensitive information between tenants.

## Sensitive Business Flows

Additional controls are required for high-risk operations such as password/email changes, payments, key generation, bulk exports, role modifications, etc.: re-authentication, MFA, transaction confirmation, rate limiting, idempotency, and dual approval mechanisms should be selected based on risk levels. Ordinary login states alone cannot satisfy all requirements of high-risk actions without further safeguards.

## Test Matrix

Each endpoint must cover at least the following scenarios: anonymous users; legitimate principals within a tenant; other principals in the same tenant; cross-tenant entities; expired or revoked tenants; regular administrators and overprivileged field access attempts. 404/403 responses should align with information leakage policies, ensuring consistency across all test cases.

## Key References

- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [OWASP API1: Broken Object Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/)
- [OWASP Transaction Authorization](https://cheatsheetseries.owasp.org/cheatsheets/Transaction_Authorization_Cheat_Sheet.html)
