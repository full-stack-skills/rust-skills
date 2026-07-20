# Rust HTTP Client Execution Scenarios

## Resilient JSON API client

User request:

> Build a reqwest client for a partner API with bearer auth, timeouts, pagination, and retries.

Define the provider contract, reuse one configured client, bound pagination and response size, classify errors, and retry only idempotent operations within one deadline. Test authentication scope, `429`, selected `5xx`, malformed JSON, timeout, and cancellation.

## Secure URL fetcher

User request:

> Fetch a user-provided URL and return the first megabyte.

Coordinate with `rust-web-security`. Restrict schemes, ports, hosts, DNS results, redirects, proxies, credentials, decompression, and actual streamed bytes. Reject private and link-local destinations according to policy and retest after every redirect.

## Diagnose latency under load

User request:

> This service creates many reqwest requests and p99 latency grows continuously.

Check whether clients are recreated, pools or queues are unbounded, responses are fully consumed, blocking work runs on async workers, retries amplify load, or a downstream origin saturates. Add admission limits and observability before tuning pool sizes.
