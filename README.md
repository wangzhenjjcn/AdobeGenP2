# Adobe 软件下载中心

自动抓取和更新Adobe软件下载链接的脚本。

![Update Status](https://github.com/wangzhenjjcn/AdobeGenP2/workflows/Update%20Adobe%20Downloads/badge.svg)





## 功能特性

- 自动抓取CyberMania网站的Adobe软件链接
- 支持分页抓取
- 自动提取版本信息和安装模式
- 生成美观的下载中心网页
- GitHub Action自动更新

## 文件结构
├── app.py # 主脚本

├── requirements.txt # 依赖包

├── .github/workflows/ # GitHub Action配置

├── data/ # 数据文件

│ └── data.txt # 抓取的链接

├── DownloadLinks/ # 下载页面文件夹

└── download_center.html # 下载中心页面

## 自动更新

本项目使用GitHub Action自动更新：

- **定时更新**: 每天凌晨2点自动运行
- **手动触发**: 可在Actions页面手动触发
- **推送触发**: 当main分支有更新时自动运行

## 本地运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行脚本：
```bash
python app.py
```

## 更新日志

查看 `update.log` 文件了解详细的更新记录。