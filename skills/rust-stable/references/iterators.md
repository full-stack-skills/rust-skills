# Iterator Patterns Reference

> Based on `library/core/src/iter/traits/iterator.rs` (official rust-lang/rust).

## Iterator Trait

```rust
pub trait Iterator {
    type Item;
    fn next(&mut self) -> Option<Self::Item>;

    // Provided methods (40+):
    fn size_hint(&self) -> (usize, Option<usize>) { (0, None) }
    fn count(self) -> usize { self.fold(0, |acc, _| acc + 1) }
    fn last(self) -> Option<Self::Item> { self.fold(None, |_, x| Some(x)) }
    fn nth(&mut self, n: usize) -> Option<Self::Item> { /* ... */ }
    fn step_by(self, step: usize) -> StepBy<Self> { /* ... */ }
    fn chain<U>(self, other: U) -> Chain<Self, U::IntoIter> where U: IntoIterator;
    fn zip<U>(self, other: U) -> Zip<Self, U::IntoIter> where U: IntoIterator;
    fn map<B, F>(self, f: F) -> Map<Self, F> where F: FnMut(Self::Item) -> B;
    fn filter<P>(self, predicate: P) -> Filter<Self, P> where P: FnMut(&Self::Item) -> bool;
    fn filter_map<B, F>(self, f: F) -> FilterMap<Self, F> where F: FnMut(Self::Item) -> Option<B>;
    fn enumerate(self) -> Enumerate<Self>;
    fn peekable(self) -> Peekable<Self>;
    fn skip(self, n: usize) -> Skip<Self>;
    fn take(self, n: usize) -> Take<Self>;
    fn flatten(self) -> Flatten<Self> where Self::Item: IntoIterator;
    fn flat_map<U, F>(self, f: F) -> FlatMap<Self, U, F> where F: FnMut(Self::Item) -> U, U: IntoIterator;
    fn fuse(self) -> Fuse<Self>;
    fn inspect<F>(self, f: F) -> Inspect<Self, F> where F: FnMut(&Self::Item);
    fn by_ref(&mut self) -> &mut Self;
    fn collect<B>(self) -> B where B: FromIterator<Self::Item>;
    fn partition<B, F>(self, f: F) -> (B, B) where B: Default + Extend<Self::Item>, F: FnMut(&Self::Item) -> bool;
    fn fold<B, F>(self, init: B, f: F) -> B where F: FnMut(B, Self::Item) -> B;
    fn reduce<F>(self, f: F) -> Option<Self::Item> where F: FnMut(Self::Item, Self::Item) -> Self::Item;
    fn for_each<F>(self, f: F) where F: FnMut(Self::Item);
    fn any<F>(&mut self, f: F) -> bool where F: FnMut(Self::Item) -> bool;
    fn all<F>(&mut self, f: F) -> bool where F: FnMut(Self::Item) -> bool;
    fn find<P>(&mut self, predicate: P) -> Option<Self::Item> where P: FnMut(&Self::Item) -> bool;
    fn position<P>(&mut self, predicate: P) -> Option<usize> where P: FnMut(Self::Item) -> bool;
    fn max(self) -> Option<Self::Item> where Self::Item: Ord;
    fn min(self) -> Option<Self::Item> where Self::Item: Ord;
    fn sum<S>(self) -> S where S: Sum<Self::Item>;
    fn product<S>(self) -> S where S: Product<Self::Item>;
    fn copied<'a, T>(self) -> Copied<Self> where T: 'a + Copy, Self::Item: &'a T;
    fn cloned<'a, T>(self) -> Cloned<Self> where T: 'a, Self::Item: &'a T;
    fn cmp<I>(self, other: I) -> Ordering where I: IntoIterator<Item = Self::Item>, Self::Item: Ord;
    fn next_chunk<const N: usize>(&mut self) -> Result<[Self::Item; N], IntoIter<Self::Item, N>>;
}
```

## Common Patterns

### Chaining adapters
```rust
let result: Vec<_> = (0..100)
    .filter(|x| x % 2 == 0)
    .map(|x| x * 3)
    .take(10)
    .collect();
```

### Custom iterator
```rust
struct Counter { count: u32 }

impl Iterator for Counter {
    type Item = u32;
    fn next(&mut self) -> Option<Self::Item> {
        self.count += 1;
        if self.count < 6 { Some(self.count) } else { None }
    }
}
```

### IntoIterator for custom types
```rust
impl IntoIterator for MyCollection {
    type Item = i32;
    type IntoIter = std::vec::IntoIter<Self::Item>;
    fn into_iter(self) -> Self::IntoIter { self.items.into_iter() }
}
```
