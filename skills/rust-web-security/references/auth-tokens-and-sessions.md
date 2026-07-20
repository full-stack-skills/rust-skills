# Authentication, Tokens and Sessions

## OAuth/OIDC

- Use the Authorization Code flow with applicable PKCE;
- Ensure exact matching of callback redirect URIs;
- Bind `state` to initiate sessions for CSRF protection, validate `nonce` when verifying ID tokens for replay semantics;
- Validate discovery endpoints/JWKS sources, issuer, and TLS configuration;
- Do not interchange access token (used by clients) with refresh token or ID token;
- Refresh tokens require secure storage, rotation, revocation mechanisms, and detection of reuse attempts;
- Never expose tokens in browser URLs, logs, or analytics data.

## JWT

- Enforce a fixed set of allowed algorithms without accepting arbitrary ones for token generation/validation;
- Trust claims only after verifying the signature;
- Require and validate `iss`, `aud`, `exp` according to protocol specifications, while validating `nbf`, `iat`, `sub`, `jti`, and `typ`;
- Configure distinct verification rules per issuer/audience/token type to prevent cross-JWT confusion attacks;
- Cache JWKS with security policies and enforce rotation; unknown `kid`s must not trigger unbounded external requests;
- Ensure clock skew is bounded and testable;
- When JWT revocation requirements are high, evaluate short-lived tokens or server-side state/opaque tokens rather than assuming JWTs cannot be revoked.

The default values for `jsonwebtoken` may vary depending on the feature set; explicitly specify required claims, issuer, audience, and algorithms, adhering to locked-down documentation versions as reference.

## Cookie Session

- Use CSPRNG (Cryptographically Secure Pseudo-Random Number Generator) for session ID generation;
- Do not include business-sensitive data in cookie content that could be inferred by clients or servers;
- Store only necessary state on the server side and avoid persisting plaintext tokens directly accessible from databases without additional protection;
- Rotate session IDs after successful login, privilege escalation, or high-risk recovery events;
- Configure cookies with `Secure`, `HttpOnly`, appropriate `SameSite` attributes, minimal valid `Path`, and exercise caution when setting `Domain`;
- Set idle timeout and absolute expiration times; invalidate sessions upon logout, password changes, or revocation requests;
- Cookies are automatically sent with browser requests, so state modifications require CSRF protection mechanisms.

If the session store fails, adopt a fail-closed strategy rather than degrading to trusting client-side cookies for security reasons.

## Passwords

- Use Argon2id hashing (or other compliant algorithms permitted by requirements) with unique salts;
- Persist password hash parameters in PHC format and measure CPU/memory usage during actual deployment to set appropriate concurrency budgets;
- Implement progressive rehashing when old passwords are detected after verification failure;
- Minimize user enumeration risks through login error messages and timing-based responses;
- Place Key Derivation Function (KDF) operations within restricted blocking work pools with enforced concurrency limits and rate limiting;
- If using a pepper, manage it via a secret manager that supports rotation policies;
- Do not store plaintext passwords or reset tokens.

## API Keys

- Generate keys sufficient in randomness but displayed only once per key lifecycle;
- Use short public prefixes for lookup purposes while servers maintain hashed/protected values corresponding to each key;
- Each key must include owner, scope, creation/expiry timestamps, last-used status, and revocation state;
- Support parallel rotation without sharing permanent global keys across services;
- Compare verification values using libraries that provide suitable methods rather than implementing custom "constant-time" comparison algorithms.

## Main References

- [RFC 8725](https://datatracker.ietf.org/doc/html/rfc8725)
- [OpenID Connect Core Specification](https://openid.net/specs/openid-connect-core-1_0.html)
- `jsonwebtoken` Validation API (Rust Docs): https://docs.rs/jsonwebtoken/latest/jsonwebtoken/struct.Validation.html
- Cookie crate documentation: https://docs.rs/cookie/
- OWASP Session Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
- OWASP Password Storage Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- RustCrypto Argon2 Documentation: https://docs.rs/argon2/
