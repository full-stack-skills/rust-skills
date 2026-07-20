#[derive(Debug, Eq, PartialEq)]
pub struct Options {
    pub verbose: bool,
    pub input: Option<String>,
}

pub fn run(
    options: &Options,
    mut stdout: impl std::io::Write,
    mut stderr: impl std::io::Write,
) -> std::io::Result<u8> {
    match options.input.as_deref() {
        Some(input) => {
            writeln!(stdout, "input={input}")?;
            if options.verbose {
                writeln!(stderr, "processed one input")?;
            }
            Ok(0)
        }
        None => {
            writeln!(stderr, "input is required")?;
            Ok(2)
        }
    }
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

    #[test]
    fn keeps_results_and_diagnostics_on_separate_streams() {
        let options = Options {
            verbose: true,
            input: Some("data.txt".into()),
        };
        let mut stdout = Vec::new();
        let mut stderr = Vec::new();

        let exit_code = run(&options, &mut stdout, &mut stderr).unwrap();

        assert_eq!(exit_code, 0);
        assert_eq!(stdout, b"input=data.txt\n");
        assert_eq!(stderr, b"processed one input\n");
    }
}
