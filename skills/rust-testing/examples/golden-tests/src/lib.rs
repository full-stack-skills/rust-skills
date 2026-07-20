/// Returns the sum of all values.
///
/// ```
/// use rust_testing_golden::sum;
/// assert_eq!(sum([1, 2, 3]), 6);
/// ```
pub fn sum(values: impl IntoIterator<Item = i32>) -> i32 {
    values.into_iter().sum()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sums_empty_input() {
        assert_eq!(sum([]), 0);
    }
}
