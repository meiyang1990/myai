# Tasks: refactor-cli-method-routing

## 1. 重构 parse_args() 为 subparsers 路由

- [x] 移除所有互斥的 `--flag` 参数（`--generate-summary`、`--context-only`、`--scan-only`、`--test-api`、`--list-memories`、`--remove-memory`）
- [x] 使用 `argparse.add_subparsers(dest="method")` 创建子命令注册
- [x] 注册 7 个子命令：`generate_summary`、`generate_comment`、`test_api`、`scan_only`、`context_only`、`list_memories`、`remove_memory`
- [x] 每个子命令只声明自己需要的参数（`project_path`、`--project-info`、`--output` 等）
- [x] 更新 parser 的 description / epilog 示例

## 2. 重构 main() 为方法分派表

- [x] 定义 `METHOD_DISPATCH` 字典，映射 method 名到处理逻辑
- [x] main() 根据 `args.method` 查表分派，替换现有的 `if args.xxx:` 链
- [x] 无 method 时打印帮助并退出

## 3. 更新文件头文档和 README

- [x] 更新 `main.py` 文件头 docstring 中的使用示例
- [x] 更新 `README.md` 中的快速开始示例和命令行参数说明表

## 4. 验证

- [x] py_compile + AST 解析验证语法
- [x] 确认 METHOD_DISPATCH 包含全部 7 个子命令
- [x] 确认所有 17 个必需函数存在
