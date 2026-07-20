# HashMap Reference

> Based on `library/alloc/src/collections/hash_map/` (official rust-lang/rust).

```rust
use std::collections::HashMap;

// Creation
let map: HashMap<String, i32> = HashMap::new();
let map: HashMap<&str, i32> = [("a", 1), ("b", 2)].into_iter().collect();

// Insert & Access
map.insert("key".to_string(), 42);
map.insert("key".to_string(), 100);         // overwrite

let val = map.get("key");                   // Option<&V>
let val = map.get_mut("key");               // Option<&mut V>
let val = map.get_key_value("key");         // Option<(&K, &V)>

// Check existence
map.contains_key("key");
map.is_empty();
map.len();

// Remove
map.remove("key");                          // Option<V>
map.remove_entry("key");                    // Option<(K, V)>

// Iteration
for (key, val) in &map { /* &K, &V */ }
for (key, val) in &mut map { /* &K, &mut V */ }
for (key, val) in map { /* owned K, V */ }

// Entry API (most idiomatic)
map.entry("key".to_string()).or_insert(0);
map.entry("key".to_string()).or_insert_with(|| expensive_default());
map.entry("key".to_string()).or_default();

// Advanced Entry API
use std::collections::hash_map::Entry;
match map.entry("key".to_string()) {
    Entry::Occupied(mut entry) => { *entry.get_mut() += 1; }
    Entry::Vacant(entry) => { entry.insert(1); }
}

// Transform
map.retain(|_, v| *v > 0);                  // in-place filter
map.keys();                                  // iterator over K
map.values();                                // iterator over V
map.values_mut();                            // iterator over &mut V
map.into_values();                           // owned V iterator

// Capacity
map.reserve(100);
map.shrink_to_fit();
```

## Custom Key Types

```rust
#[derive(Debug, PartialEq, Eq, Hash)]
struct CustomKey { id: u32, name: String }
```
