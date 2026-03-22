# -*- coding: utf-8 -*-
"""
长期记忆存储模块 - 管理「项目根目录 → 项目概要」的本地化隔离存储

本模块负责：
1. 在程序运行目录下的 memory/ 目录中维护所有项目的概要长期记忆
2. 针对每个 --project_root_dir 在 memory/ 下创建独立子目录隔离存储
3. 子目录命名采用「项目末尾目录名 + 短 hash 后缀」以保证可读性与唯一性
4. 支持保存、加载、列出、删除操作
"""

from __future__ import annotations

import os
import json
import hashlib
import logging
import shutil
import time

from config import MEMORY_BASE_DIR

logger = logging.getLogger(__name__)

# 每个项目子目录内的记忆数据文件名
_SUMMARY_FILE_NAME = "project_summary.json"


class ProjectMemoryStore:
    """
    项目概要长期记忆存储（按项目隔离）

    将各个项目的概要文档按项目独立存储在程序目录下的 memory/ 目录中，
    每个项目对应一个以「末尾目录名_短hash」命名的子目录，实现完全隔离。
    """

    def __init__(self, project_path: str) -> None:
        """
        初始化长期记忆存储

        根据传入的 project_path 计算对应的记忆子目录路径，
        自动创建 memory/ 基础目录和项目子目录（如不存在）。

        Args:
            project_path: 项目根目录的绝对路径
        """
        self.base_dir = MEMORY_BASE_DIR
        self.project_path = os.path.abspath(project_path)
        self.project_dir_name = self._make_project_dir_name(self.project_path)
        self.project_memory_dir = os.path.join(self.base_dir, self.project_dir_name)
        self.store_file = os.path.join(self.project_memory_dir, _SUMMARY_FILE_NAME)
        self._ensure_dir(self.project_memory_dir)

    @staticmethod
    def _make_project_dir_name(project_path: str) -> str:
        """
        根据项目路径生成可读且唯一的子目录名

        格式：<项目末尾目录名>_<路径MD5短hash(6位)>
        例如路径 /home/user/my-project 生成 my-project_a3b1c9

        Args:
            project_path: 项目根目录的绝对路径（已 normalize）

        Returns:
            子目录名字符串
        """
        tail = os.path.basename(project_path.rstrip(os.sep)) or "root"
        short_hash = hashlib.md5(project_path.encode("utf-8")).hexdigest()[:6]
        return f"{tail}_{short_hash}"

    @staticmethod
    def _ensure_dir(dir_path: str) -> None:
        """确保目录存在，不存在则创建"""
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"创建记忆存储目录: {dir_path}")
            except OSError as e:
                logger.error(f"创建记忆存储目录失败: {e}")

    def _load_entry(self) -> dict | None:
        """
        从当前项目的记忆文件中加载数据

        Returns:
            记忆数据字典，文件不存在或加载失败返回 None
        """
        if not os.path.isfile(self.store_file):
            return None

        try:
            with open(self.store_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"读取项目记忆文件失败: {e}")
            raise

    def _save_entry(self, entry: dict) -> bool:
        """
        将记忆数据写入当前项目的记忆文件

        Args:
            entry: 记忆数据字典

        Returns:
            是否保存成功
        """
        self._ensure_dir(self.project_memory_dir)
        try:
            with open(self.store_file, "w", encoding="utf-8") as f:
                json.dump(entry, f, ensure_ascii=False, indent=2)
            return True
        except OSError as e:
            logger.error(f"保存项目记忆文件失败: {e}")
            return False

    def save_project_summary(
        self,
        project_path: str,
        summary: str,
        project_info: str | None = None,
    ) -> bool:
        """
        保存或更新项目概要到长期记忆

        Args:
            project_path: 项目根目录的绝对路径
            summary: 大模型生成的项目概要文档
            project_info: 用户提供的项目简要信息（可选）

        Returns:
            是否保存成功
        """
        normalized_path = os.path.abspath(project_path)
        entry = {
            "project_path": normalized_path,
            "summary": summary,
            "project_info": project_info,
            "timestamp": time.time(),
            "version": "1.0",
        }

        success = self._save_entry(entry)
        if success:
            logger.info(f"项目概要已保存到长期记忆: {normalized_path}")
        return success

    def load_project_summary(self, project_path: str) -> dict | None:
        """
        按项目路径加载长期记忆中的概要

        Args:
            project_path: 项目根目录的绝对路径

        Returns:
            记忆数据字典 {project_path, summary, project_info, timestamp, version}，
            未找到返回 None
        """
        normalized_path = os.path.abspath(project_path)
        entry = self._load_entry()

        if entry is None:
            return None

        # 校验路径是否匹配（防止子目录名碰撞）
        if entry.get("project_path") != normalized_path:
            logger.warning("记忆文件中的路径与请求路径不匹配（可能是目录名碰撞），忽略")
            return None

        logger.info(f"从长期记忆加载项目概要: {normalized_path}")
        return entry

    def list_project_summaries(self) -> list[dict]:
        """
        列出所有已记忆的项目概要

        遍历 memory/ 下所有项目子目录，从每个子目录中读取记忆数据。

        Returns:
            项目记忆列表 [{project_path, summary_preview, timestamp}, ...]
        """
        results = []

        if not os.path.isdir(self.base_dir):
            return results

        for dir_name in os.listdir(self.base_dir):
            sub_dir = os.path.join(self.base_dir, dir_name)
            if not os.path.isdir(sub_dir):
                continue

            summary_file = os.path.join(sub_dir, _SUMMARY_FILE_NAME)
            if not os.path.isfile(summary_file):
                continue

            try:
                with open(summary_file, "r", encoding="utf-8") as f:
                    entry = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"读取记忆文件失败 {summary_file}: {e}")
                continue

            summary_text = entry.get("summary", "")
            # 生成概要预览（前 100 字）
            preview = summary_text[:100] + "..." if len(summary_text) > 100 else summary_text

            results.append({
                "project_path": entry.get("project_path", "unknown"),
                "summary_preview": preview,
                "project_info": entry.get("project_info"),
                "timestamp": entry.get("timestamp", 0),
                "memory_dir": sub_dir,
            })

        # 按时间戳降序排列
        results.sort(key=lambda x: x["timestamp"], reverse=True)
        return results

    def remove_project_summary(self, project_path: str) -> bool:
        """
        删除指定项目的长期记忆

        定位对应项目的记忆子目录并删除整个子目录及其中所有文件。

        Args:
            project_path: 项目根目录的绝对路径

        Returns:
            是否删除成功（项目不存在也返回 True）
        """
        if not os.path.isdir(self.project_memory_dir):
            logger.info(f"项目记忆目录不存在，无需删除: {self.project_memory_dir}")
            return True

        try:
            shutil.rmtree(self.project_memory_dir)
            logger.info(f"已删除项目长期记忆目录: {self.project_memory_dir}")
            return True
        except OSError as e:
            logger.error(f"删除项目记忆目录失败: {e}")
            return False
