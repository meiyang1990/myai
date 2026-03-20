# 架构分析引擎

## Overview

本功能负责对已加载的源码进行项目级架构分析，识别架构模式、模块关系和设计模式，为后续的注释生成提供项目上下文理解。

---

## Requirements

### Requirement: 项目结构识别

系统 SHALL 分析目标项目的目录结构和包结构，识别项目的组织方式和分层模式。

#### Scenario: 识别 Spring Boot 项目结构

- **WHEN** 分析一个标准的 Spring Boot 项目
- **THEN** 识别出 controller、service、repository、entity 等分层结构
- **AND** 理解每一层的职责和约定

#### Scenario: 识别前端项目结构

- **WHEN** 分析一个 React/Vue 前端项目
- **THEN** 识别出 components、pages、hooks、services、utils 等模块组织
- **AND** 理解组件层级和状态管理模式

---

### Requirement: 模块依赖分析

系统 SHALL 分析模块/包之间的依赖关系，构建模块依赖图。

#### Scenario: 分析 Java 包依赖

- **WHEN** 分析 Java 项目的 import 语句
- **THEN** 构建出包级别的依赖关系图
- **AND** 识别循环依赖和核心模块

#### Scenario: 分析前端模块导入

- **WHEN** 分析 TypeScript/JavaScript 的 import/require 语句
- **THEN** 构建出模块级别的依赖关系
- **AND** 识别共享组件和工具模块

---

### Requirement: 设计模式识别

系统 SHALL 识别项目中使用的常见设计模式（工厂、单例、观察者、策略等）。

#### Scenario: 识别工厂模式

- **WHEN** 代码中存在工厂类或工厂方法
- **THEN** 在注释中标注该类/方法使用了工厂模式
- **AND** 说明工厂创建的产品类型

#### Scenario: 识别 Spring 依赖注入模式

- **WHEN** 代码使用 `@Autowired`、`@Inject` 等注解
- **THEN** 在注释中说明依赖注入的关系和生命周期

---

### Requirement: 核心业务流程追踪

系统 SHALL 追踪项目中的核心业务流程，分析请求处理链路和数据流转。

#### Scenario: 追踪 REST API 调用链

- **WHEN** 分析一个 REST API 的处理流程
- **THEN** 从 Controller 入口追踪到 Service → Repository → 数据库
- **AND** 记录完整的调用链路用于注释生成

#### Scenario: 识别异步处理流程

- **WHEN** 代码中使用消息队列、异步任务等机制
- **THEN** 识别异步处理的触发点、消费点和回调逻辑
