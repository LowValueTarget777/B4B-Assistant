#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本管理工具 - 用于管理软件版本号和发布说明
"""

import sys
import argparse
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.common.version_manager import version_manager


def show_version():
    """显示当前版本信息"""
    print("📋 当前版本信息")
    print("=" * 50)
    print(f"版本号: {version_manager.version}")
    print(f"构建号: {version_manager.build_number}")
    print(f"发布日期: {version_manager.release_date}")
    print(f"预发布: {'是' if version_manager.pre_release else '否'}")
    print(f"完整版本: {version_manager.full_version}")
    
    if version_manager.release_notes:
        print(f"发布说明: {version_manager.release_notes}")
    
    print("\n📝 最近更新记录:")
    changelog = version_manager.get_version_info().get("changelog", [])
    for i, entry in enumerate(changelog[:5]):
        print(f"  {i+1}. [{entry['type']}] {entry['description']} ({entry['date']})")


def increment_version(version_type: str):
    """递增版本号"""
    old_version = version_manager.version
    version_manager.increment_version(version_type)
    
    print(f"✅ 版本号已更新: {old_version} → {version_manager.version}")
    print(f"🔢 构建号: {version_manager.build_number}")
    
    version_manager.save_version_info()
    print("💾 版本信息已保存")


def set_version(new_version: str):
    """设置特定版本号"""
    old_version = version_manager.version
    
    if not new_version.startswith('v'):
        new_version = 'v' + new_version
        
    version_manager.version = new_version
    version_manager.build_number += 1
    
    print(f"✅ 版本号已设置: {old_version} → {version_manager.version}")
    
    version_manager.save_version_info()
    print("💾 版本信息已保存")


def add_changelog(entry: str, entry_type: str = "feature"):
    """添加更新日志"""
    version_manager.add_changelog_entry(entry, entry_type)
    
    print(f"✅ 已添加更新日志: [{entry_type}] {entry}")
    
    version_manager.save_version_info()
    print("💾 版本信息已保存")


def set_release_notes(notes: str):
    """设置发布说明"""
    version_manager.release_notes = notes
    
    print(f"✅ 发布说明已设置: {notes}")
    
    version_manager.save_version_info()
    print("💾 版本信息已保存")


def set_pre_release(is_pre: bool):
    """设置是否为预发布版本"""
    version_manager.pre_release = is_pre
    
    status = "预发布" if is_pre else "正式版本"
    print(f"✅ 版本类型已设置为: {status}")
    
    version_manager.save_version_info()
    print("💾 版本信息已保存")


def export_summary():
    """导出版本摘要"""
    summary = version_manager.export_version_summary()
    print(summary)
    
    # 保存到文件
    summary_file = project_root / "VERSION_SUMMARY.md"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"📄 版本摘要已保存到: {summary_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="B4B Assistant 版本管理工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 显示版本信息
    subparsers.add_parser('show', help='显示当前版本信息')
    
    # 递增版本号
    inc_parser = subparsers.add_parser('increment', help='递增版本号')
    inc_parser.add_argument('type', choices=['major', 'minor', 'patch'], 
                           help='版本号类型 (major.minor.patch)')
    
    # 设置版本号
    set_parser = subparsers.add_parser('set', help='设置特定版本号')
    set_parser.add_argument('version', help='新版本号 (如: 1.2.3 或 v1.2.3)')
    
    # 添加更新日志
    log_parser = subparsers.add_parser('changelog', help='添加更新日志')
    log_parser.add_argument('entry', help='更新内容描述')
    log_parser.add_argument('--type', choices=['feature', 'bugfix', 'improvement', 'breaking'],
                           default='feature', help='更新类型')
    
    # 设置发布说明
    notes_parser = subparsers.add_parser('notes', help='设置发布说明')
    notes_parser.add_argument('notes', help='发布说明内容')
    
    # 设置预发布状态
    pre_parser = subparsers.add_parser('prerelease', help='设置预发布状态')
    pre_parser.add_argument('--enable', action='store_true', help='启用预发布')
    pre_parser.add_argument('--disable', action='store_true', help='禁用预发布')
    
    # 导出摘要
    subparsers.add_parser('export', help='导出版本摘要')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'show':
            show_version()
        elif args.command == 'increment':
            increment_version(args.type)
        elif args.command == 'set':
            set_version(args.version)
        elif args.command == 'changelog':
            add_changelog(args.entry, args.type)
        elif args.command == 'notes':
            set_release_notes(args.notes)
        elif args.command == 'prerelease':
            if args.enable:
                set_pre_release(True)
            elif args.disable:
                set_pre_release(False)
            else:
                print("请使用 --enable 或 --disable 参数")
        elif args.command == 'export':
            export_summary()
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
