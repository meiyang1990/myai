# Change: 新增项目上下文记忆功能

## Why

当前系统在为每个源码文件生成注释时，仅将单个文件的代码内容和基本信息（文件路径、语言类型）提交给大模型。大模型缺乏对目标项目整体架构、业务背景和设计理念的理解，导致生成的注释停留在代码表面逻辑层面，无法体现业务语义和架构上下文。

通过新增「项目上下文记忆」功能，系统将在注释生成前先调用大模型分析整个项目，生成架构设计和背景概要文档，并通过 LangChain 长期记忆机制持久化存储。后续每次为文件生成注释时，该概要文档将作为 prompt 上下文一并提交，让大模型具备项目全局视角，显著提升注释的业务含义和架构感知质量。

## What Changes

- **新增 `project_context.py` 模块**：项目上下文分析器，负责调用大模型生成项目架构设计和背景概要文档
- **新增 LangChain 长期记忆存储**：使用基于文件的持久化方案存储项目概要文档，避免每次重复生成
- **MODIFIED `comment_generator.py`**：注释生成时在 prompt 中注入项目上下文概要，增强大模型的项目全局理解
- **MODIFIED `main.py`**：在注释生成流程中增加「项目上下文分析」步骤
- **MODIFIED `config.py`**：新增项目上下文相关的配置项
- **MODIFIED `requirements.txt`**：新增依赖项

## Impact

- Affected specs: `architecture-analyzer`, `comment-generator`
- Affected code: `project_context.py`（新增）, `comment_generator.py`, `main.py`, `config.py`, `requirements.txt`
- 非破坏性变更：现有注释生成流程保持兼容，项目上下文为增量增强
