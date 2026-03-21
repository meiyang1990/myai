## MODIFIED Requirements

### Requirement: 多层级注释生成

注释生成器 SHALL 基于 LangChain + 火山引擎大模型（豆包），为源代码添加文件级、类级、方法/函数级和行内级中文注释。支持两种模式：带项目上下文和无上下文降级。

代码实现 SHALL 使用 Python 3.11.9 现代语法：
- 类定义使用 `class CommentGenerator:` 而非 `class CommentGenerator(object):`
- 字符串格式化使用 f-string 而非 `%` 操作符
- 所有公开方法添加类型注解

#### Scenario: 使用现代语法生成注释

- **WHEN** 调用 `CommentGenerator.generate_comment()` 为源码文件生成注释
- **THEN** 返回添加了中文注释的完整代码
- **AND** 代码中不包含 `class Foo(object)`、`%` 字符串格式化等旧式写法

### Requirement: 注释回写与格式保持

注释回写器 SHALL 将生成的带注释代码保存到输出目录或覆盖原文件。

代码实现 SHALL 使用 Python 3.11.9 现代语法：
- 类定义使用 `class CommentWriter:` 而非 `class CommentWriter(object):`
- 文件 I/O 使用内置 `open()` 而非 `io.open()`
- 字符串格式化使用 f-string 而非 `%` 操作符
- 异常处理使用 `except OSError` 而非 `except (IOError, OSError)`
- 所有公开方法添加类型注解

#### Scenario: 使用现代语法回写注释

- **WHEN** 调用 `CommentWriter.write_file()` 写入带注释代码
- **THEN** 文件成功写入到目标路径
- **AND** 代码中不包含 `io.open()`、`class Foo(object)`、`%` 字符串格式化等旧式写法

### Requirement: 文件处理进度跟踪

进度跟踪器 SHALL 记录文件级和目录级的断点恢复状态，持久化到 `.code_context/progress.json`。

代码实现 SHALL 使用 Python 3.11.9 现代语法：
- 类定义使用 `class ProgressTracker:` 而非 `class ProgressTracker(object):`
- 文件 I/O 使用内置 `open()` 而非 `io.open()`
- 字符串格式化使用 f-string 而非 `%` 操作符
- 异常处理使用 `except OSError` 而非 `except (IOError, OSError)`
- 所有公开方法添加类型注解

#### Scenario: 使用现代语法跟踪进度

- **WHEN** 调用 `ProgressTracker` 标记文件/目录完成状态
- **THEN** 进度数据正确持久化和加载
- **AND** 代码中不包含 `io.open()`、`class Foo(object)`、`%` 字符串格式化等旧式写法

### Requirement: 命令行工具

主程序入口 SHALL 提供命令行接口，支持基本注释生成、`--scan-only`、`--test-api`、`--refresh-context`、`--context-only` 等模式。

代码实现 SHALL 使用 Python 3.11.9 现代语法：
- 移除 `from __future__ import print_function`
- 用户确认输入统一使用 `input()` 而非 `raw_input`/`input` 兼容逻辑
- 字符串格式化使用 f-string
- 所有函数添加类型注解

#### Scenario: 使用现代语法运行命令行工具

- **WHEN** 用户执行 `python main.py --test-api` 或其他命令
- **THEN** 功能行为与重构前完全一致
- **AND** 代码中不包含 `from __future__`、`raw_input`、`%` 字符串格式化等旧式写法
