//! 对应 Java：`com.example.state.AgentStateStore`。

use crate::{AgentState, StateError};

/// 智能体状态存储契约。
///
/// 对应 Java：`com.example.state.AgentStateStore`。
pub trait AgentStateStore: Send + Sync {
    /// 加载或创建指定槽位的状态。
    ///
    /// 对应 Java：`AgentStateStore#loadOrCreateAgentState(String slotKey)`。
    ///
    /// # Errors
    ///
    /// `slot_key` 为空或存储锁不可用时返回错误。
    fn load_or_create_agent_state(&self, slot_key: &str) -> Result<AgentState, StateError>;

    /// 以原子替换方式保存指定状态。
    ///
    /// 对应 Java：`AgentStateStore#saveAgentState(AgentState state)`。
    ///
    /// # Errors
    ///
    /// 存储锁不可用时返回错误。
    fn save_agent_state(&self, state: AgentState) -> Result<(), StateError>;
}
