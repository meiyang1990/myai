# Change: 新增中文注释生成硬性规则

## Why

当前注释生成流程依赖大模型自主判断注释策略，缺少明确的硬性约束规则，导致存在以下问题：
- 大模型可能修改源码逻辑（而非仅添加注释）
- 单元测试文件和非源码文件也被处理，浪费 API 调用
- 简单的 import 语句、变量声明等也被添加冗余注释
- 短小函数逐行注释过于啰嗦
- 注释详细程度不一致，部分注释过于繁琐

需要在 System Prompt 层面和文件过滤层面引入一组硬性规则，确保注释生成行为可控、一致、高效。

## What Changes

- **MODIFIED** comment-generator 的「多层级注释生成」requirement：在 System Prompt 中新增 5 条硬性规则
  1. 绝对不能修改源码，只能添加中文注释
  2. 跳过简单代码行（import/from 导入、变量声明、简单逻辑计算）
  3. 5 行以内的简短函数只在函数上方添加注释，不逐行注释
  4. 其他情况逐行添加中文注释，注释务必简洁
- **MODIFIED** comment-generator 的「避免冗余注释」相关 scenario：细化冗余注释的判定标准
- **MODIFIED** source-code-reader 的「文件过滤」requirement：新增过滤单元测试文件的规则
- **ADDED** comment-generator 新增「注释硬性规则」requirement：系统化管理不可违反的注释约束

## Impact

- Affected specs: `comment-generator`, `source-code-reader`
- Affected code:
  - `comment_generator.py` — 修改 SYSTEM_PROMPT 常量，增加硬性规则章节
  - `source_reader.py` — 新增单元测试文件的识别和过滤逻辑
  - `config.py` — 新增测试文件匹配模式配置
