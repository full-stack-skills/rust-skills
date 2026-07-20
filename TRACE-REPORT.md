# rust-skills 评测与验证基线

基线日期：2026-07-20

插件版本：3.0.0

Rust 验证工具链：1.97.1

Rust 源码核验：`rust-lang/rust` main `9f36de775bc636c8e88c31a173c2bcb6995956a0`（2026-07-19，`src/version` 为 1.99.0 nightly）；该源码的 `RELEASES.md` 最新 stable 记录为 1.97.1。研究 checkout 仅用于只读核验，不是技能运行依赖。

## 评测定位

旧版静态 TRACE HTML 在技能补充 examples/references 前生成，不能代表当前内容，因此不再随技能目录发布。本版本把质量证据拆成三个可重复验证的层次：

1. **结构与规范**：由 `scripts/validate_skills.py` 自动检查。
2. **代码有效性**：每个技能至少一个黄金示例，执行 fmt、check、test、Clippy。
3. **触发与交接**：由 `evaluation/scenarios.json` 保存独立 Agent forward-test 输入和断言。

## 自动门禁

| 门禁 | 覆盖范围 | 当前状态 |
|---|---|---|
| Manifest parity | `plugin.json` 与 `skills/*` 双向一致 | 通过 |
| Frontmatter | name、description、目录名、唯一性 | 通过 |
| Progressive disclosure | 所有 `SKILL.md` 不超过 500 行 | 通过，最长 251 行；新增 Documentation/HTTP Client/Observability/Performance 分别为 121/97/98/95 行 |
| Local links | README、SKILL、references、examples | 通过 |
| Markdown fences | 所有 Markdown 代码围栏闭合 | 通过 |
| Agent metadata | 19 份 `agents/openai.yaml` 与默认提示 | 通过 |
| Golden examples | 19 个示例的 fmt/check/test/Clippy | 19/19 通过；三方依赖示例按 `Cargo.lock` 预取后离线验证 |
| Trigger scenarios | 44 个中英文场景覆盖全部 19 个技能 | 结构通过，待独立 Agent forward-test |
| Skill language | `skills/**` 中不含中文技能正文或代理元数据 | 通过，19 个技能均为英文 |
| Phase 2 scope | RPC、消息、数据格式、WebAssembly、底层网络协议 | 已完成边界与优先级评估，见 `PHASE-2-EVALUATION.md` |

执行命令：

```bash
python3 scripts/validate_skills.py
python3 scripts/validate_skills.py --check-examples
```

## Forward-test 规则

对 `evaluation/scenarios.json` 中的每个 case 使用全新 Agent 上下文：

1. 只提供用户 prompt 和已安装技能，不提供期望技能或 assertions。
2. 记录实际加载技能、输出、命令、测试日志和产物。
3. 评估触发准确率、错误交接、事实正确性和验证完成度。
4. 只有原始证据满足全部 assertions 才判定通过。
5. 修改技能后重新运行受影响 case；版本升级时运行全量 case。

## 成功标准

- 结构门禁零错误。
- 19/19 黄金示例通过全部命令。
- 每个技能至少两个触发或交接场景。
- 不使用当前项目 MSRV 尚未稳定的 API。
- 不把历史版本快照描述为自动更新的 stable 事实。
- 发布、删除、凭据和外部系统操作必须保留授权边界。

## 维护要求

Rust stable 发布后：

1. 更新 `rust-stable/references/release-current.md`。
2. 审查 Language、Library、Cargo、Clippy、Rustdoc 和 Compatibility Notes。
3. 更新版本敏感示例和错误说明。
4. 在新 stable 与声明的最低 MSRV 上运行验证。
5. 更新插件版本和本报告日期。
