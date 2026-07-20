# Password Dependency and Protocol Boundaries

Cryptographic crates provide primitives but cannot substitute for protocol design. The rmux web-crypto implementation separates KEM, X25519, HKDF, AEAD, record framing, transcripts, WASM bindings, and tests into distinct components; that separation is useful evidence. Do not copy a specific hybrid scheme without independent cryptographic review.

## Primitives and Crate Roles

| Purpose | Common crate | Protocol decision required |
|---|---|---|
| AEAD | `rust-crypto::chacha20poly1305` | nonce uniqueness, AAD handling, record limits, replay/sequence ordering |
| KDF | `hkdf`, `sha2` | salt, info/domain separation, output key usage |
| Key exchange | `x25519-dalek` | Identity authentication, downgrade protection, transcript binding |
| Constant-time comparison | `subtle` | Full system side-channel analysis, compilation targets, error timing |
| Memory zeroing | `zeroize` | Copies, registers, swap/core dumps, lifetimes |
| Random number generation | `getrandom`, `rand_core` | Entropy failure strategies, test RNG isolation vs. production RNG |
| WASM boundary | `wasm-bindgen` | JS typed array copying, exceptions, reproducible builds with CSP constraints |

Selection of algorithms, parameters, hybrid/PQ combinations, authentication methods, and protocol upgrades must be determined by standardization bodies, threat models, and expert review.

## Record Protocol Checks

1. Each direction uses an independent key/nonce space;
2. Nonces/counters are never reused; sessions must be forcibly reconstructed before overflow occurs;
3. AAD binds the protocol version, direction, message type, sequence number, and context;
4. Before decryption, verify frame length; authentication failures should not reveal distinguishable internal details;
5. Reject replay attacks, out-of-order messages, or explicitly defined acceptable windows;
6. Transcript covers both parties' hello exchanges, algorithm selection, public keys, and roles;
7. Key schedule derives different-purpose keys using domain-separated labels;
8. On close/error paths, clear secrets but do not claim `zeroize` has cleared all copies.

## API Boundaries

- The `secret` type must not implement leaking traits like `Debug` or `Serialize`;
- Using `Zeroizing<T>`/`ZeroizeOnDrop` still requires minimizing clone operations and cross-language copying;
- Public APIs should expose session and record operations but not internal keys that can be arbitrarily combined;
- WASM bindings receive only necessary bytes and immediately validate their length;
- KEM/EC errors must map uniformly, yet server-side logs retain sanitized diagnostic information;
- When features are disabled, the entire algorithm dependency tree cannot be compiled into the product.

## Supply Chain and Exceptions

Run `cargo deny check` / `cargo audit`, then review crypto backend feature flags. Advisory exceptions should at minimum record:

- Affected crate/version and call paths;
- Whether inputs originate from untrusted networks;
- Why this specific path is currently exploitable or not;
- Mitigation controls in place;
- Expiration dates, owners, and upgrade blockers.

"Local IPC only" can be a factual boundary for some serialization advisories, but once Web/WASM/remote input reuses that codec, exceptions must fail immediately.

## Verification

- Known-answer tests across implementations;
- Handshake roles, algorithm negotiation, transcript mismatch detection;
- Nonce/counters boundaries, replay attacks, out-of-order messages, truncation, oversized frames;
- Any ciphertext/tag/AAD bit flip must result in failure;
- Fuzz parser/framing behavior should not be equated with cryptographic security guarantees;
- Native and WASM product interoperability testing;
- When fixed toolchains or generation tools are used to verify that WASM bytes reproduce correctly, record all input versions;
- Independent security audits or protocol reviews must cover custom algorithm combinations.

## Main References

- [ChaCha20Poly1305](https://docs.rs/chacha20poly1305/latest/chacha20poly1305/)
- `zeroize` crate: https://docs.rs/zeroize/latest/zeroize/
- `subtle`: https://docs.rs/subtle/latest/subtle/
- RustCrypto organization: https://github.com/RustCrypto
- OWASP Cryptographic Storage Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
