## ADDED Requirements

### Requirement: Unified Project Root Dir Parameter

所有子命令 SHALL 强制要求传入 `--project_root_dir` 参数，指定项目源码根目录路径。该参数为必填命名参数（required=True），不再使用位置参数。

#### Scenario: generate_comment 子命令使用 --project_root_dir

- **WHEN** 用户执行 `python main.py generate_comment --project_root_dir /path/to/project`
- **THEN** 系统使用 `/path/to/project` 作为项目源码根目录执行注释生成

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
