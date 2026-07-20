# Error Handling Patterns

## Basic ? operator

```rust
use std::fs::File;
use std::io::{self, Read};

fn read_config(path: &str) -> io::Result<String> {
    let mut file = File::open(path)?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    Ok(contents)
}
```

## Custom error with thiserror

```toml
[dependencies]
thiserror = "2"
```

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("io error: {0}")]
    Io(#[from] std::io::Error),

    #[error("parse error at line {line}: {msg}")]
    Parse { line: usize, msg: String },

    #[error("config key '{0}' not found")]
    NotFound(String),
}
```

## Context with anyhow

```toml
[dependencies]
anyhow = "1"
```

```rust
use anyhow::{Context, Result};

fn process() -> Result<()> {
    let data = std::fs::read_to_string("config.toml")
        .context("failed to read config file")?;
    let parsed: serde_json::Value = serde_json::from_str(&data)
        .context("config is not valid JSON")?;
    Ok(())
}

fn main() -> Result<()> {
    process()?;
    Ok(())
}
```
