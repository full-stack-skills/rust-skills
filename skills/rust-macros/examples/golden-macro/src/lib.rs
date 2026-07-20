macro_rules! string_list {
    ($($value:expr),* $(,)?) => {
        vec![$($value.to_string()),*]
    };
}

pub fn labels() -> Vec<String> {
    string_list!["safe", "fast"]
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn expands_repeated_values() {
        assert_eq!(labels(), ["safe", "fast"]);
    }
}
