use criterion::{Criterion, criterion_group, criterion_main};
use rust_performance_golden::sum;
use std::hint::black_box;

fn benchmark_sum(criterion: &mut Criterion) {
    let values = (0_u64..1_024).collect::<Vec<_>>();
    criterion.bench_function("sum_1024", |bencher| {
        bencher.iter(|| sum(black_box(&values)));
    });
}

criterion_group!(benches, benchmark_sum);
criterion_main!(benches);
