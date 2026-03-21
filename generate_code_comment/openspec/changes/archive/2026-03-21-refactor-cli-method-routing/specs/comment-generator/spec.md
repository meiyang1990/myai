# 注释生成引擎

## MODIFIED Requirements

### Requirement: 命令行工具

系统 SHALL 提供基于 `--method <方法名>` 子命令路由的命令行界面，每个方法只声明自己需要的参数，替代原有扁平化的互斥 `--flag` 模式。

#### Scenario: 生成中文注释（generate_comment）

- **WHEN** 执行 `python main.py generate_comment /path/to/project`
- **THEN** 自动加载或生成项目上下文概要，然后扫描项目、生成注释、输出到新目录
- **AND** 支持可选参数 `-o/--output`、`--overwrite`、`--copy-others`、`--no-context`、`--refresh-context`、`--reset-progress`

#### Scenario: 生成项目概要（generate_summary）

- **WHEN** 执行 `python main.py generate_summary /path/to/project`
- **THEN** 分析项目源码并生成概要文档，写入长期记忆
- **AND** 支持可选参数 `--project-info`（项目简要信息）、`--refresh-context`（强制刷新）

#### Scenario: 扫描预览（scan_only）

- **WHEN** 执行 `python main.py scan_only /path/to/project`
- **THEN** 仅列出将处理的文件及其语言类型，不调用大模型

#### Scenario: API 测试（test_api）

- **WHEN** 执行 `python main.py test_api`
- **THEN** 测试火山引擎 API 连接并输出结果
- **AND** 不需要提供项目路径参数

#### Scenario: 仅生成上下文（context_only）

- **WHEN** 执行 `python main.py context_only /path/to/project`
- **THEN** 仅生成项目上下文概要并存储，不执行注释生成
- **AND** 支持可选参数 `--refresh-context`

#### Scenario: 列出长期记忆（list_memories）

- **WHEN** 执行 `python main.py list_memories`
- **THEN** 列出所有已记忆的项目概要
- **AND** 不需要提供项目路径参数

#### Scenario: 删除长期记忆（remove_memory）

- **WHEN** 执行 `python main.py remove_memory /path/to/project`
- **THEN** 删除指定项目的长期记忆

#### Scenario: 未指定方法

- **WHEN** 执行 `python main.py` 不带任何子命令
- **THEN** 打印帮助信息并退出
