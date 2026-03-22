## MODIFIED Requirements

### Requirement: 编程语言识别

系统 SHALL 根据文件扩展名自动识别源码文件的编程语言，支持后端和系统编程语言。前端源码文件（JavaScript、TypeScript、CSS、Vue）不在支持范围内，扫描阶段将自动跳过。

#### Scenario: 识别 Java 项目文件

- **WHEN** 扫描到 `.java` 扩展名的文件
- **THEN** 将其标记为 Java 语言源码

#### Scenario: 识别多语言项目

- **WHEN** 项目包含多种编程语言的源码文件
- **THEN** 每个文件根据扩展名被正确标记为对应的语言类型

#### Scenario: 跳过不支持的文件类型

- **WHEN** 扫描到不在语言映射表中的文件（如 `.txt`、`.md`、`.json`）
- **THEN** 自动跳过该文件

#### Scenario: 跳过前端源码文件

- **WHEN** 扫描到 `.js`、`.jsx`、`.ts`、`.tsx`、`.css`、`.vue` 扩展名的文件
- **THEN** 自动跳过该文件，不纳入注释处理范围
- **AND** 原因为前端源码文件不在本工具的注释生成目标范围内

### Requirement: 文件过滤

系统 SHALL 自动过滤非源码文件（构建产物、依赖目录、配置文件等）、单元测试代码文件和前端源码文件，只保留需要添加注释的后端/系统级业务源码文件。

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
- **AND** 文件名匹配以下模式之一：`Test*.java`、`*Test.java`、`*Tests.java`、`*Spec.java`、`test_*.py`、`*_test.py`、`*_test.go`
- **THEN** 跳过该文件，不纳入注释处理范围
- **AND** 打印跳过提示说明原因为"测试文件"

#### Scenario: 过滤测试目录

- **WHEN** 扫描到名称为 `test`、`tests`、`__tests__`、`spec`、`specs` 的目录
- **THEN** 跳过该目录及其所有子文件，不纳入注释处理范围

#### Scenario: 前端源码文件自动排除

- **WHEN** 扫描到 `.js`、`.jsx`、`.ts`、`.tsx`、`.css`、`.vue` 扩展名的文件
- **THEN** 因扩展名不在 `LANGUAGE_EXTENSIONS` 映射表中，自动跳过
- **AND** 不调用大模型，不消耗 Token 额度
