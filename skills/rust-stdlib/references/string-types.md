# String Types — Selection, Conversion, Safety

> Companion to `SKILL.md` Part 3. Canonical source: [std::str](https://doc.rust-lang.org/std/primitive.str.html), [std::string](https://doc.rust-lang.org/std/string/struct.String.html), [std::path](https://doc.rust-lang.org/std/path/index.html).

## Type map

| Type | Encoding | Owned? | Use |
|------|----------|--------|-----|
| `&str` | UTF-8 | No | Function parameters, literals |
| `String` | UTF-8 | Yes | Owned mutable UTF-8 |
| `OsString` / `OsStr` | Platform-native | Yes / No | env vars, process args |
| `PathBuf` / `Path` | Platform-native | Yes / No | Filesystem paths |
| `Cow<'a, str>` | UTF-8 | Maybe | Borrowed or owned |
| `Vec<u8>` / `&[u8]` | Bytes | Yes / No | Binary, non-UTF-8 |

## Why &str in function signatures

`&str` accepts both `&String` (via `Deref`) and `&'static str` literals, plus slices of `String`. It is the most general borrowed-text type and avoids forcing the caller to allocate.

```rust
// Accepts &str, &String, String slice, string literal — all zero-copy
fn greet(name: &str) -> String { format!("Hello, {name}!") }

greet("world");                       // literal
greet(&String::from("owned"));        // &String → &str
greet(&format!("{i}", i = 7)[..]);    // slice of String
```

Take `&str` for reads; take `String` only when the function will own the value. Use `impl Into<String>` only when the ergonomics genuinely help.

## String vs &str

| Aspect | `String` | `&str` |
|--------|----------|--------|
| Storage | Heap, growable | Borrowed (stack/heap/static) |
| Mutability | Mutable | Immutable view |
| Lifetime | Owned | `'a` |
| Construct | `String::from`, `to_string`, `format!` | `&"literal"`, slice |

```rust
let owned: String = String::from("data");
let borrowed: &str = &owned;            // Deref
let slice: &str = &owned[0..2];
let again: String = borrowed.to_string();   // clone
```

## Conversion cheat sheet

| From → To | Code |
|-----------|------|
| `&str` → `String` | `s.to_string()`, `s.to_owned()`, `String::from(s)`, `s.into()` |
| `String` → `&str` | `&s` (Deref) or `s.as_str()` |
| `String` → `Vec<u8>` | `s.into_bytes()` |
| `&[u8]` → `String` | `String::from_utf8(v)?` or `String::from_utf8_lossy(v)` |
| `OsString` → `String` | `os.into_string()?` |
| `PathBuf` → `String` | `pb.to_string_lossy().into_owned()` |
| `&str` → `&[u8]` | `s.as_bytes()` |

`to_string()`, `to_owned()`, `String::from(...)` and `.into()` are equivalent in cost for `&str → String`; pick by readability.

## OsString and OsStr

Strings in their platform-native representation (WTF-8 on Windows, bytes elsewhere). Needed for env vars, process arguments, and any path component that may not be valid UTF-8.

```rust
use std::ffi::OsString;

let var: OsString = std::env::var_os("PATH").unwrap_or_default();
match var.into_string() {
    Ok(s) => println!("utf8: {s}"),
    Err(orig) => println!("not utf8, {} bytes", orig.as_encoded_bytes().len()),
}
```

## PathBuf and Path

Always use `Path`/`PathBuf` for filesystem paths — they handle separators, parent stripping, and joining portably. Never join strings by hand.

```rust
use std::path::{Path, PathBuf};

let p = Path::new("/usr/local/bin/foo");
assert_eq!(p.parent(), Some(Path::new("/usr/local/bin")));
assert_eq!(p.file_stem(), Some(std::ffi::OsStr::new("foo")));
assert_eq!(p.extension(), None);

let joined = PathBuf::from("/etc").join("nginx").join("nginx.conf");
```

`Path`/`PathBuf` are wrappers around `OsStr`/`OsString`. Use `to_string_lossy()` when you must show a path as text but cannot guarantee UTF-8.

## Cow for mixed borrowed/owned

```rust
use std::borrow::Cow;

fn normalize<'a>(s: &'a str) -> Cow<'a, str> {
    if s.contains('\t') {
        Cow::Owned(s.replace('\t', "    "))     // allocate only when needed
    } else {
        Cow::Borrowed(s)
    }
}
```

`Cow` lets a function return either a borrow or an allocation without forcing the caller to deal with both cases.

## Binary data: Vec<u8> and &[u8]

For data that is not text, use byte buffers. Reading a file with unknown encoding, parsing a binary format, or handling network frames all want bytes.

```rust
use std::fs;

let bytes: Vec<u8> = fs::read("logo.png")?;          // Vec<u8>
let view: &[u8] = &bytes[..4];
if view == b"\x89PNG" { /* signature */ }

let text: String = String::from_utf8(bytes)?;        // fallible
let lossy = String::from_utf8_lossy(b"caf\xc3\xa9"); // replaces invalid bytes
```

## Slicing safety — is_char_boundary

`&s[a..b]` panics if `a` or `b` is not on a UTF-8 char boundary. Use `is_char_boundary` to slice safely with byte offsets.

```rust
let s = "héllo";   // 'é' is 2 bytes
assert!(s.is_char_boundary(0));
assert!(!s.is_char_boundary(1));     // middle of 'é'
let safe = s.get(0..2).unwrap_or("");   // returns Option<&str>, no panic
```

Prefer `char_indices()` for byte offsets that align to characters, and `s.split_at(idx)` only after `is_char_boundary` checks.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `fn f(s: String)` when only reading | Take `&str` |
| `path + "/" + name` | `PathBuf::join` |
| `&s[i]` for a char | `s.chars().nth(i)` or iterate |
| `String::from_utf8(b).unwrap()` | `from_utf8_lossy` or `?` |
| `to_string()` in a hot loop | Keep `&str`, format once |

## Reference

- [std::str](https://doc.rust-lang.org/std/primitive.str.html) / [std::string::String](https://doc.rust-lang.org/std/string/struct.String.html)
- [std::ffi::OsString](https://doc.rust-lang.org/std/ffi/struct.OsString.html)
- [std::path::Path](https://doc.rust-lang.org/std/path/struct.Path.html) / [PathBuf](https://doc.rust-lang.org/std/path/struct.PathBuf.html)
- [std::borrow::Cow](https://doc.rust-lang.org/std/borrow/enum.Cow.html)
- [Rust Standard Library](https://doc.rust-lang.org/std/)
