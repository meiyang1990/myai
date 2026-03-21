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

    # 独立生成项目概要并写入长期记忆
    python main.py /path/to/your/project --generate-summary

    # 独立生成项目概要，附带用户提供的项目简要信息
    python main.py /path/to/your/project --generate-summary --project-info "这是一个电商后台管理系统..."

    # 列出所有已记忆的项目概要
    python main.py --list-memories

    # 删除指定项目的长期记忆
    python main.py /path/to/your/project --remove-memory
"""

from __future__ import annotations

import sys
import os
import argparse
import logging
import time

# 将当前脚本所在目录加入 sys.path，确保模块导入正常
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

from config import validate_config, setup_logging
from source_reader import SourceReader, SourceFile
from comment_generator import CommentGenerator
from comment_writer import CommentWriter
from project_context import ProjectContextAnalyzer
from progress_tracker import ProgressTracker
from memory_store import ProjectMemoryStore

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
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
  python main.py /path/to/project --generate-summary       # 独立生成项目概要并写入长期记忆
  python main.py /path/to/project --generate-summary --project-info "项目简要信息..."
  python main.py --list-memories                            # 列出所有长期记忆
  python main.py /path/to/project --remove-memory           # 删除指定项目记忆
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

    parser.add_argument(
        "--generate-summary",
        action="store_true",
        default=False,
        help="独立生成项目概要并写入长期记忆（不执行注释生成）",
    )

    parser.add_argument(
        "--project-info",
        default=None,
        help="项目简要信息文本（如业务背景、核心功能描述等），配合 --generate-summary 使用",
    )

    parser.add_argument(
        "--list-memories",
        action="store_true",
        default=False,
        help="列出所有已记忆的项目概要",
    )

    parser.add_argument(
        "--remove-memory",
        action="store_true",
        default=False,
        help="删除指定项目的长期记忆",
    )

    args = parser.parse_args()

    # 校验：--list-memories 模式不需要项目路径
    if args.list_memories:
        return args

    # 校验：非 test-api 模式必须提供项目路径
    if not args.test_api and not args.project_path:
        parser.error("请提供目标项目路径，或使用 --test-api 测试 API 连接")

    return args


def do_test_api() -> bool:
    """
    测试火山引擎 API 连接
    """
    logger.info("=" * 50)
    logger.info("测试火山引擎大模型 API 连接...")
    logger.info("=" * 50)

    # 校验配置
    is_valid, errors = validate_config()
    if not is_valid:
        logger.error("配置错误")
        for err in errors:
            logger.error(f"  - {err}")
        return False

    generator = CommentGenerator()
    success, message = generator.test_connection()
    logger.info(message)
    return success


def do_scan_only(project_path: str) -> None:
    """
    仅扫描项目，列出将处理的文件

    Args:
        project_path: 项目根目录路径
    """
    logger.info("=" * 50)
    logger.info(f"扫描项目: {project_path}")
    logger.info("=" * 50)

    reader = SourceReader(project_path)
    source_files = reader.scan()

    logger.info(reader.get_project_summary(source_files))

    if source_files:
        logger.info("文件列表:")
        for i, sf in enumerate(source_files, 1):
            logger.info(f"  {i:3d}. [{sf.language}] {sf.rel_path} ({sf.size} bytes)")


def do_context_only(project_path: str, refresh: bool) -> bool:
    """
    仅生成项目上下文概要（不执行注释生成）

    Args:
        project_path: 项目根目录路径
        refresh: 是否强制刷新
    """
    logger.info("=" * 50)
    logger.info("项目上下文分析")
    logger.info("=" * 50)

    # 校验配置
    is_valid, errors = validate_config()
    if not is_valid:
        logger.error("配置错误")
        for err in errors:
            logger.error(f"  - {err}")
        return False

    logger.info(f"正在分析项目: {project_path}")
    analyzer = ProjectContextAnalyzer(project_path)
    summary = analyzer.get_context(force_refresh=refresh)

    if summary:
        logger.info("=" * 50)
        logger.info("项目概要内容：")
        logger.info("=" * 50)
        logger.info(summary)
        logger.info("=" * 50)
        return True
    else:
        logger.error("未能生成项目概要")
        return False


def do_generate_summary(project_path: str, project_info: str | None, refresh: bool) -> bool:
    """
    独立生成项目概要并写入长期记忆

    接收项目路径和用户提供的项目简要信息，调用大模型生成概要，
    结果同时写入项目内缓存和全局长期记忆。

    Args:
        project_path: 项目本地根目录路径
        project_info: 用户提供的项目简要信息文本（可选）
        refresh: 是否强制刷新（忽略已有缓存/记忆）

    Returns:
        是否生成成功
    """
    logger.info("=" * 50)
    logger.info("独立项目概要生成（含长期记忆）")
    logger.info("=" * 50)

    # 校验配置
    is_valid, errors = validate_config()
    if not is_valid:
        logger.error("配置错误")
        for err in errors:
            logger.error(f"  - {err}")
        return False

    memory_store = ProjectMemoryStore()

    # 如果不强制刷新，先尝试从长期记忆加载
    if not refresh:
        memory_entry = memory_store.load_project_summary(project_path)
        if memory_entry is not None:
            summary = memory_entry.get("summary", "")
            logger.info("从长期记忆中加载到已有概要：")
            logger.info("=" * 50)
            logger.info(summary)
            logger.info("=" * 50)
            logger.info("如需重新生成，请添加 --refresh-context 参数")
            return True

    # 调用 ProjectContextAnalyzer 生成概要
    logger.info(f"正在分析项目: {project_path}")
    if project_info:
        logger.info(f"用户提供的项目信息: {project_info[:200]}...")

    analyzer = ProjectContextAnalyzer(project_path)
    summary = analyzer.get_context(force_refresh=True, project_info=project_info)

    if not summary:
        logger.error("未能生成项目概要")
        return False

    # 写入长期记忆
    memory_store.save_project_summary(project_path, summary, project_info)

    logger.info("=" * 50)
    logger.info("项目概要内容：")
    logger.info("=" * 50)
    logger.info(summary)
    logger.info("=" * 50)
    logger.info(f"概要已写入长期记忆（{memory_store.store_file}）")
    return True


def do_list_memories() -> None:
    """
    列出所有已记忆的项目概要
    """
    logger.info("=" * 50)
    logger.info("已记忆的项目概要列表")
    logger.info("=" * 50)

    memory_store = ProjectMemoryStore()
    memories = memory_store.list_project_summaries()

    if not memories:
        logger.info("长期记忆为空，暂无已记忆的项目。")
        logger.info(f"存储路径: {memory_store.store_file}")
        return

    for i, entry in enumerate(memories, 1):
        import datetime
        ts = entry.get("timestamp", 0)
        time_str = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else "未知"
        project_info = entry.get("project_info")
        info_label = f" | 用户信息: {project_info[:50]}..." if project_info else ""

        logger.info(f"  {i}. {entry['project_path']}")
        logger.info(f"     时间: {time_str}{info_label}")
        logger.info(f"     概要预览: {entry['summary_preview']}")
        logger.info("")

    logger.info(f"共 {len(memories)} 个项目记忆，存储路径: {memory_store.store_file}")


def do_remove_memory(project_path: str) -> bool:
    """
    删除指定项目的长期记忆

    Args:
        project_path: 项目根目录路径

    Returns:
        是否删除成功
    """
    logger.info("=" * 50)
    logger.info(f"删除项目长期记忆: {project_path}")
    logger.info("=" * 50)

    memory_store = ProjectMemoryStore()
    success = memory_store.remove_project_summary(project_path)
    if success:
        logger.info("删除成功")
    else:
        logger.error("删除失败")
    return success


def _mark_completed_dirs(source_files: list[SourceFile], tracker: ProgressTracker) -> None:
    """
    自底向上推导并标记已完成的目录

    逻辑：收集所有文件所属的目录路径，对每个目录检查其下所有文件是否都已完成，
    如果是则标记该目录为已完成。从最深层目录开始检查。

    Args:
        source_files: SourceFile 对象列表
        tracker: 进度跟踪器实例
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


