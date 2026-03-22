# Change: 过滤前端源码文件，不生成中文注释

## Why

本工具的核心目标是为**后端/业务逻辑**源码生成高质量的中文注释。前端代码文件（`.js`、`.jsx`、`.css`、`.vue`、`.ts`、`.tsx` 等）通常属于 UI 层，在大型全栈项目（如 Apache Spark）中大量存在。为这些文件生成注释不仅无实际价值，还会：

1. **浪费大模型调用次数和 Token 额度**（前端文件可能占项目文件总量的 30%+）
2. **增加处理时间**，拉长整体注释生成耗时
3. **降低注释质量**：大模型对前端 UI 代码的注释往往流于表面描述，缺乏业务深度

因此，需要在文件扫描阶段直接过滤掉前端源码文件。

## What Changes

- 从 `LANGUAGE_EXTENSIONS` 中移除前端相关扩展名：`.js`、`.jsx`、`.ts`、`.tsx`、`.css`、`.vue`
- 同步清理 `COMMENT_STYLES` 和 `_SINGLE_LINE_COMMENT_PREFIX` 中对应的 JavaScript、TypeScript、Vue 条目
- 同步清理 `TEST_FILE_PATTERNS` 中对应的 JS/TS 测试文件模式（已不需要）
- 扫描阶段将自动跳过这些文件（因为扩展名不在映射表中）

## Impact

- Affected specs: `source-code-reader`（文件过滤规则变更）
- Affected code: `config.py`（移除前端扩展名和相关配置）
