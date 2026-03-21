# Change: 为 LangChain 大模型调用添加详细日志

## Why

当前项目中调用大模型（LangChain ChatOpenAI）的两个模块 `comment_generator.py` 和 `project_context.py` 仅在异常时记录错误日志，对正常请求的输入参数（Prompt 内容、模型名、温度等）和返回结果（响应内容、token 用量等）没有任何日志记录。这导致：
1. 调试困难：无法在日志中回溯大模型实际接收到的 Prompt 和返回的内容
2. 问题排查低效：当生成质量异常时，无法判断是 Prompt 问题还是模型返回问题
3. 成本不透明：无法统计每次调用的 token 消耗

## What Changes

- `comment_generator.py`：在 `generate_comment()` 和 `test_connection()` 中，调用大模型前后分别记录请求参数和返回内容的详细日志
- `project_context.py`：在 `_call_llm_for_summary()` 中，调用大模型前后分别记录请求参数和返回内容的详细日志
- 日志级别规划：
  - `DEBUG`：完整的 Prompt 内容、完整的返回内容（用于深度排查）
  - `INFO`：调用概要信息（模型名、Prompt 长度/token 估算、返回内容长度、耗时）

## Impact

- Affected specs: `comment-generator`、`architecture-analyzer`
- Affected code: `comment_generator.py`、`project_context.py`
