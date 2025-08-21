# 增量翻译工具使用指南

## 概述

`translate.py` 是一个优化的增量翻译工具，专为 B4B-Assistant 项目设计。它能够智能检测文件变化，只在需要时更新翻译文件，大大提高了开发效率。

## 主要特性

✅ **增量更新**: 只有在源文件发生变化时才更新翻译  
✅ **智能检测**: 基于文件哈希和修改时间的变化检测  
✅ **缓存机制**: 记录文件状态，避免重复处理  
✅ **自动工具发现**: 自动查找 pyside6-lupdate 和 pyside6-lrelease 工具  
✅ **一体化编译**: 集成翻译文件编译功能，一步到位  
✅ **详细日志**: 提供清晰的处理状态和进度信息  

## 使用方法

### 基本命令

```bash
# 执行增量翻译更新
python translate.py

# 不打开 Qt Linguist
python translate.py --no-linguist

# 强制更新所有翻译（忽略缓存）
python translate.py --force

# 只编译翻译文件（.ts -> .qm）
python translate.py --compile

# 更新并编译翻译文件（一步到位）
python translate.py --update-and-compile

# 查看翻译状态
python translate.py --status

# 清理缓存
python translate.py --clean

# 手动指定工具路径
python translate.py --lupdate-path "C:\Python311\Scripts\pyside6-lupdate.exe"
python translate.py --lrelease-path "C:\Python311\Scripts\pyside6-lrelease.exe"
```

### 命令行参数

| 参数 | 简写 | 说明 |
|------|------|------|
| `--force` | `-f` | 强制更新所有翻译，忽略缓存 |
| `--no-linguist` | | 不自动打开 Qt Linguist |
| `--status` | `-s` | 显示当前翻译状态 |
| `--clean` | `-c` | 清理缓存文件 |
| `--compile` | | 只编译翻译文件（.ts -> .qm） |
| `--update-and-compile` | | 更新并编译翻译文件（一步到位） |
| `--lupdate-path` | | 手动指定 lupdate 工具路径 |
| `--lrelease-path` | | 手动指定 lrelease 工具路径 |

## 工作原理

### 1. 文件监控
- 扫描 `app/view/ui/` 和 `app/view/` 目录下的所有 Python 文件
- 计算每个文件的 MD5 哈希值和修改时间
- 与缓存中的记录进行比较

### 2. 变化检测
- **文件修改**: 哈希值或修改时间发生变化
- **文件删除**: 文件不再存在
- **新增文件**: 缓存中没有记录的文件

### 3. 增量更新
- 只有检测到变化时才执行 `pyside6-lupdate`
- 保留现有翻译，只更新变化的部分
- 更新缓存记录，记录本次处理状态

### 4. 工具自动发现
脚本会自动在以下位置查找 `pyside6-lupdate` 和 `pyside6-lrelease` 工具：
- 系统 PATH 环境变量
- Python 安装目录的 Scripts 文件夹
- 虚拟环境的 Scripts 文件夹
- 常见的 Python 安装路径

### 5. 翻译编译
- 自动将 `.ts` 文件编译为 `.qm` 文件
- 支持单独编译或与更新一起执行
- 提供编译状态和文件大小信息

## 缓存文件

缓存信息存储在 `.translation_cache.json` 文件中，包含：

```json
{
  "files": {
    "app/view/ui/cards_ui.py": {
      "hash": "abc123...",
      "mtime": 1629876543.21,
      "size": 12345
    }
  },
  "last_update": 1629876543.21,
  "version": "1.0"
}
```

## 开发工作流

### 日常开发
```bash
# 修改 UI 文件后，更新并编译翻译（推荐）
python translate.py --update-and-compile --no-linguist

# 或者分步执行
python translate.py --no-linguist  # 更新翻译
python translate.py --compile      # 编译翻译

# 检查是否有需要翻译的新字符串
python translate.py --status
```

### 大规模重构后
```bash
# 强制完整更新并编译
python translate.py --update-and-compile --force

# 清理缓存，重新开始
python translate.py --clean
python translate.py --update-and-compile
```

