#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试链接提取功能
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import get_links_from_page, get_next_page_url, is_valid_adobe_link
from urllib.parse import urljoin

def test_link_validation():
    """测试链接验证函数"""
    print("=" * 60)
    print("测试链接验证函数")
    print("=" * 60)
    
    test_cases = [
        ("https://www.cybermania.ws/apps/photoshop-2024/", True),
        ("/apps/photoshop-2024/", True),
        ("apps/photoshop-2024/", True),
        ("https://www.cybermania.ws/apps/illustrator-2023/", True),
        ("/apps/illustrator-2023/", True),
        ("https://www.cybermania.ws/post/2/", False),  # 分页链接
        ("https://www.cybermania.ws/apps/comment-page-1/", False),  # 评论页
        ("https://www.cybermania.ws/apps/", False),  # 排除的链接
    ]
    
    for href, expected in test_cases:
        result = is_valid_adobe_link(href)
        status = "✓" if result == expected else "✗"
        print(f"{status} {href}: {result} (期望: {expected})")
    
    print()

def test_page_extraction():
    """测试页面链接提取"""
    print("=" * 60)
    print("测试页面链接提取")
    print("=" * 60)
    
    url = "https://www.cybermania.ws/?s=adobe"
    print(f"正在测试: {url}")
    
    try:
        links, soup, link_dates = get_links_from_page(url)
        print(f"✓ 成功提取链接")
        print(f"  找到 {len(links)} 个有效链接")
        
        if len(links) > 0:
            print(f"\n  前10个链接:")
            for i, link in enumerate(list(links)[:10], 1):
                date_info = ""
                if link in link_dates:
                    date_info = f" (日期: {link_dates[link].strftime('%Y-%m-%d')})"
                print(f"    {i}. {link}{date_info}")
        else:
            print("  ⚠️  警告: 没有找到任何链接，可能存在问题")
            
            # 调试信息：查看所有包含/apps/的链接
            print("\n  调试信息: 查找所有包含/apps/的链接")
            all_hrefs = []
            for a in soup.find_all("a", href=True):
                href = a.get("href", "")
                if href and "/apps/" in href:
                    absolute_href = urljoin(url, href)
                    all_hrefs.append(absolute_href)
            
            print(f"  找到 {len(all_hrefs)} 个包含/apps/的链接")
            for i, link in enumerate(all_hrefs[:10], 1):
                is_valid = is_valid_adobe_link(link)
                print(f"    {i}. {link} (有效: {is_valid})")
        
        print()
        return len(links) > 0
    except Exception as e:
        print(f"✗ 提取失败: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("链接提取功能测试")
    print("=" * 60)
    print()
    
    test_link_validation()
    test_page_extraction()
    
    print("=" * 60)
    print("测试完成")
    print("=" * 60)
