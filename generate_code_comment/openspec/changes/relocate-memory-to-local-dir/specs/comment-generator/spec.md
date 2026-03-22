## ADDED Requirements

### Requirement: 本地化记忆目录结构

系统 SHALL 将项目概要的长期记忆统一存储在程序运行目录下的 `memory/` 目录中，针对每一个 `--project_root_dir` 在 `memory/` 下创建独立的子目录来隔离存储该项目的所有记忆数据。子目录命名采用「项目末尾目录名 + 短 hash 后缀」以保证可读性与唯一性。

#### Scenario: 按项目路径创建独立记忆子目录

- **WHEN** 系统接收到一个 `--project_root_dir` 参数
- **THEN** 在程序根目录的 `memory/` 目录下，根据项目路径生成一个可读且唯一的子目录名
- **AND** 子目录名格式为 `<项目末尾目录名>_<路径短hash>`，例如 `my-project_a3b1c9`
- **AND** 该项目的所有记忆文件均存放在此子目录中

#### Scenario: 列出所有项目记忆

- **WHEN** 用户执行 `list_memories` 子命令
- **THEN** 系统遍历 `memory/` 下所有项目子目录
- **AND** 从每个子目录中读取记忆数据
- **AND** 以时间戳降序排列返回结果

#### Scenario: 删除指定项目记忆

- **WHEN** 用户执行 `remove_memory` 子命令
- **THEN** 系统定位对应项目的记忆子目录
- **AND** 删除整个子目录及其中所有文件
