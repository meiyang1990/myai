# -*- coding: utf-8 -*-
"""
智能代码注释生成器 - 主程序入口

基于 LangChain + 火山引擎大模型，自动为源码文件生成高质量中文注释。
支持项目上下文分析，让大模型理解项目全局架构后生成更有深度的注释。

使用方式：
    python main.py <项目路径> [选项]

示例：
    # 基本用法：扫描项目并生成注释到新目录（自动分析项目上下文）
    python main.py /path/to/your/project

    # 指定输出目录
    python main.py /path/to/your/project -o /path/to/output

    # 覆盖原文件（谨慎使用）
    python main.py /path/to/your/project --overwrite

    # 仅测试 API 连接
    python main.py --test-api

    # 仅扫描不生成（预览将处理哪些文件）
    python main.py /path/to/your/project --scan-only

    # 强制刷新项目上下文概要
    python main.py /path/to/your/project --refresh-context

    # 仅生成项目上下文概要（不执行注释生成）
    python main.py /path/to/your/project --context-only

    # 跳过项目上下文分析（兼容旧行为）
    python main.py /path/to/your/project --no-context
"""

from __future__ import print_function

import sys
import os
import argparse
import time

# 将当前脚本所在目录加入 sys.path，确保模块导入正常
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

from config import validate_config
from source_reader import SourceReader
from comment_generator import CommentGenerator
from comment_writer import CommentWriter
from project_context import ProjectContextAnalyzer
from progress_tracker import ProgressTracker


