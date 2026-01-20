#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证程序采集功能是否正常
"""
import sys
import os
import time
from datetime import datetime

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import (
    get_links_from_page, 
    get_next_page_url,
    has_next_page,
    is_valid_adobe_link,
    process_download_links,
    base_url,
    search_url
)

def test_link_validation():
    """测试链接验证功能"""
    print("=" * 60)
    print("测试1: 链接验证功能")
    print("=" * 60)
    
    test_links = [
        "https://www.cybermania.ws/apps/photoshop-2024/",
        "https://www.cybermania.ws/apps/illustrator-2023/",
        "https://www.cybermania.ws/apps/invalid-link/",
        "https://www.cybermania.ws/apps/",
        "https://www.cybermania.ws/cybermania/disable-adobe-genuine-software-integrity-service/",
    ]
    
    for link in test_links:
        result = is_valid_adobe_link(link)
        status = "✓" if result else "✗"
        print(f"{status} {link}: {result}")
    
    print()

def test_page_fetching():
    """测试页面抓取功能"""
    print("=" * 60)
    print("测试2: 页面抓取功能")
    print("=" * 60)
    
    try:
        start_time = time.time()
        url = search_url
        print(f"正在获取: {url}")
        
        links, soup, link_dates = get_links_from_page(url)
        
        elapsed = time.time() - start_time
        print(f"✓ 成功获取页面")
        print(f"  耗时: {elapsed:.2f}秒")
        print(f"  找到有效链接: {len(links)}个")
        print(f"  找到日期信息: {len(link_dates)}个")
        
        if links:
            print(f"\n  前5个链接示例:")
            for i, link in enumerate(list(links)[:5], 1):
                date_info = ""
                if link in link_dates:
                    date_info = f" (日期: {link_dates[link].strftime('%Y-%m-%d')})"
                print(f"    {i}. {link}{date_info}")
        
        print()
        return True
    except Exception as e:
        print(f"✗ 获取页面失败: {e}")
        print()
        return False

def test_pagination():
    """测试分页功能"""
    print("=" * 60)
    print("测试3: 分页功能")
    print("=" * 60)
    
    try:
        max_test_pages = 3
        total_links = set()
        
        for page in range(1, max_test_pages + 1):
            url = get_next_page_url(page)
            print(f"正在获取第 {page} 页: {url}")
            
            start_time = time.time()
            links, soup, link_dates = get_links_from_page(url)
            elapsed = time.time() - start_time
            
            total_links.update(links)
            print(f"  ✓ 第 {page} 页: 找到 {len(links)} 个链接 (耗时: {elapsed:.2f}秒)")
            
            if page < max_test_pages:
                has_next = has_next_page(soup, page)
                print(f"  是否有下一页: {has_next}")
                if not has_next:
                    print(f"  第 {page} 页后没有更多页面")
                    break
        
        print(f"\n✓ 总共收集到 {len(total_links)} 个唯一链接")
        print()
        return True
    except Exception as e:
        print(f"✗ 分页测试失败: {e}")
        print()
        return False

def test_single_link_processing():
    """测试单个链接处理功能"""
    print("=" * 60)
    print("测试4: 单个链接处理功能")
    print("=" * 60)
    
    # 从data.txt读取一个链接进行测试
    data_file = "data/data.txt"
    if not os.path.exists(data_file):
        print(f"✗ 数据文件不存在: {data_file}")
        print("  请先运行主程序生成数据文件")
        print()
        return False
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        if not urls:
            print("✗ 数据文件中没有链接")
            print()
            return False
        
        # 测试第一个链接
        test_url = urls[0]
        print(f"测试链接: {test_url}")
        
        from app import (
            extract_folder_name,
            beautify_software_name,
            extract_page_info,
            find_download_links,
            extract_detail_page_date
        )
        import requests
        from bs4 import BeautifulSoup
        
        start_time = time.time()
        response = requests.get(test_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        elapsed = time.time() - start_time
        
        print(f"  ✓ 成功获取页面 (耗时: {elapsed:.2f}秒)")
        
        folder_name = extract_folder_name(test_url)
        software_name = beautify_software_name(folder_name) if folder_name else "Unknown"
        print(f"  文件夹名: {folder_name}")
        print(f"  软件名: {software_name}")
        
        detail_date = extract_detail_page_date(soup)
        if detail_date:
            print(f"  发布日期: {detail_date.strftime('%Y-%m-%d')}")
        
        image_url, description = extract_page_info(soup)
        if image_url:
            print(f"  图片URL: {image_url}")
        if description:
            print(f"  描述: {description[:100]}...")
        
        download_links = find_download_links(soup)
        print(f"  下载链接数: {len(download_links)}")
        if download_links:
            for i, dl in enumerate(download_links[:3], 1):
                print(f"    {i}. 版本: {dl.get('version_info', 'N/A')}, "
                      f"安装模式: {dl.get('install_mode', 'N/A')}")
        
        print()
        return True
    except Exception as e:
        print(f"✗ 链接处理测试失败: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False

def performance_analysis():
    """性能分析"""
    print("=" * 60)
    print("性能分析报告")
    print("=" * 60)
    
    issues = []
    suggestions = []
    
    # 检查1: HTTP请求优化
    print("\n1. HTTP请求优化:")
    print("   ✗ 未使用Session复用连接")
    print("   ✗ 未设置请求超时时间")
    print("   ✗ 未实现重试机制")
    print("   ✗ 未使用并发处理（所有请求串行）")
    suggestions.append("使用requests.Session()复用连接")
    suggestions.append("设置timeout参数（建议10-30秒）")
    suggestions.append("实现重试机制（使用tenacity或自定义）")
    suggestions.append("使用concurrent.futures实现并发请求")
    
    # 检查2: 数据处理优化
    print("\n2. 数据处理优化:")
    print("   ✗ process_download_links中所有链接串行处理")
    print("   ✗ 每次处理都重新解析整个HTML")
    print("   ✗ 没有缓存机制")
    suggestions.append("使用ThreadPoolExecutor或ProcessPoolExecutor并发处理链接")
    suggestions.append("考虑使用lxml解析器（比html.parser更快）")
    suggestions.append("实现响应缓存（避免重复请求）")
    
    # 检查3: 内存优化
    print("\n3. 内存优化:")
    print("   ✗ 一次性加载所有链接到内存")
    print("   ✗ BeautifulSoup对象未及时释放")
    suggestions.append("考虑流式处理大量链接")
    suggestions.append("及时释放不需要的soup对象")
    
    # 检查4: 文件I/O优化
    print("\n4. 文件I/O优化:")
    print("   ✗ 频繁的文件读写操作")
    print("   ✗ 未使用批量写入")
    suggestions.append("批量写入文件，减少I/O次数")
    suggestions.append("使用json.dump的批量写入模式")
    
    print("\n" + "=" * 60)
    print("优化建议总结:")
    print("=" * 60)
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion}")
    print()

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("Adobe GenP 采集程序测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    results = []
    
    # 运行测试
    results.append(("链接验证", test_link_validation()))
    results.append(("页面抓取", test_page_fetching()))
    results.append(("分页功能", test_pagination()))
    results.append(("链接处理", test_single_link_processing()))
    
    # 性能分析
    performance_analysis()
    
    # 测试总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    print("=" * 60)

if __name__ == "__main__":
    main()
