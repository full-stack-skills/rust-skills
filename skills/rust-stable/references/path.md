# Path and PathBuf

- Accept borrowed paths with `Path`, or construct/safe-guard paths using `PathBuf`.
- Do not force UTF‑8 conversion; use `display()` when displaying, or `to_string_lossy()` as needed.
- Use `join` to combine path components instead of manually concatenating separators.
- `canonicalize` accesses the filesystem and may resolve symbolic links; it is unsuitable for string-only normalization.
- `extension`, `file_name`, and `parent` can all return `None`.
- When handling potentially untrusted paths, relying solely on checking for `..` does not establish a sandbox boundary; also consider absolute paths, symlinks, and race conditions.

Official source: https://doc.rust-lang.org/std/path/
