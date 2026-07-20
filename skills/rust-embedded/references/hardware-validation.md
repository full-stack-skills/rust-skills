# Hardware Verification

## Building Evidence

- Rust toolchain, target directories, and feature sets;
- Complete build commands with exit codes;
- ELF/mirror hashes and section sizes;
- Release profiles and linking parameters;
- Flash/RAM/stack usage versus budget.

## Pre-Burn Checks

- Parse probe serial number and target chip without relying on "first device";
- Confirm operations do not overwrite bootloader, calibration values, or production keys;
- Save recoverable firmware with explicit recovery procedure;
- Verify power supply, voltage levels, and wiring connections;
- Execute erase, write, and reset only within authorized user scope.

## Hardware Acceptance Matrix

| Verification Item | Input/Condition | Observation Method | Expected Outcome | Actual Evidence |
|---|---|---|---|---|
| Cold Start | Power-on after power-off | RTT/Serial Console/Led Indicators | Ready within budget time window | Logs/Videos/Metrics |
| Peripheral Communication | Normal Device State | Log Output/Logic Analyzer | Frames and Timing Correctly Captured | Capture Files |
| Timeout Recovery | Disconnected Device | Log Output/System Status | Bounded Failure followed by Recovery | Logs |
| Interrupt Stress | Maximum Event Rate | Counter/Timing Oscilloscope | No Losses or Strategy-Based Degradation | Measurements |
| Watchdog Timer | Manually Blocked State | Reset Cause Register | Resets according to strategy | Logs |

## Reporting Guidelines

- "Build Success" does not equate to "Hardware Availability";
- "Burn Successful" does not equal "Functional Acceptance Verified";
- When no target board exists, explicitly report completed host testing and cross-compilation efforts without hardware verification;
- Timing, voltage, power consumption, and RF conclusions must be derived from appropriate measurement equipment or authoritative documentation.

## Primary References

- [probe-rs Documentation](https://probe.rs/docs/)
- [cargo-binutils Repository](https://github.com/rust-embedded/cargo-binutils)
- [defmt Book](https://defmt.ferrous-systems.com/)
