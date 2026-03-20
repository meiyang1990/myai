## ADDED Requirements

### Requirement: 项目概要文档生成

系统 SHALL 扫描目标项目的源码文件，将具有代表性的文件内容提交给大模型，生成一份包含架构设计、技术栈、业务背景和模块职责的项目概要文档（Markdown 格式）。

#### Scenario: 首次分析项目

- **WHEN** 用户首次对一个项目执行注释生成
- **AND** 该项目尚无缓存的概要文档
- **THEN** 系统自动挑选关键源码文件（入口文件、配置文件、核心模块等）
- **AND** 将这些文件内容组装为分析 prompt，调用大模型生成项目概要
- **AND** 概要文档包含：项目背景与目标、技术栈与框架、架构设计与分层、核心模块职责、模块间关系、关键设计模式

#### Scenario: 控制分析成本

- **WHEN** 项目包含大量源码文件
- **THEN** 系统使用智能采样策略，优先选择入口文件、配置文件、包含关键字的核心文件
- **AND** 控制提交给大模型的总 token 数在合理范围内（可通过配置调整）

#### Scenario: 项目概要生成失败

- **WHEN** 大模型 API 调用失败或返回无效内容
- **THEN** 系统打印警告信息，继续执行后续注释生成（降级为无上下文模式）

---

### Requirement: 项目上下文持久化存储

系统 SHALL 使用基于文件系统的持久化方案，将项目概要文档存储在本地，避免重复调用大模型分析同一项目。

#### Scenario: 存储概要文档

- **WHEN** 项目概要文档成功生成
- **THEN** 将概要文档以 JSON 格式存储到 `<项目根目录>/.code_context/project_summary.json`
- **AND** 存储内容包含：概要文本、生成时间戳、项目路径哈希、版本号

#### Scenario: 加载已有概要

- **WHEN** 再次对同一项目执行注释生成
- **AND** 已存在有效的概要文档缓存
- **THEN** 直接从文件加载概要，跳过大模型分析步骤

#### Scenario: 强制重新生成

- **WHEN** 用户通过命令行参数 `--refresh-context` 显式要求刷新
- **THEN** 忽略已有缓存，重新调用大模型生成项目概要并覆盖旧缓存

#### Scenario: 缓存过期策略

- **WHEN** 缓存的概要文档超过可配置的有效期（默认 7 天）
- **THEN** 打印提示信息，建议用户使用 `--refresh-context` 更新
- **AND** 仍使用已有缓存（不自动重新生成，由用户决定）

## MODIFIED Requirements

### Requirement: 项目结构识别

系统 SHALL 分析目标项目的目录结构和包结构，识别项目的组织方式和分层模式，并将分析结果作为项目概要生成的输入。

#### Scenario: 识别 Spring Boot 项目结构

- **WHEN** 分析一个标准的 Spring Boot 项目
- **THEN** 识别出 controller、service、repository、entity 等分层结构
- **AND** 理解每一层的职责和约定

#### Scenario: 识别前端项目结构

- **WHEN** 分析一个 React/Vue 前端项目
- **THEN** 识别出 components、pages、hooks、services、utils 等模块组织
- **AND** 理解组件层级和状态管理模式

#### Scenario: 作为概要生成输入

- **WHEN** 项目结构识别完成
- **THEN** 将目录树和分层信息提供给概要生成模块，辅助大模型理解项目全貌
