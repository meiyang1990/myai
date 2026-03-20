# 源码读取与解析

## Purpose

负责扫描目标项目的目录结构，根据编程语言扩展名和忽略规则识别有效的源代码文件，加载文件内容并封装为统一的数据结构，为后续的架构分析和注释生成模块提供原始数据输入。

---
## Requirements
### Requirement: 递归目录扫描

系统 SHALL 使用自定义递归函数扫描用户指定的目标项目根目录，在每层目录中优先按文件名字典序处理源码文件，然后按目录名字典序递归进入子目录，确保处理顺序确定且可预测。

#### Scenario: 正常扫描完整项目

- **WHEN** 用户通过命令行指定一个有效的项目根目录路径
- **THEN** 系统使用自定义递归函数遍历该目录
- **AND** 在每层目录中，先按文件名字典序处理当前目录的源码文件
- **AND** 再按目录名字典序递归进入子目录处理
- **AND** 返回完整的 SourceFile 对象列表，顺序为深度优先、文件优先、字典序

#### Scenario: 指定路径不存在

- **WHEN** 用户指定的路径不存在或无法访问
- **THEN** 系统抛出 ValueError 异常，提示路径无效

#### Scenario: 忽略隐藏目录

- **WHEN** 扫描过程中遇到以 `.` 开头的目录
- **THEN** 自动跳过该目录及其所有子目录

### Requirement: 编程语言识别

系统 SHALL 根据文件扩展名自动识别源码文件的编程语言，支持 20+ 种编程语言。

#### Scenario: 识别 Java 项目文件

- **WHEN** 扫描到 `.java` 扩展名的文件
- **THEN** 将其标记为 Java 语言源码

#### Scenario: 识别多语言项目

- **WHEN** 项目包含多种编程语言的源码文件
- **THEN** 每个文件根据扩展名被正确标记为对应的语言类型

#### Scenario: 跳过不支持的文件类型

- **WHEN** 扫描到不在语言映射表中的文件（如 `.txt`、`.md`、`.json`）
- **THEN** 自动跳过该文件

---

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

### Requirement: 文件内容加载

系统 SHALL 读取源码文件内容，使用 UTF-8 编码，保持原始格式不变。

#### Scenario: 正确加载 UTF-8 编码文件

- **WHEN** 读取 UTF-8 编码的源码文件
- **THEN** 文件内容完整无损，中文字符不乱码

#### Scenario: 处理编码异常

- **WHEN** 文件包含非 UTF-8 字符
- **THEN** 使用 replace 模式替换无法解码的字符，不中断扫描流程

---

### Requirement: 项目扫描摘要

系统 SHALL 在扫描完成后生成项目摘要，包含文件总数、大小统计和语言分布。

#### Scenario: 输出扫描统计

- **WHEN** 扫描完成
- **THEN** 输出项目路径、源码文件总数、总大小和各语言文件数量

