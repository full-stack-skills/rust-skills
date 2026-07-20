# I/O Reference

> Based on `library/std/src/io/` (official rust-lang/rust).

## Core Traits

```rust
pub trait Read {
    fn read(&mut self, buf: &mut [u8]) -> Result<usize>;
    fn read_to_string(&mut self, buf: &mut String) -> Result<usize>;
    fn read_to_end(&mut self, buf: &mut Vec<u8>) -> Result<usize>;
    fn read_exact(&mut self, buf: &mut [u8]) -> Result<()>;
    fn bytes(self) -> Bytes<Self> where Self: Sized;
    fn chain<R: Read>(self, next: R) -> Chain<Self, R>;
    fn take(self, limit: u64) -> Take<Self>;
}

pub trait Write {
    fn write(&mut self, buf: &[u8]) -> Result<usize>;
    fn flush(&mut self) -> Result<()>;
    fn write_all(&mut self, buf: &[u8]) -> Result<()>;
    fn write_fmt(&mut self, fmt: fmt::Arguments<'_>) -> Result<()>;
}

pub trait BufRead: Read {
    fn fill_buf(&mut self) -> Result<&[u8]>;
    fn consume(&mut self, amt: usize);
    fn read_line(&mut self, buf: &mut String) -> Result<usize>;
    fn lines(self) -> Lines<Self>;
    fn split(self, byte: u8) -> Split<Self>;
}
```

## File Operations

```rust
use std::fs::{self, File, OpenOptions};
use std::io::{self, BufReader, BufWriter, Write, BufRead};

// Read
let contents = fs::read_to_string("file.txt")?;   // whole file → String
let bytes = fs::read("file.bin")?;                 // whole file → Vec<u8>
let file = File::open("file.txt")?;
let reader = BufReader::new(file);
for line in reader.lines() {
    println!("{}", line?);
}

// Write
fs::write("out.txt", "hello world")?;             // whole file
let file = File::create("out.txt")?;
let mut writer = BufWriter::new(file);
writeln!(writer, "line {}", 1)?;
writer.flush()?;

// Append
let mut file = OpenOptions::new()
    .append(true)
    .open("log.txt")?;
writeln!(file, "logged entry")?;
```

## Standard Streams

```rust
use std::io::{self, Write, BufRead};

let mut input = String::new();
io::stdin().read_line(&mut input)?;            // single line
let input = io::stdin().lock();                // buffered stdin

let mut stdout = io::stdout().lock();
write!(stdout, "output: {}", value)?;
writeln!(stdout, "line")?;

writeln!(io::stderr(), "error: {err}")?;       // stderr
```
