---
name: rust-http-client
description: Design, implement, test, and operate resilient Rust outbound HTTP clients with reqwest, hyper, Tower middleware, connection pooling, DNS, proxies, TLS, redirects, deadlines, retries, rate and concurrency limits, streaming bodies, cancellation, SSRF controls, and mock or real-server contract tests. Use when users ask to call REST APIs, download or upload data, configure an HTTP client, diagnose connection failures, or harden service-to-service requests; keep inbound servers in rust-web.
---

# Rust HTTP Client

Treat outbound HTTP as a resource and trust boundary. Reuse a configured client, bound every stage, preserve protocol errors, and make retry, credential, proxy, and destination policy explicit.

## Scope and Routing

Use this skill for HTTP/1.1, HTTP/2, optional HTTP/3 support, request construction, connection pools, DNS, proxies, TLS, redirects, retries, streaming, and client-side tests.

Route inbound routers and handlers to `rust-web`, SSRF and credential policy to `rust-web-security`, task lifecycle and bulk concurrency to `rust-concurrency`, telemetry to `rust-observability`, and raw TCP/UDP or protocol implementation to the later network-protocol skill.

## Workflow

### 1. Define the remote contract

Record base URLs, methods, path and query encoding, headers, authentication, request and response schemas, status semantics, idempotency, body limits, pagination, rate limits, timeout budget, retry policy, proxy and TLS requirements, and supported platforms. Inspect locked dependency versions and enabled features.

### 2. Build and reuse one configured client

Use `reqwest::Client` for ordinary application HTTP. Reuse it to retain connection pooling. Use Hyper when lower-level connection, body, or protocol control is a real requirement rather than an optimization guess.

```rust
use std::time::Duration;

let client = reqwest::Client::builder()
    .connect_timeout(Duration::from_secs(3))
    .timeout(Duration::from_secs(15))
    .redirect(reqwest::redirect::Policy::limited(3))
    .build()?;
```

Do not construct a client per request. Decide deliberately whether system proxies, redirects, cookies, compression, native roots, or custom roots are allowed. Read [Client Configuration and Transport](references/client-configuration-and-transport.md).

### 3. Bound requests and responses

- Apply an overall deadline plus stage-specific limits where supported.
- Limit concurrent in-flight requests before allocating large bodies.
- Stream uploads and downloads instead of buffering untrusted content.
- Enforce both advertised and actual decoded body size; `Content-Length` may be absent or misleading.
- Bound pagination, redirects, decompression, retries, and error-body capture.
- Preserve cancellation by dropping or selecting over the request future; verify cleanup at the caller boundary.

### 4. Retry only safe operations

Retry transport failures or selected statuses only when the operation is idempotent or protected by an idempotency key. Use bounded attempts, exponential backoff with jitter, a total deadline, and server hints such as `Retry-After` when valid. Never retry authentication failures or every `5xx` blindly. Place timeout, retry, concurrency limit, rate limit, load shedding, and circuit-breaker policies in a documented order. Read [Resilience and Backpressure](references/resilience-and-backpressure.md).

### 5. Enforce trust boundaries

- Parse destinations with `url`; never concatenate untrusted URLs.
- Restrict schemes, hosts, ports, redirect targets, DNS results, and private/link-local ranges for user-controlled destinations.
- Scope credentials to approved origins and strip sensitive headers on cross-origin redirects.
- Keep TLS verification enabled; review custom roots, client certificates, SNI, ALPN, and key logging.
- Decide whether environment proxies are trusted; use `no_proxy` or explicit proxy rules when needed.

Coordinate security policy with `rust-web-security`.

### 6. Test at several boundaries

- Unit-test request construction, URL encoding, auth selection, retry decisions, and response mapping.
- Use a mock server for status, headers, delays, redirects, truncated bodies, and malformed payloads.
- Use a real local server for sockets, streaming, cancellation, pooling, proxy, and TLS behavior.
- Keep a small external sandbox or provider contract test only when authorized and stable enough for CI.

Read [Testing HTTP Clients](references/testing-http-clients.md).

## Completion Criteria

- Reuse a client with explicit features, proxy, redirect, DNS, and TLS policy.
- Bound deadlines, concurrency, retries, redirects, pagination, and body size.
- Preserve structured transport, protocol, decoding, and application errors.
- Retry only operations with a proven replay contract.
- Prevent credential leakage and SSRF through destinations or redirects.
- Test success, timeout, overload, redirect, large body, malformed response, and cancellation paths.

## Resources

- [Client Configuration and Transport](references/client-configuration-and-transport.md)
- [Resilience and Backpressure](references/resilience-and-backpressure.md)
- [Testing HTTP Clients](references/testing-http-clients.md)
- [Execution Scenarios](examples/examples.md)
- `examples/golden-http-client/`: a compiled bounded blocking client against a local server.

## Upstream Sources

- [reqwest](https://docs.rs/reqwest/)
- [Hyper](https://hyper.rs/)
- [Tower](https://docs.rs/tower/)
- [rustls](https://rustls.dev/docs/)
- [url](https://docs.rs/url/)

## Data Privacy

This skill does not collect, store, or transmit user data. Do not send real credentials, customer payloads, or private endpoints during tests without explicit authorization.
