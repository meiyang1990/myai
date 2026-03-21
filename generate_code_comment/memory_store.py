# -*- coding: utf-8 -*-
"""
长期记忆存储模块 - 管理「项目根目录 → 项目概要」的全局映射

本模块负责：
1. 在 ~/.code_comment_memory/ 下维护全局的项目概要长期记忆
2. 以 project_path 的 MD5 hash 为 key 存储概要数据
3. 支持保存、加载、列出、删除操作
4. 跨项目共享，供注释生成时快速加载已有概要
"""

from __future__ import annotations

import os
import json
import hashlib
import logging
import time

from config import MEMORY_STORE_DIR, MEMORY_STORE_FILE

logger = logging.getLogger(__name__)


class ProjectMemoryStore:
    """
    项目概要长期记忆存储

    将各个项目的概要文档以 JSON 格式集中存储在用户 HOME 目录下，
    以 project_path 的 MD5 hash 为 key，实现「项目根目录 → 项目概要」的全局映射。
    """

    def __init__(self) -> None:
        """
        初始化长期记忆存储

        自动创建存储目录（如不存在）
        """
        self.store_dir = MEMORY_STORE_DIR
        self.store_file = os.path.join(self.store_dir, MEMORY_STORE_FILE)
        self._ensure_store_dir()

    def _ensure_store_dir(self) -> None:
        """确保存储目录存在"""
        if not os.path.exists(self.store_dir):
            try:
                os.makedirs(self.store_dir, exist_ok=True)
                logger.info(f"创建长期记忆存储目录: {self.store_dir}")
            except OSError as e:
                logger.error(f"创建长期记忆存储目录失败: {e}")

    @staticmethod
    def _path_hash(project_path: str) -> str:
        """
        生成项目路径的 MD5 hash，作为存储 key

        Args:
            project_path: 项目根目录的绝对路径

        Returns:
            MD5 hash 字符串（32 位）
        """
        normalized = os.path.abspath(project_path)
        return hashlib.md5(normalized.encode("utf-8")).hexdigest()

    def _load_store(self) -> dict:
        """
        从文件加载整个记忆存储

        Returns:
            存储字典，加载失败返回空字典
        """
        if not os.path.isfile(self.store_file):
            return {}

        try:
            with open(self.store_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"读取长期记忆文件失败: {e}")
            raise

    def _save_store(self, store: dict) -> bool:
        """
        将整个记忆存储写入文件

        Args:
            store: 存储字典

        Returns:
            是否保存成功
        """
        self._ensure_store_dir()
        try:
            with open(self.store_file, "w", encoding="utf-8") as f:
                json.dump(store, f, ensure_ascii=False, indent=2)
            return True
        except OSError as e:
            logger.error(f"保存长期记忆文件失败: {e}")
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
        key = self._path_hash(normalized_path)

        store = self._load_store()
        store[key] = {
            "project_path": normalized_path,
            "summary": summary,
            "project_info": project_info,
            "timestamp": time.time(),
            "version": "1.0",
        }

        success = self._save_store(store)
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
        key = self._path_hash(normalized_path)

        store = self._load_store()
        entry = store.get(key)

        if entry is None:
            return None

        # 校验路径是否匹配（防止 hash 碰撞）
        if entry.get("project_path") != normalized_path:
            logger.warning("长期记忆中的路径与请求路径不匹配（可能是 hash 碰撞），忽略")
            return None

        logger.info(f"从长期记忆加载项目概要: {normalized_path}")
        return entry

    def list_project_summaries(self) -> list[dict]:
        """
        列出所有已记忆的项目概要

        Returns:
            项目记忆列表 [{project_path, summary_preview, timestamp}, ...]
        """
        store = self._load_store()
        results = []

        for key, entry in store.items():
            summary_text = entry.get("summary", "")
            # 生成概要预览（前 100 字）
            preview = summary_text[:100] + "..." if len(summary_text) > 100 else summary_text

            results.append({
                "project_path": entry.get("project_path", "unknown"),
                "summary_preview": preview,
                "project_info": entry.get("project_info"),
                "timestamp": entry.get("timestamp", 0),
            })

        # 按时间戳降序排列
        results.sort(key=lambda x: x["timestamp"], reverse=True)
        return results

    def remove_project_summary(self, project_path: str) -> bool:
        """
        删除指定项目的长期记忆

        Args:
            project_path: 项目根目录的绝对路径

        Returns:
            是否删除成功（项目不存在也返回 True）
        """
        normalized_path = os.path.abspath(project_path)
        key = self._path_hash(normalized_path)

        store = self._load_store()
        if key in store:
            del store[key]
            success = self._save_store(store)
            if success:
                logger.info(f"已删除项目长期记忆: {normalized_path}")
            return success
        else:
            logger.info(f"项目在长期记忆中不存在，无需删除: {normalized_path}")
            return True