def parse_args():
    """
    解析命令行参数

    Returns:
        argparse.Namespace: 解析后的参数对象
    """
    parser = argparse.ArgumentParser(
        description="智能代码注释生成器 - 基于 AI 自动为源码添加中文注释",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py /path/to/project              # 生成注释到新目录（自动分析上下文）
  python main.py /path/to/project -o ./output   # 指定输出目录
  python main.py /path/to/project --overwrite   # 覆盖原文件
  python main.py --test-api                     # 测试 API 连接
  python main.py /path/to/project --scan-only   # 仅扫描预览
  python main.py /path/to/project --context-only          # 仅生成上下文概要
  python main.py /path/to/project --refresh-context        # 强制刷新上下文
  python main.py /path/to/project --no-context             # 跳过上下文分析
        """,
    )

    parser.add_argument(
        "project_path",
        nargs="?",
        default=None,
        help="目标项目的根目录路径",
    )

    parser.add_argument(
        "-o", "--output",
        default=None,
        help="输出目录路径（默认为 <项目路径>_commented）",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="直接覆盖原始文件（谨慎使用，建议先备份）",
    )

    parser.add_argument(
        "--scan-only",
        action="store_true",
        default=False,
        help="仅扫描并列出将处理的文件，不生成注释",
    )

    parser.add_argument(
        "--test-api",
        action="store_true",
        default=False,
        help="测试火山引擎 API 连接是否正常",
    )

    parser.add_argument(
        "--copy-others",
        action="store_true",
        default=False,
        help="在输出模式下，同时复制非源码文件到输出目录",
    )

    parser.add_argument(
        "--refresh-context",
        action="store_true",
        default=False,
        help="强制重新分析项目，刷新项目上下文概要缓存",
    )

    parser.add_argument(
        "--context-only",
        action="store_true",
        default=False,
        help="仅生成项目上下文概要并存储，不执行注释生成",
    )

    parser.add_argument(
        "--no-context",
        action="store_true",
        default=False,
        help="跳过项目上下文分析，使用无上下文模式生成注释（兼容旧行为）",
    )

    parser.add_argument(
        "--reset-progress",
        action="store_true",
        default=False,
        help="重置进度记录，清除所有断点恢复数据，从头处理所有文件",
    )

    args = parser.parse_args()

    # 校验：非 test-api 模式必须提供项目路径
    if not args.test_api and not args.project_path:
        parser.error("请提供目标项目路径，或使用 --test-api 测试 API 连接")

    return args


def do_test_api():
    """
    测试火山引擎 API 连接
    """
    print("=" * 50)
    print("测试火山引擎大模型 API 连接...")
    print("=" * 50)

    # 校验配置
    is_valid, errors = validate_config()
    if not is_valid:
        print("\n[配置错误]")
        for err in errors:
            print("  - %s" % err)
        return False

    generator = CommentGenerator()
    success, message = generator.test_connection()
    print(message)
    return success


def do_scan_only(project_path):
    """
    仅扫描项目，列出将处理的文件

    Args:
        project_path (str): 项目根目录路径
    """
    print("=" * 50)
    print("扫描项目: %s" % project_path)
    print("=" * 50)

    reader = SourceReader(project_path)
    source_files = reader.scan()

    print("\n" + reader.get_project_summary(source_files))

    if source_files:
        print("\n文件列表:")
        for i, sf in enumerate(source_files, 1):
            print("  %3d. [%s] %s (%d bytes)" % (
                i, sf.language, sf.rel_path, sf.size
            ))


def do_context_only(project_path, refresh):
    """
    仅生成项目上下文概要（不执行注释生成）

    Args:
        project_path (str): 项目根目录路径
        refresh (bool): 是否强制刷新
    """
    print("=" * 50)
    print("项目上下文分析")
    print("=" * 50)

    # 校验配置
    is_valid, errors = validate_config()
    if not is_valid:
        print("\n[配置错误]")
        for err in errors:
            print("  - %s" % err)
        return False

    print("\n正在分析项目: %s" % project_path)
    analyzer = ProjectContextAnalyzer(project_path)
    summary = analyzer.get_context(force_refresh=refresh)

    if summary:
        print("\n" + "=" * 50)
        print("项目概要内容：")
        print("=" * 50)
        print(summary)
        print("\n" + "=" * 50)
        return True
    else:
        print("\n[错误] 未能生成项目概要")
        return False


def _mark_completed_dirs(source_files, tracker):
    """
    自底向上推导并标记已完成的目录

    逻辑：收集所有文件所属的目录路径，对每个目录检查其下所有文件是否都已完成，
    如果是则标记该目录为已完成。从最深层目录开始检查。

    Args:
        source_files (list): SourceFile 对象列表
        tracker (ProgressTracker): 进度跟踪器实例
    """
    # 收集所有文件的目录路径
    dir_files = {}  # dir_rel_path -> [file_rel_path, ...]
    for sf in source_files:
        dir_path = os.path.dirname(sf.rel_path)
        if dir_path not in dir_files:
            dir_files[dir_path] = []
        dir_files[dir_path].append(sf.rel_path)

    # 按目录深度从深到浅排序
    sorted_dirs = sorted(dir_files.keys(), key=lambda d: d.count(os.sep), reverse=True)

    for dir_path in sorted_dirs:
        if not dir_path:
            continue  # 跳过根目录

        if tracker.is_dir_done(dir_path):
            continue  # 已标记

        # 检查该目录下所有文件是否都已完成
        all_files_done = all(
            tracker.is_file_done(fp) for fp in dir_files[dir_path]
        )
        if not all_files_done:
            continue

        # 检查该目录下所有子目录是否都已完成
        all_subdirs_done = True
        for other_dir in dir_files.keys():
            if other_dir != dir_path and other_dir.startswith(dir_path + os.sep):
                if not tracker.is_dir_done(other_dir):
                    all_subdirs_done = False
                    break

        if all_files_done and all_subdirs_done:
            tracker.mark_dir_done(dir_path)


def do_generate(project_path, output_dir, overwrite, copy_others,
                use_context=True, refresh_context=False, reset_progress=False):
    """
    执行完整的注释生成流程

    Args:
        project_path (str): 项目根目录路径
        output_dir (str or None): 输出目录
        overwrite (bool): 是否覆盖原文件
        copy_others (bool): 是否复制非源码文件
        use_context (bool): 是否使用项目上下文分析（默认 True）
        refresh_context (bool): 是否强制刷新项目上下文（默认 False）
        reset_progress (bool): 是否重置进度记录（默认 False）
    """
    print("=" * 50)
    print("智能代码注释生成器")
    print("=" * 50)

    total_steps = 5 if use_context else 4
    step = 0

    # 第一步：校验配置
    step += 1
    print("\n[%d/%d] 校验配置..." % (step, total_steps))
    is_valid, errors = validate_config()
    if not is_valid:
        print("[配置错误]")
        for err in errors:
            print("  - %s" % err)
        sys.exit(1)
    print("  配置校验通过 ✓")

    # 初始化进度跟踪器
    tracker = ProgressTracker(project_path)
    if reset_progress:
        tracker.reset()

    # 第二步：扫描项目
    step += 1
    print("\n[%d/%d] 扫描项目源码..." % (step, total_steps))
    reader = SourceReader(project_path)
    source_files = reader.scan(progress_tracker=tracker)

    if not source_files:
        print("  未发现可处理的源码文件，退出。")
        return

    print(reader.get_project_summary(source_files))

    # 第三步（可选）：项目上下文分析
    project_context = None
    if use_context:
        step += 1
        print("\n[%d/%d] 分析项目上下文..." % (step, total_steps))
        try:
            analyzer = ProjectContextAnalyzer(project_path)
            project_context = analyzer.get_context(force_refresh=refresh_context)
            if project_context:
                print("  项目上下文加载成功 ✓")
            else:
                print("  项目上下文不可用，将以无上下文模式继续")
        except Exception as e:
            print("  [警告] 项目上下文分析失败: %s" % str(e))
            print("  将以无上下文模式继续")

    # 第 N 步：生成注释
    step += 1
    print("\n[%d/%d] 调用大模型生成注释..." % (step, total_steps))
    generator = CommentGenerator(project_context=project_context)
    writer = CommentWriter(project_path, output_dir, overwrite)

    total = len(source_files)
    start_time = time.time()
    skipped_by_progress = 0

    for idx, sf in enumerate(source_files, 1):
        progress = "[%d/%d]" % (idx, total)

        # 断点恢复：检查文件是否已处理过
        if tracker.is_file_done(sf.rel_path):
            skipped_by_progress += 1
            print("\n%s [跳过-已处理] %s" % (progress, sf.rel_path))
            continue

        print("\n%s 处理: %s (%s, %d bytes)" % (
            progress, sf.rel_path, sf.language, sf.size
        ))

        # 调用大模型生成注释
        commented_code = generator.generate_comment(sf)

        if commented_code:
            # 写入文件
            success = writer.write_file(sf, commented_code)
            if success:
                # 标记文件处理完成
                tracker.mark_file_done(sf.rel_path)
                print("  → 注释生成并写入成功 ✓")
            else:
                print("  → 写入失败 ✗")
        else:
            writer.write_file(sf, None)  # 记录跳过
            print("  → 注释生成失败，跳过 ✗")

    elapsed = time.time() - start_time

    # 目录级断点标记：自底向上推导已完成的目录
    _mark_completed_dirs(source_files, tracker)

    if skipped_by_progress > 0:
        print("\n[断点恢复] 本次跳过 %d 个已处理文件" % skipped_by_progress)

    # 最后一步：复制非源码文件（可选）
    step += 1
    if copy_others and not overwrite:
        print("\n[%d/%d] 复制非源码文件..." % (step, total_steps))
        writer.copy_non_source_files(source_files)
        print("  复制完成 ✓")
    else:
        print("\n[%d/%d] 跳过非源码文件复制" % (step, total_steps))

    # 输出统计
    print("\n" + writer.get_summary())
    print("总耗时: %.1f 秒" % elapsed)
    print("平均每个文件: %.1f 秒" % (elapsed / total if total > 0 else 0))


def main():
    """
    主程序入口
    """
    args = parse_args()

    # 测试 API 模式
    if args.test_api:
        success = do_test_api()
        sys.exit(0 if success else 1)

    project_path = args.project_path

    # 校验项目路径
    if not os.path.isdir(project_path):
        print("[错误] 项目路径不存在或不是目录: %s" % project_path)
        sys.exit(1)

    # 仅扫描模式
    if args.scan_only:
        do_scan_only(project_path)
        return

    # 仅生成上下文模式
    if args.context_only:
        success = do_context_only(project_path, refresh=args.refresh_context)
        sys.exit(0 if success else 1)

    # 覆盖模式下给出警告
    if args.overwrite:
        print("\n⚠️  警告: 覆盖模式将直接修改原始源码文件！")
        print("建议在执行前先备份项目或使用 Git 管理版本。")
        try:
            confirm = raw_input("确认继续? (y/N): ")
        except NameError:
            confirm = input("确认继续? (y/N): ")

        if confirm.strip().lower() != "y":
            print("已取消操作。")
            return

    # 执行注释生成（根据 --no-context 决定是否使用上下文）
    do_generate(
        project_path,
        args.output,
        args.overwrite,
        args.copy_others,
        use_context=not args.no_context,
        refresh_context=args.refresh_context,
        reset_progress=args.reset_progress,
    )


if __name__ == "__main__":
    main()
