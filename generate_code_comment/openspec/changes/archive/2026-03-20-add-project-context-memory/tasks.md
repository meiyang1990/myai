## 1. 项目上下文分析模块

- [x] 1.1 新建 `project_context.py` 模块，实现 `ProjectContextAnalyzer` 类
- [x] 1.2 实现智能文件采样策略（入口文件、配置文件、README、核心模块代表文件）
- [x] 1.3 实现目录树生成功能，提取项目结构概览
- [x] 1.4 构建项目分析 Prompt，调用大模型生成架构设计和背景概要文档
- [x] 1.5 实现概要文档的 JSON 持久化存储（`.code_context/project_summary.json`）
- [x] 1.6 实现缓存加载与过期检测逻辑

## 2. 注释生成流程集成

- [x] 2.1 修改 `comment_generator.py`，支持在 System Prompt 中注入项目上下文概要
- [x] 2.2 修改 `main.py`，在注释生成流程中增加「项目上下文分析」步骤
- [x] 2.3 在 `config.py` 中添加项目上下文相关配置项（采样文件数上限、缓存有效期等）

## 3. 命令行参数扩展

- [x] 3.1 添加 `--refresh-context` 参数，支持强制刷新项目上下文
- [x] 3.2 添加 `--context-only` 参数，支持仅生成上下文不执行注释
- [x] 3.3 添加 `--no-context` 参数，支持跳过上下文分析（兼容旧行为）

## 4. 配置与依赖更新

- [x] 4.1 更新 `requirements.txt`（无需新增依赖，所有功能基于已有依赖实现）
- [x] 4.2 更新 `.env.example` 添加新配置项说明
