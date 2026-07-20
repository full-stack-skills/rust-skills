use std::collections::HashMap;

pub fn word_counts(input: &str) -> HashMap<&str, usize> {
    let mut counts = HashMap::new();
    for word in input.split_whitespace() {
        *counts.entry(word).or_default() += 1;
    }
    counts
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn counts_repeated_words() {
        let counts = word_counts("safe fast safe");
        assert_eq!(counts.get("safe"), Some(&2));
        assert_eq!(counts.get("fast"), Some(&1));
    }
}