### 翻译工作
```bash
# 更新翻译文件并打开 Qt Linguist 进行翻译
python translate.py

# 翻译完成后编译
python translate.py --compile
```

### 发布前检查
```bash
# 确保翻译文件是最新的
python translate.py --update-and-compile --force
```

## 性能优化

### 跳过不必要的更新
- 如果没有文件变化，脚本会立即退出
- 显示上次更新时间，便于跟踪

### 批量处理
- 一次性处理所有变化的文件
- 避免重复启动 lupdate 工具

### 智能缓存
- 基于文件内容哈希，而不仅仅是修改时间
- 准确检测真正的变化

## 故障排除

### 找不到工具
```bash
# 检查 PySide6 是否正确安装
pip install PySide6

# 手动指定工具路径
python translate.py --lupdate-path "完整路径\pyside6-lupdate.exe"
python translate.py --lrelease-path "完整路径\pyside6-lrelease.exe"

# 或者同时指定两个工具
python translate.py --update-and-compile \
  --lupdate-path "路径\pyside6-lupdate.exe" \
  --lrelease-path "路径\pyside6-lrelease.exe"
```

### 编译失败
```bash
# 检查源文件是否存在
python translate.py --status

# 尝试单独编译
python translate.py --compile

# 如果找不到 lrelease，使用 Python 验证
python -c "from PySide6.QtCore import QTranslator; print('PySide6 available')"
```

### 缓存问题
```bash
# 清理缓存重新开始
python translate.py --clean

# 强制更新
python translate.py --force
```

### 翻译文件损坏
```bash
# 备份现有翻译文件
copy app\resource\i18n\app.zh_CN.ts app\resource\i18n\app.zh_CN.ts.backup

# 强制重新生成
python translate.py --force
```

## 输出示例

### 更新和编译一体化
```
==================================================
增量翻译更新检查
==================================================
检测到变更的文件:
  - app\view\ui\cards_ui.py
📝 检测到变化: 变更文件: 1, 删除文件: 0
 找到 lupdate 工具: ...\pyside6-lupdate
🔄 正在更新翻译文件...
✅ 翻译文件已成功更新: ...\app.zh_CN.ts

==================================================
编译翻译文件
==================================================
🔍 找到 lrelease 工具: ...\pyside6-lrelease
🔄 执行命令: ...\pyside6-lrelease ...
✅ 成功编译翻译文件: ...\app.zh_CN.qm
📊 编译后文件大小: 7627 字节

🎉 翻译更新和编译完成！
```

### 只编译翻译
```
==================================================
编译翻译文件
==================================================
📄 源文件: ...\app.zh_CN.ts
📄 目标文件: ...\app.zh_CN.qm
🔍 找到 lrelease 工具: ...\pyside6-lrelease
✅ 成功编译翻译文件: ...\app.zh_CN.qm
📊 编译后文件大小: 7908 字节

🎉 翻译编译完成！
```

### 无变化跳过
```
==================================================
增量翻译更新检查
==================================================
✅ 没有检测到文件变化，无需更新翻译
上次更新时间: 2025-08-21 20:48:56

🎉 翻译更新完成！
```

## 与旧版本的区别

之前的工作流需要两个步骤：
```bash
# 旧方式（需要两个脚本）
python translate.py          # 更新翻译
python compile_translation.py  # 编译翻译
```

现在只需要一个命令：
```bash
# 新方式（一体化）
python translate.py --update-and-compile
```

`compile_translation.py` 的功能已经完全整合到 `translate.py` 中，可以删除旧的编译脚本。

## 注意事项

1. **备份翻译**: 在大规模更新前备份 `.ts` 文件
2. **虚拟环境**: 确保在正确的 Python 环境中运行
3. **文件编码**: 所有源文件应使用 UTF-8 编码
4. **路径问题**: 使用绝对路径避免工作目录问题

## 更新历史

- **v1.0**: 初始增量翻译实现
- **v1.1**: 添加自动工具发现功能
- **v1.2**: 改进缓存机制和错误处理
