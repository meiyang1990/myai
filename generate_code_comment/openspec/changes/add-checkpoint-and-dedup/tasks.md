# Tasks: add-checkpoint-and-dedup

## 1. 避免重复注释

- [x] 1.1 在 `comment_generator.py` 的 `SYSTEM_PROMPT` 硬性规则中新增第 6 条：避免重复添加中文注释

## 2. 进度跟踪模块

- [x] 2.1 新建 `progress_tracker.py`，实现 `ProgressTracker` 类
- [x] 2.2 实现文件级进度记录（mark_file_done / is_file_done）
- [x] 2.3 实现目录级进度记录（mark_dir_done / is_dir_done）
- [x] 2.4 实现进度持久化（JSON 存储在 `.code_context/progress.json`）
- [x] 2.5 实现重置进度功能（reset）

## 3. 集成到主流程

- [x] 3.1 修改 `main.py`，新增 `--reset-progress` 命令行参数
- [x] 3.2 修改 `do_generate()` 函数，处理文件前检查进度，已完成则跳过
- [x] 3.3 修改 `source_reader.py` 的 `_scan_directory()`，支持传入进度跟踪器跳过已完成目录

## 4. 更新 Delta Specs

- [x] 4.1 更新 `comment-generator` delta spec：新增避免重复注释规则 + 进度跟踪集成
- [x] 4.2 更新 `source-code-reader` delta spec：新增目录级断点跳过能力

## 5. 验证

- [x] 5.1 openspec validate 通过
