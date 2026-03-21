# Change: 所有子命令强制要求 --project_root_dir 参数

## Why

当前 `main.py` 中各子命令对项目路径参数的处理方式不一致：部分子命令使用位置参数 `project_path`，部分子命令（如 `test_api`、`list_memories`）则完全不接受项目路径。这导致：

1. **接口不统一**：调用方需要记住每个子命令的参数差异，增加使用成本
2. **上下文缺失**：`test_api` 和 `list_memories` 无法感知当前操作的项目，后续无法基于项目做上下文关联
3. **自动化不友好**：脚本批量调用时需要对不同子命令做特殊处理

## What Changes

- **BREAKING**: 所有子命令的 `project_path` 位置参数改为 `--project_root_dir` 命名参数（必填）
- **BREAKING**: `test_api` 子命令新增必填参数 `--project_root_dir`
- **BREAKING**: `list_memories` 子命令新增必填参数 `--project_root_dir`
- 内部所有引用 `args.project_path` 的地方统一改为 `args.project_root_dir`
- 更新文件顶部的 docstring 使用说明和 `epilog` 示例

## Impact

- Affected specs: cli-commands
- Affected code: `main.py`（`parse_args()` 函数、所有 `_handle_*` 函数、所有 `do_*` 函数的调用处）
- **BREAKING**: 所有现有的命令行调用脚本需要更新参数格式，从位置参数改为 `--project_root_dir`
