#[derive(Debug, Eq, PartialEq)]
pub struct Options {
    pub verbose: bool,
    pub input: Option<String>,
}

pub fn parse(arguments: impl IntoIterator<Item = String>) -> Result<Options, String> {
    let mut options = Options {
        verbose: false,
        input: None,
    };

    for argument in arguments {
        match argument.as_str() {
            "-v" | "--verbose" => options.verbose = true,
            value if value.starts_with('-') => return Err(format!("unknown option: {value}")),
            value if options.input.is_none() => options.input = Some(value.to_owned()),
            value => return Err(format!("unexpected argument: {value}")),
        }
    }
    Ok(options)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rejects_unknown_flags() {
        assert_eq!(
            parse(["--unknown".into()]),
            Err("unknown option: --unknown".into())
        );
    }
}
