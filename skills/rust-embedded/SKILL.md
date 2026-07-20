---
name: rust-embedded
description: Rust 嵌入式开发技能 — no_std、panic、Cortex-M、embedded-hal 1.0、PAC、GPIO、总线、中断、RTIC 2 和链接脚本。Use when building or reviewing microcontroller firmware and portable HAL drivers; require the exact chip, target, HAL/PAC versions and hardware validation, and hand raw-memory invariants to rust-unsafe-ffi.
---

# Rust 嵌入式开发

> 基于 [Embedded Rust Book](https://doc.rust-lang.org/stable/embedded-book/)、[embedded-hal](https://docs.rs/embedded-hal/) 与 [RTIC](https://rtic.rs/)。

## Capability Boundaries

### ✅ 强项
1. no_std 环境配置（#![no_std]、#![no_main]、extern crate alloc）
2. panic_handler 定义
3. Cortex-M 启动（cortex-m-rt：#[entry]、#[interrupt]、异常向量、startup）
4. embedded-hal 1.0 trait（`OutputPin`、`InputPin`、`DelayNs`、`I2c`、`SpiBus`、`SpiDevice`）
5. 外设访问（PAC：Peripherals::take、寄存器读写、VolatileCell）
6. GPIO 控制（输入/输出/推挽/开漏/上拉/下拉）
7. 定时器/PWM/ADC/UART 外设控制
8. 中断处理（NVIC 配置、enable/disable、优先级、#[interrupt]）
9. RTIC 2 属性宏（`#[rtic::app]`、硬件/软件任务、shared/local 资源、spawn）
10. 链接脚本配置（memory.x）

### ⚠️ 前置要求
1. 了解目标微控制器架构（Cortex-M、RISC-V 等）
2. Rust 基础（`rust-stable`）

### ❌ 不适用范围
1. Web 服务器 → 使用 `rust-web` 技能
2. CLI 应用 → 使用 `rust-cli` 技能

## 何时使用

- "用 Rust 做嵌入式"
- "no_std 环境配置"
- "控制 GPIO"
- "RTIC 实时框架"
- "外设中断处理"

## Data Privacy

本技能不收集、存储或传输任何用户数据。

---

## 一、no_std 环境

```rust
// 禁用标准库
#![no_std]
#![no_main]

use core::panic::PanicInfo;

#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    loop {}
}

// 使用 alloc（需要全局分配器）
extern crate alloc;
use alloc::vec::Vec;
```

## 二、Cortex-M 启动

```rust
// Cargo.toml
// [dependencies]
// cortex-m = "0.7"
// cortex-m-rt = "0.7"
// panic-halt = "0.2"

#![no_std]
#![no_main]

use cortex_m_rt::entry;
use panic_halt as _;

#[entry]
fn main() -> ! {
    loop {}
}
```

## 三、嵌入式 HAL

```rust
// Cargo.toml
// [dependencies]
// rp2040-hal = "0.10"
// embedded-hal = "1.0"

use embedded_hal::delay::DelayNs;
use embedded_hal::digital::OutputPin;
use rp2040_hal::gpio::Pins;

// GPIO 控制
fn blink(led: &mut impl OutputPin, delay: &mut impl DelayNs) {
    led.set_high().ok();
    delay.delay_ms(500);
    led.set_low().ok();
    delay.delay_ms(500);
}

// 使用通用 HAL trait 编写可移植驱动
pub struct LedDriver<P: OutputPin> {
    pin: P,
}

impl<P: OutputPin> LedDriver<P> {
    pub fn new(pin: P) -> Self {
        Self { pin }
    }
    pub fn on(&mut self) { self.pin.set_high().ok(); }
    pub fn off(&mut self) { self.pin.set_low().ok(); }
}
```

## 四、外设访问（PAC）

```rust
// PAC crate: 如 rp2040-pac、stm32f4-pac
use rp2040_pac::Peripherals;

let mut peripherals = Peripherals::take().unwrap();

// 寄存器读写（通过 svd2rust 生成的 API）
peripherals.PADS_BANK0.gpio25.modify(|_, w| w.pue().set_bit());
let val = peripherals.IO_BANK0.gpio25.ctrl.read().bits();
```

## 五、中断处理

```rust
use cortex_m::peripheral::NVIC;
use stm32f4xx_hal::interrupt;

// 启用中断
unsafe { NVIC::unmask(interrupt::TIM2); }

// 设置优先级
NVIC::set_priority(interrupt::TIM2, 128);

// 中断处理函数
#[interrupt]
fn TIM2() {
    // 中断服务程序
}
```

## 六、RTIC 实时框架

```rust
// Cargo.toml
// rtic = "2"

#![no_std]
#![no_main]

#[rtic::app(device = rp2040_pac, peripherals = true)]
mod app {
    #[shared]
    struct Shared {
        counter: u32,
    }

    #[local]
    struct Local {
        led: rp2040_hal::gpio::Pin<rp2040_hal::gpio::pin::Pin25, rp2040_hal::gpio::FunctionSioOutput>,
    }

    #[init]
    fn init(cx: init::Context) -> (Shared, Local) { /* ... */ }

    // 硬件任务（绑定中断）
    #[task(binds = TIMER_IRQ_0, shared = [counter])]
    fn timer_tick(mut cx: timer_tick::Context) {
        cx.shared.counter.lock(|c| *c += 1);
    }

    // 软件任务
    #[task]
    fn background(_cx: background::Context) { /* ... */ }
}
```

## 七、链接脚本（memory.x）

```ld
/* memory.x — 在项目根目录 */
MEMORY {
    FLASH : ORIGIN = 0x10000000, LENGTH = 2M
    RAM   : ORIGIN = 0x20000000, LENGTH = 256K
}

/* 在 build.rs 中引用 */
// fn main() {
//     println!("cargo::rustc-link-arg-bins=--nmagic");
//     println!("cargo::rerun-if-changed=memory.x");
// }
```

## 常用 Crate

| 用途 | crate | 说明 |
|------|-------|------|
| 运行时 | cortex-m-rt | 启动 + 中断向量 |
| HAL trait | embedded-hal | 硬件抽象层 |
| MCU HAL | rp2040-hal | RP2040 |
| MCU HAL | stm32f4xx-hal | STM32F4 |
| 实时框架 | rtic | RTIC v2 |
| 调试 | defmt | 高效日志 |
| 调试 | probe-rs (CLI) | 调试器 |

## Workflow

Step 1. 选择硬件 — 确定目标微控制器（Cortex-M/RISC-V/其他）
Step 2. 配置 no_std 环境 — 设置 #![no_std]、panic_handler、链接脚本
Step 3. 初始化外设 — 使用 PAC crate 获取外设所有权，配置时钟
Step 4. 实现 HAL 驱动 — 使用 embedded-hal trait 编写可移植的外设驱动
Step 5. 处理中断 — 配置 NVIC，编写中断处理函数
Step 6. 部署与调试 — 使用 probe-rs/OpenOCD 烧录和调试固件


## Gotchas

1. #![no_std] 项目可用 alloc crate - 在支持堆分配时可以 Vec、String
2. Cortex-M 中断处理函数不能有参数 - #[interrupt] fn 必须是 fn() 类型
3. embedded-hal 1.0 OutputPin::set_high() 返回 Result
4. cortex_m::Peripherals::take() 只能成功一次 - 第二次返回 None
5. RTIC spawn 在硬件任务中需用 spawn_after - 普通 spawn 不可用


## 按需资源

- [嵌入式示例](examples/examples.md)
- [常用 crate 速查](references/references.md)
- `examples/golden-no-std/`：CI 在宿主工具链上编译的 no_std trait 示例

## 官方参考

- [Embedded Rust Book](https://doc.rust-lang.org/embedded-book)
- [embedded-hal docs](https://docs.rs/embedded-hal/)
- [RTIC Book](https://rtic.rs/2/book/)
- [cortex-m-rt docs](https://docs.rs/cortex-m-rt/)
