# coding: utf-8
from pathlib import Path

# change DEBUG to False if you want to compile the code to exe
DEBUG = "__compiled__" not in globals()


YEAR = 2025
AUTHOR = "ruming"
VERSION = "v0.1.0"
APP_NAME = "B4BA"
HELP_URL = "https://github.com/PilotSherlock/B4B-Assistant"
REPO_URL = "https://github.com/PilotSherlock/B4B-Assistant/issues"
FEEDBACK_URL = "https://github.com/PilotSherlock/B4B-Assistant/issues"
DOC_URL = "https://github.com/PilotSherlock/B4B-Assistant"

CONFIG_FOLDER = Path('AppData').absolute()
CONFIG_FILE = CONFIG_FOLDER / "config.json"
