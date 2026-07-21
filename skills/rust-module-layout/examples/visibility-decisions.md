# Visibility Decision Examples

Concrete examples of choosing between `pub`, `pub(crate)`, `pub(super)`, and private.

---

## Example 1 — Default to private

```rust
// src/parser.rs
pub struct Parser {
    source: String,           // private — users don't touch
    position: usize,          // private
}

impl Parser {
    pub fn new(source: &str) -> Self {
        Self { source: source.to_string(), position: 0 }
    }

    pub fn parse(&mut self) -> Result<crate::ast::Module, crate::Error> {
        // internal helpers called:
        self.skip_whitespace();
        // ...
        unimplemented!()
    }

    fn skip_whitespace(&mut self) {              // private — implementation detail
        while self.position < self.source.len()
            && self.source.as_bytes()[self.position].is_ascii_whitespace() {
            self.position += 1;
        }
    }
}
```

**Reasoning**: `source`, `position`, and `skip_whitespace` are implementation details. If they were `pub`, we couldn't refactor them without a breaking change.

---

## Example 2 — `pub(crate)` for cross-module helpers

```rust
// src/util/hash.rs
pub(crate) fn hash_str(s: &str) -> u64 {          // visible across the crate
    // ...
    0
}
```

```rust
// src/parser.rs
use crate::util::hash::hash_str;                  // OK — same crate

pub fn parse(input: &str) -> u64 {
    hash_str(input)
}
```

**Reasoning**: `hash_str` is used by `parser` and `codegen` but not part of the public API. `pub(crate)` lets them share without exposing the helper.

---

## Example 3 — `pub(super)` for sibling modules

```rust
// src/runtime/scheduler.rs
pub(super) fn schedule_internal(task: Task) {     // visible only to runtime/
    // ...
}
```

```rust
// src/runtime/mod.rs
mod scheduler;
pub(super) use scheduler::schedule_internal;      // visible to crate root, not to users
```

**Reasoning**: `schedule_internal` is an unstable internal API. Limiting visibility to `super` (the parent module) prevents accidental external use.

---

## Example 4 — `pub(in path)` for ancestor-scoped helpers

```rust
// src/net/tcp/stream.rs
pub(in crate::net) fn low_level_read(buf: &mut [u8]) -> usize {
    // ...
    0
}
```

```rust
// src/net/udp/socket.rs
use crate::net::tcp::stream::low_level_read;     // OK — same ancestor crate::net
```

**Reasoning**: `low_level_read` is shared by `tcp` and `udp` modules but should never leak outside `net`. `pub(in crate::net)` enforces this.

---

## Example 5 — Facade-only public items

```rust
// src/lib.rs
mod connection;
mod pool;

pub use connection::Connection;                   // public type
pub use pool::Pool;                               // public type
// Note: connection/ and pool/ directories are private —
// users cannot reach pool::v2::PoolImpl
```

**Reasoning**: the entire internal tree is private. Only the curated types `Connection` and `Pool` are exposed via targeted re-exports.

---

## Example 6 — Testing private items without exposing them

```rust
// src/parser.rs
pub struct Parser { /* ... */ }

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_internal_state() {
        let mut p = Parser::new("hello");
        // Can access private fields here because `tests` is a child module
        // of `parser` — privacy is parent-bound in the *other* direction too.
        // p.position == 0 (private field accessible in tests)
    }
}
```

**Reasoning**: child modules can see private items of their ancestors. `#[cfg(test)] mod tests` leverages this to unit-test internals without widening visibility.

---

## Example 7 — Visibility tables in code review

When reviewing a crate's `lib.rs`, ask:

| Item | Visibility | Reason |
|------|-----------|--------|
| `Error` | `pub` | Users construct/inspect errors |
| `Parser` | `pub` | Users create parsers |
| `Parser::position` | private | Internal cursor state |
| `Parser::skip_whitespace` | private | Internal helper |
| `util::hash::hash_str` | `pub(crate)` | Shared helper, not user-facing |
| `connection::tcp::TcpStream` | `pub` (but module `connection` is private) | Effectively crate-internal |
| `runtime::scheduler::schedule_internal` | `pub(super)` | Only `runtime` uses it |

Every `pub` should have a justification. If you can't articulate why it's public, it should probably be `pub(crate)` or private.
