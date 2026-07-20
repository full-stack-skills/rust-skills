# HAL and Concurrency

## Layering

- `core` domain logic: independent of hardware crates.
- portable driver: depends on the `embedded-hal` trait to express protocol state and errors;
- HAL/BSP adapter: configures clocks, pins, DMA, and specific peripherals;
- PAC/registers layer: used only for HAL gaps, bootstrapping, or performance paths after formal verification;
- firmware: selects task model, combines resources, and defines product failure strategies.

## Driver Design

- Use the locked `embedded-hal` main version exclusively without mixing incompatible traits;
- Preserve low-level errors where necessary, mapping them to domain-specific errors while retaining source context;
- Distinguish shared bus semantics from exclusive device usage for bus devices;
- Establish explicit contracts regarding delays, timeouts, chip select modes, address space, and frequency;
- Implement verification calls using fake/mock data to ensure correct call ordering, frame structure, and failure recovery behavior;
- Do not hardcode pin numbers, clock trees, or PAC types within the portable driver.

## Interrupts and Shared State

- ISRs must be bounded, non-blocking, and free from uncontrollable resource allocation;
- The sequence for clearing interrupt sources must strictly follow the chip datasheet;
- Shared state protection requires a selected model; bare `static mut` declarations are forbidden to avoid ownership evasion.
- Critical sections should be as short as possible while evaluating high-priority interrupt latency impacts;
- DMA buffers must not be aliased or prematurely released during transmission;
- Atomic type availability depends on the target platform and cannot be inferred from host-side testing environments.

## Framework Selection

| Model     | Applicable Scenarios           | Primary Verification Points       |
|-----------|--------------------------------|-----------------------------------|
| Main Loop + Interrupts   | Small, deterministic firmware  | ISR boundaries, event handoff, critical sections |
| RTIC                     | Static tasks and priority-based resource models | API versions, resource locks, scheduling & priorities |
| Embassy                  | Async peripherals and executor ecosystem | Executor integration, time driver support, cancellation semantics, chip compatibility |

Do not introduce frameworks solely for convenience; make decisions based on hardware support requirements, real-time needs, team maintenance strategies, and testing methodologies.

## Main Resources

- [embedded-hal documentation](https://docs.rs/embedded-hal/)
- [RTIC Book](https://rtic.rs/2/book/en/)
- [Embassy documentation](https://embassy.dev/)
- [critical-section](https://docs.rs/critical-section/)
