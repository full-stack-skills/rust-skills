# Quick Start Workflows

## Create a new project

```bash
cargo new my-app
cd my-app
cargo run
```

## Read a file

```rust
use std::fs;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let contents = fs::read_to_string("data.txt")?;
    for line in contents.lines() {
        println!("{line}");
    }
    Ok(())
}
```

## Parse CSV

```rust
use std::fs;

struct Record { name: String, age: u32 }

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let contents = fs::read_to_string("data.csv")?;
    let records: Vec<Record> = contents
        .lines()
        .skip(1)                         // header
        .filter_map(|line| {
            let parts: Vec<&str> = line.split(',').collect();
            Some(Record {
                name: parts.first()?.to_string(),
                age: parts.get(1)?.parse().ok()?,
            })
        })
        .collect();
    Ok(())
}
```
