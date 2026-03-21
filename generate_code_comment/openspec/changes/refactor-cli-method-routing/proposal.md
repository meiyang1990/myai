# Proposal: refactor-cli-method-routing

## Summary

将 `main.py` 当前扁平化的互斥 `--flag` 模式（`--generate-summary`、`--context-only`、`--scan-only`、`--test-api`、`--list-memories`、`--remove-memory` 以及默认的注释生成模式）重构为统一的 `--method <方法名>` 子命令路由机制。每个 method 只声明自己需要的参数，调用方式更清晰、更易扩展。

## Motivation

### 现状问题

当前 `main.py` 的 CLI 设计存在以下问题：

1. **参数膨胀**：每新增一个功能模式就要加一个 `--flag`（目前已有 `--generate-summary`、`--context-only`、`--scan-only`、`--test-api`、`--list-memories`、`--remove-memory` 共 6 个互斥模式），且这些 flag 之间隐式互斥，用户无法从 `--help` 中直观感知
2. **参数绑定不清晰**：`--project-info` 只在 `--generate-summary` 下才有意义，但在 `--help` 中与所有其他参数混在一起，容易误用
3. **main() 分派逻辑冗长**：`main()` 函数中充满了 `if args.xxx:` 的链式判断，可读性差且扩展性弱
4. **新功能接入成本高**：每次新增功能都需要改动 `parse_args()`、`main()` 两个地方，且需小心维护互斥关系

### 目标

引入 `--method <方法名>` 统一路由，每个 method 绑定自己的参数列表：

```bash
# 生成项目概要（原 --generate-summary）
python main.py --method generate_summary /path/to/project --project-info "..."

# 生成中文注释（原默认模式）
python main.py --method generate_comment /path/to/project

# 其他模式统一格式
python main.py --method test_api
python main.py --method scan_only /path/to/project
python main.py --method list_memories
```

## Scope

### 改动文件

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `main.py` | 重构 | `parse_args()` 改为基于 `argparse` subparsers 的方法路由；`main()` 改为 method 分派表；移除所有互斥 `--flag` |

### 不变的部分

- 所有 `do_*()` 业务函数的签名和逻辑不变
- `config.py`、`memory_store.py`、`project_context.py`、`comment_generator.py` 等模块不变
- 功能行为完全等价，仅 CLI 调用方式变更

## Design

### 方法注册表

在 `main.py` 中定义方法注册表，每个 method 声明：
- `name`：方法名（kebab 或 underscore 风格）
- `help`：简要说明
- `args`：该方法接受的参数列表
- `handler`：关联的 `do_*()` 函数

### argparse subparsers

使用 `argparse.add_subparsers(dest="method")` 实现：

```python
subparsers = parser.add_subparsers(dest="method", help="指定要执行的方法")

# 注册 generate_summary 子命令
sp_summary = subparsers.add_parser("generate_summary", help="生成项目概要并写入长期记忆")
sp_summary.add_argument("project_path", help="项目本地根目录路径")
sp_summary.add_argument("--project-info", default=None, help="项目简要信息")
sp_summary.add_argument("--refresh-context", action="store_true", help="强制刷新")

# 注册 generate_comment 子命令
sp_comment = subparsers.add_parser("generate_comment", help="为项目源码生成中文注释")
sp_comment.add_argument("project_path", help="项目本地根目录路径")
sp_comment.add_argument("-o", "--output", default=None, help="输出目录")
sp_comment.add_argument("--overwrite", action="store_true", help="覆盖原文件")
# ... 其他参数
```

### 方法分派

```python
METHOD_DISPATCH = {
    "generate_summary": lambda args: do_generate_summary(...),
    "generate_comment": lambda args: do_generate(...),
    "test_api": lambda args: do_test_api(),
    "scan_only": lambda args: do_scan_only(args.project_path),
    "context_only": lambda args: do_context_only(...),
    "list_memories": lambda args: do_list_memories(),
    "remove_memory": lambda args: do_remove_memory(args.project_path),
}
```

### 完整方法清单

| method 名 | 对应函数 | 必需参数 | 可选参数 |
|-----------|---------|---------|---------|
| `generate_summary` | `do_generate_summary()` | `project_path` | `--project-info`, `--refresh-context` |
| `generate_comment` | `do_generate()` | `project_path` | `-o/--output`, `--overwrite`, `--copy-others`, `--no-context`, `--refresh-context`, `--reset-progress` |
| `test_api` | `do_test_api()` | 无 | 无 |
| `scan_only` | `do_scan_only()` | `project_path` | 无 |
| `context_only` | `do_context_only()` | `project_path` | `--refresh-context` |
| `list_memories` | `do_list_memories()` | 无 | 无 |
| `remove_memory` | `do_remove_memory()` | `project_path` | 无 |

### 向后兼容

此次重构为 **Breaking Change**（CLI 调用方式改变）。原有的 `--flag` 方式将全部移除，用户需要改用 `--method` 方式。文档和 README 同步更新。

## Risks

1. **用户习惯变化**：已有脚本若使用旧 CLI 语法将失效 → 通过 README 和错误提示引导迁移
2. **argparse subparsers 限制**：subparsers 不支持全局参数自动继承 → 每个子命令显式声明自己需要的参数
