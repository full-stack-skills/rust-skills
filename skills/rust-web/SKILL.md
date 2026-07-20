---
name: rust-web
description: Rust Web 开发技能 — axum 路由和提取器、serde、tower 中间件、reqwest、sqlx、事务、WebSocket、CORS 和认证边界。Use when designing, implementing, debugging, or testing Rust HTTP services and clients; combine with rust-concurrency for async lifecycle and rust-testing for endpoint and database tests.
---

# Rust Web 开发

> 基于社区主流 crate：axum、tokio、serde、sqlx、reqwest、tower-http 文档。

## Capability Boundaries

### ✅ 强项
1. axum 路由（Router::new、route、nest、layer、fallback）
2. 提取器（Path、Query、Json、Form、State、Extension、String、Bytes）
3. 响应体实现（Json、Html、StatusCode、Redirect、自定义 IntoResponse）
4. 共享状态（axum::extract::State、FromRef 模式）
5. 中间件（tower 中间件栈、tower-http 工具集）
6. serde 序列化（#[derive(Serialize, Deserialize)]、#[serde(rename/skip/tag)]）
7. HTTP 客户端（reqwest：GET/POST、JSON、headers、文件上传）
8. 数据库（sqlx：编译时 query!、query_as!、连接池、迁移）
9. WebSocket（axum::extract::ws、发送/接收消息）
10. CORS（tower-http CorsLayer）
11. JWT 认证（jsonwebtoken crate）
12. 错误处理（应用错误 → HTTP 响应、anyhow 集成）

### ⚠️ 前置要求
1. 理解 async/await（rust-concurrency）
2. Rust 基础（`rust-stable`）

### ❌ 不适用范围
1. CLI 应用 → 使用 `rust-cli` 技能
2. 纯异步编程 → 使用 `rust-concurrency` 技能

## 何时使用

- "用 axum 创建 REST API"
- "连接数据库"
- "JSON 序列化"
- "WebSocket 处理"
- "HTTP 客户端请求"

## Data Privacy

本技能不收集、存储或传输任何用户数据。

---

## 一、axum Web 框架

```toml
[dependencies]
axum = "0.8"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tower-http = { version = "0.6", features = ["cors", "trace", "compression"] }
```

```rust
use axum::{
    Router,
    extract::{Path, Query, State},
    http::StatusCode,
    response::Json,
    routing::get,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;

#[derive(Serialize, Deserialize, Clone)]
struct User {
    id: u64,
    name: String,
}

type AppState = Arc<SharedState>;
struct SharedState {
    db: Mutex<Vec<User>>,
}

async fn list_users(
    State(state): State<AppState>,
) -> Json<Vec<User>> {
    let users = state.db.lock().unwrap();
    Json(users.clone())
}

async fn get_user(
    Path(id): Path<u64>,
    State(state): State<AppState>,
) -> Result<Json<User>, StatusCode> {
    let users = state.db.lock().unwrap();
    users.iter()
        .find(|u| u.id == id)
        .map(|u| Json(u.clone()))
        .ok_or(StatusCode::NOT_FOUND)
}

#[tokio::main]
async fn main() {
    let state = Arc::new(SharedState {
        db: Mutex::new(vec![]),
    });

    let app = Router::new()
        .route("/users", get(list_users).post(create_user))
        .route("/users/:id", get(get_user))
        .with_state(state)
        .layer(tower_http::cors::CorsLayer::permissive());

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
```

## 二、数据库（sqlx）

```toml
[dependencies]
sqlx = { version = "0.8", features = ["runtime-tokio", "postgres", "mysql", "sqlite", "migrate"] }
```

```rust
use sqlx::PgPool;

#[derive(sqlx::FromRow, serde::Serialize, serde::Deserialize)]
struct User {
    id: i64,
    name: String,
    email: String,
}

// 连接池
let pool = PgPool::connect("postgres://user:pass@localhost/db").await?;

// 编译时检查查询
let user = sqlx::query_as::<_, User>(
    "SELECT id, name, email FROM users WHERE id = $1"
)
.bind(user_id)
.fetch_one(&pool)
.await?;

// 迁移
sqlx::migrate!("./migrations").run(&pool).await?;
```

