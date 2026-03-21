## 1. Implementation

- [x] 1.1 `main.py` `parse_args()`：为 `generate_comment` 子命令新增 `--source_path` **必填**参数（required=True）
- [x] 1.2 `main.py` `_handle_generate_comment()`：解析 `--source_path`，校验路径存在性（必须存在且为文件或目录）
- [x] 1.3 `main.py` `do_generate()`：新增 `target_path` 参数，区分单文件和目录两种模式传递给 `SourceReader`
- [x] 1.4 `source_reader.py` `SourceReader`：新增 `scan_path()` 方法，支持传入文件路径或目录路径；文件路径时直接返回单个 `SourceFile`，目录路径时调用现有 `_scan_directory()`
- [x] 1.5 `source_reader.py`：单文件模式下正确设置 `rel_path`（相对于 `project_root`）
- [x] 1.6 `comment_writer.py` `CommentWriter`：确认单文件场景下 `write_file()` 正确计算输出路径（无需修改，rel_path 已由 scan_path 正确设置）
- [x] 1.7 `progress_tracker.py` `ProgressTracker`：确认单文件场景下缓存目录初始化在 `project_root` 下（无需修改，do_generate 始终传入 project_path）
- [x] 1.8 更新 `main.py` 文件头 docstring 和 `epilog` 示例文本
- [x] 1.9 验证：目录模式正常、单文件模式正常
