pub fn mode() -> &'static str {
    #[cfg(feature = "diagnostics")]
    {
        "diagnostics"
    }

    #[cfg(not(feature = "diagnostics"))]
    {
        "default"
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exposes_selected_mode() {
        assert!(matches!(mode(), "default" | "diagnostics"));
    }
}
