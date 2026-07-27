use std::sync::Arc;
use std::thread;

use golden_rust_java_migration::{AgentStateStore, InMemoryAgentStateStore, StateError};

#[test]
fn rejects_empty_java_slot_key_contract() {
    let store = InMemoryAgentStateStore::new();
    assert_eq!(
        store.load_or_create_agent_state("  "),
        Err(StateError::EmptySlotKey)
    );
}

#[test]
fn preserves_state_across_load_save_and_concurrent_reads() {
    let store = Arc::new(InMemoryAgentStateStore::new());
    let initial = store.load_or_create_agent_state("agent-1").unwrap();
    store.save_agent_state(initial.next_version()).unwrap();

    let handles: Vec<_> = (0..4)
        .map(|_| {
            let store = Arc::clone(&store);
            thread::spawn(move || {
                store
                    .load_or_create_agent_state("agent-1")
                    .unwrap()
                    .version()
            })
        })
        .collect();

    for handle in handles {
        assert_eq!(handle.join().unwrap(), 1);
    }
}
