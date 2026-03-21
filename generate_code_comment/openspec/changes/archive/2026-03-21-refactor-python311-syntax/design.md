## Context

项目当前代码风格兼容 Python 2/3，但 `requirements.txt` 和 `project.md` 已标注目标运行环境为 Python >= 3.11。需要全面清理旧式写法，升级为 Python 3.11.9 现代语法，充分利用语言新特性提升代码质量。

**约束条件**：
- 重构仅涉及语法和编码风格，不改变任何业务逻辑和功能行为
- 所有现有的命令行参数、API 接口、文件输入输出行为保持不变
- 重构后代码必须在 Python 3.11.9 下正常运行

## Goals / Non-Goals

**Goals**：
- 移除所有 Python 2 兼容代码，降低代码认知负担
- 采用 f-string 统一字符串格式化风格
- 用内置 `open()` 替代 `io.open()`，减少不必要的 import
- 添加类型注解，提升 IDE 支持和代码自文档化能力
- 使用 `@dataclass` 简化数据类定义
- 统一异常类型为 Python 3 标准

**Non-Goals**：
- 不全面替换 `os.path` 为 `pathlib.Path`（仅在提升可读性的场景选择性应用）
- 不引入 `async/await` 异步模式
- 不改变项目的模块划分和架构设计
- 不升级第三方依赖版本（LangChain、OpenAI SDK 等）
- 不使用 `ExceptionGroup` / `except*`（当前项目无批量异常处理场景）

## Decisions

### D1: f-string 而非 `str.format()`
- **决策**：统一使用 f-string，而非 `str.format()` 方法
- **理由**：f-string 性能更优、语法更简洁直观，Python 3.6+ 全面支持，3.11 无兼容问题
- **例外**：Prompt 模板字符串（`comment_generator.py` 中的 `HUMAN_PROMPT_TEMPLATE`）保留 `{variable}` 占位符格式，因为它是 LangChain 的模板语法，不是 Python 字符串格式化

### D2: type hints 使用 Python 3.10+ 联合类型语法
- **决策**：使用 `str | None` 而非 `Optional[str]`，使用 `list[str]` 而非 `List[str]`
- **理由**：Python 3.10 引入 `X | Y` 联合类型语法，Python 3.9 引入内置泛型，3.11.9 完全支持
- **影响**：无需 `from __future__ import annotations` 或 `from typing import Optional, List` 等

### D3: `@dataclass` 用于纯数据容器类
- **决策**：仅将 `SourceFile` 重构为 `@dataclass`，其他类（`SourceReader`、`CommentGenerator` 等）保持不变
- **理由**：`SourceFile` 是纯数据容器，`@dataclass` 可自动生成 `__init__`、`__repr__` 等方法。其他类包含复杂业务逻辑，不适合用 `@dataclass`

### D4: 选择性使用 `pathlib.Path`
- **决策**：不全面替换 `os.path`，仅在新增或高度复杂的路径操作中引入 `pathlib`
- **理由**：全面替换改动面过大且 `os.walk()` 等 API 与 `pathlib` 搭配不够自然，强制替换可能降低可读性
- **替代方案**：保留 `os.path`，在简单的路径拼接/判断场景可选使用 `Path`

## Risks / Trade-offs

- **风险1**：f-string 替换中遗漏大括号转义（如 JSON 模板字符串中的 `{}`）
  - **缓解**：逐文件检查，对含有 `{}` 的非格式化字符串保持原样或使用 `{{` `}}` 转义
- **风险2**：LangChain Prompt 模板中的 `{variable}` 被误替换为 f-string
  - **缓解**：明确标注 Prompt 模板字符串不参与 f-string 替换（参见 D1）
- **风险3**：类型注解引入后可能触发 IDE 类型检查警告
  - **缓解**：类型注解仅添加到公开方法，对复杂内部逻辑不强制标注

## Migration Plan

1. **逐模块重构**：按 tasks.md 中的顺序逐模块改造，每完成一个模块确保可独立运行
2. **回归验证**：每个模块重构完成后运行 `python main.py --test-api` 和 `python main.py <path> --scan-only` 验证功能正常
3. **无回滚需求**：本次重构纯语法变更，可通过 Git 版本控制回退

## Open Questions

- 暂无
