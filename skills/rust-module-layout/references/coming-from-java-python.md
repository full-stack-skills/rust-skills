# Coming from Java / Python — Mental Model Translation

Rust's module system looks superficially like Java's packages or Python's modules, but the rules are different in ways that catch experienced developers off guard. This reference translates the mental models.

---

## Java → Rust

### Java mental model

- File path = package path. `src/main/java/com/foo/bar/Baz.java` declares `package com.foo.bar;` and the class `Baz`.
- Directory and package are **identical and automatic**. Drop a file in a directory → it's in that package.
- `public` / `protected` / `private` / package-private (default).
- One `public` class per file (convention).
- Imports are purely for abbreviation — `com.foo.bar.Baz` is always reachable without importing.
- JAR is a collection of compiled classes; packages span JARs freely.

### Rust translation

| Java concept | Rust equivalent | Key difference |
|--------------|-----------------|---------------|
| Package | Crate | A crate is a compilation unit; a package is one Cargo.toml that may contain multiple crates |
| Directory = package | **Directory is NOT a module by default** | You must declare `mod foo;` to make a directory a module |
| `public class` | `pub struct` / `pub trait` / `pub fn` | One *item* per declaration, but a file can hold many items |
| `protected` | (no direct equivalent) | Use `pub(crate)` or `pub(super)` for similar effect |
| Package-private | (default `pub(crate)` is close, but default Rust privacy is module-only) | Default is private to the current module *and its descendants* |
| `import com.foo.Bar;` | `use foo::Bar;` | `use` is *required* — you cannot write `com_foo::Bar` without it |
| JAR (collection of classes) | Crate (compilation unit) | Crates are versioned, compiled, and published as a unit |
| Maven multi-module | Cargo workspace | Workspace shares Cargo.lock; members are independent crates |
| `facade` package hiding impl | Private module + `pub use` re-exports | Exact same pattern works in Rust |

### The #1 Java-to-Rust gotcha

**You must declare modules.** Drop a `.rs` file in a directory → the compiler does not see it until a parent declares `mod name;`. This is the source of 80% of "why isn't my code compiling?" for Java devs.

```java
// Java: drop a file in src/main/java/com/foo/Bar.java, done.
```

```rust
// Rust: must declare at every level
// src/lib.rs
pub mod foo;

// src/foo.rs (or src/foo/mod.rs)
pub mod bar;

// src/foo/bar.rs
pub fn hello() {}
```

### The #2 Java-to-Rust gotcha

**Privacy is module-based, not class-based.** In Java, `private` means "only this class." In Rust, default privacy means "this module and its descendants." A struct in `src/parser.rs` can access private items of another struct in the same file — but not private items of a struct in `src/parser/lexer.rs` (different module).

```rust
// src/parser.rs
pub struct Parser { /* ... */ }

fn helper() {}                          // module-private — accessible in this file

mod lexer {
    // Cannot call super::helper() here — lexer is a *child* of parser,
    // so it CAN see parser's private items. (Privacy includes descendants.)
    fn use_helper() { super::helper(); }  // OK
}

mod unrelated {
    // Wait, this is a child of parser too. It can also call helper.
}
```

Actually wait — children *can* see parent privacy. Let me restate: privacy in Rust is "current module and its descendants." So:

- `parser::lexer` (child of `parser`) CAN see `parser::helper` (private in parent)
- `parser::lexer` CANNOT see `parser::other_helper` if `other_helper` is in `parser::unrelated` and is private there (different sibling)

This is more permissive than Java's class-based privacy. Plan visibility accordingly.

### The #3 Java-to-Rust gotcha

**Renaming a module is a breaking change** if the module is `pub`. In Java, moving a class between packages is also breaking, but Java tooling handles it well. In Rust, you must provide a deprecation alias:

```rust
// Old name kept for backwards compat
#[deprecated(note = "use `connection` instead")]
pub mod db {
    pub use crate::connection::*;
}
```

---

## Python → Rust

### Python mental model

- File path = module path. `foo/bar/baz.py` is `foo.bar.baz`.
- Directory + `__init__.py` = package.
- `__init__.py` can re-export items to flatten the namespace.
- Everything is public by default — leading underscore is a *convention*, not enforcement.
- `import foo.bar.baz` works without any declaration in `foo/__init__.py`.
- `__all__` controls `from foo import *`.

### Rust translation

| Python concept | Rust equivalent | Key difference |
|----------------|-----------------|---------------|
| Module (file) | Module (file) | Rust requires `mod foo;` declaration; Python doesn't |
| Package (directory + `__init__.py`) | Module directory (`foo/mod.rs` or `foo.rs`) | Rust has one root per directory, not an init file |
| `_private` convention | `pub(crate)` / private (enforced) | Rust *enforces* privacy; Python only suggests it |
| `import *` | `pub use foo::*;` | Same syntax, same warnings apply |
| `from foo import bar` | `use foo::bar;` | Identical |
| `as` alias | `as` alias | Identical: `use foo::bar as baz;` |
| pip package | Cargo crate | Crates compile separately; Python packages are interpreted |
| namespace package (PEP 420) | (no equivalent) | Every Rust crate has a single root |

### The #1 Python-to-Rust gotcha

