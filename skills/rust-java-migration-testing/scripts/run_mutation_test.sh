#!/usr/bin/env bash
# Run cargo-mutants against one crate and keep artifacts under that crate's target directory.
#
# Usage:
#   ./run_mutation_test.sh crates/my-crate
#   ./run_mutation_test.sh crates/my-crate --features feature-a,feature-b
#
# Optional:
#   CARGO_MUTANTS_OUTPUT_DIR=target/custom-mutants ./run_mutation_test.sh crates/my-crate

set -euo pipefail

if [ "$#" -lt 1 ]; then
    echo "usage: $0 <crate-path> [cargo-mutants options...]" >&2
    exit 2
fi

crate_path="$1"
shift
manifest_path="$crate_path/Cargo.toml"

if [ ! -f "$manifest_path" ]; then
    echo "error: Cargo manifest not found: $manifest_path" >&2
    exit 2
fi

if ! cargo mutants --version >/dev/null 2>&1; then
    echo "error: cargo-mutants is not installed; install it with 'cargo install cargo-mutants'" >&2
    exit 2
fi

output_dir="${CARGO_MUTANTS_OUTPUT_DIR:-$crate_path/target/mutants.out}"
mkdir -p "$(dirname "$output_dir")"

echo "running cargo-mutants"
echo "manifest: $manifest_path"
echo "output:   $output_dir"

cargo mutants \
    --manifest-path "$manifest_path" \
    --output "$output_dir" \
    "$@"

echo "mutation artifacts:"
echo "  $output_dir/outcomes.json"
echo "  $output_dir/caught.txt"
echo "  $output_dir/missed.txt"
echo "  $output_dir/timeout.txt"
echo "review surviving and timeout mutants individually; do not apply a universal score threshold"
