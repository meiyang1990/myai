## 1. Implementation

- [x] 1.1 修改 `parse_args()` 函数：将所有子命令的 `project_path` 位置参数替换为 `--project_root_dir` 命名参数（required=True）
- [x] 1.2 为 `test_api` 子命令添加 `--project_root_dir` 必填参数
- [x] 1.3 为 `list_memories` 子命令添加 `--project_root_dir` 必填参数
- [x] 1.4 修改所有 `_handle_*` 处理函数：将 `args.project_path` 改为 `args.project_root_dir`
- [x] 1.5 修改 `_validate_project_path()` 调用处以适配新参数名
- [x] 1.6 更新文件顶部 docstring 中的使用说明和示例
- [x] 1.7 更新 `parse_args()` 中的 `epilog` 示例文本
- [x] 1.8 验证所有子命令可正常解析 `--project_root_dir` 参数
