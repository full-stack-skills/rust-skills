# Web Security Scenario Examples

## Scenario: Fixing Cross-Tenant Object Privilege Escalation

User Request:
After logging in at `/documents/{id}`, the user can access documents they do not own. The current implementation only checks `is_authenticated`, which is insufficient. Instead, establish an authorization matrix and implement strict tenant-level constraints:

```text
verified Principal(tenant, subject, roles)
  -> query document constrained by tenant
  -> authorize read using owner/role/state
  -> return policy-consistent 404/403 if unauthorized
  -> audit denied access without leaking document data
```

Negative test coverage must include: other users within the same tenant; cross-tenant users; tenants with admin privileges; platform administrators, and bulk/search endpoints. Ensure no bypass paths exist.

## Scenario: Cookie-Based Authentication for SPA (Axum)

User Request:
Add authentication sessions to an Axum-based Single Page Application (SPA), allowing frontend domains to invoke APIs via cookies while respecting browser security policies.

First verify whether the request originates from a same-origin source, confirm TLS termination at the application layer, and validate native browser support for cookie handling. Then design the following controls:
- Server-side random session IDs; rotation of sessions after login;
- `Secure` flag to prevent transmission over unencrypted connections;
- `HttpOnly` attribute to mitigate XSS attacks;
- Minimal allowed path (e.g., `/auth/*`) and appropriate `SameSite` attributes (`Strict`, `Lax`, or `None`);
- Precise CORS origin configuration matching the frontend domain;
- Proper credential handling for cookie-based auth;
- CSRF protection against state-changing requests without tokens;
- Idle/absolute expiry policies to prevent stale sessions;
- Logout and password change mechanisms that invalidate all session states.

Test malicious origins, missing or malformed CSRF tokens, old session fixation attacks, and replay of invalidated sessions after logout.

## Scenario: Verifying External JWT Tokens from Enterprise IdP

User Request:
Integrate access tokens issued by an enterprise Identity Provider (IdP).

Fix the following security requirements:
- Use a fixed `discovery` endpoint to retrieve JWKS; cache and rotate them securely over time;
- Enforce explicit algorithm selection in claims, requiring specific fields such as `iss`, `aud`, `exp`, access-token type/scope, and `kid`.

Do not trust JWT claims solely after decoding. Validate:
- Incorrect audience (`aud`) values;
- ID token impersonation attempts (e.g., using an IdP-signed token where the application expects a client-side issued one);
- Unknown or mismatched key IDs (`kid`);
- Expired tokens and future `nbf` (not before) claims that may allow premature access.

Additionally, verify proper handling of JWKS rotation events to ensure continued validity without exposing sensitive keys prematurely.
