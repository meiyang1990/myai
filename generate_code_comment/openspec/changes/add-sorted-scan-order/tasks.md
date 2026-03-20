## 1. 修改扫描逻辑

- [x] 1.1 在 `source_reader.py` 中新增 `_scan_directory` 递归方法，实现文件优先+字典序遍历
- [x] 1.2 修改 `scan()` 方法，调用 `_scan_directory` 替代 `os.walk`
- [x] 1.3 移除最终的 `source_files.sort()` 排序（递归已保证顺序）

## 2. 验证

- [x] 2.1 确认处理顺序为：每层目录先按字典序处理文件，再按字典序递归子目录
