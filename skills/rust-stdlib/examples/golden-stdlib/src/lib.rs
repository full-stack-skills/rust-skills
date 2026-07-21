//! `golden-stdlib` — exercises std collections, smart pointers, interior
//! mutability, mpsc channels, scoped threads, iterators, and time APIs.

use std::cell::Cell;
use std::collections::{BTreeMap, HashMap, VecDeque};
use std::sync::mpsc;
use std::sync::OnceLock;
use std::thread;
use std::time::{Duration, Instant};

// === Collection selection ===

/// Count word frequencies using the entry API (single hash, no double lookup).
pub fn word_counts<'a>(words: &[&'a str]) -> HashMap<&'a str, u32> {
    let mut counts: HashMap<&'a str, u32> = HashMap::new();
    for &word in words {
        *counts.entry(word).or_insert(0) += 1;
    }
    counts
}

/// Sorted iteration requires BTreeMap (HashMap is unordered).
pub fn sorted_word_counts<'a>(words: &[&'a str]) -> BTreeMap<&'a str, u32> {
    let mut counts: BTreeMap<&'a str, u32> = BTreeMap::new();
    for &word in words {
        *counts.entry(word).or_insert(0) += 1;
    }
    counts
}

/// VecDeque for sliding-window operations (push/pop from both ends).
pub fn sliding_window_max(nums: &[i32], k: usize) -> Vec<i32> {
    let mut deque: VecDeque<usize> = VecDeque::new();
    let mut result = Vec::with_capacity(nums.len().saturating_sub(k - 1));
    for (i, &n) in nums.iter().enumerate() {
        while deque.front().is_some_and(|&front| front + k <= i) {
            deque.pop_front();
        }
        while deque.back().is_some_and(|&back| nums[back] <= n) {
            deque.pop_back();
        }
        deque.push_back(i);
        if i + 1 >= k {
            if let Some(&max_idx) = deque.front() {
                result.push(nums[max_idx]);
            }
        }
    }
    result
}

// === Smart pointer selection ===

/// OnceLock: lazy one-time initialization, thread-safe.
static CONFIG: OnceLock<Vec<String>> = OnceLock::new();

pub fn config() -> &'static [String] {
    CONFIG.get_or_init(|| vec!["default".to_string(), "values".to_string()])
}

// === Interior mutability ===

/// Cell<T> is for Copy types only — no runtime borrow check.
pub struct Counter {
    count: Cell<u32>,
}

impl Default for Counter {
    fn default() -> Self {
        Self::new()
    }
}

impl Counter {
    pub const fn new() -> Self {
        Self {
            count: Cell::new(0),
        }
    }

    pub fn increment(&self) {
        self.count.set(self.count.get().saturating_add(1));
    }

    pub fn value(&self) -> u32 {
        self.count.get()
    }
}

// === Iterator combinator chain ===

/// Parse numbers from strings, square the even ones, return as Vec.
pub fn parse_and_square(input: &[&str]) -> Vec<i64> {
    input
        .iter()
        .filter_map(|s| s.parse::<i64>().ok())
        .filter(|&n| n % 2 == 0)
        .map(|n| n * n)
        .collect()
}

// === Option/Result combinators ===

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct User {
    pub id: u32,
    pub name: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Error {
    NotFound,
    Empty,
}

/// Find a user by id, return Result<User, Error>.
pub fn find_user(users: &[User], id: u32) -> Result<User, Error> {
    users
        .iter()
        .find(|u| u.id == id)
        .cloned()
        .ok_or(Error::NotFound)
}

/// Chain: validate non-empty, then find.
pub fn lookup(users: &[User], query: Option<u32>) -> Result<User, Error> {
    let id = query.ok_or(Error::Empty)?;
    find_user(users, id)
}

// === mpsc channels ===

/// Spawn a worker, send numbers, return the sum received back.
pub fn channel_sum(numbers: Vec<u32>) -> u32 {
    let (tx, rx) = mpsc::channel();
    let handle = thread::spawn(move || {
        let sum: u32 = numbers.iter().sum();
        tx.send(sum).unwrap();
    });
    handle.join().unwrap();
    rx.recv().unwrap()
}

// === Scoped threads — borrow without 'static ===

/// Parallel increment of a slice, using scoped threads (Rust 1.63+).
pub fn parallel_increment(slice: &mut [i32]) {
    thread::scope(|s| {
        let chunk = slice.len().div_ceil(4);
        for sub in slice.chunks_mut(chunk) {
            s.spawn(move || {
                for x in sub.iter_mut() {
                    *x += 1;
                }
            });
        }
    });
}

// === Time ===

/// Measure elapsed time of a closure.
pub fn measure<R>(f: impl FnOnce() -> R) -> (R, Duration) {
    let start = Instant::now();
    let r = f();
    (r, start.elapsed())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hashmap_counts_words() {
        let counts = word_counts(&["a", "b", "a", "c", "a"]);
        assert_eq!(counts.get("a"), Some(&3));
        assert_eq!(counts.get("b"), Some(&1));
    }

    #[test]
    fn btreemap_is_sorted() {
        let counts = sorted_word_counts(&["b", "a", "c"]);
        let keys: Vec<_> = counts.keys().copied().collect();
        assert_eq!(keys, vec!["a", "b", "c"]);
    }

    #[test]
    fn vecdeque_for_sliding_window() {
        let result = sliding_window_max(&[1, 3, -1, 5, 3, 6, 7], 3);
        assert_eq!(result, vec![3, 5, 5, 6, 7]);
    }

    #[test]
    fn oncelock_initializes_once() {
        let a = config();
        let b = config();
        assert!(std::ptr::eq(a.as_ptr(), b.as_ptr()));
    }

    #[test]
    fn cell_for_copy_interior_mutability() {
        let counter = Counter::new();
        counter.increment();
        counter.increment();
        assert_eq!(counter.value(), 2);
    }

    #[test]
    fn iterator_combinator_chain() {
        let result = parse_and_square(&["1", "2", "3", "4", "5", "x"]);
        assert_eq!(result, vec![4, 16]);
    }

    #[test]
    fn result_combinators_for_lookup() {
        let users = vec![
            User {
                id: 1,
                name: "a".into(),
            },
            User {
                id: 2,
                name: "b".into(),
            },
        ];
        assert_eq!(lookup(&users, Some(1)).unwrap().name, "a");
        assert_eq!(lookup(&users, Some(99)).unwrap_err(), Error::NotFound);
        assert_eq!(lookup(&users, None).unwrap_err(), Error::Empty);
    }

    #[test]
    fn mpsc_channel_communicates() {
        let result = channel_sum(vec![1, 2, 3, 4, 5]);
        assert_eq!(result, 15);
    }

    #[test]
    fn scoped_threads_borrow_and_mutate() {
        let mut data = vec![1, 2, 3, 4, 5, 6, 7, 8];
        parallel_increment(&mut data);
        assert_eq!(data, vec![2, 3, 4, 5, 6, 7, 8, 9]);
    }

    #[test]
    fn instant_measures_elapsed() {
        let (val, elapsed) = measure(|| {
            thread::sleep(Duration::from_millis(10));
            42
        });
        assert_eq!(val, 42);
        assert!(elapsed >= Duration::from_millis(8));
    }
}
