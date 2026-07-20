# Daemon, IPC, and Terminal Tools

This tool diagram originates from the local terminal replayer case study in `rmux`. It is intended to assist with selection rather than serving as a default dependency template.

## Common Crates & Boundaries

| Capability | Tool | Placement |
|---|---|---|
| Arguments/Subcommands/Completers | `clap`, `clap_complete` | CLI parsing and xtask; normalized into internal commands after parsing |
| Async Daemon | `tokio` | Server/runtime; feature flags must be restricted on enablement |
| Structured Logging | `tracing` | Client/server/IPC boundaries; stdout remains machine-consumable |
| Local IPC | Tokio Unix socket/named pipe + `rustix`/`windows-sys` | Independent `ipc/os` crate |
| Signals/Terminal Recovery | `signal-hook`, Tokio signal | Process boundary; RAII-based terminal state restoration |
| Pseudo-TTY (PTY) | `rustix`/`libc` and `windows-sys` | Independent pty crate, encapsulating unsafe handles |
| TUI | `ratatui` | Pure render state separation from I/O drivers |
| Terminal Control | `crossterm` | Input handling, raw mode, cross-platform terminal adaptation |
| Width & Short Texts | `unicode-width`, `compact_str` | Only necessary when layout/profile verification confirms need |
| Protocol DTOs | `serde`, `thiserror`; binary codecs if needed | Independent proto crate with explicit wire versioning |

## End-to-End Flow

```text
argv/env/config
  -> clap RawCli
  -> Normalize and convert to internal Command
  -> Parse endpoint / auto-start strategy
  -> IPC connect + handshake (wire range, capabilities)
  -> request/response or attach/control upgrade
  -> Map stdout/stderr/ExitCode
  -> shutdown/terminal restore
```

The parsing layer should retain `OsString` and `PathBuf`, avoiding premature UTF-8 assumptions. When maintaining compatibility with existing CLI tools, allow the parser to accept surface syntax first; then apply explicit normalization to convert into internal commands and centrally validate conflicts.

## IPC Protocol Guardrails (Mandatory)

- Magic number + wire version or equivalent envelope structure;
- Client declares supported ranges; server returns negotiated capabilities upon response;
- Length prefix parsing must check maximum frame size before allocation;
- Incremental decoders correctly handle partial reads, multi-frame sequences, and trailing bytes;
- Version/capability responses are not structured error types.

User identity, socket/pipe permissions, and write access on the server side must be revalidated independently of protocol negotiation. Long-waiting requests should be cancelled upon peer disconnection. When upgrading from `request/response` to `attach/control`, preserve decoder-buffered bytes.

Use cases like `bincode` for serialization do not address versioning, length constraints, authentication, replay protection, trust models, or DoS mitigation. For public network protocols, prefer those with explicit evolution paths and established ecosystems; review via `rust-web-security`.

## Automatic Startup & Race Conditions

The `connect_or_start` function requires:

1. Establish connection first;
2. Initiate startup only if the daemon is absent ("daemon not found" condition);
3. Serialize concurrent starter instances using platform-specific locks to prevent race conditions;
4. Re-probe for existence, avoiding duplicate daemon detection loops;
5. Implement bounded waiting on readiness state;
6. Distinguish between old versions of daemons, permission errors, and actual absence;
7. Test multiple simultaneous startup scenarios concurrently.

## Terminal Lifecycle Management

- Use guards to restore `raw mode`, alternate screen, cursor positioning, and signal handlers after normal return, error conditions, panics, Ctrl-C events, or peer disconnection;
- Ensure coverage for all terminal states: successful returns, errors, panics, keyboard interrupts (Ctrl-C), and remote disconnects.

Input operations, resize events, actions, network outputs must use distinct message semantics rather than mechanically applying unbounded channels to every event type. High-frequency `resize/status` updates can be merged into a single latest-value channel; text input typically requires bounded buffering with ordered guarantees. The render core should ideally remain pure data and support snapshot testing independent of the real terminal environment.

## Release Verification Checklist

- Ensure consistency between CLI help (`--help`), man pages, and completion scripts across command surfaces;
- Test Unix sockets on Linux/macOS and named pipes/ConPTY on Windows in production environments;
- Validate release artifacts for dynamic library dependencies, system baselines, signatures, and checksums;
- Confirm version handshake compatibility between daemon binaries, main binary, and SDK components;
- Verify that `cargo package --list` includes man pages, licenses, and necessary resources.

## Primary References

- [clap derive](https://docs.rs/clap/latest/clap/_derive/)
- [Tokio](https://tokio.rs/)
- [tracing](https://docs.rs/tracing/)
- [rustix](https://docs.rs/rustix/latest/rustix/)
- [ratatui](https://ratatui.rs/)
- [crossterm](https://docs.rs/crossterm/)
