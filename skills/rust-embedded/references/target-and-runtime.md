# Goals and Runtime Environment

## Decision Table

| Fact | Source of Verification | Risks if Unconfirmed |
|---|---|---|
| MCU/Board Model | Schematic, BSP (Board Support Package), chip markings | Pin or peripheral errors |
| Target Triple | BSP templates, Rust target list | Instruction set / ABI errors |
| Runtime | Official examples and locked versions from BSP/HAL documentation | Startup vector table errors |
| Flash/RAM Layout | Data sheets, bootloader configuration, linker script | Overwriting the bootloader or memory boundary violations |
| Runner/Probe | `.cargo/config.toml`, CI pipelines, development documentation | Incorrect device for flashing/probing |
| Panic / Logging | Profile settings, probe capabilities, product strategy | Inability to diagnose issues or real-time jitter |

## Architecture Branches

- **Cortex-M**: Typically provides the vector table and entry point via the corresponding runtime. Verify whether specific cores include FPU support, atomic instructions, and target-specific features.
- **RISC-V**: Confirm ISA extensions, memory mapping, startup/runtime interaction with interrupt controllers.
- **Other Architectures**: Use only the BSP or chip ecosystem explicitly supported for a given runtime and linker configuration.

Do not infer full `target` configurations solely from architecture names; rely on repository configurations and chip documentation instead.

## Memory Layout

- Confirm bootloader location, application slots, persistent storage regions, and interrupt vector positions;
- Distinguish between physical RAM, executable RAM, cache, and DMA-accessible areas;
- Treat linker scripts as product configuration items subject to version control and review processes;
- Compare section sizes and addresses before and after modifications;
- Do not copy `memory.x` values from another board into default settings.

## `alloc` Module Usage

Introduce the `alloc` module only when all of the following conditions are met:

1. A suitable global allocator has been implemented for the target architecture;
2. Heap regions have been defined and proven to not conflict with stack or static storage areas;
3. Allocation failure strategies have been explicitly defined;
4. Worst-case memory exhaustion and fragmentation risks are acceptable within constraints.
