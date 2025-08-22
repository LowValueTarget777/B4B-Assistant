# coding: utf-8
from pathlib import Path

# change DEBUG to False if you want to compile the code to exe
DEBUG = "__compiled__" not in globals()

# 导入版本管理器
try:
    from .version_manager import version_manager
    VERSION = version_manager.version
except ImportError:
    # 如果版本管理器不可用，使用默认版本
    VERSION = "v0.1.0"

YEAR = 2025
AUTHOR = "ruming"
APP_NAME = "B4BA"
HELP_URL = "https://github.com/LowValueTarget777/B4B-Assistant"
REPO_URL = "https://github.com/LowValueTarget777/B4B-Assistant"
FEEDBACK_URL = "https://github.com/LowValueTarget777/B4B-Assistant/issues"
DOC_URL = "https://github.com/LowValueTarget777/B4B-Assistant"

CONFIG_FOLDER = Path('AppData').absolute()
CONFIG_FILE = CONFIG_FOLDER / "config.json"
