## MODIFIED Requirements

### Requirement: 项目概要文档生成

项目上下文分析器 SHALL 调用大模型分析项目架构，生成包含架构设计、技术栈、业务背景的 Markdown 概要文档。支持智能采样项目关键文件，生成目录树结构概览，支持缓存加载与过期检测。调用大模型失败时自动降级为无上下文模式。

代码实现 SHALL 使用 Python 3.11.9 现代语法：
- 类定义使用 `class ProjectContextAnalyzer:` 而非 `class ProjectContextAnalyzer(object):`
- 文件 I/O 使用内置 `open()` 而非 `io.open()`
- 字符串格式化使用 f-string 而非 `%` 操作符
- 异常处理使用 `except OSError` 而非 `except (IOError, OSError)`
- 所有公开方法添加类型注解

#### Scenario: 使用现代语法分析项目上下文

- **WHEN** 调用 `ProjectContextAnalyzer.get_context()` 分析项目
- **THEN** 返回 Markdown 格式的项目概要文档
- **AND** 代码中不包含 `io.open()`、`class Foo(object)`、`%` 字符串格式化等旧式写法

### Requirement: 项目上下文持久化存储

分析结果 SHALL 以 JSON 格式持久化存储到 `.code_context/project_summary.json`，支持缓存加载、强制刷新（`--refresh-context`）和过期策略（默认 7 天）。

代码实现 SHALL 使用 Python 3.11.9 现代语法，文件读写使用内置 `open()` 并添加类型注解。

#### Scenario: 使用现代语法持久化存储

- **WHEN** 保存或加载项目概要缓存
- **THEN** 使用内置 `open()` 读写 JSON 文件
- **AND** 缓存行为与重构前一致
