# 注释生成引擎

## Purpose

系统的核心模块，基于 LangChain 框架和火山引擎大模型 API，为代码文件生成高质量的中文注释，并将注释准确回写到源码中。

---

## Requirements

### Requirement: 多层级注释生成

系统 SHALL 通过 LangChain ChatOpenAI 接入火山引擎大模型，为代码生成文件级、类级、方法级和行内级四个层级的中文注释。系统将整个源码文件连同项目上下文概要一次性提交给大模型，由大模型返回完整的带注释代码。

#### Scenario: 整文件注释生成（带上下文）

- **WHEN** 处理一个源码文件
- **AND** 已有项目上下文概要
- **THEN** 将项目概要作为 System Prompt 的补充上下文
- **AND** 将文件完整内容、文件路径、语言类型信息一起提交给大模型
- **AND** 大模型返回添加了具有项目全局视角的多层级中文注释的完整代码

#### Scenario: 整文件注释生成（无上下文降级）

- **WHEN** 处理一个源码文件
- **AND** 项目上下文概要不可用
- **THEN** 使用现有的无上下文 prompt 方式提交给大模型
- **AND** 行为与变更前一致

#### Scenario: 生成文件级注释

- **WHEN** 大模型处理一个源码文件
- **THEN** 在文件头部生成注释，说明文件所属模块、核心职责和主要功能

#### Scenario: 生成方法级注释

- **WHEN** 大模型处理方法/函数定义
- **THEN** 生成注释说明方法功能、参数含义、返回值、异常情况和核心逻辑流程

#### Scenario: 避免冗余注释

- **WHEN** 代码行为 import/from 导入语句、简单变量声明或简单逻辑计算
- **THEN** 不生成注释
- **AND** 当函数体在 5 行以内时，仅生成函数级注释而非逐行注释

---

### Requirement: 语言特定注释格式

系统 SHALL 通过 System Prompt 指导大模型根据目标文件的编程语言，使用对应的标准注释格式。

#### Scenario: Java 文件使用 Javadoc 格式

- **WHEN** 为 Java 文件生成注释
- **THEN** 使用 `/** */` 格式的 Javadoc 注释

#### Scenario: Python 文件使用 Docstring 格式

- **WHEN** 为 Python 文件生成注释
- **THEN** 使用 `""" """` 格式的 Docstring 注释

---

### Requirement: 上下文感知注释

系统 SHALL 基于项目上下文概要文档（包含架构设计、业务背景和模块职责）生成有深度上下文意义的注释，而非仅翻译代码表面逻辑。

#### Scenario: 注释体现业务含义

- **WHEN** 方法名为 `calculateDiscount`
- **AND** 项目概要中描述了折扣业务规则
- **THEN** 注释结合项目概要中的业务上下文，说明折扣规则和适用场景

#### Scenario: 注释体现架构角色

- **WHEN** 类位于 service 层
- **AND** 项目概要中描述了分层架构设计
- **THEN** 注释引用概要中的架构描述，说明该类在整体架构中的定位和上下游关系

#### Scenario: 注释引用模块关系

- **WHEN** 代码中存在跨模块调用
- **AND** 项目概要中包含模块间关系描述
- **THEN** 注释说明该调用涉及的模块交互和数据流向

---

### Requirement: 注释回写与格式保持

系统 SHALL 将大模型返回的带注释代码写入文件，支持安全输出模式和覆盖模式。

#### Scenario: 安全输出模式

- **WHEN** 使用默认设置运行
- **THEN** 将带注释代码写入 `<项目名>_commented` 新目录，保持原始项目目录结构

#### Scenario: 覆盖模式

- **WHEN** 使用 `--overwrite` 参数运行
- **THEN** 直接覆盖原始源码文件
- **AND** 执行前要求用户二次确认

#### Scenario: 保持目录结构

- **WHEN** 输出到新目录时
- **THEN** 自动创建与原项目相同的目录层级结构

---

### Requirement: 幂等注释生成

系统 SHALL 支持幂等操作，重复运行不会产生重复注释。

#### Scenario: 避免重复注释

- **WHEN** 对已有注释的代码再次运行注释生成
- **THEN** 检测到已有注释并跳过，不产生重复注释

#### Scenario: 更新已有注释

- **WHEN** 用户明确要求更新已有注释
- **THEN** 替换旧注释为新生成的注释，不保留旧内容

---

### Requirement: 注释质量保证

系统 SHALL 通过精心设计的 System Prompt 和低温度参数确保生成注释的准确性和一致性。

#### Scenario: Prompt 工程

- **WHEN** 构建大模型请求
- **THEN** 使用包含详细注释原则和输出要求的 System Prompt

#### Scenario: 清理大模型输出

- **WHEN** 大模型返回的内容包含 markdown 代码块标记
- **THEN** 自动去除 ``` 包裹，只保留纯代码内容

---

### Requirement: 火山引擎大模型集成

系统 SHALL 通过 LangChain v0.1.16 的 ChatOpenAI 组件，利用 OpenAI 兼容协议接入火山引擎大模型 API。

#### Scenario: API 连接配置

- **WHEN** 初始化 CommentGenerator
- **THEN** 使用 .env 中的 VOLCENGINE_API_KEY、VOLCENGINE_API_BASE 和 VOLCENGINE_MODEL_ENDPOINT 配置 ChatOpenAI

#### Scenario: 连接测试

- **WHEN** 用户执行 `--test-api` 命令
- **THEN** 发送测试消息到大模型并返回连接状态

#### Scenario: 配置校验

- **WHEN** 启动程序时
- **THEN** 校验 API Key、API Base 和 Model Endpoint 是否已配置，缺失则报错提示

---

### Requirement: 命令行工具

系统 SHALL 提供命令行界面，支持多种运行模式，包括项目上下文管理。

#### Scenario: 基本注释生成

- **WHEN** 执行 `python main.py /path/to/project`
- **THEN** 自动加载或生成项目上下文概要，然后扫描项目、生成注释、输出到新目录

#### Scenario: 扫描预览

- **WHEN** 执行 `python main.py /path/to/project --scan-only`
- **THEN** 仅列出将处理的文件及其语言类型，不调用大模型

#### Scenario: API 测试

- **WHEN** 执行 `python main.py --test-api`
- **THEN** 测试火山引擎 API 连接并输出结果

#### Scenario: 刷新项目上下文

- **WHEN** 执行 `python main.py /path/to/project --refresh-context`
- **THEN** 强制重新分析项目并生成新的上下文概要，覆盖已有缓存

#### Scenario: 仅生成上下文

- **WHEN** 执行 `python main.py /path/to/project --context-only`
- **THEN** 仅生成项目上下文概要并存储，不执行注释生成
