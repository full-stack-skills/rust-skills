# Testing HTTP Clients

## Test layers

| Layer | Proves |
|---|---|
| Pure unit test | URL, headers, auth, retry and mapping decisions |
| Mock HTTP server | Request shape, status, delay, redirect, malformed and size behavior |
| Real local server | Socket, streaming, connection reuse, cancellation, proxy and TLS integration |
| Provider sandbox | External compatibility when authorized |

Do not mock the reqwest API so deeply that tests only reproduce implementation calls. Prefer observing the request received by a local server.

## Required failure cases

- connection refused and DNS failure;
- connect and overall timeout;
- redirect loop and redirect to a forbidden origin;
- `429` and `Retry-After` handling;
- selected retryable and non-retryable `5xx` responses;
- partial or truncated body;
- body larger than the configured limit, including decoded compression growth;
- malformed JSON or protocol fields;
- caller cancellation while connecting, sending, or reading;
- proxy and certificate failure where those features are supported.

Use deterministic clocks or small bounded delays. Assert attempts, elapsed budget, final error category, and that credentials were not forwarded unexpectedly.

## Sources

- [reqwest](https://docs.rs/reqwest/)
- [wiremock](https://docs.rs/wiremock/)
- [httpmock](https://docs.rs/httpmock/)
