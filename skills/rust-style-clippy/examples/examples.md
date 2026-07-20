# Style & Clippy Examples

## rustfmt config
```toml
# .rustfmt.toml
max_width = 100
tab_spaces = 4
edition = "2024"
use_field_init_shorthand = true
```

## Clippy control
```rust
#![deny(clippy::unwrap_used)]
#![allow(clippy::needless_return)]

fn safe_fn() -> Option<i32> {
    let v = risky()?;  // no unwrap allowed
    Some(v)
}
```

## Edition migration
```bash
cargo fix --edition
# Then update Cargo.toml: edition = "2024"
```
