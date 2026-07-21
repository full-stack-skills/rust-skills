//! `golden-by-example` — exercises type conversion, flow control, closures,
//! generics, traits, error handling, attributes, and module patterns.

use std::fmt;

// === Type conversions ===

/// Newtype that demonstrates From / TryFrom / Display.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct Age(u8);

impl From<u8> for Age {
    fn from(value: u8) -> Self {
        Self(value)
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AgeError;

impl fmt::Display for AgeError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "invalid age")
    }
}

impl std::error::Error for AgeError {}

impl TryFrom<i32> for Age {
    type Error = AgeError;
    fn try_from(value: i32) -> Result<Self, Self::Error> {
        if !(0..=150).contains(&value) {
            return Err(AgeError);
        }
        Ok(Self(value as u8))
    }
}

// === Flow control ===

/// Demonstrates `if let`, `match` with guards, and `@`-binding.
pub fn classify(score: i32) -> &'static str {
    match score {
        s if s < 0 => "invalid",
        0..=49 => "fail",
        50..=69 => "pass",
        70..=89 => "merit",
        90..=100 => "distinction",
        _ => "out of range",
    }
}

/// `while let` pattern — pop from a Vec.
pub fn drain(mut v: Vec<i32>) -> i32 {
    let mut sum = 0;
    while let Some(x) = v.pop() {
        sum += x;
    }
    sum
}

// === Closures ===

/// Closures capturing by reference vs `move`.
pub fn make_adder(delta: i32) -> impl Fn(i32) -> i32 {
    move |x| x + delta
}

/// Counter that returns a closure with internal state.
pub fn make_counter() -> impl FnMut() -> i32 {
    let mut count = 0;
    move || {
        count += 1;
        count
    }
}

// === Generics + Traits ===

/// Generic function with `where` clause.
pub fn sum<T>(xs: &[T]) -> T
where
    T: Default + std::ops::AddAssign + Copy,
{
    let mut acc = T::default();
    for x in xs {
        acc += *x;
    }
    acc
}

/// Trait with default method and associated type.
pub trait Accumulator {
    type Item;
    fn add(&mut self, item: Self::Item);
    fn total(&self) -> usize;
    fn is_empty(&self) -> bool {
        self.total() == 0 // default impl
    }
}

pub struct Counter {
    n: usize,
}

impl Accumulator for Counter {
    type Item = ();
    fn add(&mut self, _: Self::Item) {
        self.n += 1;
    }
    fn total(&self) -> usize {
        self.n
    }
}

// === Error handling with ? and custom errors ===

#[derive(Debug)]
pub enum ParseError {
    Empty,
    Invalid(String),
}

impl fmt::Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ParseError::Empty => write!(f, "empty input"),
            ParseError::Invalid(s) => write!(f, "invalid: {s}"),
        }
    }
}

impl std::error::Error for ParseError {}

pub fn parse_age(input: &str) -> Result<Age, ParseError> {
    let trimmed = input.trim();
    if trimmed.is_empty() {
        return Err(ParseError::Empty);
    }
    let n: i32 = trimmed
        .parse()
        .map_err(|e: std::num::ParseIntError| ParseError::Invalid(e.to_string()))?;
    Age::try_from(n).map_err(|e| ParseError::Invalid(e.to_string()))
}

// === Attributes ===

/// `#[derive]` and `#[non_exhaustive]`.
#[derive(Debug, Clone, PartialEq, Eq)]
#[non_exhaustive]
pub struct Config {
    pub retries: u32,
}

impl Default for Config {
    fn default() -> Self {
        Self { retries: 3 }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn from_into_lossless() {
        let age = Age::from(42);
        assert_eq!(age, Age(42));
        let also: Age = 42.into();
        assert_eq!(age, also);
    }

    #[test]
    fn try_from_fallible() {
        assert!(Age::try_from(-1).is_err());
        assert!(Age::try_from(200).is_err());
        assert_eq!(Age::try_from(25).unwrap(), Age(25));
    }

    #[test]
    fn match_with_guards_and_ranges() {
        assert_eq!(classify(45), "fail");
        assert_eq!(classify(75), "merit");
        assert_eq!(classify(95), "distinction");
        assert_eq!(classify(-1), "invalid");
    }

    #[test]
    fn while_let_drains_vec() {
        assert_eq!(drain(vec![1, 2, 3, 4]), 10);
    }

    #[test]
    fn closure_captures_and_returns_fn() {
        let add5 = make_adder(5);
        assert_eq!(add5(10), 15);
    }

    #[test]
    fn fnmut_carries_state() {
        let mut counter = make_counter();
        assert_eq!(counter(), 1);
        assert_eq!(counter(), 2);
        assert_eq!(counter(), 3);
    }

    #[test]
    fn generic_sum_with_where_clause() {
        assert_eq!(sum(&[1, 2, 3]), 6);
        assert_eq!(sum(&[1.5, 2.5]), 4.0);
    }

    #[test]
    fn trait_default_method() {
        let mut c = Counter { n: 0 };
        assert!(c.is_empty());
        c.add(());
        c.add(());
        assert_eq!(c.total(), 2);
        assert!(!c.is_empty());
    }

    #[test]
    fn error_propagation_with_question() {
        assert!(matches!(parse_age(""), Err(ParseError::Empty)));
        assert!(matches!(parse_age("200"), Err(ParseError::Invalid(_))));
        assert_eq!(parse_age("42").unwrap(), Age(42));
    }

    #[test]
    fn non_exhaustive_struct_default() {
        let cfg = Config::default();
        assert_eq!(cfg.retries, 3);
    }
}
