## 1. 修改 System Prompt（注释硬性规则）

- [x] 1.1 在 `comment_generator.py` 的 `SYSTEM_PROMPT` 常量中新增「硬性规则」章节，明确以下约束：
  - 禁止修改任何源码逻辑
  - import/from 导入行、变量声明、简单逻辑计算不生成注释
  - 5 行以内的简短函数仅在函数上方添加注释，不逐行注释
  - 其他情况逐行添加简洁中文注释
- [x] 1.2 调整现有「避免冗余注释」的 prompt 措辞，与新硬性规则保持一致

## 2. 新增测试文件过滤逻辑

- [x] 2.1 在 `config.py` 中新增 `TEST_FILE_PATTERNS` 配置项，定义单元测试文件的命名匹配模式列表
- [x] 2.2 在 `config.py` 中将测试目录（`test`、`tests`、`__tests__`、`spec`、`specs`）加入 `DEFAULT_IGNORE_DIRS`
- [x] 2.3 在 `source_reader.py` 的 `_should_ignore_file` 方法中新增测试文件名模式匹配逻辑
- [x] 2.4 匹配到测试文件时打印跳过提示，说明原因为"测试文件"

## 3. 验证与测试

- [x] 3.1 手动验证 System Prompt 的硬性规则措辞完整准确
- [x] 3.2 确认测试文件过滤逻辑覆盖主流语言的测试命名规范
