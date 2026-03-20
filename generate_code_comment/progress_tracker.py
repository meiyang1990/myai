# -*- coding: utf-8 -*-
"""
进度跟踪模块 - 支持文件级和目录级断点恢复

本模块负责：
1. 记录每个已成功处理的文件，下次重跑可跳过
2. 记录已完成的目录（所有文件和子目录均已处理），下次重跑可整体跳过
3. 将进度数据持久化到 .code_context/progress.json
4. 支持重置进度（清除所有记录）
"""

import os
import io
import json
import time

from config import CONTEXT_CACHE_DIR_NAME


class ProgressTracker(object):
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

    def __init__(self, project_root):
        """
        初始化进度跟踪器

        Args:
            project_root (str): 目标项目的根目录路径
        """
        self.project_root = os.path.abspath(project_root)
        self.cache_dir = os.path.join(self.project_root, CONTEXT_CACHE_DIR_NAME)
        self.progress_file = os.path.join(self.cache_dir, "progress.json")

        # 内存中的进度数据
        self.completed_files = {}
        self.completed_dirs = {}

        # 加载已有进度
        self._load()

    def _load(self):
        """
        从 progress.json 加载已有进度数据
        """
        if not os.path.isfile(self.progress_file):
            return

        try:
            with io.open(self.progress_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 校验版本和项目路径
            if data.get("project_path") != self.project_root:
                print("[进度] 进度文件的项目路径不匹配，将忽略已有进度")
                return

            self.completed_files = data.get("completed_files", {})
            self.completed_dirs = data.get("completed_dirs", {})

            total = len(self.completed_files)
            dir_total = len(self.completed_dirs)
            if total > 0 or dir_total > 0:
                print("[进度] 已加载进度记录：%d 个文件、%d 个目录已完成" % (total, dir_total))

        except (ValueError, KeyError, IOError) as e:
            print("[进度] 读取进度文件失败: %s，将从头开始" % str(e))
            self.completed_files = {}
            self.completed_dirs = {}

    def _save(self):
        """
        将当前进度数据持久化到 progress.json
        """
        # 确保缓存目录存在
        if not os.path.exists(self.cache_dir):
            try:
                os.makedirs(self.cache_dir)
            except OSError as e:
                print("[进度] 创建缓存目录失败: %s" % str(e))
                return

        data = {
            "version": "1.0",
            "project_path": self.project_root,
            "completed_files": self.completed_files,
            "completed_dirs": self.completed_dirs,
        }

        try:
            with io.open(self.progress_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except (IOError, OSError) as e:
            print("[进度] 保存进度文件失败: %s" % str(e))

    def is_file_done(self, rel_path):
        """
        检查某个文件是否已经处理过

        Args:
            rel_path (str): 文件相对于项目根的相对路径

        Returns:
            bool: 如果已处理返回 True
        """
        return rel_path in self.completed_files

    def mark_file_done(self, rel_path):
        """
        标记某个文件为已完成，并立即持久化

        Args:
            rel_path (str): 文件相对于项目根的相对路径
        """
        self.completed_files[rel_path] = {
            "timestamp": time.time(),
        }
        self._save()

    def is_dir_done(self, rel_dir):
        """
        检查某个目录是否已经全部处理完毕

        Args:
            rel_dir (str): 目录相对于项目根的相对路径

        Returns:
            bool: 如果该目录已全部完成返回 True
        """
        return rel_dir in self.completed_dirs

    def mark_dir_done(self, rel_dir):
        """
        标记某个目录为已完成，并立即持久化

        Args:
            rel_dir (str): 目录相对于项目根的相对路径
        """
        self.completed_dirs[rel_dir] = {
            "timestamp": time.time(),
        }
        self._save()

    def reset(self):
        """
        重置所有进度记录
        """
        self.completed_files = {}
        self.completed_dirs = {}

        # 删除进度文件
        if os.path.isfile(self.progress_file):
            try:
                os.remove(self.progress_file)
                print("[进度] 已清除所有进度记录")
            except OSError as e:
                print("[进度] 删除进度文件失败: %s" % str(e))
        else:
            print("[进度] 无进度记录需要清除")

    def get_summary(self):
        """
        获取进度摘要

        Returns:
            str: 进度统计文本
        """
        return "已完成: %d 个文件, %d 个目录" % (
            len(self.completed_files),
            len(self.completed_dirs),
        )
