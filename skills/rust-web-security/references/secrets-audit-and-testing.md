# Secrets, Auditing and Testing

## Secret Lifecycle

For each secret record: owner, purpose, scope, storage, loading, key ID, creation/expiry, rotation, revocation, and event response. Avoid writing secrets to env dumps, panics, Debug traces, metric labels, URLs, test fixtures or snapshots.

`secrecy`/`zeroize` can reduce accidental formatting and clean up memory under specific conditions but cannot guarantee swap core dump protection, copy security, intermediate parsing buffer confidentiality, or in-process attack resilience. Use `ExposeSecret` only for the minimal call scope required.

## Logging and Auditing

- Mark sensitive headers (Authorization, Cookie, Set-Cookie), cookies, etc., as header/body fields before recording them in TraceLayer;
- Process structured fields to handle CR/LF control characters and prevent log injection attacks;
- Do not record raw credentials or tokens on authentication failures;
- Audit events must include actor, tenant, action, target, outcome, policy/reason code, request ID, timestamp;
- Record changes before and after roles, policies, keys, sessions, and sensitive data modifications;
- Ensure audit storage is append-only, access-controlled, retained for compliance purposes, and protected against integrity tampering.

## Negative Test Matrix

| Control | Must-Fail Condition |
|---|---|
| JWT/OIDC | Invalid signature, algorithm mismatch (`alg`), issuer/audience validation errors (`iss`, `aud`), expiration/nbf/typ/kid rotation failures |
| Session | Fixed session ID, premature expiry, logout behavior, revocation handling, concurrent session issues, cookie attribute manipulation |
| Authorization | Anonymous access, tenant-level privilege escalation (same or cross-tenant), batch operations, field-level authorization bypasses, admin scope leakage |
| CSRF/CORS | Malicious Origin headers, missing tokens, invalid/expired tokens, preflight requests with wildcard credentials |
| SSRF | Loopback addresses (`127.0.0.1`/`::1`), private interfaces, IPv6 exposure, metadata leaks, DNS address resolution attacks, redirect schemes, dangerous protocols (e.g., `file`, `gopher`) |
| Abuse | Excessively large request bodies, slow response times, brute-force login attempts, high-cost cryptographic operations, concurrency and pagination limit violations |
| Disclosure | Errors in logging/trace/metrics/policy execution; absence of secrets during audit events or panic conditions |

Tests must not invoke uncontrolled public IdP/services. Use local test issuers, fake servers, or isolated environments while retaining a small subset of controlled end-to-end validations to confirm deployment configurations are secure.

## Supply Chain

- Review `Cargo.lock`, direct dependency owners/maintainers status, crypto/TLS backend implementations and feature flags;
- Run RustSec `cargo audit` per project policy; run `cargo deny` for critical projects following defined strategies;
- Advisory entries with ignored issues must include risk assessment, expiration date, and remediation plan;
- Special scrutiny required on crates sharing names or similar identifiers, git/path-based sources, and previously withdrawn versions;
- Include SBOMs in auditable builds and dependency updates within the release pipeline;
- After upgrading security-related crates, re-run protocol tests and negative test suites—do not skip testing solely due to compilation.

## Main References

- [tower-http sensitive headers](https://docs.rs/tower-http/latest/tower_http/sensitive_headers/)
- [secrecy crate documentation](https://docs.rs/secrecy/)
- [RustSec project page](https://rustsec.org/)
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [OWASP REST Assessment Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/REST_Assessment_Cheat_Sheet.html)
