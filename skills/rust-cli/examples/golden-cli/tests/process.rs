use std::process::Command;

#[test]
fn exposes_stdout_stderr_and_exit_code_contract() {
    let output = Command::new(env!("CARGO_BIN_EXE_rust-cli-golden"))
        .args(["--verbose", "data.txt"])
        .output()
        .unwrap();

    assert!(output.status.success());
    assert_eq!(output.stdout, b"input=data.txt\n");
    assert_eq!(output.stderr, b"processed one input\n");
}

#[test]
fn reports_usage_failures_on_stderr() {
    let output = Command::new(env!("CARGO_BIN_EXE_rust-cli-golden"))
        .output()
        .unwrap();

    assert_eq!(output.status.code(), Some(2));
    assert!(output.stdout.is_empty());
    assert_eq!(output.stderr, b"input is required\n");
}
