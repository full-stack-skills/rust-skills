/// 智能体状态值对象。
///
/// 维护槽位标识和版本语义。
///
/// 对应 Java：`com.example.state.AgentState`。
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct AgentState {
    slot_key: String,
    version: u64,
}

impl AgentState {
    /// 创建一个初始版本为零的状态。
    ///
    /// 对应 Java：`AgentState(String slotKey)`。
    ///
    /// # 参数
    /// - `slot_key`：状态槽位标识，不能为空。
    #[must_use]
    pub fn new(slot_key: impl Into<String>) -> Self {
        Self {
            slot_key: slot_key.into(),
            version: 0,
        }
    }

    /// 返回槽位标识。
    ///
    /// 对应 Java：`AgentState#getSlotKey()`。
    #[must_use]
    pub fn slot_key(&self) -> &str {
        &self.slot_key
    }

    /// 返回当前版本。
    ///
    /// 对应 Java：`AgentState#getVersion()`。
    #[must_use]
    pub const fn version(&self) -> u64 {
        self.version
    }

    /// 返回版本递增后的新状态。
    ///
    /// 对应 Java：`AgentState#nextVersion()`。
    #[must_use]
    pub fn next_version(&self) -> Self {
        Self {
            slot_key: self.slot_key.clone(),
            version: self.version.saturating_add(1),
        }
    }
}
