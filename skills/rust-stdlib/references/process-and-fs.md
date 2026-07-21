# Process and Filesystem — Command, fs, env

> Companion to `SKILL.md` Part 9. Canonical sources: [std::process](https://doc.rust-lang.org/std/process/index.html), [std::fs](https://doc.rust-lang.org/std/fs/index.html), [std::env](https://doc.rust-lang.org/std/env/index.html).

## process::Command

| Method | Behavior |
|--------|----------|
| `Command::new(prog)` | Start building a command |
| `.arg(x)` / `.args([...])` | Positional arguments |
| `.env(k, v)` / `.env_clear()` | Set/clear environment |
| `.current_dir(p)` | Working directory |
| `.status()` | Run to completion, return `ExitStatus` |
| `.output()` | Run to completion, capture stdout/stderr |
| `.spawn()` | Start, return `Child` for streaming I/O |

```rust
use std::process::Command;

let status = Command::new("ls").arg("-l").arg("/").status()?;
if !status.success() { eprintln!("exit code: {:?}", status.code()); }

let out = Command::new("git").args(["rev-parse", "HEAD"]).output()?;
println!("{}", String::from_utf8_lossy(&out.stdout).trim());
# Ok::<(), std::io::Error>(())
```

- `output()` is the simplest way to capture output; it sets stdin/stdout/stderr to `Stdio::piped` automatically.
- `status()` does not capture anything (children inherit the parent's std streams), good for forwarding logs.
- `spawn()` is the only way to write to stdin or stream output as it arrives.

## Stdio — piped, inherit, null

```rust
use std::process::{Command, Stdio};
use std::io::Write;

let mut child = Command::new("cat")
    .stdin(Stdio::piped())
    .stdout(Stdio::piped())
    .stderr(Stdio::null())
    .spawn()?;

child.stdin.as_mut().unwrap().write_all(b"hello\n")?;
drop(child.stdin.take());              // close stdin so `cat` sees EOF

let out = child.wait_with_output()?;  // wait + collect
assert_eq!(&out.stdout, b"hello\n");
```

| `Stdio` variant | Effect |
|-----------------|--------|
| `inherit()` | Default; child writes to parent's streams |
| `piped()` | Connect to a `Child::{stdin, stdout, stderr}` handle |
| `null()` | Discard |
| `from(file)` / `to(file)` | Redirect to a `File` |

## Exit codes and signals

`ExitStatus::success()` returns true if exit code is 0. `.code()` returns `Some(i32)` on most platforms; on Unix, signal-terminated processes return `None`, with `.signal()` available on nightly or via platform crates.

```rust
let status = Command::new("false").status()?;
assert!(!status.success());
assert_eq!(status.code(), Some(1));
```

For finer signal handling on Unix, use the [`nix`](https://docs.rs/nix) crate or `std::os::unix::process::ExitStatusExt`.

## fs module

| Function | Use |
|----------|-----|
| `fs::read(path)` | Read entire file to `Vec<u8>` |
| `fs::read_to_string(path)` | Read to `String` (requires UTF-8) |
| `fs::write(path, bytes)` | Write (overwrites) |
| `fs::create_dir(path)` | Create one directory |
| `fs::create_dir_all(path)` | Create path and intermediates |
| `fs::remove_file(path)` | Delete file |
| `fs::remove_dir(path)` | Delete empty dir |
| `fs::remove_dir_all(path)` | Delete recursively |
| `fs::rename(from, to)` | Move/rename |
| `fs::copy(from, to)` | Copy, returns bytes written |
| `fs::metadata(path)` | Stat-like info |
| `fs::canonicalize(path)` | Absolute, resolved path |

```rust
use std::fs;

fs::create_dir_all("data/cache")?;                       // mkdir -p
fs::write("data/cache/note.txt", b"hello")?;
let text = fs::read_to_string("data/cache/note.txt")?;   // "hello"
let meta = fs::metadata("data/cache/note.txt")?;
println!("{} bytes", meta.len());
# Ok::<(), std::io::Error>(())
```

## File and OpenOptions

```rust
use std::fs::OpenOptions;
use std::io::Write;

let mut f = OpenOptions::new()
    .create(true)
    .append(true)
    .open("app.log")?;
writeln!(f, "line")?;
```

| `OpenOptions` method | Effect |
|----------------------|--------|
| `.read(true)` / `.write(true)` | Open mode |
| `.create(true)` | Create if missing |
| `.create_new(true)` | Create, error if exists |
| `.append(true)` | Writes go to end |
| `.truncate(true)` | Truncate on open |

## fs::metadata

```rust
use std::fs;
use std::os::unix::fs::PermissionsExt;

let m = fs::metadata("script.sh")?;
println!("{}", m.is_file());
println!("{}", m.permissions().mode() & 0o777);
let modified = m.modified()?;
```

Platform-specific extensions (`PermissionsExt`, `MetadataExt`) live in `std::os::{unix, windows}`.

## env — variables and args

```rust
use std::env;

// Arguments: arg(0) is the program name.
for (i, a) in env::args().enumerate() { println!("{i}: {a}"); }

// Variables
let port: u16 = env::var("PORT").ok().and_then(|s| s.parse().ok()).unwrap_or(8080);
let path = env::var_os("PATH").expect("PATH not set");   // non-UTF-8 safe

// Current dir and temp dir
let cwd = env::current_dir()?;
let tmp = env::temp_dir();
println!("temp: {}", tmp.display());
# Ok::<(), std::io::Error>(())
```

Use `var_os` whenever an env value might not be valid UTF-8 (PATH, locale, custom vars on Windows).

## Cross-platform conditional compilation

```rust
#[cfg(windows)]
fn newline() -> &'static str { "\r\n" }

#[cfg(not(windows))]
fn newline() -> &'static str { "\n" }

if cfg!(target_os = "macos") { /* macOS-specific */ }
```

Common `cfg` keys: `windows`, `unix`, `target_os = "linux"`, `target_os = "macos"`, `target_os = "windows"`, `target_arch = "x86_64"`, `target_pointer_width = "64"`.

## Temp files

| Approach | Use |
|----------|-----|
| `env::temp_dir()` + manual name | Quick and dirty; you manage cleanup |
| [`tempfile`](https://docs.rs/tempfile) crate | Auto-deleted `NamedTempFile` and `TempDir`; safer random names |

```rust
// tempfile crate (add to Cargo.toml)
use tempfile::NamedTempFile;
let f = NamedTempFile::new()?;
writeln!(&f, "scratch")?;
// dropped automatically; file removed
```

For anything user-facing or long-lived, prefer the `tempfile` crate — it handles unique naming and cleanup on panic.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `format!("{} {}", args)` to build a command line | Use `Command::arg` per token (avoids quoting bugs) |
| String paths joined with `+` | `PathBuf::join` |
| `env::var("PATH").unwrap()` | `var_os` — not UTF-8 guaranteed |
| `fs::read_to_string` on binary | `fs::read` then `from_utf8_lossy` or `?` |
| Forgetting `drop(child.stdin.take())` | Child blocks waiting for input |
| `fs::remove_dir` on non-empty dir | `remove_dir_all` |

## Reference

- [std::process::Command](https://doc.rust-lang.org/std/process/struct.Command.html) / [Stdio](https://doc.rust-lang.org/std/process/struct.Stdio.html)
- [std::fs](https://doc.rust-lang.org/std/fs/index.html) / [OpenOptions](https://doc.rust-lang.org/std/fs/struct.OpenOptions.html)
- [std::env](https://doc.rust-lang.org/std/env/index.html)
- [std::path::Path](https://doc.rust-lang.org/std/path/struct.Path.html) / [PathBuf](https://doc.rust-lang.org/std/path/struct.PathBuf.html)
- [Rust Standard Library](https://doc.rust-lang.org/std/)
