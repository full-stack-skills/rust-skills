use crate::{AgentState, StateError};

/// 智能体状态存储契约。
///
/// 对应 Java：`com.example.state.AgentStateStore`。
#[allow(clippy::missing_errors_doc)]
pub trait AgentStateStore: Send + Sync {
    /// 加载或创建指定槽位的状态。
    ///
    /// 对应 Java：`AgentStateStore#loadOrCreateAgentState(String slotKey)`。
    ///
    /// # 参数
    /// - `slot_key`：状态槽位标识，不能为空。
    ///
    /// # 错误
    ///
    /// `slot_key` 为空或存储锁不可用时返回错误。
    fn load_or_create_agent_state(&self, slot_key: &str) -> Result<AgentState, StateError>;

    /// 以原子替换方式保存指定状态。
    ///
    /// 对应 Java：`AgentStateStore#saveAgentState(AgentState state)`。
    ///
    /// # 参数
    /// - `state`：需要保存的完整状态。
    ///
    /// # 错误
    ///
    /// 存储锁不可用时返回错误。
    fn save_agent_state(&self, state: AgentState) -> Result<(), StateError>;
}