def do_generate(project_path: str, output_dir: str | None, overwrite: bool, copy_others: bool,
                use_context: bool = True, refresh_context: bool = False,
                reset_progress: bool = False) -> None:
    """
    执行完整的注释生成流程

    Args:
        project_path: 项目根目录路径
        output_dir: 输出目录
        overwrite: 是否覆盖原文件
        copy_others: 是否复制非源码文件
        use_context: 是否使用项目上下文分析（默认 True）
        refresh_context: 是否强制刷新项目上下文（默认 False）
        reset_progress: 是否重置进度记录（默认 False）
    """
    logger.info("=" * 50)
    logger.info("智能代码注释生成器")
    logger.info("=" * 50)

    total_steps = 5 if use_context else 4
    step = 0

    # 第一步：校验配置
    step += 1
    logger.info(f"[{step}/{total_steps}] 校验配置...")
    is_valid, errors = validate_config()
    if not is_valid:
        logger.error("配置错误")
        for err in errors:
            logger.error(f"  - {err}")
        sys.exit(1)
    logger.info("  配置校验通过 ✓")

    # 初始化进度跟踪器
    tracker = ProgressTracker(project_path)
    if reset_progress:
        tracker.reset()

    # 第二步：扫描项目
    step += 1
    logger.info(f"[{step}/{total_steps}] 扫描项目源码...")
    reader = SourceReader(project_path)
    source_files = reader.scan(progress_tracker=tracker)

    if not source_files:
        logger.info("  未发现可处理的源码文件，退出。")
        return

    logger.info(reader.get_project_summary(source_files))

    # 第三步（可选）：项目上下文分析（集成长期记忆）
    project_context = None
    if use_context:
        step += 1
        logger.info(f"[{step}/{total_steps}] 分析项目上下文...")

        # 优先从长期记忆加载项目概要
        memory_store = ProjectMemoryStore()
        if not refresh_context:
            memory_entry = memory_store.load_project_summary(project_path)
            if memory_entry is not None:
                project_context = memory_entry.get("summary")
                if project_context:
                    logger.info("  项目上下文从长期记忆加载成功 ✓")

        # 如果长期记忆中无概要，退回自动分析
        if project_context is None:
            try:
                analyzer = ProjectContextAnalyzer(project_path)
                project_context = analyzer.get_context(force_refresh=refresh_context)
                if project_context:
                    logger.info("  项目上下文分析成功 ✓")
                    # 新生成的概要自动写入长期记忆
                    memory_store.save_project_summary(project_path, project_context)
                    logger.info("  概要已同步写入长期记忆")
                else:
                    logger.warning("  项目上下文不可用，将以无上下文模式继续")
            except Exception as e:
                logger.warning(f"  项目上下文分析失败: {e}")
                logger.warning("  将以无上下文模式继续")

    # 第 N 步：生成注释
    step += 1
    logger.info(f"[{step}/{total_steps}] 调用大模型生成注释...")
    generator = CommentGenerator(project_context=project_context)
    writer = CommentWriter(project_path, output_dir, overwrite)

    total = len(source_files)
    start_time = time.time()
    skipped_by_progress = 0

    for idx, sf in enumerate(source_files, 1):
        progress = f"[{idx}/{total}]"

        # 断点恢复：检查文件是否已处理过
        if tracker.is_file_done(sf.rel_path):
            skipped_by_progress += 1
            logger.info(f"{progress} [跳过-已处理] {sf.rel_path}")
            continue

        logger.info(f"{progress} 处理: {sf.rel_path} ({sf.language}, {sf.size} bytes)")

        # 调用大模型生成注释
        commented_code = generator.generate_comment(sf)

        if commented_code:
            # 写入文件
            success = writer.write_file(sf, commented_code)
            if success:
                # 标记文件处理完成
                tracker.mark_file_done(sf.rel_path)
                logger.info("  → 注释生成并写入成功 ✓")
            else:
                logger.error("  → 写入失败 ✗")
        else:
            writer.write_file(sf, None)  # 记录跳过
            logger.error("  → 注释生成失败，跳过 ✗")

    elapsed = time.time() - start_time

    # 目录级断点标记：自底向上推导已完成的目录
    _mark_completed_dirs(source_files, tracker)

    if skipped_by_progress > 0:
        logger.info(f"[断点恢复] 本次跳过 {skipped_by_progress} 个已处理文件")

    # 最后一步：复制非源码文件（可选）
    step += 1
    if copy_others and not overwrite:
        logger.info(f"[{step}/{total_steps}] 复制非源码文件...")
        writer.copy_non_source_files(source_files)
        logger.info("  复制完成 ✓")
    else:
        logger.info(f"[{step}/{total_steps}] 跳过非源码文件复制")

    # 输出统计
    logger.info(writer.get_summary())
    logger.info(f"总耗时: {elapsed:.1f} 秒")
    logger.info(f"平均每个文件: {elapsed / total if total > 0 else 0:.1f} 秒")


