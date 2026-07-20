# Client Configuration and Transport

## reqwest or Hyper

Start with reqwest for JSON APIs, forms, multipart, proxies, redirects, cookies, compression, and ordinary streaming. Use Hyper directly only when the application needs low-level `Service`, connector, body, upgrade, or protocol control and can own the additional lifecycle complexity.

Reuse `Client`; it owns a connection pool. Record enabled Cargo features because TLS backend, HTTP/2 or HTTP/3, compression, cookies, proxy discovery, DNS, blocking, and streaming affect binaries, platforms, and behavior.

## Timeouts and pools

Define:

- connect timeout;
- overall request deadline;
- pool idle timeout and maximum idle connections per host where relevant;
- read or body progress limits at the application layer;
- maximum concurrent requests globally and per origin.

A timeout aborts waiting but does not make the remote operation transactional. For state-changing requests, determine whether the server may have committed before the client timed out.

## DNS, proxies, and redirects

System proxy discovery may read environment variables. Decide whether deployment configuration is trusted and test `NO_PROXY` behavior. Prevent credentials from crossing origins through redirects or proxy changes.

For user-controlled destinations, validate every redirect and resolved address. DNS rebinding defenses require connection-time address policy, not only string validation before resolution.

## TLS

Prefer maintained default verification. Review any custom root store, client identity, certificate pinning, hostname verifier, SNI override, key log, early data, or disabled verification as a security-sensitive change. Compile and test each supported platform backend.

## Sources

- [reqwest ClientBuilder](https://docs.rs/reqwest/latest/reqwest/struct.ClientBuilder.html)
- [Hyper client guide](https://hyper.rs/guides/1/client/basic/)
- [rustls](https://rustls.dev/docs/)
