## 1. Implementation

- [x] 1.1 `main.py` `_handle_generate_comment()`：在现有 `--source_path` 存在性校验之后，新增路径包含关系校验，确保 `source_path` 是 `project_root_dir` 的子路径或与其相同
- [x] 1.2 `main.py`：更新 `--source_path` 的 argparse help 文本，明确标注路径约束
- [x] 1.3 验证：检查代码无 lint 错误
