---
name: rust-embedded
description: Design, implement, review, and validate embedded Rust firmware, including no_std, targets, runtime and startup, embedded-hal drivers, interrupts, DMA, shared state, async executors, hardware mocks, cross-compilation, flashing, and hardware acceptance evidence. Use when users ask about MCU firmware, portable drivers, HAL versions, bare-metal targets, interrupts, Embassy, RTIC, probe-rs, or embedded testing.
---

# Rust Embedded Firmware Delivery

Establish hardware facts first, then select abstractions and frameworks. Do not treat example code for a specific development board as portable; do not claim firmware is usable without hardware evidence.

## Determine Task Type

Distinguish between the following deliverables:

1.  **Portable `no_std` Library or Driver**: Core logic should be tested on host using mock HALs.
2.  **Specific MCU/Development Board Firmware**: Requires target, runtime, HAL/PAC, memory layout, burn tooling, and hardware acceptance testing.
3.  **Board Support or Boot Code**: Focuses on linking, startup, clocks, pins, and safety invariants.
4.  **Embedded Linux Application**: Typically uses `std`; handle as CLI, Web, or concurrency application unless device interface or cross-compilation is involved.

## Mandatory Hardware Contracts

Confirm and record before modification:

-   Exact MCU model, architecture, development board revision, peripheral connections;
-   Rust target triple, toolchain/MSRV, build profile;
-   Actual versions of runtime, HAL, PAC, BSP, `embedded-hal`, and execution framework;
-   Flash/RAM start addresses, capacity, bootloader source, linker script origin;
-   Debug probes, transmission protocol, burn tools, permissions;
-   Clocks, pin multiplexing, voltage, bus address/mode/frequency;
-   Concurrency model: bare-metal interrupts, critical sections, RTIC, Embassy, or others;
-   Observability channels: `defmt`, UART, RTT, LEDs, logic analyzers, etc.;
-   Real hardware acceptance steps and security constraints.

Do not fabricate values when chip memory layout or pin configuration is uncertain. Prioritize reading existing BSPs, datasheets, reference manuals, and locked documentation from the project repository.

## Workflow

### 1. Establish Build Baseline and Hardware Foundation

Check repository configuration, target selection, and dependency sources:

```bash
rustc --version --verbose
rustup target list --installed
cargo metadata --format-version 1
cargo tree -e features
```

Locate `.cargo/config.toml`, linker parameters, `memory.x`/linker script, `build.rs`, runner, chip feature flags, and existing burn commands. Recreate the current build or save failure logs first.

When selecting target, runtime, or memory layout, read [Target and Runtime](references/target-and-runtime.md).

### 2. Establish Minimum Boot Path

Ensure minimum firmware builds correctly on a specific target to produce checkable images before integrating complex peripherals:

```text
Reset/Startup Code
    -> Initialize Memory and Runtime
    -> Initialize Clocks and Required Peripherals
    -> Enter Unique Application Entry Point
    -> Produce Observable Heartbeat or Diagnostics
```

-   Bare-metal binaries typically use `#![no_std]`; whether to use `#![no_main]` depends on the runtime.
-   Use only `alloc` after providing a global allocator, memory space, and failure strategies.
-   Panic policies must suit both device constraints and debugging environments.
-   Memory layout must derive from chip/BSP/bootloader facts rather than copying example code from other development boards; do not hardcode single architecture assumptions for Cortex-M, RISC-V, or others.

### 3. Separate Portable Logic from Board Wiring

Recommended boundaries:

```text
Pure Domain Logic (No Hardware Dependencies)
    -> portable driver (core + embedded-hal traits)
    -> board adapter (specific HAL/PAC, pins, clocks)
    -> firmware binary (startup, tasks, failure strategies)
```

-   Portable drivers depend on `embedded-hal` trait but not specific PAC singletons.
-   Board layers handle real peripherals and configure pins, clocks, and DMA.
-   Direct access to PAC is reserved for cases where HAL cannot express startup or performance needs; do not silently discard GPIO, bus, or protocol failures using `.ok()`.
-   Document safety assumptions for registers, DMA, bare-metal pointers, and FFI in `SAFETY` comments, then review deeply with `rust-unsafe-ffi`.

### 4. Select a Concurrency Model

