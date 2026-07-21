# Splitting a Growing File (Worked Example)

A step-by-step refactor: turn a 600-line `executor.rs` into an `executor/` directory without breaking callers.

---

## Starting Point

```text
src/
├── lib.rs          // pub mod executor; pub use executor::{Executor, Pool};
└── executor.rs     // 600 lines
```

`executor.rs` contains four concerns:
1. `Executor` struct and its public API
2. `PoolGuard` — a RAII guard for borrowed connections
3. `ExecutorTrait` — the trait the executor implements
4. Internal state: `ExecutorState`, `Config`

---

## Step 1 — Plan the split

Decide which items go where. The goal is *one concern per file*.

| Concern | Target file | Visibility |
|---------|------------|-----------|
| `Executor` struct + impl | `executor/mod.rs` | `pub` (stays here) |
| `PoolGuard` | `executor/guard.rs` | `pub(crate)` |
| `ExecutorTrait` | `executor/traits.rs` | `pub` (re-export) |
| `ExecutorState`, `Config` | `executor/state.rs` | `pub(crate)` |

---

## Step 2 — Create the directory and submodules

```text
src/
├── lib.rs
└── executor/
    ├── mod.rs      // replaces executor.rs
    ├── guard.rs
    ├── traits.rs
    └── state.rs
```

---

## Step 3 — Move items (preserve old paths via re-exports)

```rust
// src/executor/mod.rs
mod guard;
mod traits;
mod state;

pub use traits::ExecutorTrait;        // re-export to preserve old path crate::executor::ExecutorTrait
pub(crate) use guard::PoolGuard;      // crate-internal
pub(crate) use state::{ExecutorState, Config};

pub struct Executor {
    state: ExecutorState,             // private field
}

impl Executor {
    pub fn new(config: Config) -> Self {
        Self { state: ExecutorState::new(config) }
    }

    pub fn acquire(&self) -> PoolGuard {
        guard::PoolGuard::new(self)
    }
}

impl ExecutorTrait for Executor {
    // ...
}
```

```rust
// src/executor/guard.rs
pub(crate) struct PoolGuard { /* ... */ }

impl PoolGuard {
    pub(crate) fn new(_executor: &super::Executor) -> Self {
        Self { /* ... */ }
    }
}

impl Drop for PoolGuard {
    fn drop(&mut self) {
        // return to pool
    }
}
```

```rust
// src/executor/traits.rs
pub trait ExecutorTrait {
    fn execute(&self, query: &str);
}
```

```rust
// src/executor/state.rs
pub(crate) struct ExecutorState { /* ... */ }
pub(crate) struct Config { /* ... */ }

impl ExecutorState {
    pub(crate) fn new(_config: Config) -> Self {
        Self { /* ... */ }
    }
}
```

---

## Step 4 — Update `lib.rs` (no changes needed for callers)

```rust
// src/lib.rs
mod executor;                        // unchanged — still `mod executor;`

pub use executor::{Executor, ExecutorTrait};  // unchanged — paths preserved
```

External callers writing `use my_crate::Executor` and `use my_crate::ExecutorTrait` continue to work with **zero changes**.

---

## Step 5 — Verify

```bash
cargo check                         # compiles with zero caller changes
cargo test                          # all existing tests still pass
cargo doc --no-deps --open          # docs look identical to users
```

---

## Common Variations

### Variation A — Keep the main type in its own file

If `Executor` is itself large, split it out of `mod.rs`:

```text
src/executor/
├── mod.rs          // pub mod executor_struct; pub use executor_struct::Executor;
├── executor_struct.rs   // the big struct
├── guard.rs
├── traits.rs
└── state.rs
```

```rust
// src/executor/mod.rs
mod executor_struct;
mod guard;
mod traits;
mod state;

pub use executor_struct::Executor;
pub use traits::ExecutorTrait;
pub(crate) use guard::PoolGuard;
pub(crate) use state::{ExecutorState, Config};
```

### Variation B — Modern layout (`executor.rs + executor/`)

Edition 2018+ lets you skip `mod.rs`:

```text
src/
├── lib.rs
├── executor.rs         // replaces executor/mod.rs
└── executor/
    ├── guard.rs
    ├── traits.rs
    └── state.rs
```

Same content as `mod.rs` goes in `executor.rs`. Pick one layout per crate.

### Variation C — Extract to a workspace member

If `executor/` grows past 2000 lines and has its own stability trajectory, promote to a separate crate. See `rust-workspace`.

---

## Anti-Example — Premature Split

Don't split if:
- The file is < 300 lines
- All items are tightly coupled and never used independently
- The split would create files with only 10–20 lines each

Premature splits hurt more than they help. Split when *navigating* the file becomes painful, not before.
