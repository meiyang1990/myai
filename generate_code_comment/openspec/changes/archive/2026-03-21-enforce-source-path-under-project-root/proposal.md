# Change: 强制 --source_path 为 --project_root_dir 的子路径或同一路径

## Why

当前 `--source_path` 和 `--project_root_dir` 之间没有路径包含关系的校验。用户可能错误地将 `--source_path` 指向一个与 `--project_root_dir` 毫无关系的路径，导致：
1. `.gitignore` 规则无法正确匹配（因 `SourceReader` 基于 `project_root` 加载 `.gitignore`）
2. 进度跟踪的相对路径计算异常（`rel_path` 可能包含 `../` 前缀）
3. 项目概要信息与实际处理文件不匹配，导致注释质量下降

## What Changes

- 在 `_handle_generate_comment()` 中新增路径关系校验：解析 `--source_path` 和 `--project_root_dir` 的绝对路径后，检查 `source_path` 是否为 `project_root_dir` 的子路径或与其相同
- 校验不通过时，输出清晰的错误信息并退出
- 更新 `--source_path` 的 argparse help 文本，明确标注此约束

## Impact

- Affected specs: `cli-commands`
- Affected code: `main.py`（`_handle_generate_comment()` 函数、`--source_path` 的 argparse help 文本）
