## 1. 日志基础设施

- [x] 1.1 在 `config.py` 中新增 `setup_logging()` 函数，配置 FileHandler 输出到日志文件
- [x] 1.2 日志格式：`%(asctime)s [%(name)s] %(levelname)s: %(message)s`
- [x] 1.3 支持 `LOG_LEVEL` 环境变量控制日志级别（默认 INFO）
- [x] 1.4 日志文件路径默认为工作目录下 `generate_code_comment.log`

## 2. 各模块 print 替换

- [x] 2.1 `source_reader.py`：替换 5 处 print 为 logging（info/warning）
- [x] 2.2 `comment_generator.py`：替换 1 处 print 为 logging（error）
- [x] 2.3 `comment_writer.py`：替换 2 处 print 为 logging（error）
- [x] 2.4 `progress_tracker.py`：替换 8 处 print 为 logging（info/warning/error）
- [x] 2.5 `project_context.py`：替换 18 处 print 为 logging（info/warning/error）
- [x] 2.6 `main.py`：替换 ~40 处 print 为 logging（info/warning/error）并在入口调用 `setup_logging()`

## 3. 验证

- [x] 3.1 所有文件通过 py_compile 语法验证
- [x] 3.2 确认无遗留 print 调用（排除注释中的）
