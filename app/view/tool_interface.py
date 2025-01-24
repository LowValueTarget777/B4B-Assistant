from PySide6.QtWidgets import (
    QWidget,
)
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from .ui.tool_ui import Ui_Tool
from ..common.logger import Logger

logger = Logger.get_logger('tool_interface')

class ToolInterface(QWidget, Ui_Tool):
    def __init__(self, parent=None):
        logger.info('Initializing tool interface')
        super().__init__(parent)
        self.setupUi(self)
        self.url_codex = "https://docs.google.com/spreadsheets/d/1zURAO8DELx_EN1D8YkuJ8hw_WQ2jY1mcLE4D8ElMYUo/htmlview?pru=AAABfKs1co8*J3UG9isrOhdIFJsulW5YKg"
        self.url_wiki = "https://back4blood.fandom.com/wiki/Cards#External_links"
        self.url_supplylines = "https://docs.qq.com/sheet/DVHNySEV6YktlVHlT?groupUin=g%252FJID29Ck%252BlQPMZvqsDz5A%253D%253D&ADUIN=243692440&ADSESSION=1634458251&ADTAG=CLIENT.QQ.5651_.0&ADPUBNO=27156&tab=p2l33n&_t=1736688314946"
        self.url_deckbuilder = "https://forthope.gg/"
        self.url_weaponsheet = "https://docs.google.com/spreadsheets/d/1eXKH4ZW6zpvbkzDQ2DwCTRWPrD2ulOCijGl7cNzkyCE/edit?gid=0#gid=0"
        self.url_calculator = "https://docs.google.com/spreadsheets/d/1JWTXjJlh6hmGK6wduPaARHQUX5OUE5cUVpHFds5yx6E/edit?gid=1333824698#gid=1333824698"
        self.url_bilibili_yanxing = "https://www.bilibili.com/video/BV1RG4y1g7A9/?share_source=copy_web&vd_source=e720eb8dfc8a2f335a72814069a12770"
        self.url_bilibili_laoring = "https://space.bilibili.com/41083124/lists/2144351"
        
        
        self.ElevatedCardWidget_wiki.clicked.connect(lambda:self.open_url(self.url_wiki))
        self.ElevatedCardWidget_codex.clicked.connect(lambda:self.open_url(self.url_codex))
        self.ElevatedCardWidget_supplylines.clicked.connect(lambda:self.open_url(self.url_supplylines))
        self.ElevatedCardWidget_calculators.clicked.connect(lambda:self.open_url(self.url_calculator))
        self.ElevatedCardWidget_deckbuilder.clicked.connect(lambda:self.open_url(self.url_deckbuilder))
        self.ElevatedCardWidget_weapon.clicked.connect(lambda:self.open_url(self.url_weaponsheet)) 
        self.ElevatedCardWidget_yanxin.clicked.connect(lambda:self.open_url(self.url_bilibili_yanxing))
        self.ElevatedCardWidget_laorin.clicked.connect(lambda:self.open_url(self.url_bilibili_laoring))
        
    def open_url(self, url):
        logger.info(f'Opening URL: {url}')
        QDesktopServices.openUrl(QUrl(url))
