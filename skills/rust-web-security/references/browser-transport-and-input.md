# Browser, Transmission and Input

## TLS and Proxying

- Explicitly define where termination occurs: application layer, sidecar proxy, load balancer (LB), or CDN;
- Enable HSTS only after confirming the entire domain and subdomain policy is enforced;
- Validate certificate renewal status, failure alerts, TLS policies, and internal hop configurations;
- mTLS identity mapping must verify certificate chains, purposes, Subject Alternative Names (SANs), revocation states, and rotation history;
- Accept `Forwarded`/`X-Forwarded-*` headers exclusively from controlled proxies; override external values at the entry point with trusted local data;
- When host/scheme/IP participates in redirection, cookie handling, signature verification, or rate limiting, test for spoofing attacks rigorously.

When using Rustls: construct configurations via secure builders and perform dedicated reviews of `danger` module usage, disabling validation checks, enabling key logging, activating early data transmission, implementing custom verifiers, and managing certificate lifecycle policies carefully.

## CORS and CSRF

- CORS determines whether browser scripts can read response bodies; it does not prevent curl-based attacks or server-side exploitation attempts by untrusted clients;
- When credentials are present, origins must be precisely matched to a controlled scheme/host/port combination rather than using arbitrary origin values;
- Do not use broad regex patterns allowing all subdomains unless every possible subdomain resides within the same trusted boundary;
- For cookie-based authentication write operations: utilize synchronizer tokens, implement signed double-submission mechanisms bound to sessions, or adopt framework-equivalent protection strategies;
`SameSite`, origin/referer headers, and fetch metadata form depth-of-defense layers that should be selected according to client compatibility needs.
- GET and HEAD requests must not execute state-changing operations; do not embed tokens in URLs or log sensitive data.

## Security Response Headers

Choose Content-Security-Policy (CSP) only if the response is HTML-based; API responses still require correct `Content-Type`, `X-Content-Type-Options` headers, caching directives, and frame policy enforcement. HSTS must be configured at the TLS termination layer—not duplicated or replicated across multiple layers without verifying that proxies do not strip, duplicate, or bypass these headers.

## Input and Resource Constraints

- Evaluate limits on body size, header fields, URL length, multipart file uploads, field counts, JSON depth, decompressed payload sizes;
- Assess pagination complexity, batch processing capabilities, search query volume, export data volumes;
- Analyze concurrency models, queue structures, timeout configurations, rate limiting policies, and per-request quotas for each entity type;
- Review upload filename validation, path traversal protection, MIME/type checking, content sanitization, storage isolation mechanisms, and virus scanning procedures;
- Ensure error responses do not leak stack traces, SQL injection details, internal hostnames, or sensitive secrets;
- Implement strict anti-mass-assignment controls: only deserialize fields explicitly permitted by the client to modify.

## SSRF (Server-Side Request Forgery) Prevention

- Prioritize using business-specific allowlists for allowed destinations and protocols;
- Restrict access strictly to required schemes and ports, deny userinfo parameters and dangerous protocol handlers entirely;
- Normalize hostnames/IP addresses: resolve A/AAAA records completely, block loopback interfaces (`127.0.0.0`), private ranges (`10.x`, `192.168.x`, etc.), link-local segments (`169.254.x`), metadata networks (e.g., 169.254.0.0/16, fe80::/10), and internal network subnets;
- Implement DNS resolution isolation between lookup operations and connection establishment to prevent rebinding or pinning bypasses via DNS tunneling or cache poisoning attacks;
- Re-validate hostnames/IPs after every redirect attempt with strict limits on the number of redirects allowed per request;
Deploy outbound proxy configurations and network segmentation policies to establish depth-based defenses against lateral movement across the internal network.
- Enforce response size, duration, and content restrictions to prevent exfiltration or command-and-control communication via redirected requests.

## Primary References

- [rustls server documentation](https://docs.rs/rustls/latest/rustls/server/)
- [tower-http CORS implementation guide](https://docs.rs/tower-http/latest/tower_http/cors/)
- [OWASP Cross-Site Request Forgery Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP Server-Side Request Forgery Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP HTTP Security Response Headers Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html)
