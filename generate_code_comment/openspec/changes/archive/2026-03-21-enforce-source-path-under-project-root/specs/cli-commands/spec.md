## ADDED Requirements

### Requirement: Source Path Under Project Root Validation

`generate_comment` 子命令 SHALL 在执行前校验 `--source_path` 的绝对路径是否为 `--project_root_dir` 绝对路径的子路径或与其相同。校验不通过时，输出错误信息并以非零状态码退出。

#### Scenario: source_path 是 project_root_dir 的子目录

- **WHEN** 用户执行 `python main.py generate_comment --project_root_dir /path/to/project --source_path /path/to/project/src`
- **THEN** 校验通过，正常执行注释生成流程

#### Scenario: source_path 与 project_root_dir 相同

- **WHEN** 用户执行 `python main.py generate_comment --project_root_dir /path/to/project --source_path /path/to/project`
- **THEN** 校验通过，正常执行注释生成流程

#### Scenario: source_path 不在 project_root_dir 下

- **WHEN** 用户执行 `python main.py generate_comment --project_root_dir /path/to/project --source_path /other/path/src`
- **THEN** 系统输出错误信息说明 `--source_path` 必须是 `--project_root_dir` 的子路径或同一路径
- **AND** 以非零状态码退出

#### Scenario: source_path 包含符号链接或相对路径

- **WHEN** `--source_path` 或 `--project_root_dir` 包含符号链接、`.` 或 `..` 等相对路径片段
- **THEN** 系统先将两个路径都解析为绝对真实路径（resolve symlinks）后再进行包含关系校验
