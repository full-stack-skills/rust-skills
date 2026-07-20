# 打包与发布

## 发布前门禁

```bash
cargo fmt --all --check
cargo test --all-targets --all-features
cargo clippy --all-targets --all-features -- -D warnings
cargo package --list
cargo package
```

继续检查：

- 版本号和 SemVer 兼容性。
- `license` 或 `license-file`。
- README、repository、description 和文档链接。
- package 内容不包含密钥、fixture 隐私数据或大型无关文件。
- 所有非 dev 依赖都能从目标 registry 解析。
- workspace 内部依赖声明了可发布版本。

`cargo publish` 是外部状态变更，应确认 registry、账号、token 来源和用户授权。发布后版本不能删除，只能 yank。

官方来源：https://doc.rust-lang.org/cargo/reference/publishing.html
