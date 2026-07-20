pub fn sum(values: &[u64]) -> u64 {
    values.iter().copied().sum()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sums_the_complete_input() {
        assert_eq!(sum(&[1, 2, 3, 4]), 10);
    }
}
