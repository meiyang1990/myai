## 1. Implementation

- [x] 1.1 在 `comment_generator.py` 的 `SYSTEM_PROMPT` 硬性规则中新增第 7 条：禁止简单翻译代码中的变量名、函数名、类名作为注释内容，注释必须说清代码或函数的实际作用、业务意义和上下文关系
- [x] 1.2 更新 `openspec/specs/comment-generator/spec.md` 中「注释硬性规则」Requirement（通过 spec delta 实现）
