## 1. Implementation

- [x] 1.1 在 `config.py` 中新增常量 `COMMENTED_MARKER_TEXT = "这个文件已经全部加上中文注释"`，供检测和写入统一使用
- [x] 1.2 在 `config.py` 中新增辅助函数 `get_comment_marker_line(language: str) -> str`，根据语言返回完整的标记注释行（如 `// 这个文件已经全部加上中文注释`）
- [x] 1.3 在 `main.py` 的 `do_generate()` 主循环中，在大模型调用之前新增标记检测逻辑：调用 `has_commented_marker(content, language)` 检查文件内容，检测到标记时跳过并标记进度
- [x] 1.4 在 `config.py` 中实现 `has_commented_marker(content: str, language: str) -> bool` 函数，逐行扫描检测是否存在标记注释行
- [x] 1.5 在 `comment_writer.py` 的 `write_file()` 方法中，写入带注释代码前在内容最开头插入标记注释行（根据语言格式），如果首行已包含标记文本则不重复插入
