# -*- coding: utf-8 -*-
"""
项目上下文分析模块 - 智能分析项目架构并生成概要文档

本模块负责：
1. 智能采样项目中的关键源码文件（入口文件、配置文件、README、核心模块代表文件）
2. 生成项目目录树结构概览
3. 调用大模型分析项目架构，生成包含架构设计、技术栈、业务背景的概要文档
4. 将概要文档以 JSON 格式持久化存储到 .code_context/project_summary.json
5. 支持缓存加载与过期检测
"""

from __future__ import annotations

import os
import json
import logging
import time
import hashlib

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from config import (
    VOLCENGINE_API_KEY,
    VOLCENGINE_API_BASE,
    VOLCENGINE_MODEL_ENDPOINT,
    TEMPERATURE,
    MAX_TOKENS,
    DEFAULT_IGNORE_DIRS,
    LANGUAGE_EXTENSIONS,
    CONTEXT_SAMPLE_FILE_LIMIT,
    CONTEXT_CHAR_BUDGET,
    CONTEXT_FILE_MAX_LINES,
    CONTEXT_CACHE_EXPIRE_DAYS,
    CONTEXT_CACHE_DIR_NAME,
)


# ========== 采样优先级定义 ==========

# 入口文件名（不含扩展名的 stem），按优先级排序
ENTRY_FILE_STEMS = [
    "main", "app", "index", "application", "server", "startup", "program",
    "manage", "run", "boot", "launch",
]

# 配置/构建文件名，按优先级排序
CONFIG_FILE_NAMES = [
    "pom.xml", "build.gradle", "build.gradle.kts",
    "package.json", "tsconfig.json",
    "requirements.txt", "setup.py", "setup.cfg", "pyproject.toml", "Pipfile",
    "go.mod", "Cargo.toml",
    "Makefile", "CMakeLists.txt",
    "Gemfile", "composer.json",
    "build.sbt", "build.xml",
]

# README 文件名
README_FILE_NAMES = [
    "README.md", "README", "README.txt", "README.rst",
    "readme.md", "readme.txt",
]


# ========== Prompt 定义 ==========

CONTEXT_ANALYSIS_SYSTEM_PROMPT = """你是一位资深的软件架构师和技术分析师。你的任务是分析一个软件项目的源码，生成一份结构清晰、内容精练的项目概要文档。

## 输出要求

请生成一份 Markdown 格式的项目概要文档，包含以下章节（如果信息不足可跳过对应章节）：

### 1. 项目背景与目标
- 项目的核心功能和业务目标
- 面向的用户群体或使用场景

### 2. 技术栈与框架
- 主要编程语言和版本要求
- 使用的框架、库和中间件
- 构建工具和依赖管理方式

### 3. 架构设计与分层
- 项目的整体架构模式（如 MVC、微服务、Clean Architecture 等）
- 分层设计及各层职责

### 4. 核心模块职责
- 列出主要模块/包，说明每个模块的核心职责

### 5. 模块间关系与数据流
- 模块之间的调用关系和依赖关系
- 主要数据流向

### 6. 关键设计模式与惯例
- 项目中使用的设计模式
- 项目的编码惯例和约定

## 注意事项
- 概要文档应该简洁精练，总长度控制在 2000-4000 字
- 基于实际代码内容分析，不要臆测不存在的功能
- 使用简体中文"""


CONTEXT_ANALYSIS_HUMAN_PROMPT = """请分析以下项目的源码，生成项目概要文档。

## 项目目录结构

{directory_tree}

## 关键文件内容

{sampled_files_content}
"""


