# -*- coding: utf-8 -*-
"""
进度跟踪模块 - 支持文件级和目录级断点恢复

本模块负责：
1. 记录每个已成功处理的文件，下次重跑可跳过
2. 记录已完成的目录（所有文件和子目录均已处理），下次重跑可整体跳过
3. 将进度数据持久化到 .code_context/progress.json
4. 支持重置进度（清除所有记录）
"""

from __future__ import annotations

import os
import json
import logging
import time

from config import CONTEXT_CACHE_DIR_NAME

logger = logging.getLogger(__name__)


class ProgressTracker:
    """
    进度跟踪器 - 管理文件级和目录级的断点恢复状态

    数据结构（progress.json）：
    {
        "version": "1.0",
        "project_path": "/abs/path/to/project",
        "completed_files": {
            "src/main.py": {"timestamp": 1234567890.0},
            ...
        },
        "completed_dirs": {
            "src/utils": {"timestamp": 1234567890.0},
            ...
        }
    }
    """

    def __init__(self, project_root: str) -> None:
        """
        初始化进度跟踪器

        Args:
            project_root: 目标项目的根目录路径
        """
        self.project_root = os.path.abspath(project_root)
        self.cache_dir = os.path.join(self.project_root, CONTEXT_CACHE_DIR_NAME)
        self.progress_file = os.path.join(self.cache_dir, "progress.json")

        # 内存中的进度数据
        self.completed_files: dict[str, dict] = {}
        self.completed_dirs: dict[str, dict] = {}

        # 加载已有进度
        self._load()

    def _load(self) -> None:
        """
        从 progress.json 加载已有进度数据
        """
        if not os.path.isfile(self.progress_file):
            return

        try:
            with open(self.progress_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 校验版本和项目路径
            if data.get("project_path") != self.project_root:
                logger.info("进度文件的项目路径不匹配，将忽略已有进度")
                return

            self.completed_files = data.get("completed_files", {})
            self.completed_dirs = data.get("completed_dirs", {})

            total = len(self.completed_files)
            dir_total = len(self.completed_dirs)
            if total > 0 or dir_total > 0:
                logger.info(f"已加载进度记录：{total} 个文件、{dir_total} 个目录已完成")

        except (ValueError, KeyError, OSError) as e:
            logger.warning(f"读取进度文件失败: {e}，将从头开始")
            self.completed_files = {}
            self.completed_dirs = {}

    def _save(self) -> None:
        """
        将当前进度数据持久化到 progress.json
        """
        # 确保缓存目录存在
        if not os.path.exists(self.cache_dir):
            try:
                os.makedirs(self.cache_dir)
            except OSError as e:
                logger.error(f"创建缓存目录失败: {e}")
                return

        data = {
            "version": "1.0",
            "project_path": self.project_root,
            "completed_files": self.completed_files,
            "completed_dirs": self.completed_dirs,
        }

        try:
            with open(self.progress_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            logger.error(f"保存进度文件失败: {e}")

    def is_file_done(self, rel_path: str) -> bool:
        """
        检查某个文件是否已经处理过

        Args:
            rel_path: 文件相对于项目根的相对路径

        Returns:
            如果已处理返回 True
        """
        return rel_path in self.completed_files

    def mark_file_done(self, rel_path: str) -> None:
        """
        标记某个文件为已完成，并立即持久化

        Args:
            rel_path: 文件相对于项目根的相对路径
        """
        self.completed_files[rel_path] = {
            "timestamp": time.time(),
        }
        self._save()

    def is_dir_done(self, rel_dir: str) -> bool:
        """
        检查某个目录是否已经全部处理完毕

        Args:
            rel_dir: 目录相对于项目根的相对路径

        Returns:
            如果该目录已全部完成返回 True
        """
        return rel_dir in self.completed_dirs

    def mark_dir_done(self, rel_dir: str) -> None:
        """
        标记某个目录为已完成，并立即持久化

        Args:
            rel_dir: 目录相对于项目根的相对路径
        """
        self.completed_dirs[rel_dir] = {
            "timestamp": time.time(),
        }
        self._save()

    def reset(self) -> None:
        """
        重置所有进度记录
        """
        self.completed_files = {}
        self.completed_dirs = {}

        # 删除进度文件
        if os.path.isfile(self.progress_file):
            try:
                os.remove(self.progress_file)
                logger.info("已清除所有进度记录")
            except OSError as e:
                logger.error(f"删除进度文件失败: {e}")
        else:
            logger.info("无进度记录需要清除")

    def get_summary(self) -> str:
        """
        获取进度摘要

        Returns:
            进度统计文本
        """
        return f"已完成: {len(self.completed_files)} 个文件, {len(self.completed_dirs)} 个目录"
