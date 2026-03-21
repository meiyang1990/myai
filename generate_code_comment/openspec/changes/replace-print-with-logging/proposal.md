# Change: 将所有 print 输出替换为 logging 模块写入日志文件

## Why

当前项目所有日志/状态输出均通过 `print()` 直接打印到终端（共约 80 处），无法持久化到日志文件，不利于生产环境下的问题排查和运行监控。需要统一替换为 Python 标准 `logging` 模块，将日志写入文件，不再输出到终端。

## What Changes

### 1. 新增日志配置
- 在 `config.py` 中新增 `setup_logging()` 函数，配置 logging 模块
- 日志输出到文件（默认 `generate_code_comment.log`），不输出到终端（stdout）
- 日志格式包含时间戳、模块名、级别和消息
- 日志级别默认 INFO，支持通过环境变量 `LOG_LEVEL` 调整

### 2. 全量替换 print → logging
- `main.py`（~40 处）：替换所有 print 为 logger.info/warning/error
- `project_context.py`（~18 处）：替换所有 print 为 logger 调用
- `progress_tracker.py`（~8 处）：替换所有 print 为 logger 调用
- `source_reader.py`（~5 处）：替换所有 print 为 logger 调用
- `comment_writer.py`（~2 处）：替换所有 print 为 logger 调用
- `comment_generator.py`（~1 处）：替换所有 print 为 logger 调用

### 3. 日志级别映射规则
- 普通状态/进度信息 → `logger.info`
- 警告信息（`[警告]`、`[提示]`）→ `logger.warning`
- 错误信息（`[错误]`、失败、异常）→ `logger.error`
- 调试/详细信息 → `logger.debug`

## Impact

- Affected specs: `source-code-reader`、`comment-generator`、`architecture-analyzer`
- Affected code:
  - `config.py`：新增 `setup_logging()` 函数
  - `main.py`：调用 `setup_logging()`，替换所有 print
  - `source_reader.py`：替换 print 为 logging
  - `comment_generator.py`：替换 print 为 logging
  - `comment_writer.py`：替换 print 为 logging
  - `progress_tracker.py`：替换 print 为 logging
  - `project_context.py`：替换 print 为 logging
