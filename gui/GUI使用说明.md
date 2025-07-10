# Adobe GenP Downloads 桌面应用程序

## 简介
这是一个桌面应用程序，使用内嵌浏览器显示 Adobe GenP 下载页面。程序具有以下特点：

- 使用系统内置浏览器引擎（Windows：Edge WebView2，macOS：Safari WebKit，Linux：WebKitGTK）
- 隐藏浏览器的菜单栏、导航栏、地址栏等UI元素
- 窗口只保留最小化、最大化和关闭按钮
- 自动加载本地的 index.html 文件

## 系统要求
- Python 3.7 或更高版本
- Windows 10/11（推荐），macOS 10.14+，或 Linux

## 安装依赖

### 方法一：自动安装（推荐）
双击运行 `gui/run_gui.bat` 文件，程序会自动检查并安装依赖。

### 方法二：手动安装
打开命令行，在项目目录下运行：
```bash
pip install pywebview
```

## 运行程序

### Windows 用户
1. 双击 `gui/run_gui.bat` 文件（推荐）
2. 或者在命令行运行：`python gui/app-gui.py`

### macOS/Linux 用户
在终端中运行：
```bash
python3 gui/app-gui.py
```

## 功能说明

### 窗口控制
- **最小化**：点击窗口左上角的最小化按钮
- **最大化**：点击窗口左上角的最大化按钮
- **关闭**：点击窗口左上角的关闭按钮

### 浏览功能
- 支持搜索功能：在搜索框中输入关键词过滤软件
- 支持鼠标滚轮滚动页面
- 支持点击下载链接（会在默认浏览器中打开）

### 窗口大小
- 默认尺寸：1200x800 像素
- 最小尺寸：800x600 像素
- 支持自由调整窗口大小

## 故障排除

### 程序无法启动
1. 确保 Python 已正确安装（版本 3.7+）
2. 检查 pywebview 依赖是否已安装
3. 确保 index.html 文件存在于程序目录中

### 页面显示异常
1. 检查 index.html 文件是否完整
2. 尝试重新启动程序
3. 检查系统浏览器是否正常工作

### Windows 特殊说明
在 Windows 系统上，程序使用 Edge WebView2 引擎。如果您的系统没有安装 Microsoft Edge，可能需要安装 WebView2 运行时。

## 技术说明

### 使用的技术
- **Python**：主要编程语言
- **pywebview**：创建桌面应用程序的库
- **系统浏览器引擎**：渲染 HTML 内容

### 文件结构
```
AdobeGenP2/
├── index.html          # 要显示的HTML页面
├── requirements.txt    # Python依赖列表
└── gui/                # GUI程序目录
    ├── app-gui.py      # 主程序文件
    ├── run_gui.bat     # Windows启动脚本
    └── GUI使用说明.md  # 本说明文档
```

## 联系支持
如果遇到问题或需要帮助，请检查项目文档或创建 Issue。 