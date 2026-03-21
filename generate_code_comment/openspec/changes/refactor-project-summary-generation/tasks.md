## 1. 长期记忆存储模块

- [x] 1.1 在 `config.py` 中新增 `MEMORY_STORE_DIR`（默认 `~/.code_comment_memory`）和 `MEMORY_STORE_FILE`（默认 `project_summaries.json`）配置常量
- [x] 1.2 新建 `memory_store.py` 模块，实现 `ProjectMemoryStore` 类
  - `save_project_summary(project_path, summary, project_info)` — 保存/更新
  - `load_project_summary(project_path)` — 加载
  - `list_project_summaries()` — 列出所有
  - `remove_project_summary(project_path)` — 删除
  - 存储格式：JSON，key 为 project_path 的 MD5 hash

## 2. 重构 ProjectContextAnalyzer 支持外部项目信息

- [x] 2.1 `get_context()` 方法新增 `project_info: str | None = None` 参数
- [x] 2.2 修改 Prompt 模板，新增 `CONTEXT_PROJECT_INFO_SECTION`，当 `project_info` 不为空时注入到 Human Prompt 中
- [x] 2.3 `_call_llm_for_summary()` 方法支持传入 `project_info`

## 3. 新增独立概要生成入口

- [x] 3.1 在 `main.py` 中新增 `do_generate_summary(project_path, project_info, refresh)` 方法
  - 调用 `ProjectContextAnalyzer.get_context(project_info=project_info, force_refresh=refresh)` 生成概要
  - 将结果通过 `ProjectMemoryStore.save_project_summary()` 写入长期记忆
  - 日志输出生成的概要内容和存储路径
- [x] 3.2 新增命令行参数：`--generate-summary`、`--project-info`、`--list-memories`、`--remove-memory`
- [x] 3.3 在 `main()` 函数中添加新模式的分派逻辑

## 4. 注释生成流程集成长期记忆

- [x] 4.1 修改 `do_generate()` 中项目上下文加载逻辑：优先从长期记忆加载，无则退回自动分析
- [x] 4.2 自动分析生成的概要同步写入长期记忆

## 5. 验证

- [x] 5.1 所有文件通过 py_compile 语法验证
- [x] 5.2 确认新增模块可正确导入无循环依赖
