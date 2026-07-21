//! Tokenizer — implementation detail of `parser`. Not exported externally.

pub(crate) fn tokenize(input: &str) -> Vec<String> {
    // Trivial tokenizer for the golden example: split on whitespace.
    input.split_whitespace().map(str::to_string).collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn splits_on_whitespace() {
        let tokens = tokenize("hello world");
        assert_eq!(tokens, vec!["hello".to_string(), "world".to_string()]);
    }
}
