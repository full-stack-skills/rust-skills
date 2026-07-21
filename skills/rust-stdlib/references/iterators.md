# Iterators — Laziness, Composition, Performance

> Companion to `SKILL.md` Part 7. Canonical source: [std::iter](https://doc.rust-lang.org/std/iter/index.html).

## Three iteration modes

| Method | Yields | Consumes source? |
|--------|--------|------------------|
| `iter()` | `&T` | No |
| `iter_mut()` | `&mut T` | No |
| `into_iter()` | `T` | Yes (moves) |

```rust
let v = vec![1, 2, 3];
for x in &v      { /* &i32 */ }     // .iter()
for x in &mut v  { /* &mut i32 */ }
for x in v       { /* i32; v gone */ }   // .into_iter()
```

`for x in collection` desugars to `collection.into_iter()`, so it consumes by value. `&collection` borrows, `&mut collection` borrows mutably.

## Lazy evaluation

Iterator adaptors do nothing until consumed. Composing many adaptors is free until you call a consumer.

```rust
let v = vec![1, 2, 3, 4, 5];
// Nothing runs yet — just an iterator state machine.
let it = v.iter().filter(|&&x| x > 1).map(|&x| x * 10);
// Consumption forces evaluation.
let out: Vec<i32> = it.collect();    // [20, 30, 40, 50]
```

## Common adaptors

| Adaptor | Effect |
|---------|--------|
| `map(f)` | Transform each item |
| `filter(p)` | Keep items passing predicate |
| `filter_map(f)` | map + filter in one (return `Option`) |
| `flat_map(f)` | map + flatten |
| `flatten()` | Collapse one level of nesting |
| `take(n)` | Stop after `n` items |
| `skip(n)` | Skip first `n` items |
| `enumerate()` | Pair with index |
| `zip(other)` | Pair two iterators |
| `chain(other)` | Concatenate |
| `rev()` | Reverse (if `DoubleEndedIterator`) |
| `peekable()` | Look at next without consuming |
| `step_by(n)` | Every nth item |
| `take_while(p)` / `skip_while(p)` | Stop/skip while predicate holds |
| `cloned()` / `copied()` | Convert `&T` to `T` |

## Consumers

| Consumer | Returns |
|----------|---------|
| `collect::<C>()` | Collection `C` |
| `sum::<T>()` / `product::<T>()` | Aggregated value |
| `fold(init, f)` | Custom fold, with seed |
| `reduce(f)` | Fold without seed (returns `Option<T>`) |
| `any(p)` / `all(p)` | `bool` (short-circuits) |
| `find(p)` / `position(p)` | First match / index |
| `count()` | Number of items |
| `max()` / `min()` | `Option<T>` (needs `Ord`) |
| `max_by_key(f)` / `min_by_key(f)` | By key |
| `nth(n)` | nth item as `Option<T>` |
| `for_each(f)` | Side-effect loop |

## collect into HashMap

`collect` works on iterators of `(K, V)` tuples.

```rust
use std::collections::HashMap;

let pairs = vec![("a", 1), ("b", 2), ("a", 3)];
let map: HashMap<&str, i32> = pairs.into_iter().collect();
// Last value wins on duplicate keys: {"a": 3, "b": 2}

// Group by key with fold-like pattern
let mut grouped: HashMap<&str, Vec<i32>> = HashMap::new();
for (k, v) in [("a", 1), ("b", 2), ("a", 3)] {
    grouped.entry(k).or_default().push(v);
}
```

## Windows and chunks (slice methods)

```rust
let s = [1, 2, 3, 4, 5];
for win in s.windows(3)  { /* [1,2,3], [2,3,4], [3,4,5] */ }
for chk in s.chunks(2)   { /* [1,2], [3,4], [5] */ }
for chk in s.chunks_mut(2) { /* mutable non-overlapping */ }
```

These are `slice` methods, not iterator adaptors — they yield subslices.

## Iterator constructors

| Function | Yields |
|----------|--------|
| `once(x)` | A single item |
| `once_with(f)` | A single item, lazily |
| `empty()` | Nothing |
| `repeat(x)` | Same item forever (needs `take`) |
| `repeat_with(f)` | Generated items forever |
| `from_fn(f)` | Items from a closure returning `Option<T>` |
| `successors(first, f)` | Items from a step function |
| `iter::zip(a, b)` | Same as `a.into_iter().zip(b)` |

```rust
use std::iter;

// Fibonacci via successors
let fib = iter::successors(Some((0u32, 1u32)), |&(a, b)| Some((b, a + b)))
    .map(|(a, _)| a)
    .take(10)
    .collect::<Vec<_>>();   // [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

// Infinite generation with from_fn
let mut i = 0;
let naturals = std::iter::from_fn(|| { i += 1; Some(i) });
```

## Implementing your own iterator

```rust
struct Counter { value: u32, max: u32 }

impl Iterator for Counter {
    type Item = u32;
    fn next(&mut self) -> Option<u32> {
        if self.value < self.max {
            self.value += 1;
            Some(self.value)
        } else { None }
    }
}

let c = Counter { value: 0, max: 3 };
assert_eq!(c.map(|x| x * 10).collect::<Vec<_>>(), vec![10, 20, 30]);
```

Implement `Iterator` only; you get `map`, `filter`, `collect`, and dozens of others for free. Add `DoubleEndedIterator` / `ExactSizeIterator` only when meaningful.

## Performance: zero-cost

Iterators compile down to tight loops — equivalent to hand-written `for`. `clippy` and the optimizer fold adapter chains into a single pass; allocating intermediate `Vec`s is the only real cost. Avoid collecting between stages unless you actually need the materialized collection.

```rust
// One pass, no allocation
let v = vec![1, 2, 3, 4, 5];
let sum_of_doubles: i32 = v.iter().filter(|&&x| x % 2 == 0).map(|&x| x * 2).sum();
assert_eq!(sum_of_doubles, 12);
```

## Gotchas

| Pitfall | Fix |
|---------|-----|
| Collecting then iterating again | Chain adaptors, collect once |
| `.collect::<Vec<_>>().into_iter()` mid-pipeline | `.collect::<Vec<_>>()` only at the end |
| `for (i, x) in v.iter().enumerate()` then ignoring `i` | Just `for x in &v` |
| Infinite iterator + `collect` | Add `.take(n)` |
| `&v.iter()` confusion | `&v` already iterates by ref; `v.iter()` also yields `&T` |

## Reference

- [std::iter](https://doc.rust-lang.org/std/iter/index.html)
- [std::slice::windows](https://doc.rust-lang.org/std/slice/trait.Slice.html#method.windows) / [chunks](https://doc.rust-lang.org/std/primitive.slice.html#method.chunks)
- [Iterator trait](https://doc.rust-lang.org/std/iter/trait.Iterator.html)
- [Rust Standard Library](https://doc.rust-lang.org/std/)
