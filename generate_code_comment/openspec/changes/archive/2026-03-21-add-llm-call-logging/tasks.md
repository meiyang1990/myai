# Tasks: add-llm-call-logging

## 1. comment_generator.py 大模型调用日志

- [x] 1.1 在 `generate_comment()` 中，调用 `self.llm.invoke()` 前记录请求日志：INFO 级别记录文件路径、语言、Prompt 总长度；DEBUG 级别记录完整 Prompt 内容
- [x] 1.2 在 `generate_comment()` 中，调用 `self.llm.invoke()` 后记录响应日志：INFO 级别记录响应长度、耗时；DEBUG 级别记录完整响应内容
- [x] 1.3 在 `generate_comment()` 中，如果响应包含 `response_metadata`（token 用量），记录 token 消耗信息
- [x] 1.4 在 `test_connection()` 中，同样添加请求和响应日志

## 2. project_context.py 大模型调用日志

- [x] 2.1 在 `_call_llm_for_summary()` 中，调用 `self.llm.invoke()` 前记录请求日志：INFO 级别记录 Prompt 总长度；DEBUG 级别记录完整 System Prompt 和 Human Prompt 内容
- [x] 2.2 在 `_call_llm_for_summary()` 中，调用 `self.llm.invoke()` 后记录响应日志：INFO 级别记录响应长度、耗时；DEBUG 级别记录完整响应内容
- [x] 2.3 如果响应包含 `response_metadata`（token 用量），记录 token 消耗信息

## 3. 验证

- [x] 3.1 py_compile 语法验证通过
- [x] 3.2 确认 INFO 级别日志不包含完整 Prompt/响应内容（避免日志文件过大）
- [x] 3.3 确认 DEBUG 级别日志包含完整的请求和返回内容
