use std::sync::Arc;
use std::sync::atomic::{AtomicUsize, Ordering};

use tracing::{Subscriber, info, info_span};
use tracing_subscriber::layer::{Context, Layer, SubscriberExt};

#[derive(Clone)]
struct EventCounter(Arc<AtomicUsize>);

impl<S> Layer<S> for EventCounter
where
    S: Subscriber,
{
    fn on_event(&self, _event: &tracing::Event<'_>, _context: Context<'_, S>) {
        self.0.fetch_add(1, Ordering::Relaxed);
    }
}

pub fn run_observed_operation(counter: Arc<AtomicUsize>, job_id: u64) {
    let subscriber = tracing_subscriber::registry().with(EventCounter(counter));
    tracing::subscriber::with_default(subscriber, || {
        let span = info_span!("process_job", job.id = job_id);
        let _entered = span.enter();
        info!(outcome = "completed", "job completed");
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn emits_one_structured_completion_event() {
        let counter = Arc::new(AtomicUsize::new(0));
        run_observed_operation(Arc::clone(&counter), 42);
        assert_eq!(counter.load(Ordering::Relaxed), 1);
    }
}
