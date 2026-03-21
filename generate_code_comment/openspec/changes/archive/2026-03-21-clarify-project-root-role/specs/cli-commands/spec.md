## MODIFIED Requirements

### Requirement: Unified Project Root Dir Parameter

所有子命令 SHALL 强制要求传入 `--project_root_dir` 参数，指定项目源码根目录路径。该参数为必填命名参数（required=True），不再使用位置参数。

对于 `generate_comment` 子命令，`--project_root_dir` SHALL **仅用于**以下用途：
1. 检索项目概要信息（从长期记忆中加载或生成项目上下文概要）
2. 作为 `.gitignore` 规则的加载路径
3. 作为进度跟踪缓存的存放基准目录

实际的注释生成处理对象由 `--source_path` 指定。

#### Scenario: generate_comment 子命令使用 --project_root_dir 检索概要

- **WHEN** 用户执行 `python main.py generate_comment --project_root_dir /path/to/project --source_path /path/to/project/src`
- **THEN** 系统使用 `/path/to/project` 检索项目概要信息和加载 `.gitignore` 规则
- **AND** 系统使用 `/path/to/project/src` 作为实际扫描和注释生成的目标路径

#### Scenario: generate_comment 默认输出目录基于 source_path

- **WHEN** 用户执行 `python main.py generate_comment --project_root_dir /path/to/project --source_path /path/to/project/src` 且未指定 `-o`
- **THEN** 默认输出目录为 `/path/to/project/src_commented`（基于 `--source_path` 而非 `--project_root_dir`）

#### Scenario: generate_comment 单文件模式默认输出

- **WHEN** 用户执行 `python main.py generate_comment --project_root_dir /path/to/project --source_path /path/to/project/src/Main.java` 且未指定 `-o`
- **THEN** 默认输出目录为 `/path/to/project/src/Main.java_commented/`，输出文件为 `/path/to/project/src/Main.java_commented/Main.java`

#### Scenario: generate_comment 覆盖模式写回 source_path

- **WHEN** 用户执行 `python main.py generate_comment --project_root_dir /path/to/project --source_path /path/to/project/src --overwrite`
- **THEN** 带注释的代码直接写回 `/path/to/project/src` 下的原始文件

#### Scenario: generate_summary 子命令使用 --project_root_dir

- **WHEN** 用户执行 `python main.py generate_summary --project_root_dir /path/to/project --project-info "..."`
- **THEN** 系统使用 `/path/to/project` 作为项目源码根目录执行概要生成

#### Scenario: test_api 子命令使用 --project_root_dir

- **WHEN** 用户执行 `python main.py test_api --project_root_dir /path/to/project`
- **THEN** 系统接受项目路径参数并完成 API 连接测试

#### Scenario: scan_only 子命令使用 --project_root_dir

- **WHEN** 用户执行 `python main.py scan_only --project_root_dir /path/to/project`
- **THEN** 系统使用 `/path/to/project` 作为扫描根目录

#### Scenario: context_only 子命令使用 --project_root_dir

- **WHEN** 用户执行 `python main.py context_only --project_root_dir /path/to/project`
- **THEN** 系统使用 `/path/to/project` 生成项目上下文概要

#### Scenario: list_memories 子命令使用 --project_root_dir

- **WHEN** 用户执行 `python main.py list_memories --project_root_dir /path/to/project`
- **THEN** 系统接受项目路径参数并列出所有已记忆的项目概要

#### Scenario: remove_memory 子命令使用 --project_root_dir

- **WHEN** 用户执行 `python main.py remove_memory --project_root_dir /path/to/project`
- **THEN** 系统使用 `/path/to/project` 定位并删除对应的长期记忆

#### Scenario: 缺少 --project_root_dir 参数时报错

- **WHEN** 用户执行任意子命令但未提供 `--project_root_dir` 参数
- **THEN** 系统输出错误信息提示该参数为必填项并退出

#### Scenario: generate_comment 缺少 --source_path 参数时报错

- **WHEN** 用户执行 `python main.py generate_comment --project_root_dir /path/to/project` 但未提供 `--source_path`
- **THEN** 系统输出错误信息提示 `--source_path` 为必填项并退出
