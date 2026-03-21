## MODIFIED Requirements

### Requirement: 递归目录扫描

源码读取器 SHALL 采用自定义递归遍历目标项目目录：每层目录先按文件名字典序处理源码文件，再按目录名字典序递归进入子目录，确保处理顺序确定且可预测。扫描过程支持传入进度跟踪器以跳过已完成的目录。

代码实现 SHALL 使用 Python 3.11.9 现代语法：
- 类定义使用 `class SourceReader:` 而非 `class SourceReader(object):`
- 字符串格式化使用 f-string 而非 `%` 操作符
- 文件 I/O 使用内置 `open()` 而非 `io.open()`
- 异常处理使用 `except OSError` 而非 `except (IOError, OSError)`
- 所有公开方法添加类型注解

#### Scenario: 扫描项目并使用现代语法

- **WHEN** 调用 `SourceReader.scan()` 扫描目标项目目录
- **THEN** 返回按文件优先+字典序排列的 `SourceFile` 列表
- **AND** 代码中不包含 `io.open()`、`class Foo(object)`、`%` 字符串格式化等旧式写法

### Requirement: 文件内容加载

源码读取器 SHALL 使用 Python 3 内置 `open()` 函数以 UTF-8 编码读取文件内容，遇到编码异常使用 `errors="replace"` 模式处理。

#### Scenario: 使用内置 open 读取文件

- **WHEN** 读取源码文件内容
- **THEN** 使用 `open(file_path, "r", encoding="utf-8", errors="replace")` 而非 `io.open()`
- **AND** 正确返回文件内容字符串

### Requirement: SourceFile 数据类

`SourceFile` SHALL 使用 `@dataclass` 装饰器定义，自动生成 `__init__` 和 `__repr__` 方法，包含 `abs_path`、`rel_path`、`language`、`content`、`size` 五个字段。

#### Scenario: 使用 dataclass 定义 SourceFile

- **WHEN** 创建 SourceFile 实例
- **THEN** 使用 `@dataclass` 自动生成的构造函数
- **AND** `repr()` 输出包含类名和字段值

### Requirement: 项目扫描摘要

扫描摘要生成 SHALL 使用 `collections.Counter` 进行语言统计计数，替代手动字典累加模式。

#### Scenario: 使用 Counter 统计语言分布

- **WHEN** 调用 `get_project_summary()` 生成摘要
- **THEN** 使用 `Counter` 统计各语言文件数量
- **AND** 输出结果与重构前一致
