---
name: rust-cli
description: Rust CLI 应用开发技能 — clap 参数与子命令、stdin/stdout/stderr、文件和路径、配置、日志、终端交互、错误与退出码。Use when building or testing command-line programs, filters, batch tools, or terminal UX; hand test harness design to rust-testing and general I/O semantics to rust-stable.
---

# Rust CLI 应用开发

> 基于 [Command Line Book](https://rust-cli.github.io/book/index.html) 与社区最佳实践。

## Capability Boundaries

### ✅ 强项
1. 命令行参数解析（clap：#[derive(Parser)] 派生式、Command::new 构建式）
2. 标准 I/O（io::stdin/stdout/stderr、BufRead trait）
3. 文件 I/O（File::open/create、read_to_string/write_all、BufReader/BufWriter）
4. 路径操作（Path/PathBuf、join/exists/read_dir/canonicalize）
5. 配置文件加载（toml/json + serde_deserialize、env 变量）
6. 日志系统（log + env_logger/tracing crate）
7. 终端输出（colored/ansi_term/clicolors、indicatif 进度条）
8. 退出码（ExitCode、process::exit）
9. 错误处理（anyhow + CLI 友好错误格式）
10. 常用 CLI 模式（管道处理、循环读取、信号处理、进度提示）

### ⚠️ 前置要求
1. 理解 Rust 基础 I/O（`rust-stable`）

### ❌ 不适用范围
1. Web 服务 → 使用 `rust-web` 技能
2. GUI 应用 → 暂不涉及

## 何时使用

- "用 Rust 写一个命令行工具"
- "解析 CLI 参数"
- "读写文件"
- "日志输出配置"
- "管道输入处理"

## Data Privacy

本技能不收集、存储或传输任何用户数据。

---

## 一、命令行参数（clap）

```toml
# Cargo.toml
[dependencies]
clap = { version = "4", features = ["derive"] }
```

```rust
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "myapp", version, about = "A CLI tool")]
struct Cli {
    /// 输入文件路径
    #[arg(short, long, default_value = "-")]
    input: String,

    /// 输出文件路径
    #[arg(short, long)]
    output: Option<String>,

    /// 详细模式
    #[arg(short, long, default_value_t = false)]
    verbose: bool,

    /// 子命令
    #[command(subcommand)]
    command: Option<Commands>,
}

#[derive(Subcommand)]
enum Commands {
    /// 初始化配置
    Init {
        /// 模板名
        #[arg(short, long)]
        template: Option<String>,
    },
    /// 运行任务
    Run {
        /// 任务名
        name: String,
    },
}

fn main() {
    let cli = Cli::parse();
    // cli.input, cli.output, cli.verbose, cli.command
}
```

## 二、标准 I/O

```rust
use std::io::{self, BufRead, Write};

// 读取 stdin 所有行
fn read_stdin() -> io::Result<()> {
    let stdin = io::stdin();
    for line in stdin.lock().lines() {
        println!("> {}", line?);
    }
    Ok(())
}

// 管道模式
fn grep<R: BufRead>(reader: R, pattern: &str) {
    for line in reader.lines().map_while(Result::ok) {
        if line.contains(pattern) {
            println!("{line}");
        }
    }
}

// 写入 stdout/stderr
let mut stdout = io::stdout().lock();
write!(stdout, "output: {value}")?;
writeln!(io::stderr(), "error occurred")?;
```

## 三、文件 I/O

```rust
use std::fs::{self, File};
use std::io::{BufReader, BufWriter, Read, Write};

// 读取文件
let contents = fs::read_to_string("input.txt")?;
let bytes = fs::read("data.bin")?;

// 写入文件
fs::write("output.txt", "hello")?;
let mut file = File::create("output.txt")?;
file.write_all(b"hello")?;

// 高效读取大文件
let file = File::open("large.txt")?;
let reader = BufReader::new(file);
for line in reader.lines() {
    println!("{}", line?);
}

// 高效写入
let file = File::create("output.log")?;
let mut writer = BufWriter::new(file);
writeln!(writer, "line 1")?;
```

## 四、路径操作

```rust
use std::path::{Path, PathBuf};

let path = Path::new("/usr/local/bin");
let file_path = path.join("myapp");

assert!(file_path.exists());
assert!(file_path.is_file());

// 遍历目录
for entry in fs::read_dir(".")? {
    let entry = entry?;
    println!("{}", entry.path().display());
}

// 路径组件
let path = Path::new("a/b/c.txt");
assert_eq!(path.parent(), Some(Path::new("a/b")));
assert_eq!(path.file_name(), Some(OsStr::new("c.txt")));
assert_eq!(path.extension(), Some(OsStr::new("txt")));
assert_eq!(path.file_stem(), Some(OsStr::new("c")));
```

## 五、日志

```rust
// Cargo.toml
// [dependencies]
// log = "0.4"
// env_logger = "0.11"

use log::{info, warn, error};

fn main() {
    env_logger::init();  // RUST_LOG=info ./myapp
    info!("application started");
    warn!("deprecated feature used");
    error!("failed to open file");
}

// 运行：RUST_LOG=info cargo run
// 日志格式：2026-06-17T10:00:00Z [INFO] myapp - message
```

## 六、终端输出

```rust
// colored — 彩色输出
// [dependencies] colored = "2"
use colored::Colorize;
println!("{}", "error".red().bold());
println!("{}", "success".green());

// indicatif — 进度条
// [dependencies] indicatif = "0.17"
use indicatif::ProgressBar;
let pb = ProgressBar::new(100);
for i in 0..100 {
    pb.inc(1);
}
pb.finish_with_message("done");
```

## 七、退出码

```rust
use std::process::{ExitCode, Termination};

// main 返回 ExitCode
fn main() -> ExitCode {
    if success {
        ExitCode::SUCCESS
    } else {
        ExitCode::FAILURE
        // 或 ExitCode::from(2)
    }
}

// 或使用 anyhow
// fn main() -> anyhow::Result<()> {
//     run()?;
//     Ok(())
// }
```

## Workflow

Step 1. 解析参数 — 使用 clap 定义 CLI 接口（参数、选项、子命令）
Step 2. 处理 I/O — 使用 stdin/stdout/stderr，支持管道模式
Step 3. 读写文件 — 使用 BufReader/BufWriter 高效处理文件
Step 4. 配置日志 — 使用 env_logger/tracing 输出运行日志
Step 5. 错误处理 — 使用 anyhow 包裹错误，提供友好的错误消息
Step 6. 测试验证 — 用 assert_cmd 测试 CLI 输出，用 assert_fs 测试文件操作


## Gotchas

1. clap 的 default_value 和 required 冲突 - 设 default_value 后 required=false
2. io::stdin().lock() 的生命周期 - StdinLock 借用 Stdin，lock() 后不能 move stdin
3. BufReader 的 lines() 已移除换行符 - 返回的 String 不含 \n
4. Path::new('') 是空路径 - path.join('') 返回 path 本身
5. env_logger::init() 只能调用一次 - 测试中需用 env_logger::try_init()


## 按需资源

- [CLI 示例](examples/examples.md)
- [常用 crate 速查](references/references.md)
- `examples/golden-cli/`：CI 编译并测试参数错误的黄金示例

## 官方参考

- [Command Line Book](https://rust-cli.github.io/book/index.html)
- [clap docs](https://docs.rs/clap/)
- [std::io](https://doc.rust-lang.org/std/io/)
- [std::fs](https://doc.rust-lang.org/std/fs/)
