# Module Naming Conventions

How to name modules so that the directory tree reads like documentation.

---

## The Naming Principle

A module name should tell the reader **what's inside** without opening the file. If a newcomer has to open `src/util.rs` to find out what "util" means, the name is wrong.

---

## Good Names

| Module name | What's inside | Why it works |
|-------------|---------------|--------------|
| `parser` | Lexer + grammar + AST construction | Domain name — answers "what does this do?" |
| `ast` | AST data types | Standard term in compilers |
| `codegen` | Code generation backends | Domain name |
| `parser/lexer` | Tokenizer | Subdomain of `parser` |
| `parser/grammar` | Grammar rules | Subdomain of `parser` |
| `net/tcp` | TCP networking | Protocol name |
| `net/dns` | DNS resolver | Protocol name |
| `buffer` | I/O buffers | What it is |
| `time` | Time utilities | What it's about |
| `error` | Error types | Standard convention |
| `crypto/hash` | Hashing functions | Specific domain |
| `crypto/symmetric` | Symmetric encryption | Specific domain |
| `tests` | Unit tests | Standard convention |
| `benches` | Benchmarks | Standard convention |
| `examples` | Usage examples | Standard convention |

---

## Bad Names

| Module name | Why it's bad | Better |
|-------------|--------------|--------|
| `util` / `utils` | Junk drawer — what utilities? | Split by concern: `hash`, `time`, `validate` |
| `common` | "Common" to whom? | Same — split by concern |
| `ext` | "Extensions" of what? | Name by what's extended, or by what's inside |
| `core` | Vague; conflicts with `core` crate | Use a domain name |
| `types` | Acceptable only as a leaf for type-only modules | Use `model`, `schema`, or domain name |
| `db` | Ambiguous — driver? ORM? pool? | `connection`, `driver`, `orm` |
| `io` | Conflicts with `std::io` | `buffer`, `transport`, `codec` |
| `rt` | Two letters; conflicts with every async runtime | `runtime` |
| `net_io` | Compound of vague terms | Split into `net` and `buffer` |
| `misc` | "Miscellaneous" is never a domain | Split by concern |
| `helpers` | Helpers for what? | Name by what's helped |
| `internal` | Acceptable *as a marker*, but name by concern is better | Use the concern name |
| `impl` | Acceptable for trait impls, but usually a junk drawer | Split by trait |

---

## Abbreviations

**Rule**: avoid abbreviations unless they are standard industry terms.

| Acceptable abbreviation | Reason |
|-------------------------|--------|
| `http`, `https`, `tls`, `ssl`, `tcp`, `udp`, `dns`, `ip` | Standard protocol names |
| `url`, `uri` | Standard |
| `json`, `xml`, `yaml`, `toml` | Standard format names |
| `uuid`, `guid` | Standard identifier names |
| `crc`, `sha`, `md5` | Standard hash names |
| `jwt`, `oauth` | Standard auth names |

| Unacceptable abbreviation | Use instead |
|---------------------------|-------------|
| `db` | `database` or specific name (`connection`, `driver`) |
| `rt` | `runtime` |
| `cfg` | `config` |
| `ctx` | `context` |
| `req` / `resp` | `request` / `response` (or accept `req`/`resp` if very common) |
| `auth` | acceptable (industry standard) |
| `crypto` | acceptable |
| `idx` | `index` |
| `msg` | `message` |

---

## Conflict Avoidance

Avoid names that conflict with:

1. **Standard library modules** — `std::io`, `std::net`, `std::fs`, `std::os`, `std::time`, `std::collections`. If your crate has a module that overlaps, prefix or rename.

```rust
// ❌ Conflicts with std::io
pub mod io { /* ... */ }

// ✅ Rename to what it actually is
pub mod buffer { /* I/O buffers */ }
```

2. **Other popular crates** — `tokio::runtime`, `serde::de`. If your crate has a similar module, users will be confused.

3. **Rust keywords** — `crate`, `self`, `super`, `fn`, `mod`, `pub`, `use`, etc. These are reserved.

4. **`core`** — the standard library's `core` crate is special. Don't name a module `core` unless you mean it (some crates legitimately have a `core` domain).

---

## File Names

Module file names follow the same rules:

| File | Module | Visibility |
|------|--------|-----------|
| `src/lib.rs` | crate root | library crate |
| `src/main.rs` | binary crate root | binary crate |
| `src/<name>.rs` | module `<name>` | whatever you declare |
| `src/<name>/mod.rs` | module `<name>` (legacy) | whatever you declare |
| `src/<name>/` + `src/<name>.rs` | module `<name>` (modern) | whatever you declare |
| `src/bin/<name>.rs` | binary `<name>` | always its own crate root |
| `tests/<name>.rs` | integration test | separate compilation |
| `benches/<name>.rs` | benchmark | separate compilation |
| `examples/<name>.rs` | example | separate compilation |

`bin/`, `tests/`, `benches/`, `examples/` are Cargo conventions — Cargo treats each file inside as a separate compilation unit. Don't put library code in these directories.

---

## Test Module Naming

| Test type | Location | Convention |
|-----------|----------|------------|
| Unit tests | `#[cfg(test)] mod tests { ... }` inside each module | Always named `tests` |
| Integration tests | `tests/<name>.rs` | Name by what's tested (`tests/parser.rs`) |
| Doc tests | Inside `///` doc comments | Implicit — run by `cargo test` |

```rust
// src/parser.rs
pub struct Parser { /* ... */ }

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_empty_input() { /* ... */ }

    #[test]
    fn parses_simple_function() { /* ... */ }
}
```

---

## Naming Process

When starting a new module, ask:

1. **What's inside?** (one sentence)
2. **What's the standard term for this?** (industry or Rust community)
3. **Does this name conflict with `std`, `core`, or popular crates?**
4. **Can a newcomer guess what's inside?**

If any answer is "I don't know", the name needs work.

```rust
// Iterating on a name:
mod stuff;          // ❌ what stuff?
mod db_stuff;       // ❌ still vague
mod db;             // ❌ ambiguous (driver? ORM? pool?)
mod connection;     // ✅ clear — this manages connections
```

---

## Renaming is a Breaking Change

Renaming a `pub mod` breaks every downstream `use my_crate::old_name::*;`. Plan for it:

```rust
// Step 1: rename and add deprecated alias (minor version bump)
mod connection;
pub use connection::*;

#[deprecated(since = "0.5.0", note = "renamed to `connection`")]
pub mod db {
    pub use crate::connection::*;
}

// Step 2: remove alias at next major version
```

Document the rename in CHANGELOG and migration guide.
