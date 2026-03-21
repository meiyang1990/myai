# -*- coding: utf-8 -*-
"""
项目配置模块 - 管理所有配置参数和环境变量

本模块负责：
1. 从操作系统环境变量中加载火山引擎 API 配置（大模型相关参数）
2. 定义文件扫描的过滤规则（忽略目录、文件扩展名映射等）
3. 提供全局配置常量供其他模块使用

大模型相关参数需在操作系统环境变量中预先设置，例如：
    export VOLCENGINE_API_KEY="your-api-key"
    export VOLCENGINE_API_BASE="https://ark.cn-beijing.volces.com/api/coding/v3"
    export VOLCENGINE_MODEL_ENDPOINT="your-endpoint-id"
    export TEMPERATURE="0.3"
    export MAX_TOKENS="4096"
"""

import os
import logging


# ========== 火山引擎 API 配置（从操作系统环境变量获取） ==========

# 火山引擎 API Key，用于身份认证（必须通过环境变量设置）
VOLCENGINE_API_KEY = os.environ.get("VOLCENGINE_API_KEY", "")

# 火山引擎 API 基础地址（兼容 OpenAI 协议）
VOLCENGINE_API_BASE = os.environ.get(
    "VOLCENGINE_API_BASE",
    "https://ark.cn-beijing.volces.com/api/coding/v3"
)

# 火山引擎推理接入点 ID（模型 endpoint，必须通过环境变量设置）
VOLCENGINE_MODEL_ENDPOINT = os.environ.get("VOLCENGINE_MODEL_ENDPOINT", "")

# 大模型生成参数（通过环境变量设置，有默认值）
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.3"))
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "4096"))


# ========== 文件扫描配置 ==========

# 支持的源码文件扩展名 -> 编程语言映射
LANGUAGE_EXTENSIONS = {
    ".java": "Java",
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".jsx": "JavaScript",
    ".go": "Go",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".c": "C",
    ".cpp": "C++",
    ".cc": "C++",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".cs": "C#",
    ".rb": "Ruby",
    ".rs": "Rust",
    ".swift": "Swift",
    ".scala": "Scala",
    ".php": "PHP",
    ".vue": "Vue",
    ".sh": "Shell",
    ".bash": "Shell",
}

# 默认需要忽略的目录（不扫描）
DEFAULT_IGNORE_DIRS = {
    "node_modules",
    "target",
    "build",
    "dist",
    "out",
    ".git",
    ".svn",
    ".hg",
    ".idea",
    ".vscode",
    ".codebuddy",
    "__pycache__",
    ".gradle",
    ".mvn",
    "vendor",
    "venv",
    ".venv",
    "env",
    ".env",
    ".tox",
    "eggs",
    "*.egg-info",
    ".mypy_cache",
    ".pytest_cache",
    "coverage",
    ".nyc_output",
    "bin",
    "obj",
    # 测试目录（Task 2.2）
    "test",
    "tests",
    "__tests__",
    "spec",
    "specs",
}

# 单元测试文件命名匹配模式列表（Task 2.1）
# 使用 fnmatch 风格的通配符模式，覆盖主流语言的测试文件命名规范
TEST_FILE_PATTERNS = [
    # Java
    "Test*.java",
    "*Test.java",
    "*Tests.java",
    "*TestCase.java",
    "*Spec.java",
    # Python
    "test_*.py",
    "*_test.py",
    # Go
    "*_test.go",
    # JavaScript / TypeScript
    "*.test.js",
    "*.test.ts",
    "*.test.tsx",
    "*.test.jsx",
    "*.spec.js",
    "*.spec.ts",
    "*.spec.tsx",
    "*.spec.jsx",
    # Kotlin
    "*Test.kt",
    "*Tests.kt",
    "*Spec.kt",
    # C# (.NET)
    "*Test.cs",
    "*Tests.cs",
    # Ruby
    "*_spec.rb",
    "test_*.rb",
    # Rust
    "*_test.rs",
    # Swift
    "*Tests.swift",
    "*Test.swift",
    # Scala
    "*Spec.scala",
    "*Test.scala",
    # PHP
    "*Test.php",
    "*_test.php",
]

# 默认需要忽略的文件模式
DEFAULT_IGNORE_FILES = {
    ".DS_Store",
    "Thumbs.db",
    ".gitignore",
    ".gitattributes",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "Cargo.lock",
    "go.sum",
    "poetry.lock",
    "Pipfile.lock",
}

