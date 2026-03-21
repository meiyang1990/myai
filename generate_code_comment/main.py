# -*- coding: utf-8 -*-
"""
智能代码注释生成器 - 主程序入口

基于 LangChain + 火山引擎大模型，自动为源码文件生成高质量中文注释。
支持项目上下文分析，让大模型理解项目全局架构后生成更有深度的注释。

核心参数说明：
    --project_root_dir  项目根目录路径，仅用于检索项目概要信息（长期记忆/上下文分析）、
                        加载 .gitignore 规则、以及进度缓存存放。不参与注释生成的核心处理。
    --source_path       实际要处理的源码路径（文件或目录），为注释生成的核心处理对象。
                        输出目录默认基于此参数计算。

使用方式：
    python main.py <子命令> [参数...]

子命令：
    generate_comment   为源码生成中文注释（基于 --source_path 处理）
    generate_summary   生成项目概要并写入长期记忆
    test_api           测试火山引擎 API 连接
    scan_only          仅扫描并列出将处理的文件
    context_only       仅生成项目上下文概要
    list_memories      列出所有已记忆的项目概要
    remove_memory      删除指定项目的长期记忆

示例：
    # 为项目某个子目录生成中文注释（输出到 <source_path>_commented）
    python main.py generate_comment --project_root_dir /path/to/project --source_path /path/to/project/src

    # 为单个文件生成中文注释
    python main.py generate_comment --project_root_dir /path/to/project --source_path /path/to/project/src/Main.java

    # 指定输出目录
    python main.py generate_comment --project_root_dir /path/to/project --source_path /path/to/project/src -o /path/to/output

    # 覆盖原文件（直接写回 --source_path 原位，谨慎使用）
    python main.py generate_comment --project_root_dir /path/to/project --source_path /path/to/project/src --overwrite

    # 强制重新处理所有文件（忽略进度记录，即使之前已处理过也重新生成注释）
    python main.py generate_comment --project_root_dir /path/to/project --source_path /path/to/project/src --force

    # 生成项目概要并写入长期记忆（--project-info 为必填参数）
    python main.py generate_summary --project_root_dir /path/to/your/project --project-info "这是一个电商后台管理系统..."

    # 测试 API 连接
    python main.py test_api --project_root_dir /path/to/your/project

    # 仅扫描不生成（预览将处理哪些文件）
    python main.py scan_only --project_root_dir /path/to/your/project

    # 仅生成项目上下文概要
    python main.py context_only --project_root_dir /path/to/your/project

    # 列出所有已记忆的项目概要
    python main.py list_memories --project_root_dir /path/to/your/project

    # 删除指定项目的长期记忆
    python main.py remove_memory --project_root_dir /path/to/your/project
"""

from __future__ import annotations

import sys
import os
import argparse
import logging
import time
from typing import Callable

# 将当前脚本所在目录加入 sys.path，确保模块导入正常
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

from config import validate_config, setup_logging, LOG_FILE, has_commented_marker
from source_reader import SourceReader, SourceFile
from comment_generator import CommentGenerator
from comment_writer import CommentWriter
from project_context import ProjectContextAnalyzer
from progress_tracker import ProgressTracker
from memory_store import ProjectMemoryStore

logger = logging.getLogger(__name__)


def _log_summary_to_file(project_path: str, summary: str) -> None:
    """
    将项目概要信息完整写入日志文件

    以清晰的分隔格式逐行写入，方便在日志文件中定位和阅读。

    Args:
        project_path: 项目根目录路径
        summary: 项目概要文本
    """
    logger.info("=" * 60)
    logger.info(f"[项目概要] 项目路径: {project_path}")
    logger.info("=" * 60)
    for line in summary.splitlines():
        logger.info(line)
    logger.info("=" * 60)
    logger.info("[项目概要] END")
    logger.info("=" * 60)


