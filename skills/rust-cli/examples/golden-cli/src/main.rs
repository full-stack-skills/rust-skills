use std::process::ExitCode;

fn main() -> ExitCode {
    let arguments = std::env::args().skip(1);
    let options = match rust_cli_golden::parse(arguments) {
        Ok(options) => options,
        Err(error) => {
            eprintln!("{error}");
            return ExitCode::from(2);
        }
    };

    match rust_cli_golden::run(&options, std::io::stdout(), std::io::stderr()) {
        Ok(code) => ExitCode::from(code),
        Err(error) => {
            eprintln!("I/O error: {error}");
            ExitCode::FAILURE
        }
    }
}
