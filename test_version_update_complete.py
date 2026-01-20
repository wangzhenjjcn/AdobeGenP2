#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整版本更新测试：模拟从旧版本到新版本的更新过程
"""
import sys
import os
import re
import json
import shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import (
    process_single_link,
    load_processed_links,
    load_list_page_dates,
    get_session,
    create_main_download_page,
    parse_version,
    save_processed_links
)
os.environ['CI'] = 'true'

def test_version_update_scenario():
    """测试版本更新场景"""
    print("=" * 60)
    print("完整版本更新测试")
    print("=" * 60)
    print()
    
    url = 'https://www.cybermania.ws/appz/photoshop-2025/'
    session = get_session()
    
    # 步骤1: 模拟只有旧版本的情况
    print("步骤1: 模拟初始状态（只有旧版本 26.8.1.8）")
    print("-" * 60)
    
    folder_path = '../DownloadLinks/photoshop-2025'
    backup_folder = '../DownloadLinks/photoshop-2025-backup'
    
    # 备份当前文件
    if os.path.exists(folder_path):
        if os.path.exists(backup_folder):
            shutil.rmtree(backup_folder)
        shutil.copytree(folder_path, backup_folder)
        print("✓ 已备份当前文件")
    
    # 只保留旧版本文件
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith('.html') and '26.11.0.18' in filename:
                old_file = os.path.join(folder_path, filename)
                os.remove(old_file)
                print(f"  删除新版本文件: {filename}")
    
    # 检查文件
    if os.path.exists(folder_path):
        files = [f for f in os.listdir(folder_path) if f.endswith('.html')]
        print(f"  当前文件: {files}")
    print()
    
    # 步骤2: 模拟processed_links中有旧日期记录
    print("步骤2: 设置processed_links（旧日期）")
    print("-" * 60)
    processed_links = load_processed_links()
    processed_links[url] = {
        'detail_date': '2025-09-26',  # 与网站日期相同
        'processed_at': '2026-01-01 00:00:00',
        'folder_name': 'photoshop-2025',
        'software_name': 'Photoshop 2025'
    }
    save_processed_links(processed_links)
    print(f"  设置日期: 2025-09-26")
    print()
    
    # 步骤3: 处理链接（应该检测到版本变化并更新）
    print("步骤3: 处理链接（检测版本变化）")
    print("-" * 60)
    list_page_dates = load_list_page_dates()
    
    result = process_single_link(url, processed_links, list_page_dates, session)
    print(f"  处理结果: {result['status']}")
    print(f"  已更新: {result.get('updated', False)}")
    print(f"  已跳过: {result.get('skipped', False)}")
    if result.get('reason'):
        print(f"  原因: {result['reason']}")
    print()
    
    # 步骤4: 检查更新后的文件
    print("步骤4: 检查更新后的文件")
    print("-" * 60)
    if os.path.exists(folder_path):
        files = [f for f in os.listdir(folder_path) if f.endswith('.html')]
        print(f"  文件数: {len(files)}")
        
        def get_version_from_file(filename):
            match = re.search(r'^(\d+\.\d+\.\d+\.\d+|\d+\.\d+\.\d+|\d+\.\d+|\d+)', filename)
            if match:
                return parse_version(match.group(1))
            return (0,)
        
        sorted_files = sorted(files, key=get_version_from_file, reverse=True)
        for f in sorted_files:
            match = re.search(r'^(\d+\.\d+\.\d+\.\d+|\d+\.\d+\.\d+|\d+\.\d+|\d+)', f)
            version = match.group(1) if match else 'Unknown'
            print(f"  {f} (版本: {version})")
        
        # 验证是否有新版本
        has_new_version = any('26.11.0.18' in f for f in files)
        if has_new_version:
            print(f"\n  ✓ 新版本文件已创建")
        else:
            print(f"\n  ✗ 新版本文件未创建")
    print()
    
    # 步骤5: 检查index.html显示
    print("步骤5: 检查index.html显示")
    print("-" * 60)
    create_main_download_page()
    
    index_file = '../index.html'
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找Photoshop 2025的版本
        pattern = r'data-name=\"photoshop 2025\".*?<div class=\"download-links\">(.*?)</div>'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            section = match.group(1)
            versions = re.findall(r'<div class=\"version-info\">([^<]+)</div>', section)
            
            print(f"  显示的版本数: {len(versions)}")
            for i, v in enumerate(versions, 1):
                print(f"    {i}. {v.strip()}")
            
            # 验证第一个是否是最新版本
            if versions and '26.11.0.18' in versions[0]:
                print(f"\n  ✓ 第一个版本是最新版本 26.11.0.18")
                print(f"\n✓ 所有测试通过！")
            else:
                print(f"\n  ✗ 第一个版本不是最新版本")
                print(f"    显示: {versions[0] if versions else 'N/A'}")
    print()
    
    # 恢复备份
    if os.path.exists(backup_folder):
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        shutil.copytree(backup_folder, folder_path)
        shutil.rmtree(backup_folder)
        print("✓ 已恢复备份文件")

if __name__ == "__main__":
    test_version_update_scenario()
