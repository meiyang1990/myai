# -*- coding: utf-8 -*-
"""
源码读取模块 - 递归扫描项目目录，识别并加载源码文件

本模块负责：
1. 递归扫描目标项目的源码目录
2. 根据文件扩展名识别编程语言
3. 过滤非源码文件（构建产物、依赖目录等）
4. 支持 .gitignore 规则
5. 读取源码文件内容并返回结构化数据
"""

import os
import io

from config import (
    LANGUAGE_EXTENSIONS,
    DEFAULT_IGNORE_DIRS,
    DEFAULT_IGNORE_FILES,
    MAX_FILE_SIZE,
)

# 尝试导入 pathspec 用于解析 .gitignore，如果不可用则降级处理
try:
    import pathspec
    HAS_PATHSPEC = True
except ImportError:
    HAS_PATHSPEC = False


class SourceFile(object):
    """
    源码文件数据结构

    封装单个源码文件的基本信息和内容，包括：
    - 文件路径（绝对路径和相对路径）
    - 编程语言类型
    - 文件内容
    - 文件大小
    """

    def __init__(self, abs_path, rel_path, language, content, size):
        """
        初始化源码文件对象

        Args:
            abs_path (str): 文件的绝对路径
            rel_path (str): 相对于项目根目录的相对路径
            language (str): 编程语言类型（如 "Java", "Python" 等）
            content (str): 文件的完整文本内容
            size (int): 文件大小（字节）
        """
        self.abs_path = abs_path
        self.rel_path = rel_path
        self.language = language
        self.content = content
        self.size = size

    def __repr__(self):
        return "SourceFile(rel_path='%s', language='%s', size=%d)" % (
            self.rel_path, self.language, self.size
        )


