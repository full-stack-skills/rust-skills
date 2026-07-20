---
name: rust-web-security
description: Threat-model, implement, review, and test Rust web security, including authentication, object and tenant authorization, sessions, cookies, JWT and OIDC validation, CSRF, CORS, SSRF, input limits, secrets, cryptographic dependency boundaries, audit logging, and negative security tests. Use when users ask to secure or audit Rust web services, tokens, browser transport, multi-tenant access, secret handling, or security incident fixes.
---

# Rust Web Security Delivery

Establish attacker, asset, and trust boundaries first; then select crates and middleware. Rust's memory safety does not automatically provide authentication, authorization, protocol enforcement, or business logic security; default to deny all, and use negative testing to prove control is effective.

## Confirming the Security Contract

Before modifications:
- Identify service exposure surfaces, callers, browser/API/service-to-service traffic, and management endpoints;
- Determine where TLS terminates, which proxies are trusted, and how client IP/host/scheme originates;
- Define identity providers, authentication protocols, token/session types/lifecycles;
- Specify roles, scopes, object ownership, tenant boundaries, and sensitive business operations;
- Manage key storage/renewal for cookies, passwords, API keys, webhooks;
- Configure CORS, CSRF, redirects, uploads, outbound URLs, and webhook scenarios;
- Define rate limiting budgets per body size/parallelism/timeout requirements and abuse resistance policies;
- Establish audit event definitions, privacy standards, compliance needs, and incident response procedures;
- Lock versions of `axum`, `tower`, `rustls`, `cookie` crates along with Rust MSRV.

When security requirements are incomplete, explicitly state assumptions and uncovered risks. Do not bypass validation by weakening tests to achieve pass/fail outcomes.

## Workflow

### 1. Establish Attack Surface and Baselines
```bash
rustc --version --verbose
cargo metadata --format-version 1
cargo tree -e features
cargo test --all-targets
```
Enumerate all routes, methods, extractors, middleware proxies callbacks management endpoints outbound requests. Identify authentication context establishment points authorization decision points session/token storage key loading and audit logging locations. Run existing repository security gates; install or upgrade security tools must comply with project constraints.

### 2. Write Threat Model and Authorization Matrix
Record at minimum:
```text
Asset -> Entry Point -> Trust Boundary -> Attacker Capability -> Control -> Verification Evidence
```
Construct subject × action × resource × tenant × context matrices for each sensitive operation. Authentication only proves "who"; authorization must verify in every request whether the user can perform this action on that object. Default deny; do not rely solely on login checks or frontend button visibility.

Object-level, attribute-level, and tenant-based authorization details are available at [Threat Model and Authorization](references/threat-model-and-authorization.md).

### 3. Establish Identity in a Single Boundary
- Use mature IdP/protocols with maintained crates; do not invent token/password protocols yourself;
- Convert authentication results into minimal `Principal`/claims contexts;
- Failures of auth middleware must terminate requests without anonymous identity fallbacks to silent downgrade;
- Return 401 for missing or invalid credentials, and 403 when identity is known but permissions are denied;
- Management, internal, and user identities require distinct audiences, scopes, or credentials;
- For high-risk operations requiring re-authentication, MFA, or transactional confirmation without relying on stale sessions.

### 4. Correctly Validate Tokens, Sessions, and Passwords
JWT validation must enforce fixed allowed algorithms verifying signatures, issuer, audience, expiry, not-before, token type/scope requirements; different token types require mutually exclusive verification rules with JWKS caching/renewal handling. Decoding headers/claims does not constitute valid authentication.

Cookie sessions should include `Secure`, `HttpOnly` flags aligned to threat models for `SameSite`, minimal `Path`; typically omit broad `Domain`. Rotate session IDs after login and privilege escalation; define server-side invalidation and absolute/idle expiration upon logout or revocation.

Password hashing uses maintained password-hashing APIs with Argon2id-like parameters measured per deployment size; avoid generic fast hashes. Expensive KDFs must not block async runtime workers. API keys/tokens should be displayed once, stored in verifiable forms with scope prefixes, expiry, and renewal capabilities. OAuth/OIDC/JWT/session/password/API key details are covered at [Authentication Tokens and Sessions](references/auth-tokens-and-sessions.md).

### 5. Authorize Each Resource Boundary
- Authorization inputs include trusted principals, actions, actual resource attributes, and tenant;
- Query by tenant first, then object/field permissions to prevent BOLA/IDOR attacks;
- Management roles must have explicit scopes; do not treat `is_admin` as a global escape hatch;
- Batch operations authorize per-object or via equivalent database policies;
- Write DTOs use allowlists preventing mass assignment of sensitive fields like role, tenant, owner;
- Cached authorization results include policy version, subject, resource, action, and expiration.

Database Row Level Security (RLS) provides defense-in-depth but cannot replace application-level strategies and testing.

