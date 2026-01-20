#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试版本更新功能
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import (
    process_single_link,
    load_processed_links,
    load_list_page_dates,
    get_session,
    create_main_download_page,
    parse_version
)
import os
os.environ['CI'] = 'true'

def test_version_parsing():
    """测试版本号解析"""
    print("=" * 60)
    print("测试1: 版本号解析")
    print("=" * 60)
    
    test_cases = [
        ("26.11.0.18", (26, 11, 0, 18)),
        ("26.8.1.8", (26, 8, 1, 8)),
        ("25.6.4.003", (25, 6, 4, 3)),
        ("", (0,)),
        ("invalid", (0,)),
    ]
    
    for version_str, expected in test_cases:
        result = parse_version(version_str)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{version_str}' -> {result} (期望: {expected})")
    print()

def test_version_comparison():
    """测试版本号比较"""
    print("=" * 60)
    print("测试2: 版本号比较")
    print("=" * 60)
    
    versions = [
        "26.11.0.18",
        "26.8.1.8",
        "25.6.4.003",
        "26.1.0.0",
    ]
    
    sorted_versions = sorted(versions, key=parse_version, reverse=True)
    print("按版本号降序排序:")
    for v in sorted_versions:
        print(f"  {v} -> {parse_version(v)}")
    print()

def test_photoshop_update():
    """测试Photoshop更新流程"""
    print("=" * 60)
    print("测试3: Photoshop 2025 更新流程")
    print("=" * 60)
    
    url = 'https://www.cybermania.ws/appz/photoshop-2025/'
    processed_links = load_processed_links()
    list_page_dates = load_list_page_dates()
    session = get_session()
    
    print(f"URL: {url}")
    print(f"当前processed_links中的记录: {url in processed_links}")
    
    if url in processed_links:
        info = processed_links[url]
        print(f"  上次处理日期: {info.get('detail_date')}")
        print(f"  上次处理时间: {info.get('processed_at')}")
    
    # 检查现有文件
    folder_path = '../DownloadLinks/photoshop-2025'
    if os.path.exists(folder_path):
        files = [f for f in os.listdir(folder_path) if f.endswith('.html')]
        print(f"\n现有文件 ({len(files)} 个):")
        for f in sorted(files, key=lambda x: parse_version(re.search(r'^(\d+\.\d+\.\d+\.\d+|\d+\.\d+\.\d+|\d+\.\d+|\d+)', x).group(1) if re.search(r'^(\d+\.\d+\.\d+\.\d+|\d+\.\d+\.\d+|\d+\.\d+|\d+)', x) else ''), reverse=True):
            match = re.search(r'^(\d+\.\d+\.\d+\.\d+|\d+\.\d+\.\d+|\d+\.\d+|\d+)', f)
            version = match.group(1) if match else 'Unknown'
            print(f"  {f} (版本: {version})")
    
    # 处理链接
    print(f"\n处理链接...")
    result = process_single_link(url, processed_links, list_page_dates, session)
    
    print(f"结果:")
    print(f"  Status: {result['status']}")
    print(f"  Updated: {result.get('updated', False)}")
    print(f"  Skipped: {result.get('skipped', False)}")
    if result.get('reason'):
        print(f"  Reason: {result['reason']}")
    
    # 检查更新后的文件
    if os.path.exists(folder_path):
        files = [f for f in os.listdir(folder_path) if f.endswith('.html')]
        print(f"\n更新后文件 ({len(files)} 个):")
        for f in sorted(files, key=lambda x: parse_version(re.search(r'^(\d+\.\d+\.\d+\.\d+|\d+\.\d+\.\d+|\d+\.\d+|\d+)', x).group(1) if re.search(r'^(\d+\.\d+\.\d+\.\d+|\d+\.\d+\.\d+|\d+\.\d+|\d+)', x) else ''), reverse=True):
            match = re.search(r'^(\d+\.\d+\.\d+\.\d+|\d+\.\d+\.\d+|\d+\.\d+|\d+)', f)
            version = match.group(1) if match else 'Unknown'
            print(f"  {f} (版本: {version})")
    
    print()

def test_index_generation():
    """测试主页面生成"""
    print("=" * 60)
    print("测试4: 主页面生成（版本排序）")
    print("=" * 60)
    
    create_main_download_page()
    
    # 检查index.html中的Photoshop版本顺序
    index_file = '../index.html'
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找Photoshop 2025的版本信息
        import re
        ps_section = re.search(r'Photoshop 2025.*?download-links">(.*?)</div>', content, re.DOTALL)
        if ps_section:
            versions = re.findall(r'<div class="version-info">([^<]+)</div>', ps_section.group(1))
            print(f"index.html中Photoshop 2025的版本顺序:")
            for i, v in enumerate(versions, 1):
                print(f"  {i}. {v}")
            
            # 验证第一个是否是最新版本
            if versions:
                first_version = versions[0]
                if '26.11.0.18' in first_version:
                    print(f"\n✓ 第一个版本是最新版本: {first_version}")
                else:
                    print(f"\n✗ 第一个版本不是最新版本: {first_version}")
    print()

if __name__ == "__main__":
    import re
    print("\n" + "=" * 60)
    print("版本更新功能测试")
    print("=" * 60)
    print()
    
    test_version_parsing()
    test_version_comparison()
    test_photoshop_update()
    test_index_generation()
    
    print("=" * 60)
    print("测试完成")
    print("=" * 60)
