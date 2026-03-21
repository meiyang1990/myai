## ADDED Requirements

### Requirement: 项目概要生成大模型调用日志

系统 SHALL 在 `ProjectContextAnalyzer` 调用大模型生成项目概要时，将请求参数和返回内容记录到日志文件中，便于调试和问题排查。日志分为 INFO 级别（概要信息）和 DEBUG 级别（完整内容）。

#### Scenario: 概要生成请求日志

- **WHEN** `_call_llm_for_summary()` 准备调用大模型
- **THEN** 以 INFO 级别记录：System Prompt 长度、Human Prompt 长度、Prompt 总字符数
- **AND** 以 DEBUG 级别记录：完整的 System Prompt 和 Human Prompt 内容

#### Scenario: 概要生成响应日志

- **WHEN** 大模型返回项目概要生成结果
- **THEN** 以 INFO 级别记录：响应内容长度、调用耗时（秒）
- **AND** 以 DEBUG 级别记录：完整的响应内容
- **AND** 如果响应中包含 token 用量信息，以 INFO 级别记录 prompt_tokens、completion_tokens、total_tokens