## 三、HTTP 客户端（reqwest）

```rust
let client = reqwest::Client::new();

// GET
let resp = client.get("https://api.github.com/users")
    .header("User-Agent", "my-app")
    .send()
    .await?;

let body = resp.text().await?;
let json: serde_json::Value = resp.json().await?;

// POST JSON
let user = serde_json::json!({"name": "Alice"});
let resp = client.post("https://api.example.com/users")
    .json(&user)
    .send()
    .await?;
```

## 四、中间件模式

```rust
use tower::ServiceBuilder;
use tower_http::{
    cors::CorsLayer,
    trace::TraceLayer,
    compression::CompressionLayer,
    timeout::TimeoutLayer,
};

let middleware = ServiceBuilder::new()
    .layer(TraceLayer::new_for_http())
    .layer(CompressionLayer::new())
    .layer(CorsLayer::permissive())
    .layer(TimeoutLayer::new(Duration::from_secs(30)));

let app = Router::new()
    .route("/api/:path", get(handler))
    .layer(middleware);
```

## 五、WebSocket

```rust
use axum::extract::ws::{WebSocket, WebSocketUpgrade, Message};

async fn ws_handler(
    ws: WebSocketUpgrade,
) -> impl axum::response::IntoResponse {
    ws.on_upgrade(handle_socket)
}

async fn handle_socket(mut socket: WebSocket) {
    while let Some(msg) = socket.recv().await {
        let msg = msg.unwrap();
        match msg {
            Message::Text(text) => {
                socket.send(Message::Text(text)).await.unwrap();
            }
            Message::Close(_) => break,
            _ => {}
        }
    }
}
```

## 常用 Crate 速查

| 用途 | crate | 说明 |
|------|-------|------|
| Web 框架 | axum | 基于 tokio/tower，推荐 |
| 运行时 | tokio | async 运行时 |
| 序列化 | serde / serde_json | JSON 序列化 |
| HTTP 客户端 | reqwest | async HTTP client |
| 数据库 | sqlx | 编译时检查 SQL |
| ORM | sea-orm | 异步 ORM |
| WebSocket | axum::extract::ws | 内置 |
| JWT | jsonwebtoken | JWT 编解码 |
| 模板 | askama | 编译时模板 |

## Workflow

Step 1. 选择框架 — 确定使用 axum（推荐）或其他框架
Step 2. 设计路由 — 规划 RESTful API 路由和 handler 签名
Step 3. 连接数据库 — 配置 sqlx 连接池，编写编译时检查的查询
Step 4. 添加中间件 — 配置 CORS、跟踪、压缩、超时等中间件
Step 5. 错误处理 — 统一错误类型，将应用错误转为 HTTP 响应
Step 6. 测试 — 编写集成测试，使用 axum::test 或 reqwest 测试端点


## Gotchas

1. axum extract::Path 顺序依赖路由参数名 - /:id 必须匹配 Path<u32> 类型
2. tokio::spawn 的 Future 必须 Send - AppState 含 Rc/RefCell 会编译失败
3. sqlx::query! 需要运行时数据库验证 - CI 中需启动数据库或改用 query_as
4. serde #[serde(flatten)] 性能开销 - 创建临时 Value 中间表示
5. axum WebSocket::recv() 返回 None 表示连接已关闭


## 按需资源

- [Web 示例](examples/examples.md)
- [Web crate 速查](references/references.md)
- `examples/golden-handler/`：CI 编译的纯 handler 边界示例

## 官方参考

- [axum docs](https://docs.rs/axum/)
- [tokio docs](https://docs.rs/tokio/)
- [serde docs](https://serde.rs/)
- [sqlx docs](https://docs.rs/sqlx/)
- [reqwest docs](https://docs.rs/reqwest/)
