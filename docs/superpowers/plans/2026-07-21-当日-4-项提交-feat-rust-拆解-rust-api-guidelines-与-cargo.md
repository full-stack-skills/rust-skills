# rust-skills 历史任务：当日 4 项提交（feat(rust): 拆解 Rust API Guidelines 与 Cargo Book，新增 3 技能、优化 4 技能 等）（2026-07-21）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> **本计划为历史任务回填**：依据 git 提交记录还原，全部任务已完成，复选框均为 `- [x]`。

**Goal:** 本日完成 4 项提交：

1. feat(rust): 拆解 Rust API Guidelines 与 Cargo Book，新增 3 技能、优化 4 技能
2. refactor(rust): rust-project-structure 重命名为 rust-workspace
3. feat(rust): rust-project-structure 全面增强 workspace 内容
4. feat(rust): 新增 rust-module-layout 技能，聚焦 crate 内部模块布局

**Architecture:** 仓库元数据与文档维护、技能内容更新（SKILL.md）、技能参考/示例资料更新。

**Tech Stack:** JSON、Markdown。

**Spec:** 无独立规格文档；依据提交 `03e99c0`, `1f4c333`, `5d196ec`, `fd460a8` 还原。

## Global Constraints

- 本计划依据 git 历史回填，仅记录已完成工作（4 个提交均已落地）
- 不含未完成或计划中的工作；步骤复选框全部为已完成状态

---

### Task 1: feat(rust): 拆解 Rust API Guidelines 与 Cargo Book，新增 3 技能、优化 4 技能

**Files:**
- `.claude-plugin/plugin.json`
- `README.md`
- `README.zh-CN.md`
- `evaluation/scenarios.json`
- `skills/rust-api-design/SKILL.md`
- `skills/rust-api-design/agents/openai.yaml`
- `skills/rust-api-design/examples/anti-patterns.md`
- `skills/rust-api-design/examples/golden-api/Cargo.lock`
- `skills/rust-api-design/examples/golden-api/Cargo.toml`
- `skills/rust-api-design/examples/golden-api/src/lib.rs`
- `skills/rust-api-design/references/api-guidelines-checklist.md`
- `skills/rust-api-design/references/future-proofing.md`
- `skills/rust-api-design/references/naming-and-conversions.md`
- `skills/rust-cargo-build/SKILL.md`
- `skills/rust-cargo-build/references/cargo-reference-cheatsheet.md`
- …等共 37 个文件

- [x] **Step 1: 完成「feat(rust): 拆解 Rust API Guidelines 与 Cargo Book，新增 3 技能、优化 4 技能」（wandl-6A72h）**
- [x] **Step 2: 提交** — `03e99c0` feat(rust): 拆解 Rust API Guidelines 与 Cargo Book，新增 3 技能、优化 4 技能

---

### Task 2: refactor(rust): rust-project-structure 重命名为 rust-workspace

**Files:**
- `.claude-plugin/plugin.json`
- `README.md`
- `README.zh-CN.md`
- `evaluation/scenarios.json`
- `skills/rust-cargo-build/SKILL.md`
- `skills/rust-macros/SKILL.md`
- `skills/rust-module-layout/SKILL.md`
- `skills/rust-module-layout/examples/splitting-files.md`
- `skills/rust-module-layout/references/large-crate-layout.md`
- `skills/rust-project-structure/agents/openai.yaml`
- `skills/rust-stable/SKILL.md`
- `skills/rust-testing/SKILL.md`
- `skills/rust-workspace/SKILL.md`
- `skills/rust-workspace/agents/openai.yaml`
- `skills/rust-workspace/examples/examples.md`
- …等共 34 个文件

- [x] **Step 1: 完成「refactor(rust): rust-project-structure 重命名为 rust-workspace」（wandl-6A72h）**
- [x] **Step 2: 提交** — `1f4c333` refactor(rust): rust-project-structure 重命名为 rust-workspace

---

### Task 3: feat(rust): rust-project-structure 全面增强 workspace 内容

**Files:**
- `evaluation/scenarios.json`
- `skills/rust-workspace/SKILL.md`
- `skills/rust-workspace/examples/golden-workspace/Cargo.lock`
- `skills/rust-workspace/examples/golden-workspace/Cargo.toml`
- `skills/rust-workspace/examples/golden-workspace/my-cli/Cargo.toml`
- `skills/rust-workspace/examples/golden-workspace/crates/my-cli/src/main.rs`
- `skills/rust-workspace/examples/golden-workspace/my-core/Cargo.toml`
- `skills/rust-workspace/examples/golden-workspace/my-core/src/lib.rs`
- `skills/rust-workspace/examples/golden-workspace/my-net/Cargo.toml`
- `skills/rust-workspace/examples/golden-workspace/my-net/src/lib.rs`
- `skills/rust-workspace/examples/golden-workspace/src/lib.rs`
- `skills/rust-workspace/references/dependency-direction.md`
- `skills/rust-workspace/references/mixed-root-package-antipattern.md`
- `skills/rust-workspace/references/virtual-vs-root-manifest.md`
- `skills/rust-workspace/references/workspace-dependencies.md`
- …等共 16 个文件

- [x] **Step 1: 完成「feat(rust): rust-project-structure 全面增强 workspace 内容」（wandl-6A72h）**
- [x] **Step 2: 提交** — `5d196ec` feat(rust): rust-project-structure 全面增强 workspace 内容

---

### Task 4: feat(rust): 新增 rust-module-layout 技能，聚焦 crate 内部模块布局

**Files:**
- `.claude-plugin/plugin.json`
- `README.md`
- `README.zh-CN.md`
- `evaluation/scenarios.json`
- `skills/rust-module-layout/SKILL.md`
- `skills/rust-module-layout/agents/openai.yaml`
- `skills/rust-module-layout/examples/README.md`
- `skills/rust-module-layout/examples/golden-facade/Cargo.lock`
- `skills/rust-module-layout/examples/golden-facade/Cargo.toml`
- `skills/rust-module-layout/examples/golden-facade/src/ast.rs`
- `skills/rust-module-layout/examples/golden-facade/src/ast/print.rs`
- `skills/rust-module-layout/examples/golden-facade/src/error.rs`
- `skills/rust-module-layout/examples/golden-facade/src/lib.rs`
- `skills/rust-module-layout/examples/golden-facade/src/parser.rs`
- `skills/rust-module-layout/examples/golden-facade/src/parser/grammar.rs`
- …等共 29 个文件

- [x] **Step 1: 完成「feat(rust): 新增 rust-module-layout 技能，聚焦 crate 内部模块布局」（wandl-6A72h）**
- [x] **Step 2: 提交** — `fd460a8` feat(rust): 新增 rust-module-layout 技能，聚焦 crate 内部模块布局
