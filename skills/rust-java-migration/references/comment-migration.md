# Comment Migration Contract

Use this contract for the complete migration batch. Preserve documentation
semantics; translate into clear Chinese Rust documentation rather than copying
JavaDoc syntax mechanically.

## Contents

- [Mandatory mappings](#mandatory-mappings)
- [Complete example](#complete-example)
- [Batch audit](#batch-audit)

## Mandatory mappings

| Java source | Required Rust target |
|---|---|
| class/interface/enum/record/annotation/exception JavaDoc | Rust-native `///` immediately before the primary Rust type; an optional source anchor may appear here |
| constructor/method JavaDoc | Rust-native `///` immediately before the associated function, method, or trait method; an optional source signature may appear here |
| `@param <T>` | `# 类型参数` entry using only the Rust generic name and its real contract |
| `@param value` | `# 参数` entry using only the mapped Rust parameter and its real contract |
| `@return` | `# 返回值`; omit only when both APIs truly return no value |
| `@throws` | `# 错误`, naming each Rust error variant and its actual trigger |
| `@since`, `@deprecated`, `@see` | equivalent doc section/link and Rust attribute when applicable |
| semantic inline/block comment | Chinese `//` comment beside the corresponding Rust branch or invariant |

Apply these rules:

- Write Rust documentation for users of the new Rust project. Do not expose old
  Java parameter names, exception types, or `对应 Java` labels below the type or
  method level.
- Keep detailed object, signature, overload, parameter-name, return, and
  exception mappings in the four migration documents, not in Rust `# 参数`,
  `# 返回值`, `# 错误`, field, variant, or inline comments.
- Preserve preconditions, defaults, nullability, units, ranges, ownership,
  ordering, side effects, thread safety, blocking/async behavior, lifecycle,
  security, and compatibility notes.
- Document every source `@param`; also document any new public Rust parameter and
  explain its Rust contract without migration-history prose.
- When several Java overloads map to one Rust API, merge their documentation
  without losing signature-specific defaults, errors, or side effects.
- When parameters become an options struct, transfer each `@param` contract to
  the corresponding documented field and record the mapping.
- Preserve meaningful documentation on private methods too. Public Rust items
  require useful Rust-native documentation even when the Java source lacks
  JavaDoc; record newly authored clarification in the migration documents.
- Do not preserve stale or false claims silently. Record the source statement,
  explain the approved semantic change, and update all four migration documents.
- Do not count comments, blank descriptions, translated names alone, or generic
  boilerplate as documentation parity.
- When a project denies Clippy `missing_errors_doc` but requires the localized
  `# 错误` heading, configure or narrowly allow that lint at the documented API;
  do not replace real error conditions with generic prose merely to satisfy it.

## Complete example

Java source:

```java
/**
 * 账户扣款服务。实现必须保证同一账户的扣款操作串行可见。
 *
 * @since 2.0
 */
public final class AccountService {
    /**
     * 从账户扣减指定金额。
     *
     * @param accountId 账户标识，不能为空
     * @param amount 扣款金额，必须大于零，单位为元
     * @return 包含扣款后余额的回执
     * @throws IllegalArgumentException 金额不为正数时抛出
     * @throws AccountNotFoundException 账户不存在时抛出
     * @deprecated 使用 withdraw 以获得幂等键支持
     * @see AccountLedger
     */
    @Deprecated(since = "2.1", forRemoval = false)
    public Receipt debit(String accountId, BigDecimal amount) {
        // 先校验金额，避免无效请求触发存储查询。
        // ...
    }
}
```

Rust target:

```rust
/// 账户扣款服务。
///
/// 实现必须保证同一账户的扣款操作串行可见。
///
/// 对应 Java：`com.example.account.AccountService`。
/// 来源文件：`account/src/main/java/com/example/account/AccountService.java`。
///
/// # 起始版本
/// 自 2.0 起提供。
pub struct AccountService {
    repository: AccountRepository,
}

impl AccountService {
    /// 从账户扣减指定金额。
    ///
    /// 对应 Java：
    /// `AccountService#debit(String, BigDecimal)`。
    ///
    /// # 参数
    /// - `account_id`：账户标识，不能为空。
    /// - `amount`：扣款金额，必须大于零，单位为元。
    ///
    /// # 返回值
    /// 返回包含扣款后余额的回执。
    ///
    /// # 错误
    /// - [`AccountError::InvalidAmount`]：`amount` 小于或等于零。
    /// - [`AccountError::NotFound`]：`account_id` 指定的账户不存在。
    ///
    /// # 弃用
    /// 自 2.1 起建议改用 `withdraw`，以获得幂等键支持。
    ///
    /// # 另请参阅
    /// [`AccountLedger`]。
    #[deprecated(since = "2.1.0", note = "请改用 withdraw 以获得幂等键支持")]
    pub fn debit(
        &self,
        account_id: &str,
        amount: Decimal,
    ) -> Result<Receipt, AccountError> {
        // 先校验金额，避免无效请求触发存储查询。
        ensure_positive(amount)?;
        self.repository.debit(account_id, amount)
    }
}
```

## Batch audit

Before implementation, inventory documented objects, methods/constructors,
generic parameters, value parameters, return tags, throws tags, metadata tags,
and semantic inline comments in the migration documents. After the complete
implementation freezes, audit that inventory once against Rust-native
documentation and run:

```bash
python3 "$SKILL_DIR/scripts/audit_migration_layout.py" \
  --rust-root . \
  --require-source-comments \
  --fail-on-warning
cargo doc --workspace --all-features --no-deps
```

The script and `cargo doc` catch only structural/public-documentation failures.
The frozen comment inventory remains the authority for semantic completeness.
