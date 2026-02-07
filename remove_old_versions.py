#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import re
import shutil
from pathlib import Path
from collections import defaultdict

try:
    from packaging import version
except ImportError:
    print("错误: 需要安装 packaging 模块")
    print("请运行: pip install packaging")
    sys.exit(1)


def extract_prefix_and_version(name):
    """
    从文件名/文件夹名中提取前缀和版本号
    
    例如:
    - autoconf-2.72.tar.xz -> (autoconf-, 2.72)
    - autoconf-archive-2023.02.20.tar.xz -> (autoconf-archive-, 2023.02.20)
    - autoconf-2.71.tar.xz -> (autoconf-, 2.71)
    """
    # 匹配模式: 前缀-版本号.扩展名 或 前缀-版本号
    # 版本号以数字开头，可能包含数字、点和连字符
    # 使用非贪婪匹配找到最后一个以数字开头的版本号部分
    pattern = r'^(.+?)-(\d+(?:\.\d+)*(?:\.\d+)?(?:-\d+)?)(?:\.[^.]+)*$'
    match = re.match(pattern, name)
    
    if match:
        prefix = match.group(1) + '-'
        version_str = match.group(2)
        return prefix, version_str
    
    return None, None


def compare_versions(ver1, ver2):
    """
    比较两个版本号字符串
    返回: -1 if ver1 < ver2, 0 if ver1 == ver2, 1 if ver1 > ver2
    """
    try:
        # 使用 packaging.version 进行版本比较
        v1 = version.parse(ver1)
        v2 = version.parse(ver2)
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            return 0
    except Exception:
        # 如果版本解析失败，使用字符串比较作为后备
        if ver1 < ver2:
            return -1
        elif ver1 > ver2:
            return 1
        else:
            return 0


def find_files_by_prefix(target_dir):
    """
    扫描目标目录，按前缀分组文件和文件夹
    返回: {prefix: [(name, version_str, full_path), ...]}
    """
    prefix_groups = defaultdict(list)
    target_path = Path(target_dir)
    
    if not target_path.exists():
        print(f"错误: 目录不存在: {target_dir}")
        return {}
    
    if not target_path.is_dir():
        print(f"错误: 不是目录: {target_dir}")
        return {}
    
    # 遍历目录中的所有项
    for item in target_path.iterdir():
        name = item.name
        prefix, version_str = extract_prefix_and_version(name)
        
        if prefix and version_str:
            prefix_groups[prefix].append((name, version_str, item))
    
    return prefix_groups


def remove_old_versions(target_dir, dry_run=False):
    """
    删除有共同前缀但版本号更旧的文件/文件夹
    
    Args:
        target_dir: 目标目录路径
        dry_run: 如果为True，只显示将要删除的文件，不实际删除
    """
    print(f"扫描目录: {target_dir}")
    if dry_run:
        print("模式: 预览模式（不会实际删除文件）")
    print()
    
    prefix_groups = find_files_by_prefix(target_dir)
    
    if not prefix_groups:
        print("未找到符合模式的文件/文件夹（格式: 前缀-版本号）")
        return
    
    total_deleted = 0
    
    for prefix, items in prefix_groups.items():
        if len(items) < 2:
            # 如果只有一个文件，不需要删除
            continue
        
        print(f"前缀组: {prefix}")
        print(f"  找到 {len(items)} 个文件/文件夹:")
        
        # 按版本号排序（从高到低）
        sorted_items = sorted(items, key=lambda x: version.parse(x[1]), reverse=True)
        
        # 显示所有文件
        for name, ver, path in sorted_items:
            print(f"    - {name} (版本: {ver})")
        
        # 保留最新版本，删除其他所有旧版本
        latest = sorted_items[0]
        old_versions = sorted_items[1:]
        
        print(f"  保留最新版本: {latest[0]} (版本: {latest[1]})")
        print(f"  将删除 {len(old_versions)} 个旧版本:")
        
        for name, ver, path in old_versions:
            if dry_run:
                print(f"    [预览] 将删除: {name}")
            else:
                try:
                    if path.is_file():
                        path.unlink()
                        print(f"    ✓ 已删除文件: {name}")
                    elif path.is_dir():
                        shutil.rmtree(path)
                        print(f"    ✓ 已删除文件夹: {name}")
                    total_deleted += 1
                except Exception as e:
                    print(f"    ✗ 删除失败: {name} - {e}")
        
        print()
    
    if not dry_run:
        print(f"总共删除了 {total_deleted} 个文件/文件夹")
    else:
        print(f"预览模式: 将删除 {sum(len(items) - 1 for items in prefix_groups.values() if len(items) >= 2)} 个文件/文件夹")


def main():
    if len(sys.argv) < 2:
        print("用法: python remove_old_versions.py <目标目录> [--dry-run]")
        print()
        print("参数:")
        print("  目标目录    要扫描的目录路径")
        print("  --dry-run   预览模式，只显示将要删除的文件，不实际删除")
        print()
        print("示例:")
        print("  python remove_old_versions.py /path/to/dir")
        print("  python remove_old_versions.py /path/to/dir --dry-run")
        sys.exit(1)
    
    target_dir = sys.argv[1]
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    
    remove_old_versions(target_dir, dry_run=dry_run)


if __name__ == "__main__":
    main()

