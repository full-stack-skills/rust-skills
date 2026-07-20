use std::sync::atomic::{AtomicUsize, Ordering};

use rayon::prelude::*;

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

pub fn parallel_sum(values: &[u64]) -> u64 {
    values.par_iter().copied().sum()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn joins_all_scoped_workers() {
        assert_eq!(count_workers(4), 4);
    }

    #[test]
    fn uses_cpu_parallelism_for_independent_items() {
        assert_eq!(parallel_sum(&[1, 2, 3, 4]), 10);
    }
}
