use std::collections::HashMap;
use std::sync::RwLock;

use crate::{AgentState, AgentStateStore, StateError};

/// 基于内存的线程安全状态存储。
///
/// 使用 `RwLock<HashMap<...>>` 保证复合“加载或创建”操作的原子性。
///
/// 对应 Java：`com.example.state.InMemoryAgentStateStore`。
#[derive(Debug, Default)]
pub struct InMemoryAgentStateStore {
    states: RwLock<HashMap<String, AgentState>>,
}

impl InMemoryAgentStateStore {
    /// 创建空状态存储。
    ///
    /// 对应 Java：`InMemoryAgentStateStore()`。
    #[must_use]
    pub fn new() -> Self {
        Self::default()
    }
}

impl AgentStateStore for InMemoryAgentStateStore {
    fn load_or_create_agent_state(&self, slot_key: &str) -> Result<AgentState, StateError> {
        if slot_key.trim().is_empty() {
            return Err(StateError::EmptySlotKey);
        }

        // 在同一写锁临界区完成查询和插入，保证复合操作的原子性。
        let mut states = self.states.write().map_err(|_| StateError::LockPoisoned)?;
        let state = states
            .entry(slot_key.to_owned())
            .or_insert_with(|| AgentState::new(slot_key));
        Ok(state.clone())
    }

    fn save_agent_state(&self, state: AgentState) -> Result<(), StateError> {
        let mut states = self.states.write().map_err(|_| StateError::LockPoisoned)?;
        states.insert(state.slot_key().to_owned(), state);
        Ok(())
    }
}
