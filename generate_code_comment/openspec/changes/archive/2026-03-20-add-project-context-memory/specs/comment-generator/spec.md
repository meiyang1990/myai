## MODIFIED Requirements

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

- **WHEN** 代码逻辑简单且命名清晰
- **THEN** 不生成显而易见的冗余注释

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
