# Collections — Selection, Allocation, and Patterns

> Companion to `SKILL.md` Part 1. Canonical source: [std::collections](https://doc.rust-lang.org/std/collections/index.html).

## Map selection: HashMap vs BTreeMap

| Aspect | `HashMap<K, V>` | `BTreeMap<K, V>` |
|--------|-----------------|------------------|
| Lookup | O(1) average, O(n) worst | O(log n) |
| Ordering | None (insertion-unstable) | Sorted by key |
| Range queries | No | `range`, `range_mut` |
| Key trait | `Hash + Eq` | `Ord` |
| Memory | Higher (buckets + load factor) | Compact nodes |
| Stable addresses | No (rehash moves entries) | Mostly stable |

```rust
use std::collections::{BTreeMap, HashMap};

// HashMap: fast unordered lookup
let mut hits: HashMap<&str, u32> = HashMap::new();
hits.entry("/").or_insert(0);

// BTreeMap: ordered iteration + range
let mut prices: BTreeMap<&str, u32> = BTreeMap::new();
prices.insert("a", 1);
prices.insert("c", 3);
for (k, v) in prices.range("a".."c") {   // ("a", 1)
    println!("{k}={v}");
}
```

Choose `BTreeMap` when you need sorted iteration, range queries, or deterministic key order across runs. Otherwise prefer `HashMap`.

## Allocation behavior

| Method | Effect |
|--------|--------|
| `Vec::new()` | No allocation (capacity 0) |
| `Vec::with_capacity(n)` | One allocation of `n` |
| `.reserve(additional)` | Ensure room for `additional` more items |
| `.reserve_exact(n)` | Do not over-reserve (still correct) |
| `.shrink_to_fit()` | Free unused capacity (may realloc) |
| `.push(x)` when full | Grow capacity ~2x, then insert (amortized O(1)) |

```rust
let mut v: Vec<i32> = Vec::with_capacity(1000);
for i in 0..1000 { v.push(i); }     // no reallocation
v.shrink_to_fit();                  // drop extra capacity
```

If you know the size up front, `with_capacity` avoids the growth reallocations (each doubles and copies). `shrink_to_fit` after bulk insertion trims wasted memory; do not call it repeatedly in a hot loop — it can reallocate.

## Entry API patterns

`Entry` lets you read-or-write a key in a single lookup, avoiding the double hash of `get` then `insert`.

```rust
use std::collections::HashMap;

let mut counts: HashMap<&str, u32> = HashMap::new();
for w in ["a", "b", "a", "c", "a"] {
    *counts.entry(w).or_insert(0) += 1;
}
assert_eq!(counts["a"], 3);

// and_modify + or_insert: update-if-present, set-if-absent
counts.entry("a").and_modify(|c| *c += 10).or_insert(99);
```

| Entry method | When |
|--------------|------|
| `or_insert(v)` | Provide default if missing |
| `or_insert_with(\|\| ..)` | Lazy default (compute only when missing) |
| `or_default()` | `Default::default()` if missing |
| `and_modify(f)` | Mutate existing value |
| `insert(v)` | Replace + return old |

## VecDeque for queues

Double-ended buffer; `push_back` / `pop_front` is the FIFO pattern.

```rust
use std::collections::VecDeque;

let mut q: VecDeque<i32> = VecDeque::with_capacity(4);
q.push_back(1); q.push_back(2);
assert_eq!(q.pop_front(), Some(1));   // FIFO
q.push_front(0);                       // LIFO side also available
```

Prefer `VecDeque` over `Vec` when you remove from the front — `Vec::remove(0)` is O(n).

## BinaryHeap for priority queues

A max-heap by default. Wrap in `Reverse` for a min-heap.

```rust
use std::collections::BinaryHeap;
use std::cmp::Reverse;

let mut max = BinaryHeap::from([3, 1, 5]);
assert_eq!(max.pop(), Some(5));            // largest first

let mut min = BinaryHeap::new();
for x in [3, 1, 5] { min.push(Reverse(x)); }
assert_eq!(min.pop(), Some(Reverse(1)));   // smallest first
```

`peek` is O(1); `push`/`pop` are O(log n). Items must implement `Ord`.

## Sets

`HashSet<T>` mirrors `HashMap<T, ()>`; `BTreeSet<T>` mirrors `BTreeMap<T, ()>`. Same selection logic: unordered fast membership vs sorted membership.

```rust
use std::collections::HashSet;

let a: HashSet<i32> = [1, 2, 3].into_iter().collect();
let b: HashSet<i32> = [2, 3, 4].into_iter().collect();
assert_eq!(a.intersection(&b).copied().collect::<Vec<_>>(), vec![2, 3]);
```

## When LinkedList is appropriate

Almost never. `LinkedList<T>` has poor cache locality, no random access, and `Vec<T>` beats it even on middle insertion for moderate sizes. Justifiable only when you need O(1) split/merge with cursor APIs on long-lived lists. Default to `Vec` and revisit if profiling demands otherwise.

## Hasher selection

`HashMap` uses `RandomState` (SipHash-1-3) by default. SipHash is collision-resistant against adversarial keys but slower than non-cryptographic hashers.

| Hasher | Crate | Use |
|--------|-------|-----|
| `RandomState` (SipHash) | std | Default; safe against HashDoS |
| `FxHashMap` / `BuildHasherDefault<FxHasher>` | `fxhash` | Integer-like keys, trusted input |
| `AHashMap` | `ahash` | Fast general-purpose, still randomized |
| `BuildHasherDefault<DefaultHasher>` | std | Deterministic (not for untrusted input) |

```rust
// Faster hashing for trusted keys
use fxhash::FxHashMap;
let mut m: FxHashMap<u64, &str> = FxHashMap::default();
m.insert(1, "fast");
```

Only swap the hasher when hashing is a measured hotspot. Randomization matters when keys come from untrusted input.

## Iteration characteristics

| Collection | Order |
|-------------|-------|
| `Vec`, `VecDeque` | Insertion (front-to-back) |
| `LinkedList` | Insertion |
| `HashMap`, `HashSet` | Arbitrary, may change across runs |
| `BTreeMap`, `BTreeSet` | Sorted |
| `BinaryHeap` | Heap order at the top, not fully sorted |

`into_iter()` consumes; `.iter()` borrows; `.iter_mut()` mutably borrows. For `(K, V)` maps, `.iter()` yields `(&K, &V)`.

## Capacity and reallocation cost

Reallocation is the dominant cost in growing collections. It allocates a new buffer, copies all elements, and frees the old one. To avoid it: call `with_capacity`, `reserve`, or `try_reserve` before bulk insertion. `try_reserve` returns a `Result` instead of aborting on allocation failure.

```rust
let n = items.len();
let mut out = Vec::with_capacity(n);
out.try_reserve(n).ok().expect("oom");
for it in items { out.push(transform(it)); }
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `map.get(&k).unwrap_or(&0)` then `map.insert(k, v)` | Use `entry(k)` |
| `Vec::new()` then 10000 `push` in a loop | `with_capacity` |
| `vec.remove(0)` in a loop | `VecDeque::pop_front` |
| `HashMap` for small N (under ~20) | `Vec<(K, V)>` + `.iter().find()` |
| Sorting `HashMap` keys repeatedly | Use `BTreeMap` |

## Reference

- [std::collections](https://doc.rust-lang.org/std/collections/index.html)
- [std::collections::hash_map::Entry](https://doc.rust-lang.org/std/collections/hash_map/struct.Entry.html)
- [std::vec::Vec](https://doc.rust-lang.org/std/vec/struct.Vec.html)
- [Rust Standard Library](https://doc.rust-lang.org/std/)
