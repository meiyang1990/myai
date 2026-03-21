# Change: 基于 Python 3.11.9 语法重构项目

## Why

当前项目代码中保留了大量 Python 2/3 兼容写法和旧式编码模式（如 `from __future__ import`、`class Foo(object)`、`%` 字符串格式化、`io.open()` 等）。项目已明确要求 Python >= 3.11，这些过时的兼容写法增加了代码冗余度，降低了可读性，且未充分利用 Python 3.11.9 的现代语言特性。本提案旨在全面升级为 Python 3.11.9 现代语法，提升代码质量和可维护性。

## What Changes

### 1. 移除 Python 2 兼容代码
- **移除 `from __future__ import print_function`**（`main.py`）
- **移除 `raw_input` 兼容逻辑**：`try: raw_input(...) except NameError: input(...)` → 直接使用 `input()`（`main.py`）
- **移除继承 `object` 的冗余写法**：`class Foo(object):` → `class Foo:`（所有模块）

### 2. 字符串格式化升级
- **`%` 格式化 → f-string**：将所有 `"xxx %s" % value` 和 `"xxx %d" % value` 替换为 `f"xxx {value}"` 风格（所有模块）

### 3. 文件 I/O 现代化
- **`io.open()` → 内置 `open()`**：Python 3 内置 `open()` 已原生支持 `encoding` 参数，移除 `import io` 和 `io.open()` 调用（`source_reader.py`、`comment_writer.py`、`progress_tracker.py`、`project_context.py`）

### 4. 异常处理简化
- **`except (IOError, OSError)` → `except OSError`**：Python 3 中 `IOError` 是 `OSError` 的别名，统一为 `OSError`（所有涉及文件 I/O 的模块）

### 5. 类型注解（Type Hints）
- 为所有公开方法和函数添加 Python 3.11 风格的类型注解，使用 `str | None` 联合类型语法而非 `Optional[str]`（所有模块）
- 使用内置 `list`、`dict`、`tuple`、`set` 泛型而非 `typing.List` 等（Python 3.9+）

### 6. 数据类现代化
- **`SourceFile` 类 → `@dataclass`**：使用 `dataclasses.dataclass` 装饰器替代手写 `__init__`（`source_reader.py`）

### 7. 路径操作现代化
- **`os.path` → `pathlib.Path`**：在适当场景下使用 `pathlib.Path` 替代 `os.path` 拼接、判断等操作，提升代码可读性（视具体模块适度改进，不强制全面替换）

### 8. 其他 Python 3.11+ 特性应用
- 使用 `collections.Counter` 替代手动字典计数（`source_reader.py` 的 `get_project_summary`）
- 使用 `ExceptionGroup` / `except*` 语法改进批量异常处理（视实际场景评估）
- 利用 `tomllib`（Python 3.11 内置）替代可能的 toml 解析场景

### 9. 项目配置更新
- 更新 `project.md` 中的技术栈描述：`Python >= 3.6` → `Python >= 3.11.9`

## Impact

- Affected specs: `source-code-reader`、`comment-generator`、`architecture-analyzer`
- Affected code:
  - `main.py`：移除 future import、raw_input 兼容、% 格式化、type hints
  - `config.py`：% 格式化升级、type hints
  - `source_reader.py`：class 写法、io.open、% 格式化、dataclass、type hints
  - `comment_generator.py`：class 写法、% 格式化、type hints
  - `comment_writer.py`：class 写法、io.open、% 格式化、type hints
  - `progress_tracker.py`：class 写法、io.open、% 格式化、type hints
  - `project_context.py`：class 写法、io.open、% 格式化、type hints
  - `requirements.txt`：确认版本注释
  - `openspec/project.md`：更新技术栈描述