# 文件大小上限（字节），超过此大小的文件跳过（默认 1MB）
MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", str(1024 * 1024)))


# ========== 项目上下文分析配置 ==========

# 智能采样文件数量上限（默认 20 个）
CONTEXT_SAMPLE_FILE_LIMIT = int(os.environ.get("CONTEXT_SAMPLE_FILE_LIMIT", "20"))

# 采样文件的总字符预算（默认约 8000 字符 ≈ 4000 token）
CONTEXT_CHAR_BUDGET = int(os.environ.get("CONTEXT_CHAR_BUDGET", "8000"))

# 单个采样文件截取的最大行数（默认 200 行）
CONTEXT_FILE_MAX_LINES = int(os.environ.get("CONTEXT_FILE_MAX_LINES", "200"))

# 项目概要缓存有效期（天），超过后提示用户刷新（默认 7 天）
CONTEXT_CACHE_EXPIRE_DAYS = float(os.environ.get("CONTEXT_CACHE_EXPIRE_DAYS", "7"))

# 项目上下文缓存目录名称
CONTEXT_CACHE_DIR_NAME = os.environ.get("CONTEXT_CACHE_DIR_NAME", ".code_context")


# ========== 长期记忆存储配置 ==========

# 长期记忆存储目录（默认在用户 HOME 目录下）
MEMORY_STORE_DIR = os.path.expanduser(
    os.environ.get("MEMORY_STORE_DIR", "~/.code_comment_memory")
)

# 长期记忆存储文件名
MEMORY_STORE_FILE = os.environ.get("MEMORY_STORE_FILE", "project_summaries.json")


# ========== 已注释标记配置 ==========

# 标记文本常量：当文件中包含此文本的单行注释时，视为"已处理"
COMMENTED_MARKER_TEXT = "这个文件已经全部加上中文注释"

# 各编程语言的单行注释前缀映射（用于生成和检测标记行）
_SINGLE_LINE_COMMENT_PREFIX = {
    "Java": "//",
    "Python": "#",
    "JavaScript": "//",
    "TypeScript": "//",
    "Go": "//",
    "Kotlin": "//",
    "C": "//",
    "C++": "//",
    "C/C++ Header": "//",
    "C++ Header": "//",
    "C#": "//",
    "Ruby": "#",
    "Rust": "//",
    "Swift": "//",
    "Scala": "//",
    "PHP": "//",
    "Vue": "//",
    "Shell": "#",
}


def get_comment_marker_line(language: str) -> str:
    """
    根据编程语言返回完整的已注释标记行

    例如:
        Java  -> "// 这个文件已经全部加上中文注释"
        Python -> "# 这个文件已经全部加上中文注释"

    Args:
        language: 编程语言名称（与 LANGUAGE_EXTENSIONS 的值一致）

    Returns:
        完整的标记注释行字符串
    """
    prefix = _SINGLE_LINE_COMMENT_PREFIX.get(language, "//")
    return f"{prefix} {COMMENTED_MARKER_TEXT}"


def has_commented_marker(content: str, language: str) -> bool:
    """
    检测源码内容中是否存在已注释标记行

    逐行扫描文件内容，检查是否存在一行去除首尾空白后以该语言的单行注释符开头，
    且包含 COMMENTED_MARKER_TEXT 文本。

    Args:
        content: 源码文件的完整文本内容
        language: 编程语言名称

    Returns:
        如果检测到标记行返回 True，否则返回 False
    """
    prefix = _SINGLE_LINE_COMMENT_PREFIX.get(language, "//")
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix) and COMMENTED_MARKER_TEXT in stripped:
            return True
    return False


# ========== 注释风格配置 ==========

