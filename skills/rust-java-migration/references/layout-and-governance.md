# Layout and Migration Governance

## Source-to-target layout

- Map each Java class, interface, enum, or record to one primary Rust file.
- Convert the object name to `snake_case.rs`; keep the Rust type in `PascalCase`.
- Keep a tightly coupled Java inner builder with its primary type only when it is not an independently referenced object.
- Map the final meaningful Java package level to the same Rust directory name.
- Use deeper Rust directories only when they preserve an existing Java domain boundary.
- Keep `lib.rs` and `mod.rs` limited to module declarations, visibility, documentation, and re-exports.
- Keep runtime compatibility facades thin. Put real object behavior in the corresponding object files.

## Documentation contract

Every migrated type must include Chinese Rust doc comments:

```rust
//! 对应 Java：com.example.state.AgentStateStore
//! 来源文件：module/src/main/java/com/example/state/AgentStateStore.java

/// 智能体状态存储契约。
///
/// 保留 Java 对象的加载、创建与并发可见性语义。
pub trait AgentStateStore {
    /// 加载或创建指定槽位的状态。
    ///
    /// 对应 Java：`AgentStateStore#loadOrCreateAgentState(String)`。
    ///
    /// # 参数
    /// - `slot_key`：Java 参数 `slotKey`。
    ///
    /// # 错误
    /// 持久化或反序列化失败时返回错误。
    fn load_or_create_agent_state(&self, slot_key: &str) -> Result<AgentState, StateError>;
}
```

Translate semantic points from JavaDoc, including null handling, ordering, thread safety, defaults, exceptions, side effects, and version notes. Do not copy license-incompatible prose verbatim beyond what the project license permits.

## Overloads

Create one row per Java overload before implementing any of them. Decide:

- whether one generic Rust function can preserve every contract;
- which signature owns the canonical base name;
- which semantic suffix distinguishes variants;
- whether a trait, builder, `Into`, `AsRef`, iterator, or options object is clearer;
- whether Java defaults need explicit Rust wrapper functions.

Avoid numeric suffixes and avoid using Rust default arguments, which do not exist.

## Planned exceptions

An exception record must contain:

| Field | Required value |
|---|---|
| Scope | exact module/object/method |
| State | `JAVA_ONLY_EXEMPT` or `PLANNED_BLOCKED` |
| Reason | technical incompatibility or named dependency |
| User approval | date/issue/decision reference |
| Runtime exposure | disabled, isolated feature, or non-default facade |
| Coverage accounting | excluded from implemented and verified numerators |
| Exit criteria | concrete dependency/version/test required |
| Owner | responsible project/team |

For an approved placeholder module, label the module exception `PLANNED_BLOCKED`. Preserve the object/signature plan and label each signature-only object row `SKELETON` (or `PLANNED_BLOCKED` when that object has its own external blocker). Neither state enters implementation or behavior numerators. Never describe the module as implemented.

## Existing implementation preservation

Before editing an existing Rust port:

1. Record dirty files and current tests.
2. Query callers and blast radius.
3. Identify real behavior already implemented, even if its shape is imperfect.
4. Add missing compatibility wrappers or split files incrementally.
5. Preserve tests and observable behavior.
6. Do not replace a rich implementation with a generated facade merely to improve counts.

## Red-flag patterns

- many public migrated types in `lib.rs`, `mod.rs`, or `compat.rs`;
- per-object files containing only `pub use` of one compatibility module;
- `todo!()`, `unimplemented!()`, empty blocks, unconditional placeholder errors;
- manifest rows marked complete without executable tests;
- wildcard imports masking unclear dependencies;
- merged Java objects without an approved mapping row;
- methods that ignore parameters with `let _ = ...`;
- returns of constant/default values where Java computes results;
- tests that assert only construction or registration;
- Rust-only facades counted as migrated Java objects.

Treat the static audit script as a detector, then confirm every finding from source and tests.
