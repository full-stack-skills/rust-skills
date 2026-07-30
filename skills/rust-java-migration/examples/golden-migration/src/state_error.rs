use std::error::Error;
use std::fmt;

/// 状态存储错误。
///
/// 对应 Java：`com.example.state.StateException`。
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum StateError {
    /// 状态槽位标识为空。
    EmptySlotKey,
    /// 并发锁发生中毒，存储状态不再可信。
    LockPoisoned,
}

impl fmt::Display for StateError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::EmptySlotKey => formatter.write_str("slot_key must not be empty"),
            Self::LockPoisoned => formatter.write_str("state store lock is poisoned"),
        }
    }
}

impl Error for StateError {}