def parse_args() -> argparse.Namespace:
    """
    解析命令行参数（基于 subparsers 子命令路由）

    使用 argparse.add_subparsers 将各功能注册为独立子命令，
    每个子命令只声明自己需要的参数，调用方式更清晰。

    Returns:
        argparse.Namespace: 解析后的参数对象，包含 method 字段标识子命令
    """
    parser = argparse.ArgumentParser(
        description="智能代码注释生成器 - 基于 AI 自动为源码添加中文注释",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py generate_comment --project_root_dir /path/to/project --source_path /path/to/project/src             # 处理子目录（输出到 src_commented）
  python main.py generate_comment --project_root_dir /path/to/project --source_path /path/to/project/src/Main.java   # 处理单文件
  python main.py generate_comment --project_root_dir /path/to/project --source_path /path/to/project/src -o ./output # 指定输出目录
  python main.py generate_comment --project_root_dir /path/to/project --source_path /path/to/project/src --overwrite # 覆盖原文件（写回 source_path 原位）
  python main.py generate_comment --project_root_dir /path/to/project --source_path /path/to/project/src --force    # 强制重新处理（忽略进度记录）
  python main.py generate_summary --project_root_dir /path/to/project --project-info "项目简要信息..."  # 生成项目概要
  python main.py test_api --project_root_dir /path/to/project                      # 测试 API 连接
  python main.py scan_only --project_root_dir /path/to/project                     # 仅扫描预览
  python main.py context_only --project_root_dir /path/to/project                  # 仅生成上下文概要
  python main.py list_memories --project_root_dir /path/to/project                 # 列出所有长期记忆
  python main.py remove_memory --project_root_dir /path/to/project                 # 删除指定项目记忆
        """,
    )

    subparsers = parser.add_subparsers(dest="method", help="指定要执行的方法")

    # ---- generate_summary：生成项目概要并写入长期记忆 ----
    sp_summary = subparsers.add_parser(
        "generate_summary",
        help="生成项目概要并写入长期记忆",
        description="分析项目源码结构，调用大模型生成项目概要，结果同时写入项目缓存和全局长期记忆。",
    )
    sp_summary.add_argument("--project_root_dir", required=True, help="项目源码根目录路径")
    sp_summary.add_argument(
        "--project-info", required=True,
        help="项目简要信息文本（如业务背景、核心功能描述等），可提升概要质量",
    )
    sp_summary.add_argument(
        "--refresh-context", action="store_true", default=False,
        help="强制刷新，忽略已有缓存/记忆，重新生成概要",
    )

    # ---- generate_comment：为源码生成中文注释 ----
    sp_comment = subparsers.add_parser(
        "generate_comment",
        help="为源码生成中文注释（基于 --source_path 处理）",
        description=(
            "扫描 --source_path 指定的源码文件或目录，调用大模型生成高质量中文注释。"
            "--project_root_dir 仅用于检索项目概要信息和加载 .gitignore 规则。"
        ),
    )
    sp_comment.add_argument(
        "--project_root_dir", required=True,
        help="项目根目录路径（仅用于检索项目概要/长期记忆、加载 .gitignore 规则和进度缓存存放）",
    )
    sp_comment.add_argument(
        "--source_path", required=True,
        help=(
            "要处理的源码路径（文件或目录），为注释生成的核心处理对象。"
            "必须是 --project_root_dir 的子路径或与其相同。"
            "目录时递归处理其下所有源码文件，单文件时仅处理该文件。"
            "默认输出目录基于此参数计算（<source_path>_commented）。"
        ),
    )
    sp_comment.add_argument(
        "-o", "--output", default=None,
        help="输出目录路径（默认为 <source_path>_commented）",
    )
    sp_comment.add_argument(
        "--overwrite", action="store_true", default=False,
        help="直接覆盖 --source_path 原位文件（谨慎使用，建议先备份）",
    )
    sp_comment.add_argument(
        "--copy-others", action="store_true", default=False,
        help="在输出模式下，同时复制非源码文件到输出目录",
    )
    sp_comment.add_argument(
        "--no-context", action="store_true", default=False,
        help="跳过项目上下文分析，使用无上下文模式生成注释",
    )
    sp_comment.add_argument(
        "--refresh-context", action="store_true", default=False,
        help="强制刷新项目上下文概要缓存",
    )
    sp_comment.add_argument(
        "--reset-progress", action="store_true", default=False,
        help="重置进度记录，从头处理所有文件",
    )
    sp_comment.add_argument(
        "--force", action="store_true", default=False,
        help="强制重新处理所有文件和目录，忽略进度记录中已处理的状态（不删除进度文件，处理完成后更新进度）",
    )

    # ---- test_api：测试 API 连接 ----
    sp_test = subparsers.add_parser(
        "test_api",
        help="测试火山引擎 API 连接是否正常",
        description="向火山引擎大模型发送测试请求，验证 API Key 和 Endpoint 配置是否正确。",
    )
    sp_test.add_argument("--project_root_dir", required=True, help="项目源码根目录路径")

    # ---- scan_only：仅扫描项目 ----
    sp_scan = subparsers.add_parser(
        "scan_only",
        help="仅扫描并列出将处理的文件",
        description="递归扫描项目目录，列出所有将被处理的源码文件，不执行注释生成。",
    )
    sp_scan.add_argument("--project_root_dir", required=True, help="项目源码根目录路径")

    # ---- context_only：仅生成项目上下文概要 ----
    sp_ctx = subparsers.add_parser(
        "context_only",
        help="仅生成项目上下文概要",
        description="分析项目结构并生成上下文概要，不执行注释生成。",
    )
    sp_ctx.add_argument("--project_root_dir", required=True, help="项目源码根目录路径")
    sp_ctx.add_argument(
        "--refresh-context", action="store_true", default=False,
        help="强制刷新，忽略已有缓存",
    )

    # ---- list_memories：列出所有长期记忆 ----
    sp_list = subparsers.add_parser(
        "list_memories",
        help="列出所有已记忆的项目概要",
        description="读取全局长期记忆存储，列出所有已保存的项目概要信息。",
    )
    sp_list.add_argument("--project_root_dir", required=True, help="项目源码根目录路径")

    # ---- remove_memory：删除指定项目的长期记忆 ----
    sp_rm = subparsers.add_parser(
        "remove_memory",
        help="删除指定项目的长期记忆",
        description="从全局长期记忆中移除指定项目的概要记录。",
    )
    sp_rm.add_argument("--project_root_dir", required=True, help="项目源码根目录路径")

    args = parser.parse_args()

    # 未指定子命令时打印帮助并退出
    if args.method is None:
        parser.print_help()
        sys.exit(1)

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
        project_info: 用户提供的项目简要信息文本（必填）
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
            _log_summary_to_file(project_path, summary)
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

    # 将完整概要写入日志文件
    _log_summary_to_file(project_path, summary)
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
                reset_progress: bool = False, target_path: str | None = None,
                force: bool = False) -> None:
    """
    执行完整的注释生成流程

    参数职责：
    - project_path: 项目根目录路径，**仅用于**检索项目概要（长期记忆/上下文分析）、
      加载 .gitignore 规则、以及进度跟踪缓存的存放基准
    - target_path: 实际要处理的源码路径（文件或目录），为注释生成的核心处理对象

    Args:
        project_path: 项目根目录路径（用于元信息检索和 .gitignore 加载）
        output_dir: 输出目录
        overwrite: 是否覆盖原文件
        copy_others: 是否复制非源码文件
        use_context: 是否使用项目上下文分析（默认 True）
        refresh_context: 是否强制刷新项目上下文（默认 False）
        reset_progress: 是否重置进度记录（默认 False）
        target_path: 要处理的源码路径（文件或目录），为 None 时默认使用 project_path
        force: 是否强制重新处理所有文件（忽略进度记录，默认 False）
    """
    logger.info("=" * 50)
    logger.info("智能代码注释生成器")
    if force:
        logger.info("  --force 模式：忽略进度记录，强制重新处理所有文件")
    logger.info("=" * 50)

    # 确定实际处理路径（--source_path 为核心处理对象）
    effective_target = target_path if target_path else project_path
    is_single_file = os.path.isfile(effective_target)

    if is_single_file:
        logger.info(f"模式: 单文件处理")
        logger.info(f"目标文件: {effective_target}")
    else:
        logger.info(f"模式: 目录递归处理")
        logger.info(f"目标目录: {effective_target}")
    logger.info(f"项目根目录（元信息）: {project_path}")

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

    # 初始化进度跟踪器（基于 project_path，进度以项目为单位管理）
    tracker = ProgressTracker(project_path)
    if reset_progress:
        tracker.reset()

    # 第二步：扫描源码
    # SourceReader 基于 project_path 初始化（加载 .gitignore），但扫描 target_path
    # --force 模式下不传 progress_tracker，这样扫描时不会跳过已完成目录
    step += 1
    logger.info(f"[{step}/{total_steps}] 扫描源码...")
    reader = SourceReader(project_path)

    if is_single_file:
        source_files = reader.scan_path(effective_target)
    else:
        scan_tracker = None if force else tracker
        source_files = reader.scan_path(effective_target, progress_tracker=scan_tracker)

    if not source_files:
        logger.info("  未发现可处理的源码文件，退出。")
        return

    logger.info(reader.get_project_summary(source_files))

    # 第三步（可选）：项目上下文分析（集成长期记忆）
    # 项目概要基于 project_path 检索，这是 --project_root_dir 的核心用途
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
                logger.error(f"项目上下文分析失败: {e}")
                raise

    # 第 N 步：生成注释
    # CommentWriter 基于 effective_target 初始化（输出路径以 source_path 为基准）
    step += 1
    logger.info(f"[{step}/{total_steps}] 调用大模型生成注释...")
    generator = CommentGenerator(project_context=project_context)
    writer = CommentWriter(effective_target, output_dir, overwrite)

    total = len(source_files)
    start_time = time.time()
    skipped_by_progress = 0
    skipped_by_marker = 0

    for idx, sf in enumerate(source_files, 1):
        progress = f"[{idx}/{total}]"

        # 断点恢复：检查文件是否已处理过（--force 模式跳过此检查）
        if not force and tracker.is_file_done(sf.rel_path):
            skipped_by_progress += 1
            logger.info(f"{progress} [跳过-已处理] {sf.rel_path}")
            continue

        # 已注释标记检测：读取源码内容，检查是否包含"已处理"标记注释
        if sf.content and has_commented_marker(sf.content, sf.language):
            skipped_by_marker += 1
            tracker.mark_file_done(sf.rel_path)
            logger.info(f"{progress} [跳过-已包含注释标记] {sf.rel_path}")
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
    if skipped_by_marker > 0:
        logger.info(f"[注释标记] 本次跳过 {skipped_by_marker} 个已包含注释标记的文件")

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


def _validate_project_path(project_path: str) -> None:
    """
    校验项目路径是否存在且为目录

    Args:
        project_path: 项目根目录路径

    Raises:
        SystemExit: 路径不存在或不是目录时退出
    """
    if not os.path.isdir(project_path):
        logger.error(f"项目路径不存在或不是目录: {project_path}")
        sys.exit(1)


def _handle_generate_summary(args: argparse.Namespace) -> None:
    """generate_summary 子命令处理"""
    _validate_project_path(args.project_root_dir)
    success = do_generate_summary(
        args.project_root_dir,
        project_info=args.project_info,
        refresh=args.refresh_context,
    )
    if success:
        log_path = os.path.abspath(LOG_FILE)
        print(f"[generate_summary] 项目概要已写入日志文件: {log_path}")
    sys.exit(0 if success else 1)


def _handle_generate_comment(args: argparse.Namespace) -> None:
    """generate_comment 子命令处理"""
    _validate_project_path(args.project_root_dir)

    # 校验 --source_path：必须存在且为文件或目录
    source_path = os.path.abspath(args.source_path)
    if not os.path.exists(source_path):
        logger.error(f"--source_path 路径不存在: {source_path}")
        sys.exit(1)
    if not os.path.isfile(source_path) and not os.path.isdir(source_path):
        logger.error(f"--source_path 既不是文件也不是目录: {source_path}")
        sys.exit(1)

    # 校验 --source_path 必须是 --project_root_dir 的子路径或同一路径
    real_source = os.path.realpath(source_path)
    real_project_root = os.path.realpath(args.project_root_dir)
    if real_source != real_project_root and not real_source.startswith(real_project_root + os.sep):
        logger.error(
            f"--source_path 必须是 --project_root_dir 的子路径或与其相同。\n"
            f"  --project_root_dir (解析后): {real_project_root}\n"
            f"  --source_path      (解析后): {real_source}"
        )
        sys.exit(1)

    # 覆盖模式下给出警告
    if args.overwrite:
        logger.warning("覆盖模式将直接修改原始源码文件！")
        logger.warning("建议在执行前先备份项目或使用 Git 管理版本。")
        confirm = input("确认继续? (y/N): ")
        if confirm.strip().lower() != "y":
            logger.info("已取消操作。")
            return

    do_generate(
        args.project_root_dir,
        args.output,
        args.overwrite,
        args.copy_others,
        use_context=not args.no_context,
        refresh_context=args.refresh_context,
        reset_progress=args.reset_progress,
        target_path=source_path,
        force=args.force,
    )


def _handle_test_api(args: argparse.Namespace) -> None:
    """test_api 子命令处理"""
    _validate_project_path(args.project_root_dir)
    success = do_test_api()
    sys.exit(0 if success else 1)


def _handle_scan_only(args: argparse.Namespace) -> None:
    """scan_only 子命令处理"""
    _validate_project_path(args.project_root_dir)
    do_scan_only(args.project_root_dir)


def _handle_context_only(args: argparse.Namespace) -> None:
    """context_only 子命令处理"""
    _validate_project_path(args.project_root_dir)
    success = do_context_only(args.project_root_dir, refresh=args.refresh_context)
    sys.exit(0 if success else 1)


def _handle_list_memories(args: argparse.Namespace) -> None:
    """list_memories 子命令处理"""
    _validate_project_path(args.project_root_dir)
    do_list_memories()


def _handle_remove_memory(args: argparse.Namespace) -> None:
    """remove_memory 子命令处理"""
    _validate_project_path(args.project_root_dir)
    success = do_remove_memory(args.project_root_dir)
    sys.exit(0 if success else 1)


# 方法分派表：子命令名 -> 处理函数
METHOD_DISPATCH: dict[str, Callable[[argparse.Namespace], None]] = {
    "generate_summary": _handle_generate_summary,
    "generate_comment": _handle_generate_comment,
    "test_api": _handle_test_api,
    "scan_only": _handle_scan_only,
    "context_only": _handle_context_only,
    "list_memories": _handle_list_memories,
    "remove_memory": _handle_remove_memory,
}


def main() -> None:
    """
    主程序入口

    基于 argparse subparsers 子命令路由，通过 METHOD_DISPATCH 分派表
    将各子命令映射到对应的处理函数。
    """
    setup_logging()
    args = parse_args()

    handler = METHOD_DISPATCH.get(args.method)
    if handler is None:
        logger.error(f"未知的方法: {args.method}")
        sys.exit(1)

    handler(args)


if __name__ == "__main__":
    main()
