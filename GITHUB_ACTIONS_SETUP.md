# GitHub Actions 配置说明

## 工作流文件
- `.github/workflows/update-downloads.yml` - 主工作流文件

## 功能说明
- **自动更新**: 每天凌晨2点自动运行
- **手动触发**: 支持手动触发更新
- **推送触发**: 当main分支有更新时自动运行

## 配置要求

### 1. 仓库权限设置
确保仓库的Actions权限设置正确：
1. 进入仓库 Settings > Actions > General
2. 确保 "Workflow permissions" 设置为 "Read and write permissions"
3. 确保 "Allow GitHub Actions to create and approve pull requests" 已启用

### 2. 认证方式
当前工作流使用默认的 `GITHUB_TOKEN`，无需额外配置：
- 自动提供，无需手动设置
- 适用于公开仓库和私有仓库
- 权限由仓库设置控制

## 故障排除

### 常见错误
```
could not read Username for 'https://github.com': terminal prompts disabled
```

### 解决方案
1. **检查仓库权限**: 确保工作流有写入权限
2. **检查仓库设置**: 确保Actions权限设置正确
3. **检查分支保护**: 确保main分支允许工作流推送

### 测试步骤
1. 进入GitHub仓库页面
2. 点击 "Actions" 标签
3. 选择 "Update Adobe Downloads"
4. 点击 "Run workflow"

## 禁用自动更新
如需禁用自动更新，在工作流文件中注释掉schedule部分：
```yaml
# schedule:
#   - cron: '0 2 * * *'
``` 