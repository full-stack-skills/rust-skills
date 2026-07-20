# Trait 与泛型

## 选择模型

- 编译期多态和性能优先：泛型 `T: Trait`。
- 运行时异构集合或插件边界：`dyn Trait`。
- 调用者只需一种关联结果类型：associated type。
- 同一实现需要多种结果类型：泛型参数。
- 需要组合多个独立能力：小 trait + blanket impl。

## API 规则

- 把约束放在最接近使用点的位置，避免无意义的宽泛 bounds。
- 公共 trait 保持最小；便利方法可提供默认实现。
- 公开 `impl Trait` 前考虑它对 SemVer 和可表达能力的影响。
- 使用 newtype 遵守 orphan rule，并封装外部类型语义。
- trait object 需要对象安全；含泛型方法或返回 `Self` 的方法通常需要 `where Self: Sized` 或重构。
- 不稳定语言特性必须显式转到 nightly 场景，不能写进 stable 示例。

## 常见验证

```bash
cargo check --all-targets --all-features
cargo test --doc
cargo semver-checks check-release
```

最后一个命令需要第三方工具，只有项目已采用或用户允许安装时才执行。

官方来源：

- https://doc.rust-lang.org/book/ch10-02-traits.html
- https://doc.rust-lang.org/reference/items/traits.html
- https://rust-lang.github.io/api-guidelines/
