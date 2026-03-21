## ADDED Requirements

### Requirement: generate_comment 支持 --source_path 文件或目录路径（必填）

`generate_comment` 子命令 SHALL 强制要求通过 `--source_path` 参数指定要处理的源码路径。该参数为必填命名参数（required=True）。该路径可以是一个目录（递归处理其下所有源码文件和子目录），也可以是一个单独的源码文件（直接对该文件生成注释）。

#### Scenario: --source_path 传入目录路径

- **WHEN** 用户执行 `python main.py generate_comment --project_root_dir /project --source_path /project/src/module`
- **THEN** 系统递归扫描 `/project/src/module` 目录下的所有源码文件和子目录，生成中文注释

#### Scenario: --source_path 传入单文件路径

- **WHEN** 用户执行 `python main.py generate_comment --project_root_dir /project --source_path /project/src/Main.java`
- **THEN** 系统仅对 `/project/src/Main.java` 这一个文件生成中文注释

#### Scenario: 未提供 --source_path 参数时报错

- **WHEN** 用户执行 `python main.py generate_comment --project_root_dir /project`（不提供 --source_path）
- **THEN** 系统输出错误信息提示 `--source_path` 参数为必填项并退出

#### Scenario: --source_path 路径不存在时报错

- **WHEN** 用户提供的 `--source_path` 路径不存在
- **THEN** 系统输出错误信息提示路径不存在并退出

#### Scenario: --source_path 为不可识别的文件类型

- **WHEN** 用户传入的单文件路径扩展名不在已支持语言列表中
- **THEN** 系统提示该文件类型不支持，不生成注释

## MODIFIED Requirements

### Requirement: Unified Project Root Dir Parameter

所有子命令 SHALL 强制要求传入 `--project_root_dir` 参数，指定项目源码根目录路径。该参数为必填命名参数（required=True），不再使用位置参数。

`generate_comment` 子命令额外强制要求 `--source_path` 参数，用于指定要处理的具体路径（可以是文件或目录）。

#### Scenario: generate_comment 子命令同时使用 --project_root_dir 和 --source_path

- **WHEN** 用户执行 `python main.py generate_comment --project_root_dir /path/to/project --source_path /path/to/project/src`
- **THEN** 系统使用 `/path/to/project` 作为项目根目录（用于上下文分析、记忆等），使用 `/path/to/project/src` 作为实际处理路径

#### Scenario: 缺少 --project_root_dir 参数时报错

- **WHEN** 用户执行任意子命令但未提供 `--project_root_dir` 参数
- **THEN** 系统输出错误信息提示该参数为必填项并退出

#### Scenario: 缺少 --source_path 参数时报错

- **WHEN** 用户执行 `generate_comment` 子命令但未提供 `--source_path` 参数
- **THEN** 系统输出错误信息提示该参数为必填项并退出
