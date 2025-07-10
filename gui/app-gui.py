#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adobe GenP 下载页面桌面应用程序
使用内嵌浏览器显示 index.html 文件

功能特点：
- 使用系统内置浏览器引擎
- 隐藏浏览器菜单栏、导航栏等UI元素
- 只显示窗口的最小化、最大化、关闭按钮
- 自动加载本地 index.html 文件
"""

import os
import sys
from pathlib import Path

# 检查并导入依赖
try:
    import webview
except ImportError:
    print("错误：缺少必要的依赖库 'pywebview'")
    print("请运行以下命令安装：")
    print("pip install pywebview")
    print("或者运行 run_gui.bat 自动安装")
    input("按回车键退出...")
    sys.exit(1)

def get_html_path():
    """获取 index.html 文件的绝对路径"""
    # 获取当前脚本所在目录的上级目录（因为现在在gui子目录中）
    current_dir = Path(__file__).parent.parent.absolute()
    html_file = current_dir / "index.html"
    
    if html_file.exists():
        return f"file:///{html_file.as_posix()}"
    else:
        print(f"错误：找不到 index.html 文件，期望位置：{html_file}")
        print(f"当前脚本位置：{Path(__file__).parent.absolute()}")
        print(f"查找位置：{html_file}")
        sys.exit(1)

def main():
    """主函数"""
    try:
        # 获取 HTML 文件路径
        html_url = get_html_path()
        
        # 创建窗口
        window = webview.create_window(
            title='Adobe GenP Downloads',  # 窗口标题
            url=html_url,                  # 要加载的本地HTML文件
            width=1200,                    # 窗口宽度
            height=800,                    # 窗口高度
            min_size=(800, 600),          # 最小尺寸
            resizable=True,               # 允许调整大小
            fullscreen=False,             # 不全屏
            minimized=False,              # 不最小化启动
            on_top=False,                 # 不置顶
            shadow=True,                  # 窗口阴影
        )
        
        # 启动应用程序
        # debug=False 隐藏开发者工具
        # gui='cef' 可以使用 CEF 浏览器引擎（需要安装 cefpython3）
        # 如果不指定 gui 参数，将使用系统默认浏览器引擎
        webview.start(
            debug=False,           # 不显示开发者工具和地址栏
            http_server=False,     # 不启动内置HTTP服务器
        )
        
    except Exception as e:
        print(f"启动应用程序时出错：{e}")
        input("按回车键退出...")
        sys.exit(1)

if __name__ == '__main__':
    main()
