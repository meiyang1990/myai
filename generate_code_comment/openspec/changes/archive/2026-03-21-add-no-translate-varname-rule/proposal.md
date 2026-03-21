# Change: 新增 Prompt 规则 —— 禁止简单翻译变量名，注释须说清代码/函数作用

## Why

当前大模型生成注释时，经常出现"翻译变量名"式的低质量注释，例如把 `getUserName()` 注释为"获取用户名"、把 `orderList` 注释为"订单列表"。这种注释对代码阅读者毫无帮助——他们看变量名就能知道这些。真正有价值的注释应该解释代码或函数**做了什么事、为什么这样做、在业务流程中承担什么角色**。

## What Changes

- 在 `comment_generator.py` 的 `SYSTEM_PROMPT` 中新增一条硬性规则（第 7 条），明确禁止"翻译变量名"式注释，要求注释聚焦于**代码/函数的实际作用和业务意义**
- 同步更新 spec：修改「注释硬性规则」Requirement，追加第 7 条规则及对应 Scenario

## Impact

- Affected specs: `comment-generator`（修改「注释硬性规则」Requirement）
- Affected code: `comment_generator.py`（`SYSTEM_PROMPT` 常量）