**Privacy is enforced in Rust.** In Python, `_helper()` is callable from anywhere — the underscore is a *hint*. In Rust, private items cannot be referenced from outside their module. This catches bugs but also means you must consciously decide visibility.

```python
# Python
def _internal():
    pass

# Anyone can call module._internal() — convention says don't, but you can.
```

```rust
// Rust
fn internal() {}     // private — compiler rejects external calls

pub fn api() {
    internal();      // OK — same module
}
```

### The #2 Python-to-Rust gotcha

**`__init__.py` re-exports are explicit in Rust.** Python:

```python
# foo/__init__.py
from .bar import baz
```

Makes `foo.baz` work. Rust equivalent:

```rust
// src/foo.rs (or src/foo/mod.rs)
mod bar;
pub use bar::baz;       // explicit — what you want exposed
```

The Python `from .bar import *` is `pub use bar::*;` in Rust. Apply the same warnings.

### The #3 Python-to-Rust gotcha

**No namespace packages.** Python lets two separate packages share a namespace (`zope.interface`, `zope.testing`). Rust crates have unique names — two crates cannot both be called `foo`. The crates.io registry enforces this.

---

## Common Anti-Patterns from Java/Python Authors

### Anti-pattern: "Flat package, all imports at the top"

Java devs often write:

```java
// com/mycompany/MyClass.java
package com.mycompany;

import com.mycompany.db.*;
import com.mycompany.net.*;
import com.mycompany.util.*;
```

Translated naively to Rust:

```rust
// src/lib.rs — ❌ anti-pattern
pub mod db;
pub use db::*;
pub mod net;
pub use net::*;
pub mod util;
pub use util::*;
```

This is the "flat lib.rs" anti-pattern. In Java it works because `com.mycompany.db.Pool` and `com.mycompany.Pool` are both reachable. In Rust, glob re-export at the crate root dumps everything into one namespace and destroys the hierarchy.

**Correct Rust**:

```rust
// src/lib.rs
mod db;                              // private — implementation detail
mod net;
mod util;

pub use db::Pool;                    // targeted — only what users need at the root
pub use net::TcpListener;
```

### Anti-pattern: "Singleton class with hundreds of methods"

Java authors sometimes create one giant class with every operation. Translated naively:

```rust
// src/lib.rs — ❌ anti-pattern
pub struct Database {
    // ... 50 fields ...
}

impl Database {
    pub fn new() -> Self { /* ... */ }
    pub fn connect() { /* ... */ }
    pub fn query() { /* ... */ }
    pub fn insert() { /* ... */ }
    pub fn delete() { /* ... */ }
    pub fn migrate() { /* ... */ }
    // ... 40 more methods ...
}
```

**Correct Rust**: split by concern into separate types and modules.

```rust
// src/lib.rs
pub use connection::Connection;
pub use pool::Pool;
pub use migration::Migrator;

mod connection;
mod pool;
mod migration;
```

### Anti-pattern: "Abstract base class + many subclasses"

Java's deep inheritance hierarchies don't translate to Rust. Rust uses traits + composition.

```java
// Java
abstract class AbstractDatabase { ... }
class MySqlDatabase extends AbstractDatabase { ... }
class PostgresDatabase extends AbstractDatabase { ... }
```

```rust
// Rust
pub trait Database {
    fn connect(&self) -> Result<(), Error>;
    fn query(&self, q: &str) -> Result<Rows, Error>;
}

pub struct MySqlConnection { /* ... */ }
pub struct PgConnection { /* ... */ }

impl Database for MySqlConnection { /* ... */ }
impl Database for PgConnection { /* ... */ }
```

### Anti-pattern: "Setters and getters for everything"

Java IDEs auto-generate getters/setters. Rust authors should resist — encapsulation is the default and widening visibility should be deliberate.

```java
// Java
public class User {
    private String name;
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
}
```

```rust
// Rust — DON'T auto-generate
pub struct User {
    pub name: String,                  // ❌ blanket pub
}
```

```rust
// Rust — DO keep private until you have a reason
pub struct User {
    name: String,                      // private
}

impl User {
    pub fn new(name: String) -> Self { Self { name } }
    pub fn name(&self) -> &str { &self.name }   // read-only by default
    // No setter unless you actually need one
}
```

---

## Mental Model Summary

| Question | Java answer | Python answer | Rust answer |
|----------|-------------|---------------|-------------|
| How do I make a new module? | Drop a file in a directory | Drop a file in a directory | Declare `mod foo;` in the parent |
| How do I expose something? | `public` modifier | No enforcement, just convention | `pub` modifier (privacy is enforced) |
| How do I flatten a namespace? | Re-export in package | Re-export in `__init__.py` | `pub use foo::Bar;` at the root |
| How do I hide implementation? | package-private, `protected` | leading underscore | default privacy (private to module) |
| Where does the crate/package start? | `pom.xml`, `setup.py` | Same | `Cargo.toml` |
| What's the compilation unit? | Class | Module (file) | Crate |
| Can I move things around freely? | Yes (refactoring tools handle it) | Yes (just move files) | Yes, but renaming `pub mod` is a breaking change — add deprecation aliases |

The biggest shift is **explicitness**: Rust makes you write `mod foo;` and `pub use foo::Bar;` everywhere. This feels verbose at first but pays off when refactoring — every change is visible in diffs, every public item is a deliberate decision.
