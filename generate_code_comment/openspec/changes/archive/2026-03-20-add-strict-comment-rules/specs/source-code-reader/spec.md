## MODIFIED Requirements

### Requirement: 文件过滤

系统 SHALL 自动过滤非源码文件（构建产物、依赖目录、配置文件等）和单元测试代码文件，只保留需要添加注释的业务源码文件。

#### Scenario: 过滤构建产物

- **WHEN** 扫描到 `target/`、`build/`、`dist/`、`node_modules/` 等构建/依赖目录
- **THEN** 跳过这些目录不进行处理

#### Scenario: 遵守 .gitignore 规则

- **WHEN** 项目根目录存在 `.gitignore` 文件
- **THEN** 使用 pathspec 库解析规则，被 `.gitignore` 忽略的文件和目录不被扫描

#### Scenario: 过滤超大文件

- **WHEN** 源码文件大小超过 MAX_FILE_SIZE 阈值（默认 1MB）
- **THEN** 打印跳过提示并忽略该文件

#### Scenario: 过滤单元测试文件

- **WHEN** 扫描到符合单元测试文件命名规则的文件
- **AND** 文件名匹配以下模式之一：`Test*.java`、`*Test.java`、`*Tests.java`、`*Spec.java`、`test_*.py`、`*_test.py`、`*_test.go`、`*.test.js`、`*.test.ts`、`*.test.tsx`、`*.spec.js`、`*.spec.ts`、`*.spec.tsx`
- **THEN** 跳过该文件，不纳入注释处理范围
- **AND** 打印跳过提示说明原因为"测试文件"

#### Scenario: 过滤测试目录

- **WHEN** 扫描到名称为 `test`、`tests`、`__tests__`、`spec`、`specs` 的目录
- **THEN** 跳过该目录及其所有子文件，不纳入注释处理范围
