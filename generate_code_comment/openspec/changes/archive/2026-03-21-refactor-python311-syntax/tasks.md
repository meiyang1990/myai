## 1. 基础清理：移除 Python 2 兼容代码

- [x] 1.1 移除 `main.py` 中的 `from __future__ import print_function`
- [x] 1.2 移除 `main.py` 中 `raw_input` / `input` 兼容逻辑，统一使用 `input()`
- [x] 1.3 将所有模块中 `class Foo(object):` 改为 `class Foo:`
  - `source_reader.py`：`SourceFile(object)` → `SourceFile`，`SourceReader(object)` → `SourceReader`
  - `comment_generator.py`：`CommentGenerator(object)` → `CommentGenerator`
  - `comment_writer.py`：`CommentWriter(object)` → `CommentWriter`
  - `progress_tracker.py`：`ProgressTracker(object)` → `ProgressTracker`
  - `project_context.py`：`ProjectContextAnalyzer(object)` → `ProjectContextAnalyzer`

## 2. 字符串格式化升级

- [x] 2.1 将 `main.py` 中所有 `%` 格式化替换为 f-string
- [x] 2.2 将 `config.py` 中所有 `%` 格式化替换为 f-string
- [x] 2.3 将 `source_reader.py` 中所有 `%` 格式化替换为 f-string
- [x] 2.4 将 `comment_generator.py` 中所有 `%` 格式化替换为 f-string
- [x] 2.5 将 `comment_writer.py` 中所有 `%` 格式化替换为 f-string
- [x] 2.6 将 `progress_tracker.py` 中所有 `%` 格式化替换为 f-string
- [x] 2.7 将 `project_context.py` 中所有 `%` 格式化替换为 f-string

## 3. 文件 I/O 现代化

- [x] 3.1 将 `source_reader.py` 中 `io.open()` 替换为内置 `open()`，移除 `import io`
- [x] 3.2 将 `comment_writer.py` 中 `io.open()` 替换为内置 `open()`，移除 `import io`
- [x] 3.3 将 `progress_tracker.py` 中 `io.open()` 替换为内置 `open()`，移除 `import io`
- [x] 3.4 将 `project_context.py` 中 `io.open()` 替换为内置 `open()`，移除 `import io`

## 4. 异常处理简化

- [x] 4.1 将所有模块中 `except (IOError, OSError)` 简化为 `except OSError`
- [x] 4.2 将所有模块中 `except (ValueError, KeyError, IOError)` 简化为 `except (ValueError, KeyError, OSError)`

## 5. 类型注解添加

- [x] 5.1 为 `config.py` 的 `validate_config()` 添加返回类型注解
- [x] 5.2 为 `source_reader.py` 所有公开方法添加类型注解
- [x] 5.3 为 `comment_generator.py` 所有公开方法添加类型注解
- [x] 5.4 为 `comment_writer.py` 所有公开方法添加类型注解
- [x] 5.5 为 `progress_tracker.py` 所有公开方法添加类型注解
- [x] 5.6 为 `project_context.py` 所有公开方法添加类型注解
- [x] 5.7 为 `main.py` 的函数添加类型注解

## 6. 数据类现代化

- [x] 6.1 将 `source_reader.py` 中的 `SourceFile` 类重构为 `@dataclass`

## 7. 其他现代化改进

- [x] 7.1 `source_reader.py` 的 `get_project_summary` 中使用 `collections.Counter` 替代手动计数
- [x] 7.2 在适当位置引入 `from __future__ import annotations` 确保类型注解语法兼容

## 8. 项目配置与文档更新

- [x] 8.1 更新 `openspec/project.md` 中技术栈描述 `Python >= 3.6` → `Python >= 3.11.9`
- [x] 8.2 确认 `requirements.txt` 版本注释与实际一致
