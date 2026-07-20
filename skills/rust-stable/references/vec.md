# Vec Reference

> Based on `library/alloc/src/vec/mod.rs` (official rust-lang/rust).

```rust
// Creation
let v: Vec<i32> = Vec::new();       // empty
let v = vec![1, 2, 3];              // macro
let v = vec![0; 100];               // 100 zeros

// From iterators
let v: Vec<_> = (0..10).collect();
let v: Vec<_> = "a,b,c".split(',').collect();

// Access
let x = &v[0];                      // index (panics on OOB)
let x = v.get(0);                   // Option<&T>
let first = v.first();              // Option<&T>
let last = v.last();                // Option<&T>

// Mutation
v.push(4);
let last = v.pop();                 // Option<T>
v.insert(1, 99);                    // shift elements right
v.remove(0);                        // shift elements left
v.swap_remove(0);                   // swap with last, then pop (O(1))
v.truncate(5);                      // keep first 5
v.clear();

// Search & sort
v.sort();
v.sort_by(|a, b| b.cmp(a));         // descending
v.sort_unstable();                  // faster, may reorder equals
v.reverse();
v.dedup();
v.contains(&2);
v.binary_search(&3);

// Transform
v.retain(|x| *x > 0);               // in-place filter
v.dedup_by(|a, b| a == b);
v.resize(10, 0);                    // grow/shrink with fill value
v.extend([4, 5, 6]);                // append iterable

// Capacity
v.reserve(100);                     // reserve capacity
v.shrink_to_fit();                  // shrink to len
v.capacity();
v.len();
v.is_empty();

// Raw parts (unsafe)
let ptr = v.as_ptr();
let ptr = v.as_mut_ptr();
let (ptr, len, cap) = v.into_raw_parts();
```
