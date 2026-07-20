# Concurrency, Daemoning, and Platform Testing

The correctness of production asynchronous systems often hinges on "when tasks complete," "whether resources are returned," or "how to handle slow consumers" rather than the happy path. The `rmux` case study abstracts connection disconnections, concurrent subscriptions, real daemons, platform IPC, and runtime resource testing into the following strategies:

## Test Layers

| Layer | Objective |
|---|---|
| Pure Unit Tests | State machines, queue watermarks (high/low), frame codec, ID overflow policies |
| Async Components | Channel full/close semantics, cancellation, reordering completions, partial failures, lag |
| In-Memory Transport | Complete request-response cycles over `duplex` socket pairs |
| Real Processes | CLI daemon startup, stdio/stdout/stderr behavior, exit codes, disconnections and cleanup |
| Platform Integration | Unix sockets, Windows named pipes via ConPTY, signals handling |
| Stress/Performance Smoke Tests | Concurrent subscriptions, slow attach scenarios, large numbers of short-lived connections, RSS (Resident Set Size) and latency budgets |

## Waiting Without Guessing Luck

- Use `Notify`, channels, or observable counters to wait for "arrival" states; do not rely on fixed sleep intervals to guess timing.
- Wrap outer logic with a brief timeout to prevent CI jobs from hanging indefinitely, but ensure failure messages report the current state explicitly.
- After cancellation, continue polling until waiter/subscription/task counts reach zero, proving successful termination.
- Manually pause execution points to construct race conditions involving `delete`, `subscribe`, `shutdown`, and `request`.
- For inputs with reordering or task completions in arbitrary order, assert that the API output restores a specified sequence.

## Must-Fail Paths (Critical Failure Cases)

1. Channel full condition where all senders/receivers drop;
2. Peer disconnection during an active request;
3. Simultaneous shutdown and new connection attempts;
4. Reader EOF, writer errors, decoding failures, and mismatched responses;
5. Broadcast lag or slow consumers exceeding age/byte budgets;
6. One fan-out subtask panics/fails while others continue: do they get recycled?
7. Frame overflow/partial frames, multi-frame scenarios, version mismatches;
8. When `Drop` (best-effort cleanup) fails explicitly, can the system still report results correctly?

## Real Process Isolation

- Each test uses a unique temporary directory name for sockets and pipes along with configuration directories.
- Do not modify shared files under `$HOME` or `$PATH`; use process isolation when testing environment variables.
- Save child handles; upon test completion, request normal closure first before bounded waits, then terminate gracefully.
- Capture stdout/stderr from failed children but apply data masking/obfuscation as needed.
- Verify daemon disappearance behavior, old version compatibility, automatic re-start under concurrency, and residual socket states.

## Limit Expensive Parallelism

Global `--test-threads=1` can mask isolation defects while slowing down the entire test suite. Prioritize:

1. Resource uniqueness per process;
2. Encapsulate shared systems as fixtures;
3. Use only nextest test groups for expensive tests;
4. Local serial execution on Windows or when platform constraints exist.

```toml
[test-groups]
daemon-integration = { max-threads = 4 }

[[profile.default.overrides]]
filter = 'kind(test) & package(my-daemon)'
test-group = 'daemon-integration'
```

Numeric values must be determined by CI resource limits, port/socket handle constraints, and stability measurements.

## Source Gates (Static Verification)

Beyond compilation tests, add repository invariant scripts:

- Platform-neutral crates should not expose platform-specific APIs;
- Runtime code must never perform network access without explicit permission;
- `unsafe` blocks require clear SAFETY documentation;
- Debug assertions must contain no side effects;
- Frame/body/queue constants must exist and be actively tested in the test suite;
- Dependency matrix and feature flags must align with expected behavior.

Source gates can only verify statically expressible constraints and cannot replace runtime testing.

## Key References

- [Tokio Testing](https://tokio.rs/tokio/topics/testing)
- [cargo-nextest Test Groups Configuration](https://nexte.st/docs/configuration/test-groups/)
- [Cargo Test Command Reference](https://doc.rust-lang.org/cargo/commands/cargo-test.html)
- [Rust Integration Tests Book Chapter 11.03](https://doc.rust-lang.org/book/ch11-03-test-organization.html)