class SourceReader(object):
    """
    源码读取器 - 扫描项目目录并加载源码文件

    核心功能：
    - 递归遍历目标项目目录
    - 自动识别编程语言
    - 过滤无关文件和目录
    - 支持 .gitignore 规则
    - 加载文件内容并返回 SourceFile 对象列表
    """

    def __init__(self, project_root, extra_ignore_dirs=None, extra_extensions=None):
        """
        初始化源码读取器

        Args:
            project_root (str): 目标项目的根目录路径
            extra_ignore_dirs (set or None): 额外需要忽略的目录名称集合
            extra_extensions (dict or None): 额外的文件扩展名->语言映射
        """
        # 转为绝对路径
        self.project_root = os.path.abspath(project_root)

        # 合并忽略目录
        self.ignore_dirs = set(DEFAULT_IGNORE_DIRS)
        if extra_ignore_dirs:
            self.ignore_dirs.update(extra_ignore_dirs)

        # 合并语言扩展名映射
        self.language_map = dict(LANGUAGE_EXTENSIONS)
        if extra_extensions:
            self.language_map.update(extra_extensions)

        # 加载 .gitignore 规则
        self.gitignore_spec = self._load_gitignore()

    def _load_gitignore(self):
        """
        加载项目根目录的 .gitignore 文件，解析为 pathspec 匹配规则

        Returns:
            pathspec.PathSpec or None: 解析后的 gitignore 规则，无则返回 None
        """
        if not HAS_PATHSPEC:
            return None

        gitignore_path = os.path.join(self.project_root, ".gitignore")
        if not os.path.isfile(gitignore_path):
            return None

        try:
            with io.open(gitignore_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            spec = pathspec.PathSpec.from_lines("gitwildmatch", lines)
            return spec
        except Exception:
            return None

    def _should_ignore_dir(self, dir_name, rel_dir_path):
        """
        判断目录是否应该被忽略

        Args:
            dir_name (str): 目录名称
            rel_dir_path (str): 目录相对于项目根的相对路径

        Returns:
            bool: 如果应该忽略返回 True
        """
        # 检查默认忽略列表
        if dir_name in self.ignore_dirs:
            return True

        # 以 . 开头的隐藏目录
        if dir_name.startswith("."):
            return True

        # 检查 .gitignore 规则
        if self.gitignore_spec is not None:
            # pathspec 需要以 / 结尾标识目录
            check_path = rel_dir_path + "/"
            if self.gitignore_spec.match_file(check_path):
                return True

        return False

    def _should_ignore_file(self, file_name, rel_file_path):
        """
        判断文件是否应该被忽略

        Args:
            file_name (str): 文件名称
            rel_file_path (str): 文件相对于项目根的相对路径

        Returns:
            bool: 如果应该忽略返回 True
        """
        # 检查默认忽略文件
        if file_name in DEFAULT_IGNORE_FILES:
            return True

        # 以 . 开头的隐藏文件
        if file_name.startswith("."):
            return True

        # 检查 .gitignore 规则
        if self.gitignore_spec is not None:
            if self.gitignore_spec.match_file(rel_file_path):
                return True

        return False

    def _detect_language(self, file_name):
        """
        根据文件扩展名检测编程语言

        Args:
            file_name (str): 文件名称

        Returns:
            str or None: 编程语言名称，未识别则返回 None
        """
        _, ext = os.path.splitext(file_name)
        ext = ext.lower()
        return self.language_map.get(ext, None)

    def _read_file_content(self, file_path):
        """
        读取文件内容，使用 UTF-8 编码，遇到编码错误则跳过

        Args:
            file_path (str): 文件的绝对路径

        Returns:
            str or None: 文件内容，读取失败返回 None
        """
        try:
            with io.open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            return content
        except (IOError, OSError):
            return None

    def scan(self):
        """
        扫描项目目录，返回所有可处理的源码文件列表

        Returns:
            list[SourceFile]: 源码文件对象列表

        Raises:
            ValueError: 当项目根目录不存在或不可访问时
        """
        if not os.path.isdir(self.project_root):
            raise ValueError(
                "项目路径不存在或不是目录: %s" % self.project_root
            )

        source_files = []

        for dirpath, dirnames, filenames in os.walk(self.project_root):
            # 计算当前目录相对于项目根目录的路径
            rel_dir = os.path.relpath(dirpath, self.project_root)
            if rel_dir == ".":
                rel_dir = ""

            # 过滤需要忽略的子目录（原地修改 dirnames 可阻止 os.walk 进入）
            filtered_dirs = []
            for d in dirnames:
                sub_rel = os.path.join(rel_dir, d) if rel_dir else d
                if not self._should_ignore_dir(d, sub_rel):
                    filtered_dirs.append(d)
            dirnames[:] = filtered_dirs

            # 处理当前目录中的文件
            for fname in filenames:
                rel_file = os.path.join(rel_dir, fname) if rel_dir else fname

                # 判断是否需要忽略
                if self._should_ignore_file(fname, rel_file):
                    continue

                # 检测编程语言
                language = self._detect_language(fname)
                if language is None:
                    continue

                abs_file = os.path.join(dirpath, fname)

                # 检查文件大小
                try:
                    file_size = os.path.getsize(abs_file)
                except OSError:
                    continue

                if file_size > MAX_FILE_SIZE:
                    print("[跳过] 文件过大(%d bytes): %s" % (file_size, rel_file))
                    continue

                if file_size == 0:
                    continue

                # 读取文件内容
                content = self._read_file_content(abs_file)
                if content is None:
                    print("[跳过] 无法读取: %s" % rel_file)
                    continue

                source_file = SourceFile(
                    abs_path=abs_file,
                    rel_path=rel_file,
                    language=language,
                    content=content,
                    size=file_size,
                )
                source_files.append(source_file)

        # 按相对路径排序，保证输出顺序稳定
        source_files.sort(key=lambda sf: sf.rel_path)

        print("[扫描完成] 共发现 %d 个源码文件" % len(source_files))
        return source_files

    def get_project_summary(self, source_files):
        """
        生成项目扫描摘要信息

        Args:
            source_files (list[SourceFile]): 源码文件列表

        Returns:
            str: 项目概况的文字描述
        """
        # 按语言统计文件数量
        lang_count = {}
        total_size = 0
        for sf in source_files:
            lang_count[sf.language] = lang_count.get(sf.language, 0) + 1
            total_size += sf.size

        lines = []
        lines.append("项目路径: %s" % self.project_root)
        lines.append("源码文件总数: %d" % len(source_files))
        lines.append("源码总大小: %.2f KB" % (total_size / 1024.0))
        lines.append("语言分布:")
        for lang, count in sorted(lang_count.items(), key=lambda x: -x[1]):
            lines.append("  - %s: %d 个文件" % (lang, count))

        return "\n".join(lines)
