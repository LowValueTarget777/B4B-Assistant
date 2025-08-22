# 版本管理和自动更新系统使用指南

## 概述

B4B Assistant 现在拥有完整的版本管理和自动更新系统，包括：

- 📋 **版本管理器**: 统一管理版本信息
- 🔄 **自动更新**: 在线检查和下载更新
- 🛠️ **版本工具**: 命令行版本管理工具
- 📦 **构建集成**: 构建时自动更新版本信息

## 版本号存储位置

### 1. 主要位置
- **`version.json`**: 主要版本信息文件（项目根目录）
- **`app/common/setting.py`**: 应用配置中的版本号（自动同步）

### 2. 文件结构
```json
{
  "version": "v0.1.0",           // 版本号
  "build_number": 1,             // 构建号
  "release_date": "2025-08-22",  // 发布日期
  "release_notes": "...",        // 发布说明
  "pre_release": false,          // 是否预发布
  "changelog": [...],            // 更新日志
  "build_info": {...}            // 构建信息
}
```

## 版本管理工具使用

### 基本命令

```bash
# 显示当前版本信息
python version_tool.py show

# 递增版本号
python version_tool.py increment patch   # 0.1.0 → 0.1.1
python version_tool.py increment minor   # 0.1.0 → 0.2.0
python version_tool.py increment major   # 0.1.0 → 1.0.0

# 设置特定版本
python version_tool.py set 1.2.3

# 添加更新日志
python version_tool.py changelog "修复了卡牌显示问题" --type bugfix
python version_tool.py changelog "新增卡组导出功能" --type feature

# 设置发布说明
python version_tool.py notes "这是一个重要的更新版本"

# 设置预发布状态
python version_tool.py prerelease --enable   # 启用预发布
python version_tool.py prerelease --disable  # 禁用预发布

# 导出版本摘要
python version_tool.py export
```

### 更新类型说明

| 类型 | 描述 | 示例 |
|------|------|------|
| `feature` | 新功能 | 新增卡组分享功能 |
| `bugfix` | 错误修复 | 修复卡牌图片显示问题 |
| `improvement` | 改进优化 | 优化界面响应速度 |
| `breaking` | 破坏性更改 | 更改配置文件格式 |

## 自动更新系统

### 1. 更新流程

```
检查更新 → 下载ZIP包 → 解压文件 → 备份当前版本 → 替换文件 → 重启应用
```

### 2. 更新触发方式

#### 手动检查更新
- 在设置界面点击"检查更新"按钮
- 或在启动时自动检查（可在设置中开关）

#### 程序化检查
```python
from app.common.updater import UpdateManager
from app.common.setting import VERSION

# 创建更新管理器
update_manager = UpdateManager(VERSION)

# 检查更新
checker = update_manager.check_for_updates()
checker.updateAvailable.connect(handle_update_available)
checker.noUpdateAvailable.connect(handle_no_update)
checker.checkFailed.connect(handle_check_failed)
```

### 3. 更新包要求

更新的ZIP包必须包含：
- `main.py` 文件（主程序入口）
- 或包含 `app/` 目录的完整项目结构

系统会自动跳过以下文件/目录：
- `AppData/` - 用户数据
- `logs/` - 日志文件
- `.venv/` - 虚拟环境
- `__pycache__/` - Python缓存
- `.git/` - Git仓库
- `backup/` - 备份目录

## 发布工作流程

### 1. 开发阶段
```bash
# 开发新功能时添加日志
python version_tool.py changelog "实现卡牌搜索功能" --type feature

# 修复bug时添加日志
python version_tool.py changelog "修复程序启动时的崩溃问题" --type bugfix
```

### 2. 准备发布
```bash
# 递增版本号
python version_tool.py increment minor

# 设置发布说明
python version_tool.py notes "此版本新增搜索功能，修复多个已知问题"

# 查看版本信息
python version_tool.py show
```

### 3. 构建发布
```bash
# 使用统一部署脚本构建
python unified_deploy.py

# 构建过程中会自动更新构建信息到version.json
```

### 4. GitHub发布
1. 将构建的应用打包成ZIP文件
2. 在GitHub创建Release，标签使用版本号（如 `v0.1.0`）
3. 上传ZIP文件作为Release Asset
4. 用户的应用会自动检测到新版本

## 版本号规范

### 语义化版本控制

采用 `v{MAJOR}.{MINOR}.{PATCH}` 格式：

- **MAJOR**: 重大更改，可能不兼容旧版本
- **MINOR**: 新功能，向后兼容
- **PATCH**: 错误修复，向后兼容

### 示例
- `v1.0.0` - 首个正式版本
- `v1.1.0` - 新增功能
- `v1.1.1` - 修复bug
- `v2.0.0` - 重大更新

### 预发布版本
- `v1.1.0-pre` - 预发布版本
- 用于测试新功能，不推荐生产使用

## API集成

### 在代码中使用版本信息

```python
# 获取版本信息
from app.common.version_manager import version_manager

# 基本信息
print(f"当前版本: {version_manager.version}")
print(f"构建号: {version_manager.build_number}")
print(f"完整版本: {version_manager.full_version}")

# 版本比较
if version_manager.is_newer_than("v0.9.0"):
    print("当前版本比v0.9.0新")

# 获取完整信息
version_info = version_manager.get_version_info()
```

### 在界面中显示版本

```python
# 在关于对话框中显示
about_text = f"B4B Assistant {version_manager.get_display_version()}"

# 在窗口标题中显示
window_title = f"B4B Assistant - {version_manager.version}"
```

## 自动化脚本

### 发布脚本示例

```bash
#!/bin/bash
# release.sh - 自动发布脚本

echo "🚀 开始发布流程..."

# 1. 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ 存在未提交的更改，请先提交"
    exit 1
fi

# 2. 递增版本号
python version_tool.py increment patch

# 3. 构建应用
python unified_deploy.py

# 4. 创建发布包
cd build/main.dist
zip -r "../../B4B-Assistant-$(python ../../version_tool.py show | grep '版本号' | cut -d' ' -f2).zip" .
cd ../..

# 5. 提交版本更新
git add version.json
git commit -m "Bump version to $(python version_tool.py show | grep '版本号' | cut -d' ' -f2)"
git push

echo "✅ 发布流程完成!"
```

## 故障排除

### 常见问题

1. **版本文件损坏**
   ```bash
   # 重新初始化版本文件
   rm version.json
   python version_tool.py show  # 会自动创建默认版本文件
   ```

2. **更新下载失败**
   - 检查网络连接
   - 检查GitHub Release是否存在
   - 查看应用日志获取详细错误信息

3. **更新安装失败**
   - 检查应用是否有足够的文件写入权限
   - 确认ZIP包格式正确
   - 查看backup目录是否有备份文件

4. **版本比较错误**
   - 确保版本号格式正确（v1.2.3）
   - 检查version.json文件格式

### 调试模式

```python
# 启用详细日志
import logging
logging.getLogger('version_manager').setLevel(logging.DEBUG)
logging.getLogger('updater').setLevel(logging.DEBUG)
```

## 最佳实践

1. **定期备份**: 重要更新前手动备份用户数据
2. **测试发布**: 使用预发布版本测试新功能
3. **渐进更新**: 避免在单个版本中进行过多更改
4. **文档同步**: 及时更新用户文档和发布说明
5. **回滚准备**: 保持上一个稳定版本的下载链接

这个系统让版本管理变得简单而强大，支持从开发到发布的完整流程！
