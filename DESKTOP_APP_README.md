# Adobe Download Center - Desktop Application

## 📱 Desktop App Features

- **无边框设计**: 现代化的应用界面
- **自定义标题栏**: 包含最小化、最大化、关闭按钮
- **可调整窗口大小**: 支持窗口拖拽和调整
- **禁用右键菜单**: 防止用户意外操作
- **自动刷新**: 定期检查更新
- **响应式设计**: 适配不同屏幕尺寸

## 🚀 Quick Start

### 方法1: 使用批处理文件 (Windows)
1. 双击 `start_app.bat` 文件
2. 等待依赖安装完成
3. 应用将自动启动

### 方法2: 手动启动
1. 安装依赖:
   ```bash
   pip install pywebview requests beautifulsoup4
   ```

2. 运行应用:
   ```bash
   python run_desktop_app.py
   ```

## 📋 系统要求

- **Python**: 3.7 或更高版本
- **操作系统**: Windows 10/11, macOS, Linux
- **内存**: 至少 512MB 可用内存
- **网络**: 需要互联网连接来下载 Adobe 软件

## 🔧 依赖包

- `pywebview>=4.0.0` - 创建桌面应用窗口
- `requests>=2.28.0` - HTTP 请求处理
- `beautifulsoup4>=4.11.0` - HTML 解析

## 📱 应用功能

### 主要特性
- ✅ 现代化 UI 设计
- ✅ 无边框窗口
- ✅ 自定义标题栏
- ✅ 窗口拖拽和调整
- ✅ 禁用右键菜单
- ✅ 禁用开发者工具
- ✅ 自动刷新功能
- ✅ 响应式布局

### 窗口控制
- **最小化**: 点击标题栏的 `-` 按钮
- **最大化/还原**: 点击标题栏的 `□` 按钮或双击标题栏
- **关闭**: 点击标题栏的 `✕` 按钮
- **拖拽**: 点击并拖拽标题栏区域
- **调整大小**: 拖拽窗口边缘

## 🛠️ 故障排除

### 常见问题

1. **应用无法启动**
   - 确保 Python 已正确安装
   - 检查依赖是否已安装: `pip list | grep pywebview`

2. **依赖安装失败**
   ```bash
   pip install --upgrade pip
   pip install pywebview requests beautifulsoup4
   ```

3. **页面显示空白**
   - 首先运行 `python app.py` 生成下载数据
   - 确保 `index.html` 文件存在

4. **窗口无法调整大小**
   - 这是正常的，某些平台可能有限制
   - 可以使用最大化功能

### Linux 额外要求
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk python3-dev

# CentOS/RHEL
sudo yum install tkinter python3-devel
```

### macOS 额外要求
```bash
# 使用 Homebrew
brew install python-tk
```

## 📁 文件结构

```
├── run_desktop_app.py      # 桌面应用启动器
├── desktop_app.py          # 桌面应用主程序
├── start_app.bat          # Windows 批处理启动文件
├── requirements_desktop.txt # 桌面应用依赖
├── index.html             # 主页面 (由 app.py 生成)
└── DownloadLinks/         # 下载链接文件夹
```

## 🔐 安全特性

- **禁用右键菜单**: 防止用户查看源代码
- **禁用开发者工具**: 防止调试和检查
- **禁用键盘快捷键**: F12, Ctrl+Shift+I, Ctrl+U 等
- **自动更新**: 定期刷新内容

## 📞 技术支持

如果您遇到任何问题，请：

1. 检查系统要求是否满足
2. 确保网络连接正常
3. 重新安装依赖包
4. 查看控制台错误信息

## 🎯 使用建议

1. **首次使用**: 先运行 `python app.py` 生成数据
2. **定期更新**: 应用会自动刷新，也可手动刷新
3. **网络环境**: 确保网络连接稳定
4. **系统性能**: 关闭不必要的程序以提高性能

---

**享受您的 Adobe Download Center 桌面应用体验！** 🎨 