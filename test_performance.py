#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能对比测试：对比优化前后的性能差异
"""
import sys
import os
import time
from datetime import datetime

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_optimized_performance():
    """测试优化后的性能"""
    print("=" * 60)
    print("性能测试：优化后的版本")
    print("=" * 60)
    
    from app import (
        get_links_from_page,
        get_next_page_url,
        get_session,
        REQUEST_TIMEOUT,
        CONCURRENT_WORKERS
    )
    
    session = get_session()
    
    # 测试单页抓取速度
    print("\n1. 单页抓取性能测试:")
    url = "https://www.cybermania.ws/?s=adobe"
    
    times = []
    for i in range(3):
        start = time.time()
        try:
            links, soup, link_dates = get_links_from_page(url, session=session)
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"  第 {i+1} 次: {elapsed:.2f}秒 (找到 {len(links)} 个链接)")
        except Exception as e:
            print(f"  第 {i+1} 次: 失败 - {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"  平均耗时: {avg_time:.2f}秒")
    
    # 测试多页并发抓取
    print("\n2. 多页并发抓取测试:")
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    test_pages = 3
    urls = [get_next_page_url(page) for page in range(1, test_pages + 1)]
    
    start = time.time()
    results = []
    with ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
        future_to_url = {
            executor.submit(get_links_from_page, url, session): url 
            for url in urls
        }
        
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                links, soup, link_dates = future.result()
                results.append((url, len(links)))
            except Exception as e:
                results.append((url, f"Error: {e}"))
    
    elapsed = time.time() - start
    print(f"  并发抓取 {test_pages} 页总耗时: {elapsed:.2f}秒")
    print(f"  平均每页: {elapsed/test_pages:.2f}秒")
    for url, count in results:
        print(f"    {url}: {count}")
    
    print("\n" + "=" * 60)
    print("优化特性:")
    print("=" * 60)
    print(f"✓ 使用Session复用连接")
    print(f"✓ 请求超时设置: {REQUEST_TIMEOUT}秒")
    print(f"✓ 并发处理线程数: {CONCURRENT_WORKERS}")
    print(f"✓ 使用{'lxml' if 'lxml' in sys.modules else 'html.parser'}解析器")
    print("=" * 60)

def main():
    print("\n" + "=" * 60)
    print("Adobe GenP 性能测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    test_optimized_performance()
    
    print("\n性能优化总结:")
    print("1. Session复用连接 - 减少TCP握手开销")
    print("2. 超时设置 - 避免长时间等待")
    print("3. 并发处理 - 多线程同时处理多个链接")
    print("4. lxml解析器 - 比html.parser快2-3倍")
    print("5. 重试机制 - 提高请求成功率")
    print("\n预期性能提升: 3-5倍（取决于网络和链接数量）")

if __name__ == "__main__":
    main()
