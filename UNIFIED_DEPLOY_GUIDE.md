# 统一部署脚本使用说明

## 概述

`unified_deploy.py` 是一个整合了原 `deploy.py` 和 `copy_files.py` 功能的统一部署脚本，提供完整的构建和部署流程。

## 主要功能

### ✨ 核心功能
- 🔍 **环境检测**: 自动检测虚拟环境和依赖包
- 🏗️ **Nuitka 构建**: 使用 Nuitka 编译生成可执行文件
- 📁 **文件复制**: 自动复制 AppData 和依赖库
- 📦 **依赖管理**: 检查和安装缺失的依赖包
- ✅ **构建验证**: 验证构建结果的完整性

### 🔧 替代的脚本功能
- **替代 `deploy.py`**: Nuitka 构建和基础文件复制
- **替代 `copy_files.py`**: AppData 和依赖包复制
- **整合优化**: 统一的错误处理和进度显示

## 使用方法

### 基本使用

```bash
# 完整部署（推荐）
python unified_deploy.py

# 跳过构建，只复制文件
python unified_deploy.py --skip-build

# 不清理构建目录
python unified_deploy.py --no-clean

# 使用系统 Python（不推荐）
python unified_deploy.py --no-venv
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `--help` | 显示帮助信息 |
| `--no-venv` | 不使用虚拟环境，使用系统 Python |
| `--no-clean` | 不清理构建目录，保留之前的构建 |
| `--skip-build` | 跳过 Nuitka 构建，只复制文件 |

## 部署流程

### 1. 环境检查阶段 🔍
- 检测虚拟环境是否存在（`.venv`, `venv`, `env`, `.env`）
- 验证 Python 和 pip 可执行文件
- 确认主程序文件 `main.py` 存在

### 2. 依赖验证阶段 📦
检查以下必需依赖包：
- `nuitka` - 构建工具
- `pyside6` - Qt 框架
- `pyside6-fluent-widgets` - UI 组件库
- `opencv-python` - 图像处理
- `pillow` - 图像库
- `numpy` - 数值计算
- `openvino` - AI 推理
- `rapidocr-openvino` - OCR 引擎

如果发现缺失包，会提示是否自动安装。

### 3. 构建准备阶段 🧹
- 清理旧的构建目录（可选：`--no-clean` 跳过）
- 创建新的构建结构
- 准备 Nuitka 构建参数

### 4. 应用构建阶段 🔨
使用 Nuitka 构建参数：
```bash
nuitka --standalone --mingw64 \
  --windows-icon-from-ico=app/resource/images/logo.ico \
  --enable-plugins=pyside6 \
  --windows-disable-console \
  --output-filename=B4ba.exe \
  main.py
```

### 5. 文件复制阶段 📁
- **AppData 复制**: 复制应用数据，排除 `game_positions.json` 和 `deck.json`
- **依赖包复制**: 复制必需的 Python 包到输出目录
- **标准库复制**: 复制必要的标准库文件

### 6. 验证阶段 ✅
- 检查可执行文件是否生成
- 验证关键目录是否存在
- 统计文件和目录数量
- 生成部署信息文件

## 输出结构

```
build/
└── main.dist/
    ├── B4ba.exe                    # 主要可执行文件
    ├── AppData/                    # 应用数据目录
    │   ├── cards/                 # 卡牌数据
    │   ├── images/                # 图片资源
    │   └── model/                 # AI 模型文件
    ├── numpy/                      # numpy 库
    ├── PIL/                        # Pillow 库
    ├── openvino/                   # OpenVINO 库
    ├── rapidocr_openvino/          # OCR 库
    ├── deployment_info.json        # 部署信息
    └── [其他依赖库文件...]
```

## 与旧脚本的对比

| 特性 | deploy.py | copy_files.py | unified_deploy.py |
|------|-----------|---------------|-------------------|
| Nuitka 构建 | ✅ | ❌ | ✅ |
| 文件复制 | 基础 | ✅ | ✅ |
| 环境检测 | ❌ | ❌ | ✅ |
| 依赖检查 | ❌ | ❌ | ✅ |
| 错误处理 | 基础 | 基础 | 详细 |
| 进度显示 | 简单 | 无 | 详细 |
| 自动安装依赖 | ❌ | ❌ | ✅ |
| 构建验证 | ❌ | ❌ | ✅ |
| 部署信息 | ❌ | ❌ | ✅ |

## 常见问题

### 1. 虚拟环境未检测到
**问题**: 脚本报告找不到虚拟环境

**解决方案**:
```bash
# 确保虚拟环境存在
python -m venv .venv

# 激活虚拟环境
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# 或使用系统 Python
python unified_deploy.py --no-venv
```

### 2. 依赖包缺失
**问题**: 检测到缺失的依赖包

**解决方案**:
```bash
# 自动安装（推荐）
# 脚本会提示是否安装，选择 'y'

# 手动安装
pip install -r requirements.txt

# 安装特定包
pip install pyside6 opencv-python pillow
```

### 3. Nuitka 构建失败
**问题**: 构建过程中出现编译错误

**解决方案**:
```bash
# 检查 MinGW 是否安装（Windows）
# 清理后重新构建
python unified_deploy.py --no-clean

# 只复制文件，跳过构建
python unified_deploy.py --skip-build
```

### 4. 构建文件过大
**问题**: 生成的可执行文件太大

**解决方案**:
- 检查是否包含了不必要的依赖
- 考虑使用 `--nofollow-import-to` 排除大型库
- 移除不常用的包

## 日常使用建议

### 开发期间
```bash
# 快速测试（跳过构建）
python unified_deploy.py --skip-build --no-clean
```

### 发布准备
```bash
# 完整构建
python unified_deploy.py
```

### 问题排查
```bash
# 检查环境和依赖
python unified_deploy.py --skip-build
```

## 配置优化

### Nuitka 优化参数
脚本使用的 Nuitka 参数已经针对 B4B Assistant 优化：
- `--standalone`: 生成独立可执行文件
- `--mingw64`: 使用 MinGW 编译器
- `--enable-plugins=pyside6`: 启用 PySide6 插件
- `--windows-disable-console`: 隐藏控制台窗口

### 文件复制优化
- 自动排除开发文件（`game_positions.json`, `deck.json`）
- 只复制必需的依赖包
- 智能检测虚拟环境路径

## 技术细节

### 环境检测逻辑
1. 按优先级检测虚拟环境目录：`.venv` > `venv` > `env` > `.env`
2. 验证 Scripts/bin 目录和 python 可执行文件
3. 自动适配 Windows/Linux/macOS 路径差异

### 依赖检查机制
- 使用 subprocess 实际导入包进行验证
- 区分 pip 包名和导入名（如 `opencv-python` vs `cv2`）
- 10秒超时保护，避免挂起

### 错误恢复策略
- 详细的错误信息和建议
- 分阶段验证，失败时立即停止
- 保留中间文件用于问题排查

这个统一脚本大大简化了部署流程，提供了更好的用户体验和错误处理。建议替换原有的 `deploy.py` 和 `copy_files.py` 脚本。
