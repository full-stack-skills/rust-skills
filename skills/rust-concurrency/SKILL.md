---
name: rust-concurrency
description: Rust 并发编程技能 — scoped threads、Mutex/RwLock、原子、channel、Send/Sync、Future 和 Tokio。Use when designing, debugging, or testing threaded and async Rust, cancellation, task lifetimes, lock scope, atomics, or message passing; hand basic ownership to rust-stable and unsafe invariants to rust-unsafe-ffi.
---

# Rust 并发编程

> 基于 Rust 标准库 `std::thread`、`std::sync`、`std::sync::atomic` 与 [Async Book](https://rust-lang.github.io/async-book/)。

## Capability Boundaries

### ✅ 强项
1. OS 线程（thread::spawn、Builder、join、scoped threads、move 闭包）
2. 同步原语（Mutex、RwLock、Barrier、Condvar、OnceLock、LazyLock）
3. 原子类型（AtomicBool/Isize/Usize、load/store/fetch_add/swap/compare_exchange、Ordering）
4. 通道（mpsc：多生产者单消费者、Receiver、Sender）
5. Send/Sync trait 系统（自动推导与手动实现）
6. async/await 语法与 Future trait
7. Tokio 运行时（tokio::main、tokio::spawn、select!、JoinSet）
8. 异步 I/O 基础（tokio::fs、tokio::net、tokio::io）

### ⚠️ 前置要求
1. 理解 Rust 所有权模型（`rust-stable`）

### ❌ 不适用范围
1. 不安全代码并发 → 使用 `rust-unsafe-ffi` 技能
2. 基础所有权/借用 → 使用 `rust-stable` 技能

## 何时使用

- "多线程处理数据"
- "async/await 怎么写"
- "Tokio 运行时使用"
- "线程间共享数据"
- "避免数据竞争"

## Data Privacy

本技能不收集、存储或传输任何用户数据。

---

## 一、OS 线程

```rust
use std::thread;

let handle = thread::spawn(move || {
    println!("Hello from thread!");
});
handle.join().unwrap();

// 带配置的线程
let builder = thread::Builder::new()
    .name("worker".into())
    .stack_size(1024 * 1024);
let handle = builder.spawn(move || { /* ... */ }).unwrap();

// scoped threads（1.63+）
let mut v = vec![1, 2, 3];
thread::scope(|s| {
    s.spawn(|| {
        v.push(4);  // 借用，不需 move
    });
});
println!("{v:?}");  // v 仍可用
```

## 二、同步原语

```rust
use std::sync::{Arc, Mutex, RwLock, Barrier, OnceLock, LazyLock};

// Mutex（互斥锁）
let counter = Arc::new(Mutex::new(0));
let mut handles = vec![];

for _ in 0..10 {
    let counter = Arc::clone(&counter);
    handles.push(thread::spawn(move || {
        let mut num = counter.lock().unwrap();
        *num += 1;
    }));
}

// RwLock（读写锁）
let data = Arc::new(RwLock::new(vec![1, 2, 3]));
let read = data.read().unwrap();
let write = data.write().unwrap();

// OnceLock（线程安全懒初始化）
static CONFIG: OnceLock<String> = OnceLock::new();
let config = CONFIG.get_or_init(|| load_config());

// LazyLock
static CACHE: LazyLock<HashMap<String, Data>> = LazyLock::new(HashMap::new);
```

## 三、原子操作

```rust
use std::sync::atomic::{
    AtomicBool, AtomicU64, Ordering
};

static COUNTER: AtomicU64 = AtomicU64::new(0);
COUNTER.fetch_add(1, Ordering::SeqCst);

static READY: AtomicBool = AtomicBool::new(false);
READY.store(true, Ordering::Release);
let ready = READY.load(Ordering::Acquire);

// Ordering 级别
// Relaxed — 无顺序保证（仅原子性）
// Release — 写入可见
// Acquire — 读取可见
// AcqRel — 读+写
// SeqCst — 全局顺序（最强，默认）
```

## 四、通道

```rust
use std::sync::mpsc;

let (tx, rx) = mpsc::channel();
thread::spawn(move || {
    tx.send(1).unwrap();
    tx.send(2).unwrap();
});
for received in rx {
    println!("Got: {received}");
}

// 多生产者
let (tx, rx) = mpsc::channel();
let tx1 = tx.clone();
```

## 五、async/await

```rust
use tokio::time;

async fn do_work(id: u32) -> &'static str {
    time::sleep(time::Duration::from_secs(1)).await;
    println!("Task {id} done");
    "ok"
}

#[tokio::main]
async fn main() {
    // 并发执行
    let (r1, r2) = tokio::join!(do_work(1), do_work(2));

    // select!
    tokio::select! {
        result = do_work(1) => println!("task1: {result}"),
        result = do_work(2) => println!("task2: {result}"),
    }

    // tokio::spawn
    let handle = tokio::spawn(do_work(3));
    handle.await.unwrap();
}
```

## 六、Send / Sync

```rust
// Send: T 的所有权可跨线程转移
// Sync: &T 可跨线程共享引用

// Send + Sync 类型：Arc<Mutex<T>>、i32、&str
// !Send 类型：Rc<T>、*const T
// !Sync 类型：RefCell<T>、Cell<T>

// 手动实现（需 unsafe）
struct MyType(*const u8);
unsafe impl Send for MyType {}
unsafe impl Sync for MyType {}
```

## Workflow

Step 1. 确认并发模型 — 选择 OS 线程、async/await（Tokio）还是 scoped threads
Step 2. 数据共享设计 — 确定哪些数据需跨线程共享，选择 Arc/Mutex/Channel
Step 3. 处理同步 — 使用 Mutex/RwLock/Barrier/atomic 协调多线程访问
Step 4. 处理异步 — 选择 Tokio 运行时，使用 async fn + await + tokio::spawn
Step 5. 错误处理 — 处理 Mutex 中毒、JoinHandle 错误、channel 关闭场景
Step 6. 测试验证 — cargo test -- --test-threads=1 测试并发代码


## Gotchas

1. Mutex::lock() 返回 MutexGuard - drop 前不要 await，可能导致死锁
2. tokio::spawn 的 Future 必须是 Send + 'static - 非 Send 引用会导致编译失败
3. async 闭包捕获与普通闭包不同 - 需要 move 关键字传递所有权
4. select! 中取消的 Future 不会执行清理 - 分支被取消后 Future 直接 drop
5. Atomic Ordering 不是关系型的 - 滥用 Relaxed 可能导致意外 memory ordering 问题


## 按需资源

- [并发示例](examples/examples.md)
- [类型与工具速查](references/references.md)
- `examples/golden-threads/`：CI 编译的 scoped thread 示例

## 官方参考

- [std::thread](https://doc.rust-lang.org/std/thread/)
- [std::sync](https://doc.rust-lang.org/std/sync/)
- [std::sync::atomic](https://doc.rust-lang.org/std/sync/atomic/)
- [Async Book](https://rust-lang.github.io/async-book/)
- [Tokio Guide](https://tokio.rs/tokio/tutorial)
