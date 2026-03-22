## 1. Implementation

- [x] 1.1 修改 `config.py`：新增 `MEMORY_BASE_DIR` 配置项（默认为程序根目录下的 `memory/`），废弃旧的 `MEMORY_STORE_DIR` 和 `MEMORY_STORE_FILE`
- [x] 1.2 重构 `memory_store.py` 的 `ProjectMemoryStore`：构造函数接收 `project_path`，为每个项目在 `memory/` 下创建独立子目录（目录名采用项目末尾目录名 + 短 hash 后缀），记忆文件独立存放
- [x] 1.3 修改 `memory_store.py` 的 `list_project_summaries()`：遍历 `memory/` 下所有项目子目录
- [x] 1.4 修改 `memory_store.py` 的 `remove_project_summary()`：删除对应项目的子目录
- [x] 1.5 修改 `main.py`：所有创建 `ProjectMemoryStore` 的地方传入 `project_path` 参数
- [x] 1.6 更新 `openspec/specs/comment-generator/spec.md` 中相关 Requirement（通过 spec delta 实现）
