#[must_use]
pub fn normalized_names(names: &[String]) -> Vec<String> {
    names
        .iter()
        .map(|name| name.trim().to_lowercase())
        .filter(|name| !name.is_empty())
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn trims_filters_and_normalizes() {
        let names = [" Ferris ".to_owned(), " ".to_owned()];
        assert_eq!(normalized_names(&names), ["ferris"]);
    }
}
