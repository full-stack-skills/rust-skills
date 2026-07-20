---
name: rust-cli
description: Design, implement, test, and release production Rust command-line applications, including command contracts, subcommands, configuration precedence, stdin/stdout/stderr, exit codes, file safety, daemon IPC, terminal handling, packaging, and process-level tests. Use when users ask for a Rust CLI, command parser, clap integration, Unix-style pipelines, daemon clients, PTY/TUI behavior, shell completion, or CLI release engineering.
---

# Rust CLI Delivery

Treat the command-line interface as a stable user protocol rather than embedding business logic directly in `main`. Complete an end-to-end loop from contract confirmation, implementation to real process verification.

## Confirm Constraints

Before making changes, confirm requirements, existing help text, scripts, READMEs, tests, and release configurations:

- Command name, subcommands, arguments, defaults, mutual exclusions, compatibility requirements;
- Human output format versus machine output (quiet mode, verbose, JSON, colorless);
- Input priority for stdin, files, and arguments; stdout/file write destinations;
- Exit codes corresponding to success, usage errors, data errors, transient failures;
- Supported platforms, shells, TTY/pipes environments, MSRV, dependency versions;
- Configuration file precedence over environment variables over command-line options.

If critical contracts are missing, infer the minimal compatible solution from existing behavior and tests while explicitly stating assumptions. Do not arbitrarily alter flags, output text, or exit codes.

## Workflow

### 1. Establish Behavior Baseline

Check entry points and build boundaries:

```bash
rustc --version --verbose
cargo metadata --no-deps --format-version 1
cargo test --all-targets
cargo run -- --help
```

Record at least one successful invocation with its parameters, stdout, stderr, and exit code; record at least one failed invocation. Existing snapshots or shell callers serve as compatibility constraints.

### 2. Define Command Contracts

Write a behavior matrix first, then implement parsing logic. Distinguish:

- Required positional arguments, optional arguments, repeatable options, subcommands;
- User input errors versus runtime errors;
- Normal data output versus diagnostic output;
- Interactive vs non-interactive modes;
- Stable machine format versus evolvable human-readable formats.

When using parsers like `clap`, rely on official documentation for locked repository versions. Do not mix derive attributes or APIs from different major versions based on memory.

### 3. Separate Parsing, Execution, and Presentation

Keep the entry point thin:

```text
Process parameters & environment
    -> Parse into Options/Command
    -> Call testable run(command, io, context)
    -> Map domain results to output and ExitCode
```

Let domain logic return structured results or errors; only decide color codes, newlines, stderr messages, and exit codes at boundaries. Avoid calling `process::exit` directly in deep functions, reading global environment variables indiscriminately, or printing unconditionally.

### 4. Implement I/O with Configuration Priority

- Inject input/output adapters using `BufRead`, `Write`, or explicit wrappers for testable pipe behavior;
- Write normal results to stdout; diagnostic and progress messages go to stderr;
- Do not mix logs, colors, or progress bars when consuming pipes from stdout;
- Enable interactive prompts only after detecting a TTY, providing an option to override this behavior;
- Use `Path`/`PathBuf`; do not manually concatenate platform-specific paths.

Explicitly define precedence: CLI > Environment Variables > Configuration Files > Defaults. Write tests for conflicts where applicable. When writing files, consider partial writes, atomic replacement strategies, existing file policies, and permission sensitivities. Read [Command Contract & I/O](references/contract-and-io.md) if specific command matrices, standard streams, or configuration patterns are needed.

### 5. Design Operable Errors

- Provide short, contextual, actionable error messages for expected failures;
- Do not print debug stacks or sensitive values to terminal users by default;
- Retain the full error chain for detailed modes and logging purposes;
- Map error categories into stable exit codes;
- Handle broken pipes correctly: do not generate noise when downstream filters close prematurely.

Do not use `unwrap()`/`expect()` on user input, files, network operations, or configuration failures.

### 6. Verify with Real Processes

Ensure coverage of at least the following scenarios:

1. `--help` and `--version`;
2. A successful execution path;
3. Unknown parameters, missing arguments, conflicting options;
4. Separation between stdout and stderr streams;
5. Precise exit codes;
6. stdin pipe or temporary file behavior;
7. Configuration precedence without TTY support;
8. Path risks involving spaces, non-UTF-8 content, or platform differences (when applicable).

Prioritize testing compiled binaries over parsing functions alone. Read [CLI Testing & Release](references/testing-and-release.md) if test coverage and release artifacts are required. General test stratification is delegated to `rust-testing`.

### 7. Validate Distribution Forms

Enforce repository-level gates:

```bash
cargo fmt --all -- --check
cargo check --all-targets
cargo test --all-targets
cargo clippy --all-targets -- -D warnings
cargo build --release
```

If cross-platform or specific target support is declared, verify in the corresponding environment or CI matrix. Packaging, features, workspace configuration, cross-compilation, and release details are handled by `rust-cargo-build`.

### 8. Handle Daemon, IPC, Terminal Modes

When a CLI includes persistent daemons, local IPC, PTYs, TUIes, or similar: do not keep all code in the binary crate. Separate parsing logic, protocol DTOs, platform layers, clients, servers, and public SDKs accordingly. Write end-to-end tests for handshake versions, capability negotiation, frame sizes, race conditions during auto-startup, signals, attach upgrades, shutdown sequences, and tool/boundary selection per [Daemon & IPC Terminal Toolkit](references/daemon-ipc-terminal-toolkit.md).

## Completion Criteria

Report completion only when all of the following are satisfied:

- Command contracts and compatibility assumptions are clearly defined;
- Business logic is separated from process boundaries;
- Real-process tests exist for stdout, stderr, exit codes, and configuration precedence;
- `fmt`, `check`, `test`, and Clippy pass;
- Supported platforms and distribution artifacts have evidence of support; unverified parts are explicitly marked.

## Handoff Boundaries

| Primary Concern | Assigned To |
|---|---|
| Ownership, path semantics, I/O trait definitions or error types | `rust-stable` |
| Test stratification, coverage, fuzzing, benchmarks | `rust-testing` |
| Cargo features, workspace configuration, cross-compilation, packaging, release | `rust-cargo-build` |
| Tokio tasks, cancellation, signals, async lifetimes | `rust-concurrency` |
| HTTP services | `rust-web` |

## On-Demand Resources

- [Command Contract & I/O](references/contract-and-io.md): Read when designing parameters, standard streams, configuration, and exit codes.
- [CLI Testing & Release](references/testing-and-release.md): Read before writing real-process tests or preparing for release.
- [Daemon & IPC Terminal Toolkit](references/daemon-ipc-terminal-toolkit.md): Read when building local daemons, control protocols, PTYs, TUIes, or cross-platform terminal applications.
- [Example Scenarios](examples/examples.md): Read if end-to-end task templates are required.
- `examples/golden-cli/`: Use offline compilation to verify stdout, stderr, and exit codes for golden examples.

## References

- [Rust Command-line apps](https://www.rust-lang.org/what/cli)
- [Command Line Applications in Rust](https://rust-cli.github.io/book/)
- `std::process` (https://doc.rust-lang.org/stable/std/process/)
- `std::io` (https://doc.rust-lang.org/stable/std/io/)
- `std::path` (https://doc.rust-lang.org/stable/std/path/)
