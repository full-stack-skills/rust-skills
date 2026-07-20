# CLI Scenario Examples

## Scenario: Building a Filter Pipeline-Ready

User Request:
Build `rgrep PATTERN [FILE]`. When FILE is omitted, read from stdin; match lines to stdout; write errors and file parameter mismatches to stderr; do not crash the runtime on unmatched input.

Execution Strategy: Establish an initial contract first:

| Scenario | stdout | stderr | Exit Code |
|---|---|---|---|
| Match Found | Matching line(s) | Empty | 0 |
| No Matches | Empty | Empty (project convention value) | Project-defined default |
| File Not Found | Empty | Path and reason included | Non-zero exit code |
| Missing Arguments | Empty | Usage diagnostics | Parser-convention value |

Subsequently, decompose into:

```rust
struct Options {
    pattern: String,
    input: Option<std::path::PathBuf>,
}

fn filter(
    options: &Options,
    input: impl std::io::BufRead,
    output: &mut impl std::io::Write,
) -> std::io::Result<bool> {
    // Return whether a match was found; do not exit the process or write diagnostics here.
    todo!()
}
```

Finally, validate parameter handling, stdin input, file existence, stdout output, stderr error messages, and exit codes using real processes.

## Scenario: Adding Configuration Overrides

User Request:
Enable `tool sync` to support configuration files, the environment variable `TOOL_ENDPOINT`, and the command-line flag `--endpoint`.

Establish precedence order as follows:
```text
--endpoint > TOOL_ENDPOINT > config file > default value
```
Preserve source information for each layer. Conduct separate tests for each layer; additionally include a test that sets all four layers simultaneously to verify conflict resolution. Do not print tokens or full URLs containing credentials in error messages.