### 6. Harden Browser and Transport Boundaries
- Enforce full HTTPS coverage with HSTS, certificates, mTLS, and TLS policies validated at the actual termination layer;
- Trust only forwarded headers explicitly injected by trusted proxies to avoid host/scheme/IP spoofing;
- CORS defines browser read strategies rather than server-side access control; use precise origin allowlists when credentials are present;
Implement CSRF token defenses alongside state-changing cookie-based auth endpoints; rely on SameSite cookies solely to align protection against threats within the specific threat model.

Set Content Security Policy (CSP), frame, content-type, referrer, and cache headers matching the response body type. Apply rate limits on body size, header manipulation, uploads, pagination, parallelism, timeouts, and expensive operations. Prevent SSRF via user-controllable URL/webhook restrictions: limit scheme/host/port; parse all addresses to block private networks/metadata targets; re-verify after redirects.

Outbound responses also enforce size/type/time constraints. See [Browser Transport and Input](references/browser-transport-and-input.md) for specific checks.

### 7. Protect Secrets and Establish Audit
- Inject secrets from controlled configuration/secret managers into code, image layers, errors, or logs only; use `secrecy` types to reduce accidental exposure via Debug serialization without claiming memory isolation equivalence;
- Explicitly define key ID, owner, purpose, algorithm, creation/expiry/renewal/cancellation policies;
- Mark/sanitize sensitive body content before trace logging; audit login failures, permission denials, policy/role/key changes and high-risk operations.

Audit records must include actor, action, target, outcome, request ID, and timestamp without secrets. Prevent log injection attacks by limiting the number of attacker-controllable labels. Rotating or revoking production keys, sessions, users, tokens alters external state; only explicitly authorized actions may execute these changes.

### 8. Prove Control via Negative Testing
Cover at least:
1. Unauthenticated/expired requests with invalid issuer/audience/algorithms/token types;
2. Tenant-level permission gaps (same tenant vs cross-tenant), object ownership, and field-level privilege escalation;
3. Session fixation, logout/revoke scenarios, absolute/idle expiration policies;
4. CSRF/CORS preflight attacks against malicious origins/cookie attributes;
5. SSRF via private networks, IPv6, DNS multi-address resolution, redirects, non-HTTP schemes;
6. Large body sizes, slow requests, high concurrency costs and expensive authentication flows;
7. Error responses leaking trace IDs or audit log secrets;
8. Dependency vulnerabilities and feature/crypto backend changes.

See [Secrets Audit and Testing](references/secrets-audit-and-testing.md) for test/audit/supply chain documentation.

## Common Gates
```bash
cargo fmt --all -- --check
cargo check --all-targets
cargo test --all-targets
cargo clippy --all-targets -- -D warnings
cargo audit
```
`cargo audit` requires the tool and advisory data to be available. If either is unavailable, report that the audit was not run rather than claiming a pass. Supplement it with `cargo deny`, DAST, proxy/TLS configuration tests, and authorization-matrix validation according to repository policy.

## Completion Criteria
- Threat model, trust boundaries, and authorization matrices are explicit;
- All sensitive routes default to deny all and verify object/tenant/action ownership;
- Tokens/sessions/passwords/API keys use mature protocols with complete verification;
- TLS/proxies/CORS/CSRF/header/resource limits align with actual deployment configurations;
- Secrets do not appear in responses/logs; rotation/revoke policies are explicit;
- Negative testing and dependency audits pass; unverified IdP, proxies, TLS or production configs explicitly marked.

## Handoff Boundaries

| Primary Responsibility | Owner |
|---|---|
| Router, extractor, handler, middleware, shutdown logic | `rust-web` |
| User/session/tenant/API key persistence and transactions | `rust-database` |
| Async KDF isolation, timeouts, cancellation concurrency limits | `rust-concurrency` |
| Test layering, fuzz testing coverage/performance gates | `rust-testing` |
| Dependency features, crypto backend, build/release configuration | `rust-cargo-build` |
| Cryptography/FFI/unsafe implementation review | `rust-unsafe-ffi` |

## On-Demand Resources
- [Threat Model and Authorization](references/threat-model-and-authorization.md): Read when designing permissions, tenant boundaries, sensitive business flows.
- [Authentication Tokens and Sessions](references/auth-tokens-and-sessions.md): Access OIDC/JWT/cookie sessions/passwords/API keys during implementation.
- [Browser Transport and Input](references/browser-transport-and-input.md): Configure TLS/proxies/CORS/CSRF/header/uploads/SSRF checks when deploying services.
- [Secrets Audit and Testing](references/secrets-audit-and-testing.md): Handle secrets, logs, negative testing, dependency audits during implementation.
- [Crypto Dependency Boundaries](references/crypto-dependency-boundaries.md): Select AEAD/KDF/constant-time/clearing crates; review nonce/transcript/WASM or protocol versions when implementing cryptographic features.
- [Example Scenarios](examples/examples.md): Read for end-to-end task decomposition templates requiring production-ready examples.

`examples/golden-authorization/`: Offline compilation and validation of default deny/object/tenant authorization golden tests available here.
