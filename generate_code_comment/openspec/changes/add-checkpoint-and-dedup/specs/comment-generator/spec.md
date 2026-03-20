# Delta: comment-generator

## MODIFIED Requirements

### Requirement: 注释硬性规则

系统 SHALL 在 System Prompt 中定义一组不可违反的注释硬性规则，确保大模型严格遵守注释行为约束，所有规则优先级高于其他注释策略。新增第 6 条规则：避免对已有中文注释的代码重复添加注释。

#### Scenario: 避免重复添加中文注释

- **WHEN** 代码行或函数体上方已经包含中文注释
- **THEN** 保留已有的中文注释不做修改
- **AND** 不再为该代码行或函数体重复生成新的中文注释
- **AND** 仅对尚无中文注释的代码段落添加新注释

## ADDED Requirements

### Requirement: 文件处理进度跟踪

系统 SHALL 在注释生成流程中集成进度跟踪器，记录每个成功处理的文件，支持断点恢复以避免重复调用大模型。进度数据持久化存储在目标项目的 `.code_context/progress.json` 文件中。

#### Scenario: 跳过已处理文件

- **WHEN** 开始处理某个源码文件
- **AND** 进度记录显示该文件已在之前的运行中成功处理
- **THEN** 跳过该文件，不调用大模型
- **AND** 打印跳过提示

#### Scenario: 记录文件处理成功

- **WHEN** 某个文件的注释生成并成功写入
- **THEN** 在进度记录中标记该文件为已完成，并持久化保存

#### Scenario: 重置进度

- **WHEN** 用户使用 `--reset-progress` 参数运行
- **THEN** 清除所有进度记录，从头处理所有文件
