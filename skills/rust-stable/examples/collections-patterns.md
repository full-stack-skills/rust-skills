# Collections Patterns

## Word frequency counter

```rust
use std::collections::HashMap;

fn word_freq(text: &str) -> HashMap<&str, u32> {
    let mut freq = HashMap::new();
    for word in text.split_whitespace() {
        *freq.entry(word).or_insert(0) += 1;
    }
    freq
}
```

## Group by key

```rust
use std::collections::HashMap;

#[derive(Debug)]
struct Item { category: String, price: f64 }

fn group_by_category(items: Vec<Item>) -> HashMap<String, Vec<Item>> {
    let mut groups = HashMap::new();
    for item in items {
        groups.entry(item.category.clone()).or_default().push(item);
    }
    groups
}
```

## Iterator chain — filter, map, collect

```rust
let nums: Vec<i32> = (0..20)
    .filter(|n| n % 2 == 0)             // even numbers
    .map(|n| n * n)                      // squared
    .collect();
```

## Custom sorting

```rust
let mut people = vec![
    ("Alice", 30), ("Bob", 25), ("Charlie", 35),
];
people.sort_by(|a, b| a.1.cmp(&b.1));   // sort by age
```
