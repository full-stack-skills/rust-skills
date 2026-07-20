# std::fs

## Common Operations

- Small files: `read`, `read_to_string`, and `write`
- Streaming large files: Use the `File` type with `BufReader` / `BufWriter`
  - Note: The official documentation recommends using `std::io::ReadExt` for streaming operations.
- Directories: `create_dir_all`, `read_dir`, and `remove_dir`
- Metadata: `metadata` (for regular files) and `symlink_metadata` (for symbolic links)
- Atomic replacement: Write to a temporary file, flush/sync it, then rename

## Rules

- Do not swallow `io::Error` in library code; preserve the path and operation context.
- When handling symbolic links, explicitly use either `metadata` or `symlink_metadata`.
- Assume that `read_dir` does **not** guarantee a stable order of results; sort directories deterministically if needed.
- Before deleting, overwriting, or performing recursive operations on files/directories, verify the exact target to avoid unintended glob pattern matching.
- In security-sensitive code, be cautious about TOCTOU (Time-of-check-to-time-of-use) race conditions when checking permissions after a file operation completes.

Official source: https://doc.rust-lang.org/std/fs/