Do not arbitrarily mix bare-metal interrupts, multiple executors, or different resource locking models within the same firmware.

-   **Bare-Metal Interrupts**: Ensure ISRs are bounded, non-blocking, and minimize allocations; delegate work to main loop or tasks.
-   **Critical Sections**: Minimize interrupt masking time, explicitly define priority inversion and nesting semantics.
-   **RTIC**: Verify resource locking versions, priorities, and task APIs against the lock version.
-   **Embassy**: Confirm executor configuration, time drivers, chip integration, and cancellation behavior.
-   **DMA**: Buffer ownership and transmission lifecycles must be constrained by types or clear invariants.

When HAL, shared state, or framework selection is required, read [HAL and Concurrency](references/hal-and-concurrency.md). Complex language-level concurrency semantics should use `rust-concurrency`.

### 5. Increase Observability and Failure Strategies

-   Provide recoverable log/probe paths for development builds;
-   Do not let logging timing obscure interrupt or real-time issues;
Distinguish between developer panic scenarios, hardware watchdog reset events, and production graceful degradation strategies.
-   Preserve context for sensor timeouts, bus errors, checksum failures, peripheral unavailability.

Do not leak device keys, pairing credentials, or sensitive identifiers in logs.

### 6. Layered Verification

Verify from fastest to slowest:

1.  Host unit tests on pure logic;
2.  Use mock `embedded-hal` for driver protocol and error path testing;
3.  Cross-compile all relevant features/profiles against the real target;
4.  Check ELF, sections, symbols, image size, stack/heap budgets;
5.  Burn and save probe/UART logs;
6.  Verify pins, buses, timing, interrupts, reset paths on real hardware;
7.  Use oscilloscopes or logic analyzers to confirm electrical and timing facts when needed.

Complete evidence list available in [Hardware Validation](references/hardware-validation.md).

## Common Gateways

Replace `<target>` and `<package>` based on repository configuration:

```bash
cargo fmt --all -- --check
cargo test -p <portable-package> --all-targets
cargo clippy -p <portable-package> --all-targets -- -D warnings
cargo build -p <firmware-package> --target <target> --release
cargo size -p <firmware-package> --target <target> --release
```

`cargo size` requires the project to be installed and `cargo-binutils`; otherwise, use existing ELF/section check tools in the repository. Only execute burn or run commands if the runner is configured for that target and hardware goals are confirmed. Burning changes device state; parse exact targets first and adhere strictly to user authorization scopes.

## Completion Criteria

-   Hardware contracts, dependency versions, memory layout sources clearly defined;
-   Portable logic separated from board code with errors not silently swallowed;
-   Host tests and cross-compilation against target pass;
-   Concurrency, DMA, registers, or unsafe invariants documented;
-   Image size and resource budgets checked;
-   Real hardware acceptance has log/measure evidence.

Mark "Build Verification Only" if no real hardware is available during verification.

## Handoff Boundaries

| Primary Issue | Assigned To |
|---|---|
| Bare pointers, MMIO, FFI, safety encapsulation invariants | `rust-unsafe-ffi` |
| Async, cancellation, Send/Sync and general concurrency semantics | `rust-concurrency` |
| Host tests, attribute tests, coverage or benchmarks | `rust-testing` |
| Target configuration, feature flags, build scripts | `rust-cargo-build` |
| Language ownership, traits, errors, and `core` API | `rust-stable` |

## On-Demand Resources

-   [Target and Runtime](references/target-and-runtime.md): Read when confirming target, startup, or memory layout.
-   [HAL and Concurrency](references/hal-and-concurrency.md): Read while writing driver code for interrupts, RTIC, Embassy tasks.
-   [Hardware Validation](references/hardware-validation.md): Read during build, burn, measurement, and reporting of results.
-   [Scenario Examples](examples/examples.md): Read when task splitting templates are needed.
-   `examples/golden-no-std/`: Host-compilable, mock-testable `no_std` driver boundary examples.

## Basis

-   [The Embedded Rust Book](https://doc.rust-lang.org/stable/embedded-book/)
-   [Rust Embedded Working Group](https://github.com/rust-embedded)
-   [`embedded-hal`](https://docs.rs/embedded-hal/)
-   [The Rust Reference: no_std](https://doc.rust-lang.org/stable/reference/names/preludes.html#the-no_std-attribute)
