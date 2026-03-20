# Change: 目录扫描改为文件优先+字典序递归

## Why

当前 `SourceReader.scan()` 使用 `os.walk` 遍历目录，其遍历顺序依赖操作系统和文件系统实现，不保证稳定性。且 `os.walk` 对文件和子目录的处理是混合的——先列出当前目录所有文件，再进入子目录，但子目录的顺序不确定。

需要改为：每个目录下优先按字典序处理源码文件，然后按字典序递归进入子目录处理，确保处理顺序确定、可预测。

## What Changes

- **MODIFIED** source-code-reader 的「递归目录扫描」requirement：将 `os.walk` 替换为自定义递归函数，每层目录先按文件名字典序处理源码文件，再按目录名字典序递归子目录

## Impact

- Affected specs: `source-code-reader`
- Affected code:
  - `source_reader.py` — 重写 `scan()` 方法，替换 `os.walk` 为自定义递归
