## Context

本项目需要实现一个基于 AI 的智能代码注释生成命令行工具。核心约束条件：
- Python >= 3.6 语法
- LangChain v0.1.16 框架
- 火山引擎大模型 API（豆包模型）
- 整个代码文件一次性提交大模型生成注释

## Goals / Non-Goals

- Goals:
  - 实现端到端可运行的命令行工具
  - 支持 20+ 种编程语言的源码识别和注释生成
  - 安全的文件输出策略（默认不修改原文件）
  - 简单易用的配置方式（.env 文件）

- Non-Goals:
  - 不实现架构分析引擎（后续迭代）
  - 不实现增量处理和缓存机制（后续优化）
  - 不实现 Web UI 或 GUI 界面

## Decisions

### 大模型接入方式

- **Decision**: 使用 LangChain 的 `ChatOpenAI` 通过 OpenAI 兼容协议接入火山引擎大模型
- **Rationale**: 火山引擎 v3 API 完全兼容 OpenAI 协议，无需额外 SDK。通过设置 `openai_api_base` 指向火山引擎端点即可，复用 LangChain 成熟的 ChatOpenAI 实现
- **Alternatives considered**:
  - `VolcEngineMaasLLM`（langchain_community）：需要额外的 `volcengine` SDK，且是 LLM 而非 Chat 接口，功能受限
  - 直接使用 OpenAI SDK：绕过了 LangChain 的编排能力，不利于后续扩展 Chain/Agent

### 注释生成策略

- **Decision**: 整个文件一次性提交给大模型，返回完整的带注释代码
- **Rationale**: 大模型需要完整的文件上下文才能生成有意义的注释（理解类之间关系、方法调用链等）。分段处理会丢失上下文
- **Trade-off**: 对于超大文件（>1MB）可能超出 token 限制，通过 `MAX_FILE_SIZE` 配置跳过此类文件

### 输出策略

- **Decision**: 默认输出到 `<项目名>_commented` 新目录，保持原文件不变
- **Rationale**: 安全第一原则，避免意外覆盖用户源码。覆盖模式需要二次确认

## Risks / Trade-offs

- **Token 限制**: 大文件可能超出大模型的 token 上下文窗口 → 通过 `MAX_FILE_SIZE` 配置限制，默认 1MB
- **API 费用**: 大量文件会产生较高的 API 调用费用 → 提供 `--scan-only` 预览模式，让用户评估
- **注释质量**: 大模型生成的注释可能不够准确 → 通过精心设计的 System Prompt 和低温度参数（0.3）提高稳定性

## Open Questions

- 后续是否需要支持流式输出以显示生成进度？
- 是否需要引入注释质量评估机制（如让另一个 AI 评审生成的注释）？
