## 1. Implementation

- [x] 1.1 修改 `comment_generator.py` 的 `SYSTEM_PROMPT` 第 3 条硬性规则：所有函数/方法（无论简单复杂）MUST 添加函数级中文注释；简短函数（5行以内）不对内部逐行注释的限制保留
- [x] 1.2 在 `SYSTEM_PROMPT` 硬性规则中新增第 8 条：所有类定义（无论简单复杂）MUST 添加类级中文注释
- [x] 1.3 修改 `SYSTEM_PROMPT` 注释原则第 3 条：调整冗余注释规则描述，与新的硬性规则保持一致
- [x] 1.4 更新 `openspec/specs/comment-generator/spec.md` 中「注释硬性规则」Requirement（通过 spec delta 实现）