class ProjectContextAnalyzer:
    """
    项目上下文分析器

    负责对目标项目进行智能分析，生成架构设计和背景概要文档，
    并将结果持久化存储，供注释生成时作为上下文使用。

    工作流程：
    1. 检查是否存在有效缓存 → 如有则直接加载
    2. 智能采样项目关键文件
    3. 生成项目目录树
    4. 构建分析 Prompt，调用大模型生成概要
    5. 将结果 JSON 持久化到 .code_context/project_summary.json
    """

    def __init__(self, project_root: str) -> None:
        """
        初始化项目上下文分析器

        Args:
            project_root: 目标项目的根目录路径
        """
        self.project_root = os.path.abspath(project_root)
        self.cache_dir = os.path.join(self.project_root, CONTEXT_CACHE_DIR_NAME)
        self.cache_file = os.path.join(self.cache_dir, "project_summary.json")

        # 初始化大模型客户端
        self.llm = ChatOpenAI(
            model=VOLCENGINE_MODEL_ENDPOINT,
            openai_api_key=VOLCENGINE_API_KEY,
            openai_api_base=VOLCENGINE_API_BASE,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )

    def get_context(self, force_refresh: bool = False) -> str | None:
        """
        获取项目上下文概要

        如果存在有效缓存且未要求强制刷新，则直接加载缓存。
        否则重新分析项目并生成概要。

        Args:
            force_refresh: 是否强制重新生成（忽略缓存）

        Returns:
            项目概要文档（Markdown 格式），失败返回 None
        """
        # 尝试加载缓存
        if not force_refresh:
            cached = self._load_cache()
            if cached is not None:
                return cached

        # 重新分析项目
        logger.info("正在分析项目架构...")

        # 步骤 1：生成目录树
        directory_tree = self._generate_directory_tree()
        logger.info("目录树生成完毕")

        # 步骤 2：智能采样关键文件
        sampled_content = self._sample_key_files()
        if not sampled_content:
            logger.warning("未能采样到任何关键文件")
            return None

        logger.info(f"已采样 {sampled_content['file_count']} 个关键文件")

        # 步骤 3：调用大模型生成概要
        summary = self._call_llm_for_summary(directory_tree, sampled_content["content"])
        if not summary:
            logger.warning("大模型未能生成有效概要，将以无上下文模式继续")
            return None

        logger.info(f"项目概要生成成功（{len(summary)} 字）")

        # 步骤 4：持久化存储
        self._save_cache(summary)
        logger.info(f"概要已缓存到 {self.cache_file}")

        return summary

    def _load_cache(self) -> str | None:
        """
        尝试从文件加载已缓存的项目概要

        Returns:
            缓存的概要文档，无有效缓存返回 None
        """
        if not os.path.isfile(self.cache_file):
            return None

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 校验缓存结构
            if "summary" not in data or "timestamp" not in data:
                logger.warning("缓存文件格式无效，将重新生成")
                return None

            # 校验项目路径是否匹配
            cached_path_hash = data.get("project_path_hash", "")
            current_hash = self._get_project_hash()
            if cached_path_hash != current_hash:
                logger.info("缓存的项目路径不匹配，将重新生成")
                return None

            # 检测过期
            cache_age_days = (time.time() - data["timestamp"]) / 86400.0
            if cache_age_days > CONTEXT_CACHE_EXPIRE_DAYS:
                logger.info(f"项目概要缓存已过期（{cache_age_days:.1f} 天），建议使用 --refresh-context 更新")
                logger.info("本次仍使用已有缓存")

            summary = data["summary"]
            logger.info(f"已从缓存加载项目概要（{len(summary)} 字）")
            return summary

        except (ValueError, KeyError, OSError) as e:
            logger.warning(f"读取缓存失败: {e}，将重新生成")
            return None

    def _save_cache(self, summary: str) -> None:
        """
        将项目概要保存到 JSON 缓存文件

        Args:
            summary: 项目概要文档内容
        """
        # 确保缓存目录存在
        if not os.path.exists(self.cache_dir):
            try:
                os.makedirs(self.cache_dir)
            except OSError as e:
                logger.warning(f"创建缓存目录失败: {e}")
                return

        data = {
            "summary": summary,
            "timestamp": time.time(),
            "project_path": self.project_root,
            "project_path_hash": self._get_project_hash(),
            "version": "1.0",
        }

        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            logger.warning(f"保存缓存失败: {e}")

        # 尝试追加 .code_context 到项目的 .gitignore
        self._ensure_gitignore()

    def _get_project_hash(self) -> str:
        """
        生成项目路径的 hash 值，用于缓存校验

        Returns:
            str: 项目路径的 MD5 hash（前 16 位）
        """
        return hashlib.md5(self.project_root.encode("utf-8")).hexdigest()[:16]

    def _ensure_gitignore(self) -> None:
        """
        检查项目 .gitignore 中是否已包含 .code_context/，
        如果没有则自动追加
        """
        gitignore_path = os.path.join(self.project_root, ".gitignore")
        ignore_entry = CONTEXT_CACHE_DIR_NAME + "/"

        # 如果 .gitignore 存在，检查是否已包含
        if os.path.isfile(gitignore_path):
            try:
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    content = f.read()
                if ignore_entry in content:
                    return  # 已包含，无需追加
            except OSError:
                return

        # 追加到 .gitignore
        try:
            with open(gitignore_path, "a", encoding="utf-8") as f:
                f.write("\n# 代码注释生成器的项目上下文缓存\n")
                f.write(ignore_entry + "\n")
        except OSError:
            pass  # 无法写入 .gitignore 不影响主流程

    def _generate_directory_tree(self, max_depth: int = 3) -> str:
        """
        生成项目的目录树结构（限制深度以避免过长）

        Args:
            max_depth (int): 最大遍历深度

        Returns:
            str: 目录树的文本表示
        """
        lines = []
        self._walk_tree(self.project_root, "", lines, depth=0, max_depth=max_depth)
        return "\n".join(lines)

    def _walk_tree(self, current_path: str, prefix: str, lines: list[str],
                   depth: int, max_depth: int) -> None:
        """
        递归生成目录树

        Args:
            current_path: 当前目录的绝对路径
            prefix: 当前行的缩进前缀
            lines: 收集输出行的列表
            depth: 当前深度
            max_depth: 最大深度
        """
        if depth > max_depth:
            return

        try:
            entries = sorted(os.listdir(current_path))
        except OSError:
            return

        # 分离目录和文件
        dirs = []
        files = []
        for entry in entries:
            if entry.startswith("."):
                continue
            full_path = os.path.join(current_path, entry)
            if os.path.isdir(full_path):
                if entry not in DEFAULT_IGNORE_DIRS:
                    dirs.append(entry)
            else:
                files.append(entry)

        all_entries = [(d, True) for d in dirs] + [(f, False) for f in files]
        total = len(all_entries)

        for i, (name, is_dir) in enumerate(all_entries):
            is_last = (i == total - 1)
            connector = "└── " if is_last else "├── "

            if is_dir:
                lines.append(f"{prefix}{connector}{name}/")
                extension = "    " if is_last else "│   "
                self._walk_tree(
                    os.path.join(current_path, name),
                    prefix + extension,
                    lines,
                    depth + 1,
                    max_depth,
                )
            else:
                lines.append(f"{prefix}{connector}{name}")

    def _sample_key_files(self) -> dict[str, str | int] | None:
        """
        智能采样项目中的关键文件

        按优先级依次采样：
        1. README 文件
        2. 配置/构建文件
        3. 入口文件
        4. 各一级子目录的代表性文件

        Returns:
            {"content": str, "file_count": int}，无文件可采样返回 None
        """
        sampled_files = []
        sampled_paths = set()  # 已采样文件路径集合，避免重复
        char_budget = CONTEXT_CHAR_BUDGET

        # 第 1 轮：README 文件
        for readme_name in README_FILE_NAMES:
            if len(sampled_files) >= CONTEXT_SAMPLE_FILE_LIMIT:
                break
            readme_path = os.path.join(self.project_root, readme_name)
            if os.path.isfile(readme_path):
                content = self._read_sample_file(readme_path)
                if content and len(content) <= char_budget:
                    sampled_files.append((readme_name, content))
                    sampled_paths.add(readme_path)
                    char_budget -= len(content)
                break  # 只需要一个 README

        # 第 2 轮：配置/构建文件
        for config_name in CONFIG_FILE_NAMES:
            if len(sampled_files) >= CONTEXT_SAMPLE_FILE_LIMIT or char_budget <= 0:
                break
            config_path = os.path.join(self.project_root, config_name)
            if os.path.isfile(config_path) and config_path not in sampled_paths:
                content = self._read_sample_file(config_path)
                if content and len(content) <= char_budget:
                    sampled_files.append((config_name, content))
                    sampled_paths.add(config_path)
                    char_budget -= len(content)

        # 第 3 轮：入口文件（项目根目录和一级子目录中查找）
        entry_candidates = self._find_entry_files()
        for rel_path, abs_path in entry_candidates:
            if len(sampled_files) >= CONTEXT_SAMPLE_FILE_LIMIT or char_budget <= 0:
                break
            if abs_path not in sampled_paths:
                content = self._read_sample_file(abs_path)
                if content and len(content) <= char_budget:
                    sampled_files.append((rel_path, content))
                    sampled_paths.add(abs_path)
                    char_budget -= len(content)

        # 第 4 轮：各一级子目录的代表性源码文件
        subdirs = self._get_first_level_subdirs()
        for subdir_name in subdirs:
            if len(sampled_files) >= CONTEXT_SAMPLE_FILE_LIMIT or char_budget <= 0:
                break
            rep_file = self._pick_representative_file(subdir_name)
            if rep_file:
                rel_path, abs_path = rep_file
                if abs_path not in sampled_paths:
                    content = self._read_sample_file(abs_path)
                    if content and len(content) <= char_budget:
                        sampled_files.append((rel_path, content))
                        sampled_paths.add(abs_path)
                        char_budget -= len(content)

        if not sampled_files:
            return None

        # 组装采样结果
        parts = []
        for rel_path, content in sampled_files:
            parts.append(f"### 文件: {rel_path}\n\n```\n{content}\n```")

        return {
            "content": "\n\n---\n\n".join(parts),
            "file_count": len(sampled_files),
        }

    def _find_entry_files(self) -> list[tuple[str, str]]:
        """
        在项目根目录和一级子目录中查找入口文件

        Returns:
            list: [(rel_path, abs_path), ...] 入口文件列表
        """
        results = []

        # 扫描目录列表：根目录 + 一级子目录
        scan_dirs = [("", self.project_root)]
        try:
            for entry in os.listdir(self.project_root):
                full_path = os.path.join(self.project_root, entry)
                if os.path.isdir(full_path) and not entry.startswith(".") and entry not in DEFAULT_IGNORE_DIRS:
                    scan_dirs.append((entry, full_path))
        except OSError:
            pass

        # 在各目录中查找入口文件
        all_extensions = set(LANGUAGE_EXTENSIONS.keys())
        for dir_rel, dir_abs in scan_dirs:
            try:
                files_in_dir = os.listdir(dir_abs)
            except OSError:
                continue

            for fname in files_in_dir:
                stem, ext = os.path.splitext(fname)
                if stem.lower() in ENTRY_FILE_STEMS and ext.lower() in all_extensions:
                    abs_path = os.path.join(dir_abs, fname)
                    rel_path = os.path.join(dir_rel, fname) if dir_rel else fname
                    results.append((rel_path, abs_path))

        return results

    def _get_first_level_subdirs(self) -> list[str]:
        """
        获取项目的一级子目录列表（排除忽略目录和隐藏目录）

        Returns:
            list: 子目录名称列表
        """
        subdirs = []
        try:
            for entry in sorted(os.listdir(self.project_root)):
                if entry.startswith(".") or entry in DEFAULT_IGNORE_DIRS:
                    continue
                full_path = os.path.join(self.project_root, entry)
                if os.path.isdir(full_path):
                    subdirs.append(entry)
        except OSError:
            pass
        return subdirs

    def _pick_representative_file(self, subdir_name: str) -> tuple[str, str] | None:
        """
        从指定子目录中选取一个代表性源码文件

        优先选择：文件名包含 service/controller/handler/model/entity 等关键词的文件，
        其次选择最大的源码文件（通常包含最多逻辑）。

        Args:
            subdir_name (str): 一级子目录名称

        Returns:
            tuple or None: (rel_path, abs_path)，无合适文件返回 None
        """
        subdir_path = os.path.join(self.project_root, subdir_name)
        all_extensions = set(LANGUAGE_EXTENSIONS.keys())

        # 关键词优先级
        priority_keywords = [
            "service", "controller", "handler", "model", "entity",
            "repository", "dao", "manager", "core", "base", "util",
        ]

        candidates = []

        # 递归收集子目录中的源码文件（限制深度为 3）
        for dirpath, dirnames, filenames in os.walk(subdir_path):
            # 限制深度
            rel_to_sub = os.path.relpath(dirpath, subdir_path)
            depth = 0 if rel_to_sub == "." else rel_to_sub.count(os.sep) + 1
            if depth > 3:
                dirnames[:] = []
                continue

            # 过滤忽略目录
            dirnames[:] = [
                d for d in dirnames
                if not d.startswith(".") and d not in DEFAULT_IGNORE_DIRS
            ]

            for fname in filenames:
                _, ext = os.path.splitext(fname)
                if ext.lower() not in all_extensions:
                    continue

                abs_path = os.path.join(dirpath, fname)
                rel_path = os.path.join(
                    subdir_name,
                    os.path.relpath(abs_path, subdir_path),
                )

                # 计算优先级分数
                score = 0
                fname_lower = fname.lower()
                for i, kw in enumerate(priority_keywords):
                    if kw in fname_lower:
                        score = len(priority_keywords) - i
                        break

                try:
                    file_size = os.path.getsize(abs_path)
                except OSError:
                    file_size = 0

                candidates.append((score, file_size, rel_path, abs_path))

        if not candidates:
            return None

        # 按优先级分数降序，然后按文件大小降序排序
        candidates.sort(key=lambda x: (-x[0], -x[1]))
        best = candidates[0]
        return (best[2], best[3])

    def _read_sample_file(self, file_path: str) -> str | None:
        """
        读取采样文件内容，截取前 N 行

        Args:
            file_path: 文件的绝对路径

        Returns:
            文件内容（截取后），读取失败返回 None
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= CONTEXT_FILE_MAX_LINES:
                        lines.append(f"\n... (文件截断，仅显示前 {CONTEXT_FILE_MAX_LINES} 行)")
                        break
                    lines.append(line)
                return "".join(lines)
        except OSError:
            return None

    def _call_llm_for_summary(self, directory_tree: str, sampled_content: str) -> str | None:
        """
        调用大模型生成项目概要文档

        Args:
            directory_tree: 项目目录树文本
            sampled_content: 采样文件的组装内容

        Returns:
            生成的概要文档，失败返回 None
        """
        human_prompt = CONTEXT_ANALYSIS_HUMAN_PROMPT.format(
            directory_tree=directory_tree,
            sampled_files_content=sampled_content,
        )

        messages = [
            SystemMessage(content=CONTEXT_ANALYSIS_SYSTEM_PROMPT),
            HumanMessage(content=human_prompt),
        ]

        try:
            response = self.llm.invoke(messages)
            if response and response.content:
                summary = response.content.strip()
                # 简单校验：概要不能太短
                if len(summary) < 100:
                    logger.warning(f"大模型返回的概要过短（{len(summary)} 字），可能无效")
                    return None
                return summary
            else:
                logger.warning("大模型返回为空")
                return None
        except Exception as e:
            logger.error(f"调用大模型分析项目失败: {e}")
            return None
