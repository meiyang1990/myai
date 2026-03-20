# -*- coding: utf-8 -*-
"""
智能代码注释生成器 - 主程序入口

基于 LangChain + 火山引擎大模型，自动为源码文件生成高质量中文注释。

使用方式：
    python main.py <项目路径> [选项]

示例：
    # 基本用法：扫描项目并生成注释到新目录
    python main.py /path/to/your/project

    # 指定输出目录
    python main.py /path/to/your/project -o /path/to/output

    # 覆盖原文件（谨慎使用）
    python main.py /path/to/your/project --overwrite

    # 仅测试 API 连接
    python main.py --test-api

    # 仅扫描不生成（预览将处理哪些文件）
    python main.py /path/to/your/project --scan-only
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
  python main.py /path/to/project              # 生成注释到新目录
  python main.py /path/to/project -o ./output   # 指定输出目录
  python main.py /path/to/project --overwrite   # 覆盖原文件
  python main.py --test-api                     # 测试 API 连接
  python main.py /path/to/project --scan-only   # 仅扫描预览
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


def do_generate(project_path, output_dir, overwrite, copy_others):
    """
    执行完整的注释生成流程

    Args:
        project_path (str): 项目根目录路径
        output_dir (str or None): 输出目录
        overwrite (bool): 是否覆盖原文件
        copy_others (bool): 是否复制非源码文件
    """
    print("=" * 50)
    print("智能代码注释生成器")
    print("=" * 50)

    # 第一步：校验配置
    print("\n[1/4] 校验配置...")
    is_valid, errors = validate_config()
    if not is_valid:
        print("[配置错误]")
        for err in errors:
            print("  - %s" % err)
        sys.exit(1)
    print("  配置校验通过 ✓")

    # 第二步：扫描项目
    print("\n[2/4] 扫描项目源码...")
    reader = SourceReader(project_path)
    source_files = reader.scan()

    if not source_files:
        print("  未发现可处理的源码文件，退出。")
        return

    print(reader.get_project_summary(source_files))

    # 第三步：生成注释
    print("\n[3/4] 调用大模型生成注释...")
    generator = CommentGenerator()
    writer = CommentWriter(project_path, output_dir, overwrite)

    total = len(source_files)
    start_time = time.time()

    for idx, sf in enumerate(source_files, 1):
        progress = "[%d/%d]" % (idx, total)
        print("\n%s 处理: %s (%s, %d bytes)" % (
            progress, sf.rel_path, sf.language, sf.size
        ))

        # 调用大模型生成注释
        commented_code = generator.generate_comment(sf)

        if commented_code:
            # 写入文件
            success = writer.write_file(sf, commented_code)
            if success:
                print("  → 注释生成并写入成功 ✓")
            else:
                print("  → 写入失败 ✗")
        else:
            writer.write_file(sf, None)  # 记录跳过
            print("  → 注释生成失败，跳过 ✗")

    elapsed = time.time() - start_time

    # 第四步：复制非源码文件（可选）
    if copy_others and not overwrite:
        print("\n[4/4] 复制非源码文件...")
        writer.copy_non_source_files(source_files)
        print("  复制完成 ✓")
    else:
        print("\n[4/4] 跳过非源码文件复制")

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

    # 执行注释生成
    do_generate(project_path, args.output, args.overwrite, args.copy_others)


if __name__ == "__main__":
    main()
