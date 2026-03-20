# -*- coding: utf-8 -*-
"""
项目配置模块 - 管理所有配置参数和环境变量

本模块负责：
1. 从 .env 文件或环境变量中加载火山引擎 API 配置
2. 定义文件扫描的过滤规则（忽略目录、文件扩展名映射等）
3. 提供全局配置常量供其他模块使用
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()


# ========== 火山引擎 API 配置 ==========

# 火山引擎 API Key，用于身份认证
VOLCENGINE_API_KEY = os.getenv("VOLCENGINE_API_KEY", "")

# 火山引擎 API 基础地址（兼容 OpenAI 协议）
VOLCENGINE_API_BASE = os.getenv(
    "VOLCENGINE_API_BASE",
    "https://ark.cn-beijing.volces.com/api/coding/v3"
)

# 火山引擎推理接入点 ID（模型 endpoint）
VOLCENGINE_MODEL_ENDPOINT = os.getenv("VOLCENGINE_MODEL_ENDPOINT", "")

# 大模型生成参数
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))


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
}

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
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(1024 * 1024)))


# ========== 项目上下文分析配置 ==========

# 智能采样文件数量上限（默认 20 个）
CONTEXT_SAMPLE_FILE_LIMIT = int(os.getenv("CONTEXT_SAMPLE_FILE_LIMIT", "20"))

# 采样文件的总字符预算（默认约 8000 字符 ≈ 4000 token）
CONTEXT_CHAR_BUDGET = int(os.getenv("CONTEXT_CHAR_BUDGET", "8000"))

# 单个采样文件截取的最大行数（默认 200 行）
CONTEXT_FILE_MAX_LINES = int(os.getenv("CONTEXT_FILE_MAX_LINES", "200"))

# 项目概要缓存有效期（天），超过后提示用户刷新（默认 7 天）
CONTEXT_CACHE_EXPIRE_DAYS = float(os.getenv("CONTEXT_CACHE_EXPIRE_DAYS", "7"))

# 项目上下文缓存目录名称
CONTEXT_CACHE_DIR_NAME = os.getenv("CONTEXT_CACHE_DIR_NAME", ".code_context")


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


def validate_config():
    """
    校验必填配置项是否已正确设置

    Returns:
        tuple: (是否通过校验, 错误信息列表)
    """
    errors = []

    if not VOLCENGINE_API_KEY:
        errors.append(
            "未设置 VOLCENGINE_API_KEY，请在 .env 文件或环境变量中配置"
        )

    if not VOLCENGINE_MODEL_ENDPOINT:
        errors.append(
            "未设置 VOLCENGINE_MODEL_ENDPOINT，请在 .env 文件或环境变量中配置推理接入点 ID"
        )

    if not VOLCENGINE_API_BASE:
        errors.append(
            "未设置 VOLCENGINE_API_BASE，请在 .env 文件或环境变量中配置 API 地址"
        )

    is_valid = len(errors) == 0
    return is_valid, errors
