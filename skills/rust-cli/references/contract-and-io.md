# Command Contracts and I/O

## Behavior Matrix

For each major call record:

| Call | Input Source | stdout | stderr | Exit Code | Stable Interface? |
|---|---|---|---|---|---|
| `tool --help` | Parameters | Help text | Empty | 0 | Yes |
| `tool run FILE` | File | Result output | Diagnostics | 0 or non-0 | Yes |
| `producer tool` | stdin | Filtered results | Diagnostics | 0 or non-0 | Yes |

When scripts parse outputs, they should explicitly provide a clear `--format json` (or other versioned format) rather than requiring the script to interpret colored human-readable text.

## Standard Stream Conventions

- **stdout**: Data promised by the command execution.
- **stderr**: Diagnostics, warnings, logs, and progress information.
- **Quiet mode**: Suppresses non-critical diagnostics while still requesting data from requests.
- **Verbose mode**: Increases diagnostic output without altering the machine's structural output format.
- **Colors**: Default behavior depends on terminal capabilities; explicit options take precedence.

When handling broken pipes (downstream normal early closure), identify scenarios where downstream processes close normally and do not treat them as application-level failures with backtraces.

## Configuration Priority

Declare before implementation, for example:

```text
Command-line arguments > Environment variables > Project configuration > User configuration > Built-in defaults
```

Test each layer separately and ensure at least one conflict is covered per layer. Distinguish between "not provided" (missing) versus "explicitly empty value," to avoid losing source information after parsing.

## Exit Codes

Commit only the categories that callers genuinely need to distinguish. Maintain centralized mappings, for example:

- `0`: Success;
- `2`: Command usage error (if parser conventions dictate this);
- Other non-zero values: Differentiate between data errors, configuration issues, or temporary faults according to project protocol.

Do not assume all platforms and dependencies use the same extended exit code scheme. Existing protocols take precedence over new designs.

## Paths and Texts

- CLI parameters are `OsString` at the OS level; UTF-8 is not guaranteed.
- Convert text only when required by the protocol, deciding on invalid encoding handling accordingly.
- Use `PathBuf` to store paths; display using lossy or escaped strategies suitable for user interfaces.
- Avoid string concatenation of paths and do not assume consistent `/`, drive letter, or case rules across systems.

## Key Resources

- [CLI Book: Writing output](https://rust-cli.github.io/book/tutorial/output.html)
- [CLI Book: Human communication](https://rust-cli.github.io/book/in-depth/human-communication.html)
- [CLI Book: Machine communication](https://rust-cli.github.io/book/in-depth/machine-communication.html)
- `std::ffi::OsString` (documentation link provided in original text).
