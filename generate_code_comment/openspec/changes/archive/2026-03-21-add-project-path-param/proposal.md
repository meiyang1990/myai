# Change: generate_comment 子命令新增 --source_path 必填参数，支持目录和单文件

## Why

当前 `generate_comment` 子命令只能接受项目根目录作为输入（通过 `--project_root_dir`），然后递归扫描整个目录树。但实际使用中，用户经常只需要为**某个子目录**或**单个文件**生成注释，而非整个项目。

当前的限制：

1. **粒度过粗**：想为单个文件生成注释，必须把整个项目目录传入，等待全项目扫描
2. **效率低下**：大型项目中只想处理某个子目录或某个文件时，扫描和处理范围过大
3. **灵活性不足**：无法针对指定路径（文件或子目录）做精准操作

## What Changes

- `generate_comment` 子命令**新增** `--source_path` **必填**参数：指定要处理的源码路径，可以是目录（递归处理其下所有文件和子目录）或单个文件
- `_validate_project_path()` 修改为同时支持文件和目录的校验
- `SourceReader` 新增单文件处理能力：当传入路径为文件时，直接将该文件作为唯一待处理文件返回
- `do_generate()` 适配：单文件场景下正确处理输出路径、进度跟踪等
- `CommentWriter` 适配：单文件场景下正确计算输出路径
- `ProgressTracker` 适配：单文件场景下正确初始化缓存目录

## Impact

- Affected specs: cli-commands
- Affected code: `main.py`（`parse_args()`、`_handle_generate_comment()`、`_validate_project_path()`、`do_generate()`）、`source_reader.py`（`SourceReader`）、`comment_writer.py`（`CommentWriter`）、`progress_tracker.py`（`ProgressTracker`）
- BREAKING CHANGE：`generate_comment` 子命令新增 `--source_path` 为**必填**参数，所有调用脚本需更新
