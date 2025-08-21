from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QUrl, Signal
from PySide6.QtGui import QDesktopServices
from .ui.tool_ui import Ui_Tool
from ..common.logger import Logger
import os

logger = Logger.get_logger('tool_interface')

class ToolInterface(QWidget, Ui_Tool):
    def __init__(self, parent=None):
        logger.info('Initializing enhanced tool interface')
        super().__init__(parent)
        self.setupUi(self)
        
        # URL 配置
        self.urls = {
            'wiki': "https://back4blood.fandom.com/wiki/Cards#External_links",
            'codex': "https://docs.google.com/spreadsheets/d/1zURAO8DELx_EN1D8YkuJ8hw_WQ2jY1mcLE4D8ElMYUo/htmlview?pru=AAABfKs1co8*J3UG9isrOhdIFJsulW5YKg",
            'supplylines': "https://docs.qq.com/sheet/DVHNySEV6YktlVHlT?groupUin=g%252FJID29Ck%252BlQPMZvqsDz5A%253D%253D&ADUIN=243692440&ADSESSION=1634458251&ADTAG=CLIENT.QQ.5651_.0&ADPUBNO=27156&tab=p2l33n&_t=1736688314946",
            'deckbuilder': "https://forthope.gg/",
            'weapon': "https://docs.google.com/spreadsheets/d/1eXKH4ZW6zpvbkzDQ2DwCTRWPrD2ulOCijGl7cNzkyCE/edit?gid=0#gid=0",
            'calculators': "https://docs.google.com/spreadsheets/d/1JWTXjJlh6hmGK6wduPaARHQUX5OUE5cUVpHFds5yx6E/edit?gid=1333824698#gid=1333824698",
            'yanxin': "https://www.bilibili.com/video/BV1RG4y1g7A9/?share_source=copy_web&vd_source=e720eb8dfc8a2f335a72814069a12770",
            'laorin': "https://space.bilibili.com/41083124/lists/2144351"
        }
        
        # 连接信号
        self._connect_signals()
        
        # 设置工具提示
        self._setup_tooltips()
        
        # 应用自定义样式
        self._apply_custom_styles()
        
    def _connect_signals(self):
        """连接所有卡片的点击信号"""
        self.ElevatedCardWidget_wiki.clicked.connect(lambda: self.open_url(self.urls['wiki']))
        self.ElevatedCardWidget_codex.clicked.connect(lambda: self.open_url(self.urls['codex']))
        self.ElevatedCardWidget_supplylines.clicked.connect(lambda: self.open_url(self.urls['supplylines']))
        self.ElevatedCardWidget_deckbuilder.clicked.connect(lambda: self.open_url(self.urls['deckbuilder']))
        self.ElevatedCardWidget_weapon.clicked.connect(lambda: self.open_url(self.urls['weapon']))
        self.ElevatedCardWidget_calculator.clicked.connect(lambda: self.open_url(self.urls['calculators']))
        self.ElevatedCardWidget_yanxin.clicked.connect(lambda: self.open_url(self.urls['yanxin']))
        self.ElevatedCardWidget_laorin.clicked.connect(lambda: self.open_url(self.urls['laorin']))
        
    def _setup_tooltips(self):
        """设置工具提示"""
        tooltips = {
            'wiki': "访问 Back 4 Blood 官方 Wiki 页面",
            'codex': "查看详细的卡牌数据和游戏攻略",
            'supplylines': "查看中文版供应线路图表",
            'deckbuilder': "使用在线卡组构建工具",
            'weapon': "查看详细的武器数据表格",
            'calculators': "使用各种游戏数据计算器",
            'yanxin': "观看是颜芯呀的游戏攻略视频",
            'laorin': "观看 LaoRin 的游戏教程合集"
        }
        
        for key, tooltip in tooltips.items():
            widget = getattr(self, f'ElevatedCardWidget_{key}', None)
            if widget:
                widget.setToolTip(tooltip)
                
    def _apply_custom_styles(self):
        """应用自定义样式"""
        try:
            # 首先尝试基础样式文件
            style_path = "app/resource/qss/tool_interface.qss"
            
            if os.path.exists(style_path):
                with open(style_path, 'r', encoding='utf-8') as f:
                    style_content = f.read()
                    self.setStyleSheet(style_content)
                logger.info(f'Applied custom styles from {style_path}')
            else:
                logger.warning(f'Style file not found: {style_path}')
                # 应用简单的内联样式作为后备
                self.setStyleSheet("""
                    QWidget#Tool {
                        background-color: #fafafa;
                    }
                    TitleLabel {
                        font-size: 24px;
                        font-weight: bold;
                        color: #2c3e50;
                        margin: 10px;
                    }
                    BodyLabel {
                        font-size: 14px;
                        color: #7f8c8d;
                        margin: 5px;
                    }
                    ElevatedCardWidget {
                        border-radius: 8px;
                        background-color: white;
                        border: 1px solid #e0e0e0;
                        padding: 10px;
                        margin: 5px;
                    }
                    ElevatedCardWidget:hover {
                        background-color: #f0f8ff;
                        border: 2px solid #0078d4;
                    }
                """)
                logger.info('Applied fallback inline styles')
        except Exception as e:
            logger.error(f'Failed to apply custom styles: {e}')
            # 最基本的样式
            self.setStyleSheet("QWidget { background-color: #fafafa; }")
            
    def _detect_theme(self):
        """检测当前主题"""
        try:
            # 尝试从父组件或配置中获取主题信息
            if hasattr(self.parent(), 'theme') and self.parent().theme:
                return self.parent().theme
            # 默认使用浅色主题
            return "light"
        except:
            return "light"
        
    def open_url(self, url):
        """打开 URL"""
        logger.info(f'Opening URL: {url}')
        try:
            QDesktopServices.openUrl(QUrl(url))
            logger.info('URL opened successfully')
        except Exception as e:
            logger.error(f'Failed to open URL: {e}')
