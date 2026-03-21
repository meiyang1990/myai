# Change: 明确 --project_root_dir 仅用于检索项目概要，注释生成以 --source_path 为核心

## Why

当前 `generate_comment` 子命令中，`--project_root_dir` 参数承担了过多职责：

1. **作为项目上下文/概要信息的检索基准**（查长期记忆、分析项目上下文）
2. **作为 `SourceReader` 的初始化根目录**（加载 `.gitignore`、过滤规则的基准）
3. **作为 `CommentWriter` 输出路径的基准**（默认输出到 `project_root_commented`）
4. **作为 `ProgressTracker` 进度缓存的存放目录**（缓存存放在 `project_root/.code_context/`）

用户的意图是：`--project_root_dir` **仅仅**用来告诉系统项目根目录在哪，以便检索项目概要信息。**实际的注释生成处理对象是 `--source_path`。**

这带来的问题：
- `SourceReader` 用 `project_root_dir` 加载 `.gitignore`，当 `--source_path` 的实际根目录与 `--project_root_dir` 不同时，`.gitignore` 规则可能不适用
- `CommentWriter` 默认输出目录为 `project_root_dir_commented`，而用户期望输出应围绕 `--source_path` 组织
- 概念不清晰：`project_root_dir` 既是"元信息查找路径"又是"处理基准"，职责混乱

## What Changes

- **`--project_root_dir` 职责精简**：仅用于检索项目概要（长期记忆加载、项目上下文分析），以及作为 `.gitignore` 规则的加载路径
- **`--source_path` 成为注释生成的核心处理路径**：`SourceReader` 仍基于 `project_root_dir` 初始化（保留 `.gitignore` 加载），但扫描和处理只针对 `--source_path`
- **`CommentWriter` 输出路径调整**：默认输出目录改为以 `source_path` 为基准（`source_path_commented`），而非 `project_root_dir_commented`
- **`ProgressTracker` 缓存路径调整**：进度缓存存放在 `project_root_dir/.code_context/` 下（保持不变，因为进度应该以项目为单位管理）
- **`do_generate()` 签名和逻辑调整**：明确各参数用途，`project_path` 用于概要检索和 `.gitignore`，`target_path` 用于实际处理

## Impact

- Affected specs: cli-commands
- Affected code: `main.py`（`do_generate()`、`_handle_generate_comment()`）、`comment_writer.py`（`CommentWriter.__init__()`）
- **BREAKING CHANGE**：默认输出目录从 `project_root_dir_commented` 变更为 `source_path_commented`（当 `--source_path` 为目录时）或 `source_file_commented/` （当 `--source_path` 为单文件时）
