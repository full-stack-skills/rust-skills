# 类型转换

## 选择规则

- 无损、不会失败且语义明确：实现 `From<T>`，自动获得 `Into<U>`。
- 可能失败：实现 `TryFrom<T>`，自动获得 `TryInto<U>`。
- 只需要借用视图：`AsRef<T>` / `AsMut<T>`。
- 昂贵复制或分配：使用 `to_*` 命名并让成本可见。
- 廉价借用视图：使用 `as_*` 命名。
- 数值窄化：优先 `TryFrom`，不要默认 `as` 截断是正确业务语义。

## API 提示

- 泛型入口可接受 `impl AsRef<Path>`、`impl Into<String>`，但不要过度泛化导致错误难读。
- 错误类型通过 `From` 支持 `?` 转换时，应保留原始 source。
- FFI 类型转换、布局和指针转换转到 `rust-unsafe-ffi`。

官方来源：https://doc.rust-lang.org/std/convert/
