## 1. Implementation

- [x] 1.1 `main.py` `do_generate()`：明确 `project_path` 仅用于项目概要检索、`.gitignore` 加载和进度跟踪，`target_path`（即 `--source_path`）用于实际扫描和处理
- [x] 1.2 `main.py` `do_generate()`：将 `CommentWriter` 的初始化从 `CommentWriter(project_path, ...)` 改为基于 `target_path` 计算输出路径
- [x] 1.3 `comment_writer.py` `CommentWriter.__init__()`：当非覆盖模式下，默认输出目录改为 `source_path_commented`（目录）或在 `source_file` 同级创建输出（单文件）
- [x] 1.4 `main.py` `do_generate()`：确保覆盖模式（`--overwrite`）下直接写回 `source_path` 原位，不受 `project_root_dir` 影响
- [x] 1.5 更新 `main.py` 文件头 docstring 和 epilog 示例，明确两个参数的职责说明
- [x] 1.6 验证：目录模式、单文件模式、覆盖模式、输出模式均正确
