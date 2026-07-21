# I/O Streams — Read, Write, BufRead, Seek

> Companion to `SKILL.md` Part 6. Canonical source: [std::io](https://doc.rust-lang.org/std/io/index.html).

## Trait hierarchy

```
Read            bytes-in
Write           bytes-out
BufRead: Read   buffered reads, lines(), read_until
Seek            random access (File, Cursor)
```

Async equivalents live in `tokio::io` (`AsyncRead`, `AsyncWrite`, `AsyncBufRead`, `AsyncSeek`) — see the `rust-concurrency` skill.

## Trait selection

| Need | Trait | Implementations |
|------|-------|-----------------|
| Read raw bytes | `Read` | `File`, `Stdin`, `Cursor`, `&[u8]`, sockets |
| Buffered reading, line-by-line | `BufRead` | `BufReader<File>`, `BufReader<Cursor>` |
| Write bytes | `Write` | `File`, `Stdout`, `Stderr`, `Vec<u8>`, `Cursor` |
| Random access | `Seek` | `File`, `Cursor` |
| In-memory buffer | `Cursor<T>` | over `&[u8]`, `Vec<u8>` |

## Read and Write basics

```rust
use std::io::{self, Read, Write};

// Read into a buffer; returns bytes read.
let mut f = std::fs::File::open("/etc/hostname")?;
let mut buf = [0u8; 64];
let n = f.read(&mut buf)?;            // may be < buf.len()

// read_to_string reads until EOF, requires UTF-8.
let mut s = String::new();
std::fs::File::open("notes.txt")?.read_to_string(&mut s)?;

// Write
let mut out = std::fs::File::create("out.bin")?;
out.write_all(b"hello")?;             // writes all bytes (loops internally)
out.flush()?;                         // ensure buffers drained
# Ok::<(), io::Error>(())
```

`read` may return fewer bytes than the buffer size — loop or use `read_exact` (errors on EOF before fill) / `read_to_end` / `read_to_string`.

## BufReader and BufWriter

Direct `File` reads issue a syscall per call. Wrapping in `BufReader` amortizes that; `BufWriter` coalesces small writes.

```rust
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::fs::File;

let f = File::open("log.txt")?;
let reader = BufReader::new(f);
for line in reader.lines() {
    let line = line?;
    if line.contains("ERROR") { println!("{line}"); }
}

let f = File::create("out.log")?;
let mut w = BufWriter::new(f);
for i in 0..1000 {
    writeln!(w, "row {i}")?;          // buffered; one syscall per flush
}
w.flush()?;                            // flush before drop to detect errors
```

Always wrap a `File` in `BufReader`/`BufWriter` unless you are reading a single large block.

## Cursor — in-memory I/O

`Cursor<T>` adapts a `Vec<u8>` or `&[u8]` to `Read + Write + Seek`. Handy for testing I/O code without touching disk.

```rust
use std::io::{Cursor, Read, Seek, SeekFrom};

let mut c = Cursor::new(b"hello world".to_vec());
let mut head = [0u8; 5];
c.read_exact(&mut head)?;
c.seek(SeekFrom::Start(6))?;            // skip "hello "
let mut rest = String::new();
c.read_to_string(&mut rest)?;
assert_eq!(rest, "world");
```

## Stdin, Stdout, Stderr

```rust
use std::io::{self, BufRead, Write};

let stdin = io::stdin();
for line in stdin.lock().lines() {
    let line = line?;
    println!("echo: {line}");
}

let stdout = io::stdout();   // line-buffered; lock for throughput
let mut h = stdout.lock();
writeln!(h, "faster batch write")?;
```

`Stdin::lock` (and the stdout/stderr equivalents) avoids locking on every call — important inside loops.

## io::Result and io::Error

```rust
use std::io::{self, Write};

fn write_log(msg: &str) -> io::Result<()> {
    let mut f = std::fs::OpenOptions::new().append(true).create(true).open("app.log")?;
    writeln!(f, "{msg}")
}

match write_log("boot") {
    Ok(()) => {}
    Err(e) if e.kind() == io::ErrorKind::NotFound => eprintln!("dir missing"),
    Err(e) => return Err(e),
}
```

| Common `ErrorKind` | Meaning |
|--------------------|---------|
| `NotFound` | File or path missing |
| `PermissionDenied` | Access refused |
| `AlreadyExists` | Create collided |
| `InvalidInput` / `InvalidData` | Bad args or bytes |
| `UnexpectedEof` | `read_exact` hit EOF early |
| `TimedOut` | Operation timed out |
| `BrokenPipe` | Reader closed (e.g. piped stdout) |
| `Interrupted` | Retryable (signal) |

Construct errors with `io::Error::new(kind, payload)` or `io::Error::other(non_io_error)` to wrap arbitrary errors.

## Common patterns

```rust
// Copy bytes from reader to writer
std::io::copy(&mut reader, &mut writer)?;

// Read all bytes
let bytes: Vec<u8> = {
    let mut f = std::fs::File::open(path)?;
    let mut v = Vec::new();
    f.read_to_end(&mut v)?;
    v
};

// One-shot helpers in std::fs
let text = std::fs::read_to_string(path)?;
let bytes = std::fs::read(path)?;
std::fs::write(path, b"data")?;
```

`io::copy` uses an internal 8 KiB buffer (larger with `copy_buf`); it does not need a `BufReader`.

## bytes::Buf / BufMut (third party)

For high-throughput zero-copy byte handling (network code, parsers), the [`bytes`](https://docs.rs/bytes) crate provides `Bytes` / `BytesMut` and the `Buf`/`BufMut` traits, which support cheap slicing and reference counting without copying. The std traits are sufficient for file/process I/O; reach for `bytes` when buffer reuse and split/merge dominate.

## Async I/O — mention tokio

`tokio::io` mirrors the std traits as `AsyncReadExt::read`, `AsyncWriteExt::write_all`, and `AsyncBufReadExt::lines`. The patterns above (buffer, copy, line iteration) carry over; the difference is `await` points and that files and sockets come from async-specific constructors. See the `rust-concurrency` skill.

## Gotchas

| Pitfall | Fix |
|---------|-----|
| Calling `read` once and assuming full buffer | Use `read_exact` / `read_to_end` / loop |
| Wrapping `BufReader` around `Stdin` and also calling `io::stdin().lines()` | Lock stdin once |
| `BufWriter::drop` swallows flush errors | Call `flush()?` explicitly before drop |
| Treating `read` short read as EOF | Loop until `Ok(0)` |
| Locking `Stdout` per `println!` in a hot loop | `let mut h = io::stdout().lock();` |

## Reference

- [std::io](https://doc.rust-lang.org/std/io/index.html)
- [std::io::Read](https://doc.rust-lang.org/std/io/trait.Read.html) / [Write](https://doc.rust-lang.org/std/io/trait.Write.html) / [BufRead](https://doc.rust-lang.org/std/io/trait.BufRead.html) / [Seek](https://doc.rust-lang.org/std/io/trait.Seek.html)
- [std::io::BufReader](https://doc.rust-lang.org/std/io/struct.BufReader.html) / [BufWriter](https://doc.rust-lang.org/std/io/struct.BufWriter.html)
- [std::io::Cursor](https://doc.rust-lang.org/std/io/struct.Cursor.html)
- [Rust Standard Library](https://doc.rust-lang.org/std/)
