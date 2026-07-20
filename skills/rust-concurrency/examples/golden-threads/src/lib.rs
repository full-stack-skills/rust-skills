use std::sync::atomic::{AtomicUsize, Ordering};

pub fn count_workers(workers: usize) -> usize {
    let completed = AtomicUsize::new(0);
    std::thread::scope(|scope| {
        for _ in 0..workers {
            scope.spawn(|| {
                completed.fetch_add(1, Ordering::Relaxed);
            });
        }
    });
    completed.load(Ordering::Relaxed)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn joins_all_scoped_workers() {
        assert_eq!(count_workers(4), 4);
    }
}
