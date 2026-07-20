# Embedded Scenario Examples

## Scenario: Writing a Portable GPIO Driver for High-Level Enable Devices

**User Request:**
Write a driver using `embedded-hal` to enable an external peripheral with high-level enable, and test it without a development board.

**Execution Boundaries:**

1. Confirm the main version of `embedded-hal` from `Cargo.lock`;
2. The portable crate only depends on the corresponding digital output trait;
3. Return pin errors without calling `.ok()`;
4. Use fake pins to record high/low level calls and inject failures;
5. Complete specific pin type conversions in the board adapter;
6. Report host test evidence, but do not claim electrical verification has been performed.

## Scenario: Adding Firmware for a Specific Development Board

**User Request:**
Add sensor sampling firmware to an existing workspace using development board interrupts that output measurement values once per second.

First, generate and output the hardware contract table confirming MCU type, board revision, target architecture, HAL/PAC/runtime versions, total number of sensors, and pin assignments. Then proceed in sequence:

```text
Minimum Boot & Heartbeat
  -> Bus initialization and sensor identity readout
  -> Single-shot sampling without interrupts
  -> Selection and integration of a scheduling model
  -> Error/timeout handling with observability
  -> Cross-build verification, image inspection, flashing, and measurement
```

Interrupts only publish bounded events; bus transactions and formatted output are handled by regular tasks. Without the board card, cross-build evidence stops at this stage, and pending hardware acceptance items must be listed.
