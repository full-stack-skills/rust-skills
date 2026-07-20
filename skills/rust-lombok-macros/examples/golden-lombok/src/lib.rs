use lombok_macros::{CustomDebug, Data, Getter, New, Setter};

#[derive(Getter, Setter, New, CustomDebug)]
#[new(pub(crate))]
pub struct WorkerConfig {
    #[get(pub)]
    #[set(pub, type(Into<String>))]
    name: String,

    #[get(pub, type(copy))]
    #[set(pub)]
    workers: usize,

    #[debug(skip)]
    #[new(skip)]
    token: String,
}

impl WorkerConfig {
    pub fn with_token(name: impl Into<String>, workers: usize, token: impl Into<String>) -> Self {
        Self {
            name: name.into(),
            workers,
            token: token.into(),
        }
    }

    pub fn has_token(&self) -> bool {
        !self.token.is_empty()
    }
}

#[derive(Data)]
pub struct ScratchBuffer {
    #[get(pub)]
    #[get_mut(pub(crate))]
    #[set(pub)]
    bytes: Vec<u8>,
}

impl ScratchBuffer {
    pub fn new(bytes: Vec<u8>) -> Self {
        Self { bytes }
    }

    pub fn clear_inside_crate(&mut self) {
        self.get_mut_bytes().clear();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn generated_accessors_and_constructor_keep_the_contract() {
        let mut config = WorkerConfig::new("worker".to_owned(), 4);
        assert_eq!(config.get_name(), "worker");
        assert_eq!(config.get_workers(), 4);
        assert!(!config.has_token());

        config.set_name("batch").set_workers(8);
        assert_eq!(config.get_name(), "batch");
        assert_eq!(config.get_workers(), 8);
    }

    #[test]
    fn custom_debug_redacts_the_token() {
        let config = WorkerConfig::with_token("worker", 4, "actual-secret");
        let output = format!("{config:?}");

        assert!(config.has_token());
        assert!(!output.contains("token"));
        assert!(!output.contains("actual-secret"));
    }

    #[test]
    fn data_is_reserved_for_unconstrained_scratch_data() {
        let mut buffer = ScratchBuffer::new(vec![1, 2]);
        assert_eq!(buffer.get_bytes(), &[1, 2]);

        buffer.set_bytes(vec![3, 4]);
        buffer.clear_inside_crate();
        assert!(buffer.get_bytes().is_empty());
    }
}
