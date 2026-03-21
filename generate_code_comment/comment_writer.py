# -*- coding: utf-8 -*-
"""
注释回写模块 - 将大模型生成的带注释代码写回文件

本模块负责：
1. 将生成的带注释代码保存到输出目录（保持原始目录结构）
2. 支持覆盖原文件或输出到独立目录两种模式
3. 提供预览功能，输出前后对比
4. 确保文件编码和格式的正确性
"""

from __future__ import annotations

import os
import logging
import shutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from source_reader import SourceFile

logger = logging.getLogger(__name__)


class CommentWriter:
    """
    注释回写器 - 将带注释的代码写入文件

    支持两种写入模式：
    - output 模式：写入到指定的输出目录，保持原始目录结构（默认模式，安全）
    - overwrite 模式：直接覆盖原始源码文件（需用户明确确认）

    输出路径基于 source_path（实际处理路径）计算，而非 project_root_dir。
    """

    def __init__(self, source_path: str, output_dir: str | None = None,
                 overwrite: bool = False) -> None:
        """
        初始化注释回写器

        Args:
            source_path: 实际处理的源码路径（文件或目录），用于计算默认输出目录
            output_dir: 输出目录路径。为 None 时：
                        - 目录模式：默认为 <source_path>_commented
                        - 单文件模式：默认为 <文件所在目录>/<文件名>_commented/
            overwrite: 是否直接覆盖原文件。默认 False（安全模式）
        """
        self.source_path = os.path.abspath(source_path)
        self.overwrite = overwrite

        if overwrite:
            # 覆盖模式：write_file() 直接使用 source_file.abs_path 写回原位，
            # output_root 仅用于 get_summary() 展示
            self.output_root = self.source_path
        else:
            # 输出模式：写入到独立目录
            if output_dir:
                self.output_root = os.path.abspath(output_dir)
            elif os.path.isfile(self.source_path):
                # 单文件模式：在文件所在目录创建 <文件名>_commented/
                parent_dir = os.path.dirname(self.source_path)
                file_stem = os.path.splitext(os.path.basename(self.source_path))[0]
                self.output_root = os.path.join(parent_dir, file_stem + "_commented")
            else:
                # 目录模式：<source_path>_commented
                self.output_root = self.source_path + "_commented"

        # 统计信息
        self.success_count = 0
        self.fail_count = 0
        self.skip_count = 0

    def write_file(self, source_file: SourceFile, commented_code: str | None) -> bool:
        """
        将带注释的代码写入文件

        Args:
            source_file: SourceFile 对象，包含原始文件信息
            commented_code: 大模型生成的带注释代码

        Returns:
            写入是否成功
        """
        if commented_code is None:
            self.skip_count += 1
            return False

        # 计算输出文件路径
        if self.overwrite:
            # 覆盖模式：直接写回原始文件的绝对路径，避免 output_root + rel_path 拼接导致路径嵌套
            output_path = source_file.abs_path
        else:
            # 输出模式：将 abs_path 转换为相对于 source_path 的路径，再拼接 output_root。
            # 注意：source_file.rel_path 是相对于 project_root 的，而 output_root 基于
            # source_path 计算，两者基准不同，直接拼接会导致目录嵌套 bug。
            if os.path.isfile(self.source_path):
                # 单文件模式：直接使用文件名
                rel_to_source = os.path.basename(source_file.abs_path)
            else:
                # 目录模式：计算相对于 source_path 的路径
                rel_to_source = os.path.relpath(source_file.abs_path, self.source_path)
            output_path = os.path.join(self.output_root, rel_to_source)

        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                logger.error(f"创建目录失败 {output_dir}: {e}")
                raise

        # 写入文件
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(commented_code)

            self.success_count += 1
            return True

        except OSError as e:
            logger.error(f"写入文件失败 {output_path}: {e}")
            raise

    def copy_non_source_files(self, source_files: list[SourceFile]) -> None:
        """
        在输出模式下，将非源码文件（配置文件、资源文件等）也复制到输出目录，
        以保持完整的项目结构。

        仅在非覆盖模式下且 source_path 为目录时有效。

        Args:
            source_files: 已处理的 SourceFile 对象列表
        """
        if self.overwrite:
            return

        # 单文件模式下不复制非源码文件
        if os.path.isfile(self.source_path):
            return

        # 收集已处理文件相对于 source_path 的路径集合
        # 注意：sf.rel_path 是相对于 project_root 的，这里需要转换为相对于 source_path
        processed_rels = set()
        for sf in source_files:
            try:
                rel = os.path.relpath(sf.abs_path, self.source_path)
            except ValueError:
                rel = sf.rel_path
            processed_rels.add(rel)

        # 遍历 source_path 目录，复制未处理的文件
        for dirpath, dirnames, filenames in os.walk(self.source_path):
            rel_dir = os.path.relpath(dirpath, self.source_path)
            if rel_dir == ".":
                rel_dir = ""

            # 跳过隐藏目录和常见忽略目录
            skip = False
            parts = rel_dir.split(os.sep) if rel_dir else []
            for part in parts:
                if part.startswith(".") or part in (
                    "node_modules", "target", "build", "dist", "__pycache__"
                ):
                    skip = True
                    break
            if skip:
                continue

            for fname in filenames:
                rel_file = os.path.join(rel_dir, fname) if rel_dir else fname

                # 已处理的源码文件跳过（已经由 write_file 写入）
                if rel_file in processed_rels:
                    continue

                # 跳过隐藏文件
                if fname.startswith("."):
                    continue

                src_path = os.path.join(dirpath, fname)
                dst_path = os.path.join(self.output_root, rel_file)

                dst_dir = os.path.dirname(dst_path)
                if not os.path.exists(dst_dir):
                    try:
                        os.makedirs(dst_dir)
                    except OSError as e:
                        logger.error(f"创建目录失败 {dst_dir}: {e}")
                        raise

                try:
                    shutil.copy2(src_path, dst_path)
                except OSError as e:
                    logger.error(f"复制文件失败 {src_path} -> {dst_path}: {e}")
                    raise

    def get_summary(self) -> str:
        """
        获取回写操作的统计摘要

        Returns:
            统计摘要文本
        """
        total = self.success_count + self.fail_count + self.skip_count
        mode = "覆盖原文件" if self.overwrite else "输出到新目录"
        lines = [
            "=" * 50,
            "注释回写统计",
            "=" * 50,
            f"输出目录: {self.output_root}",
            f"写入模式: {mode}",
            f"成功: {self.success_count} 个文件",
            f"失败: {self.fail_count} 个文件",
            f"跳过: {self.skip_count} 个文件",
            f"合计: {total} 个文件",
            "=" * 50,
        ]

        return "\n".join(lines)
