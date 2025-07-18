#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

def get_source_files(config_in):
    """读取Config.in文件，获取所有source的文件路径"""
    source_files = []
    config_dir = os.path.dirname(config_in)
    
    try:
        with open(config_in, "r") as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if line.startswith("source "):
                source_file = line.split()[1].strip('"')
                full_path = os.path.join(config_dir, source_file)
                source_files.append(full_path)
                print(f"发现source文件: {source_file}")
    
    except FileNotFoundError:
        print(f"警告: {config_in}文件不存在")
    
    return source_files

def parse_config_file(config_file):
    """解析配置文件，找到所有default引用，排除choice块中的引用"""
    referenced_configs = set()
    
    try:
        with open(config_file, "r") as f:
            lines = f.readlines()
        
        in_choice = False
        for i, line in enumerate(lines):
            line = line.strip()
            
            # 检查是否进入choice块
            if line == "choice":
                in_choice = True
                continue
            
            # 检查是否退出choice块
            if line == "endchoice":
                in_choice = False
                continue
            
            # 查找类似 "default BUSYBOX_DEFAULT_*" 的行，但排除choice块中的
            if line.startswith("default BUSYBOX_DEFAULT_") and not in_choice:
                config_name = line.split()[1]
                referenced_configs.add(config_name)
                print(f"发现被引用的配置: {config_name}")
    
    except FileNotFoundError:
        print(f"警告: {config_file}文件不存在")
    
    return referenced_configs

def read_config_in_references(config_in):
    """读取Config.in文件和所有source的文件，找到所有被引用的配置项"""

    # 创建排除列表
    exclude_list = [
        "archival",
        "init",
        "mailutils",
        "networking",
        "selinux",
        "sysklogd",
    ]

    all_referenced_configs = set()
    
    # 然后解析所有source的文件
    source_files = get_source_files(config_in)
    for source_file in source_files:
        if any(exclude_item in source_file for exclude_item in exclude_list):
            continue
        referenced = parse_config_file(source_file)
        all_referenced_configs.update(referenced)
    
    return all_referenced_configs

def modify_config(config_defaults_path):
    # 创建排除列表
    exclude_list = [
        "_FEATURE_",
        "_BEEP",
        "_DEVFSD",
    ]
    
    # 构造Config.in的路径
    base_dir = os.path.dirname(config_defaults_path)
    config_in_path = os.path.join(base_dir, "config", "Config.in")
    
    # 读取Config.in中被引用的配置项
    referenced_configs = read_config_in_references(config_in_path)
    print(f"总共发现 {len(referenced_configs)} 个被引用的配置项")
    
    with open(config_defaults_path, "r") as f:
        lines = f.readlines()
    
    modified_lines = []
    i = 0
    modified_count = 0
    skipped_count = 0
    excluded_count = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # 检查是否是config行
        if line.startswith("config "):
            config_name = line.split()[1]
            
            # 检查下一行是否是bool类型
            if i + 1 < len(lines) and lines[i + 1].strip() == "bool":
                # 检查配置名是否包含排除列表中的元素
                is_excluded = any(exclude_item in config_name for exclude_item in exclude_list)
                
                if not is_excluded:
                    # 检查是否是被Config.in引用的配置项
                    if config_name in referenced_configs:
                        # 被引用的配置项需要修改
                        modified_lines.append(lines[i])
                        modified_lines.append(lines[i + 1])
                        
                        # 检查default行
                        if i + 2 < len(lines) and lines[i + 2].strip().startswith("default "):
                            current_default = lines[i + 2].strip().split()[1]
                            if current_default != "y":
                                modified_lines.append(f"\tdefault y\n")
                                modified_count += 1
                                print(f"修改配置: {config_name} 从 {current_default} 改为 y")
                            else:
                                modified_lines.append(lines[i + 2])
                            i += 3
                        else:
                            i += 2
                    else:
                        # 不是被引用的配置项，保持不变
                        modified_lines.append(lines[i])
                        modified_lines.append(lines[i + 1])
                        if i + 2 < len(lines) and lines[i + 2].strip().startswith("default "):
                            modified_lines.append(lines[i + 2])
                            skipped_count += 1
                            print(f"保持不变 (未被引用): {config_name}")
                        i += 3
                else:
                    # 在排除列表中的配置，原样保留
                    modified_lines.append(lines[i])
                    modified_lines.append(lines[i + 1])
                    if i + 2 < len(lines) and lines[i + 2].strip().startswith("default "):
                        modified_lines.append(lines[i + 2])
                        excluded_count += 1
                        print(f"保持不变 (排除): {config_name}")
                    i += 3
            else:
                # 非bool类型，原样保留
                modified_lines.append(lines[i])
                i += 1
        else:
            # 非config行，原样保留
            modified_lines.append(lines[i])
            i += 1
    
    # 写回文件
    with open(config_defaults_path, "w") as f:
        f.writelines(modified_lines)
    
    print(f"总共修改了 {modified_count} 个配置项")
    print(f"保持不变 (未被引用) {skipped_count} 个配置项")
    print(f"保持不变 (排除列表) {excluded_count} 个配置项")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python busybox.py <Config-defaults.in文件路径>")
        sys.exit(1)
    modify_config(sys.argv[1])
    
