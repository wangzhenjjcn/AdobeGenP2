# GUI程序目录

此目录包含Adobe GenP Downloads的桌面GUI应用程序。

## 快速启动

### 方法一：从项目根目录启动（推荐）
双击项目根目录的 `启动GUI.bat` 文件

### 方法二：从gui目录启动
双击本目录的 `run_gui.bat` 文件

### 方法三：命令行启动
```bash
# 从项目根目录
python gui/app-gui.py

# 从gui目录
python app-gui.py
```

## 文件说明

- `app-gui.py` - 主程序文件
- `run_gui.bat` - Windows启动脚本
- `GUI使用说明.md` - 详细使用说明
- `README.md` - 本说明文件

## 注意事项

程序会自动查找项目根目录的 `index.html` 文件进行显示。请确保该文件存在。 