# 各编程语言的注释格式模板
COMMENT_STYLES = {
    "Java": {
        "file_comment_start": "/**",
        "file_comment_line": " * ",
        "file_comment_end": " */",
        "inline_comment": "// ",
    },
    "Python": {
        "file_comment_start": '"""',
        "file_comment_line": "",
        "file_comment_end": '"""',
        "inline_comment": "# ",
    },
    "JavaScript": {
        "file_comment_start": "/**",
        "file_comment_line": " * ",
        "file_comment_end": " */",
        "inline_comment": "// ",
    },
    "TypeScript": {
        "file_comment_start": "/**",
        "file_comment_line": " * ",
        "file_comment_end": " */",
        "inline_comment": "// ",
    },
    "Go": {
        "file_comment_start": "//",
        "file_comment_line": "// ",
        "file_comment_end": "",
        "inline_comment": "// ",
    },
    "Kotlin": {
        "file_comment_start": "/**",
        "file_comment_line": " * ",
        "file_comment_end": " */",
        "inline_comment": "// ",
    },
    "C": {
        "file_comment_start": "/**",
        "file_comment_line": " * ",
        "file_comment_end": " */",
        "inline_comment": "// ",
    },
    "C++": {
        "file_comment_start": "/**",
        "file_comment_line": " * ",
        "file_comment_end": " */",
        "inline_comment": "// ",
    },
    "C/C++ Header": {
        "file_comment_start": "/**",
        "file_comment_line": " * ",
        "file_comment_end": " */",
        "inline_comment": "// ",
    },
    "C++ Header": {
        "file_comment_start": "/**",
        "file_comment_line": " * ",
        "file_comment_end": " */",
        "inline_comment": "// ",
    },
    "C#": {
        "file_comment_start": "/**",
        "file_comment_line": " * ",
        "file_comment_end": " */",
        "inline_comment": "// ",
    },
    "Ruby": {
        "file_comment_start": "=begin",
        "file_comment_line": "",
        "file_comment_end": "=end",
        "inline_comment": "# ",
    },
    "Rust": {
        "file_comment_start": "//!",
        "file_comment_line": "//! ",
        "file_comment_end": "",
        "inline_comment": "// ",
    },
    "Swift": {
        "file_comment_start": "/**",
        "file_comment_line": " * ",
        "file_comment_end": " */",
        "inline_comment": "// ",
    },
    "Scala": {
        "file_comment_start": "/**",
        "file_comment_line": " * ",
        "file_comment_end": " */",
        "inline_comment": "// ",
    },
    "PHP": {
        "file_comment_start": "/**",
        "file_comment_line": " * ",
        "file_comment_end": " */",
        "inline_comment": "// ",
    },
    "Vue": {
        "file_comment_start": "<!--",
        "file_comment_line": "  ",
        "file_comment_end": "-->",
        "inline_comment": "// ",
    },
    "Shell": {
        "file_comment_start": "#",
        "file_comment_line": "# ",
        "file_comment_end": "",
        "inline_comment": "# ",
    },
}


# ========== 日志配置 ==========

# 日志文件路径（默认工作目录下的 generate_code_comment.log）
LOG_FILE = os.environ.get("LOG_FILE", "generate_code_comment.log")

# 日志级别（默认 INFO，可通过环境变量 LOG_LEVEL 调整）
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()


def setup_logging() -> None:
    """
    配置全局日志，将所有日志输出到文件，不输出到终端

    日志格式：时间戳 [模块名] 级别: 消息
    日志级别通过环境变量 LOG_LEVEL 控制，默认 INFO
    日志文件通过环境变量 LOG_FILE 控制，默认 generate_code_comment.log
    """
    level = getattr(logging, LOG_LEVEL, logging.INFO)

    # 创建文件 handler，写入日志文件
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    # 配置根 logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    # 移除默认的 StreamHandler（如果有）
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)


def validate_config() -> tuple[bool, list[str]]:
    """
    校验必填配置项是否已正确设置

    Returns:
        tuple: (是否通过校验, 错误信息列表)
    """
    errors: list[str] = []

    if not VOLCENGINE_API_KEY:
        errors.append(
            "未设置 VOLCENGINE_API_KEY，请在操作系统环境变量中配置，例如: export VOLCENGINE_API_KEY=\"your-api-key\""
        )

    if not VOLCENGINE_MODEL_ENDPOINT:
        errors.append(
            "未设置 VOLCENGINE_MODEL_ENDPOINT，请在操作系统环境变量中配置推理接入点 ID，"
            "例如: export VOLCENGINE_MODEL_ENDPOINT=\"ep-xxx\""
        )

    if not VOLCENGINE_API_BASE:
        errors.append(
            "未设置 VOLCENGINE_API_BASE，请在操作系统环境变量中配置 API 地址，"
            "例如: export VOLCENGINE_API_BASE=\"https://ark.cn-beijing.volces.com/api/coding/v3\""
        )

    is_valid = len(errors) == 0
    return is_valid, errors
