#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整流程测试：验证版本更新和显示功能
"""
import sys
import os
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import (
    get_links_from_page,
    process_single_link,
    load_processed_links,
    load_list_page_dates,
    get_session,
    create_main_download_page,
    parse_version
)
os.environ['CI'] = 'true'

def test_complete_flow():
    """完整流程测试"""
    print("=" * 60)
    print("完整流程测试：Photoshop 2025 版本更新")
    print("=" * 60)
    print()
    
    url = 'https://www.cybermania.ws/appz/photoshop-2025/'
    session = get_session()
    processed_links = load_processed_links()
    list_page_dates = load_list_page_dates()
    
    # 步骤1: 检查网站上的版本
    print("步骤1: 检查网站上的版本")
    print("-" * 60)
    response = session.get(url, timeout=30)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    from app import find_download_links
    download_links = find_download_links(soup)
    print(f"网站上的版本数: {len(download_links)}")
    for i, dl in enumerate(download_links, 1):
        print(f"  {i}. 版本: {dl.get('version_info', 'N/A')}, 安装模式: {dl.get('install_mode', 'N/A')}")
    
    # 获取最新版本
    if download_links:
        latest_version = download_links[0].get('version_info', '')
        print(f"\n最新版本: {latest_version}")
    print()
    
    # 步骤2: 检查本地文件
    print("步骤2: 检查本地文件")
    print("-" * 60)
    folder_path = '../DownloadLinks/photoshop-2025'
    if os.path.exists(folder_path):
        files = [f for f in os.listdir(folder_path) if f.endswith('.html')]
        print(f"本地文件数: {len(files)}")
        
        # 按版本号排序
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
        
        # 检查是否有最新版本
        if sorted_files:
            first_file = sorted_files[0]
            match = re.search(r'^(\d+\.\d+\.\d+\.\d+|\d+\.\d+\.\d+|\d+\.\d+|\d+)', first_file)
            local_latest = match.group(1) if match else ''
            
            if latest_version and local_latest == latest_version:
                print(f"\n✓ 本地已有最新版本: {local_latest}")
            elif latest_version:
                print(f"\n⚠ 本地版本 ({local_latest}) 与网站版本 ({latest_version}) 不一致")
                print("  需要更新...")
                
                # 处理链接
                print("\n步骤3: 处理链接更新")
                print("-" * 60)
                result = process_single_link(url, processed_links, list_page_dates, session)
                print(f"处理结果: {result['status']}")
                print(f"已更新: {result.get('updated', False)}")
                if result.get('reason'):
                    print(f"原因: {result['reason']}")
    print()
    
    # 步骤4: 检查index.html中的显示
    print("步骤4: 检查index.html中的版本显示")
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
            
            print(f"index.html中显示的版本数: {len(versions)}")
            for i, v in enumerate(versions, 1):
                print(f"  {i}. {v.strip()}")
            
            # 验证第一个是否是最新版本
            if versions and latest_version:
                first_version = versions[0].strip()
                if latest_version in first_version:
                    print(f"\n✓ 第一个版本是最新版本: {first_version}")
                    print("✓ 测试通过！")
                else:
                    print(f"\n✗ 第一个版本不是最新版本")
                    print(f"  显示: {first_version}")
                    print(f"  期望: {latest_version}")
                    print("✗ 测试失败！")
        else:
            print("未找到Photoshop 2025部分")
    print()

if __name__ == "__main__":
    test_complete_flow()
