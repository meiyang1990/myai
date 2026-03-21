# Change: 重构项目概要生成为独立入口方法，并引入长期记忆机制

## Why

当前项目概要生成逻辑嵌入在 `do_generate()` 和 `do_context_only()` 流程中，由 `ProjectContextAnalyzer` 自动扫描目录树和采样文件后调用大模型生成概要。存在以下不足：

1. **无法接受用户提供的项目简要信息**：现有方式完全依赖自动采样，用户无法传入项目的业务背景、核心功能描述等额外信息，导致大模型生成的概要可能缺少人工可补充的关键上下文
2. **概要生成与注释生成耦合**：概要生成没有独立、可复用的入口方法，不方便单独调用
3. **缺乏长期记忆**：每个项目的概要以 JSON 缓存形式存储在项目内部的 `.code_context/` 目录，不同项目之间的概要无法集中管理；且后续注释生成时仅以单次 prompt 注入方式使用，没有「项目根目录 → 概要」的全局映射机制

## What Changes

### 1. 新增独立的项目概要生成入口方法

在 `main.py` 中新增 `do_generate_summary(project_path, project_info, refresh)` 方法：
- 接收参数：
  - `project_path`：项目本地根目录路径
  - `project_info`：用户提供的项目简要信息文本（如业务背景、核心功能、技术栈等）
  - `refresh`：是否强制刷新（忽略已有缓存/记忆）
- 内部调用 `ProjectContextAnalyzer` 生成概要，并将用户提供的 `project_info` 作为额外上下文一起喂给大模型
- 生成结果同时写入长期记忆存储

### 2. 重构 `ProjectContextAnalyzer` 支持接收外部项目信息

- `get_context()` 方法新增可选参数 `project_info: str | None`
- 修改 Prompt 模板，当 `project_info` 不为空时，在 Human Prompt 中增加「用户提供的项目简要信息」章节
- 大模型在自动扫描的目录树、采样文件基础上，结合用户信息生成更准确的概要

### 3. 引入长期记忆存储（项目根目录 → 项目概要映射）

- 新增 `memory_store.py` 模块，提供全局的长期记忆管理
- 记忆存储路径：`~/.code_comment_memory/project_summaries.json`（用户 HOME 目录下，跨项目共享）
- 数据结构：以 `project_path` 的 hash 为 key，存储 `{project_path, summary, project_info, timestamp, version}`
- 提供方法：
  - `save_project_summary(project_path, summary, project_info)` — 保存/更新长期记忆
  - `load_project_summary(project_path)` — 按项目路径加载记忆
  - `list_project_summaries()` — 列出所有已记忆的项目
  - `remove_project_summary(project_path)` — 删除指定项目记忆
- 原 `.code_context/project_summary.json` 作为项目内缓存保留，长期记忆作为全局共享层

### 4. 注释生成流程集成长期记忆

- `do_generate()` 流程中，优先从长期记忆加载项目概要
- 如果长期记忆中有该项目的概要，且未要求强制刷新，则直接使用（不再调用大模型）
- 如果长期记忆中无概要，退回到原有的 `ProjectContextAnalyzer` 自动分析流程
- 新生成的概要自动写入长期记忆

### 5. 新增命令行参数

- `--generate-summary`：触发独立的概要生成模式
- `--project-info "..."`：传入项目简要信息文本
- `--list-memories`：列出所有已记忆的项目概要
- `--remove-memory`：删除指定项目的长期记忆

## Impact

- Affected specs: `architecture-analyzer`
- Affected code:
  - `main.py`：新增 `do_generate_summary()` 方法、新增命令行参数、修改 `do_generate()` 集成长期记忆
  - `project_context.py`：`get_context()` 和 Prompt 支持接收 `project_info`
  - `memory_store.py`：**新增**，长期记忆存储管理模块
  - `config.py`：新增 `MEMORY_STORE_DIR` 等配置常量
