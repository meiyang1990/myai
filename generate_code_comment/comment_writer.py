# -*- coding: utf-8 -*-
"""
注释回写模块 - 将大模型生成的带注释代码写回文件

本模块负责：
1. 将生成的带注释代码保存到输出目录（保持原始目录结构）
2. 支持覆盖原文件或输出到独立目录两种模式
3. 提供预览功能，输出前后对比
4. 确保文件编码和格式的正确性
"""

import os
import io
import shutil


class CommentWriter(object):
    """
    注释回写器 - 将带注释的代码写入文件

    支持两种写入模式：
    - output 模式：写入到指定的输出目录，保持原始项目的目录结构（默认模式，安全）
    - overwrite 模式：直接覆盖原始源码文件（需用户明确确认）
    """

    def __init__(self, project_root, output_dir=None, overwrite=False):
        """
        初始化注释回写器

        Args:
            project_root (str): 原始项目的根目录路径
            output_dir (str or None): 输出目录路径。为 None 时默认为 项目根目录_commented
            overwrite (bool): 是否直接覆盖原文件。默认 False（安全模式）
        """
        self.project_root = os.path.abspath(project_root)
        self.overwrite = overwrite

        if overwrite:
            # 覆盖模式：直接写回原位置
            self.output_root = self.project_root
        else:
            # 输出模式：写入到独立目录
            if output_dir:
                self.output_root = os.path.abspath(output_dir)
            else:
                self.output_root = self.project_root + "_commented"

        # 统计信息
        self.success_count = 0
        self.fail_count = 0
        self.skip_count = 0

    def write_file(self, source_file, commented_code):
        """
        将带注释的代码写入文件

        Args:
            source_file: SourceFile 对象，包含原始文件信息
            commented_code (str): 大模型生成的带注释代码

        Returns:
            bool: 写入是否成功
        """
        if commented_code is None:
            self.skip_count += 1
            return False

        # 计算输出文件路径
        output_path = os.path.join(self.output_root, source_file.rel_path)

        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                print("[错误] 创建目录失败 %s: %s" % (output_dir, str(e)))
                self.fail_count += 1
                return False

        # 写入文件
        try:
            with io.open(output_path, "w", encoding="utf-8") as f:
                f.write(commented_code)

            self.success_count += 1
            return True

        except (IOError, OSError) as e:
            print("[错误] 写入文件失败 %s: %s" % (output_path, str(e)))
            self.fail_count += 1
            return False

    def copy_non_source_files(self, source_files):
        """
        在输出模式下，将非源码文件（配置文件、资源文件等）也复制到输出目录，
        以保持完整的项目结构。

        仅在非覆盖模式下有效。

        Args:
            source_files: 已处理的 SourceFile 对象列表
        """
        if self.overwrite:
            return

        # 收集已处理文件的相对路径集合
        processed_rels = set()
        for sf in source_files:
            processed_rels.add(sf.rel_path)

        # 遍历项目目录，复制未处理的文件
        for dirpath, dirnames, filenames in os.walk(self.project_root):
            rel_dir = os.path.relpath(dirpath, self.project_root)
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
                    except OSError:
                        continue

                try:
                    shutil.copy2(src_path, dst_path)
                except (IOError, OSError):
                    pass

    def get_summary(self):
        """
        获取回写操作的统计摘要

        Returns:
            str: 统计摘要文本
        """
        lines = []
        lines.append("=" * 50)
        lines.append("注释回写统计")
        lines.append("=" * 50)
        lines.append("输出目录: %s" % self.output_root)
        lines.append("写入模式: %s" % ("覆盖原文件" if self.overwrite else "输出到新目录"))
        lines.append("成功: %d 个文件" % self.success_count)
        lines.append("失败: %d 个文件" % self.fail_count)
        lines.append("跳过: %d 个文件" % self.skip_count)
        total = self.success_count + self.fail_count + self.skip_count
        lines.append("合计: %d 个文件" % total)
        lines.append("=" * 50)

        return "\n".join(lines)
