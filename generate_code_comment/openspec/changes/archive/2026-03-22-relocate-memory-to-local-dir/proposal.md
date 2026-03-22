# Change: 记忆存储迁移到程序本地 memory 目录并按项目隔离

## Why

当前记忆（项目概要）存储在用户 HOME 目录下 `~/.code_comment_memory/project_summaries.json`，所有项目的概要集中放在一个 JSON 文件中，以 MD5 hash 作为 key 区分项目。这种方案存在以下问题：

1. **不直观**：数据散落在用户 HOME 目录深处，难以查看、管理和备份
2. **单文件瓶颈**：所有项目共享一个 JSON 文件，在并发场景或项目数量大时存在读写冲突风险
3. **可移植性差**：程序目录迁移后，记忆仍留在旧机器的 HOME 目录中

用户期望：**记忆统一存储在当前运行程序的 `memory/` 目录下，针对每一个 `--project_root_dir` 在 `memory/` 下创建对应的子目录来存储该项目的所有记忆数据。**

## What Changes

- 新增 `config.py` 配置项 `MEMORY_BASE_DIR`：默认值为程序运行目录下的 `memory/`（即 `<程序根目录>/memory/`）
- 修改 `memory_store.py` 的 `ProjectMemoryStore`：
  - 构造函数接收 `project_path` 参数，根据项目路径生成可读的子目录名（采用路径末尾目录名 + 短 hash 后缀避免冲突）
  - 每个项目的记忆文件独立存放在 `memory/<项目子目录>/project_summary.json`
  - `list_project_summaries()` 遍历 `memory/` 下所有子目录
  - `remove_project_summary()` 删除对应项目的子目录
- 修改 `main.py`：在创建 `ProjectMemoryStore` 时传入 `project_path`
- 废弃 `config.py` 中旧的 `MEMORY_STORE_DIR` 和 `MEMORY_STORE_FILE` 配置项

## Impact

- Affected specs: `comment-generator`（修改「长期记忆存储」相关行为）
- Affected code: `config.py`（配置项）、`memory_store.py`（核心重构）、`main.py`（调用方适配）
- **数据迁移**：旧的 `~/.code_comment_memory/project_summaries.json` 数据不会自动迁移，用户可通过 `generate_summary` 子命令重新生成