def main() -> None:
    """
    主程序入口
    """
    setup_logging()
    args = parse_args()

    # 测试 API 模式
    if args.test_api:
        success = do_test_api()
        sys.exit(0 if success else 1)

    # 列出所有长期记忆模式（不需要项目路径）
    if args.list_memories:
        do_list_memories()
        return

    project_path = args.project_path

    # 校验项目路径
    if not os.path.isdir(project_path):
        logger.error(f"项目路径不存在或不是目录: {project_path}")
        sys.exit(1)

    # 仅扫描模式
    if args.scan_only:
        do_scan_only(project_path)
        return

    # 删除长期记忆模式
    if args.remove_memory:
        success = do_remove_memory(project_path)
        sys.exit(0 if success else 1)

    # 独立生成项目概要模式
    if args.generate_summary:
        success = do_generate_summary(
            project_path,
            project_info=args.project_info,
            refresh=args.refresh_context,
        )
        sys.exit(0 if success else 1)

    # 仅生成上下文模式
    if args.context_only:
        success = do_context_only(project_path, refresh=args.refresh_context)
        sys.exit(0 if success else 1)

    # 覆盖模式下给出警告
    if args.overwrite:
        logger.warning("覆盖模式将直接修改原始源码文件！")
        logger.warning("建议在执行前先备份项目或使用 Git 管理版本。")
        confirm = input("确认继续? (y/N): ")

        if confirm.strip().lower() != "y":
            logger.info("已取消操作。")
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
