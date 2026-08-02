# Workspace Examples

## Binary + lib crate
```rust
// src/lib.rs
pub fn greet(name: &str) -> String { format!("Hello, {name}!") }

// src/main.rs
fn main() { println!("{}", my_crate::greet("world")); }
```

## Module tree
```rust
// src/lib.rs
pub mod front_of_house;
mod back_of_house;

// src/front_of_house.rs or front_of_house/mod.rs
pub mod hosting;

// src/front_of_house/hosting.rs
pub fn add_to_waitlist() {}
```

## Workspace
```toml
# root Cargo.toml
[workspace]
members = ["my-core", "my-cli"]
```

Small cohesive workspaces default to root-flat members. Use `support/*` or a
`crates/` container only when project scale, stable families, root noise, or a
multi-language repository justifies it.
