# coding: utf-8
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, QColor
from PySide6.QtWidgets import QApplication

from qfluentwidgets import NavigationItemPosition, MSFluentWindow, SplashScreen
from qfluentwidgets import FluentIcon as FIF

from .setting_interface import SettingInterface
from .deck_interface import DeckInterface
from .cards_interface import CardsInterface
from .tool_interface import ToolInterface
from ..common.config import cfg
from ..common.icon import Icon
from ..common.signal_bus import signalBus
from ..common.logger import Logger
from ..common import resource
from ..common.setting import VERSION

logger = Logger.get_logger('main_window')

class MainWindow(MSFluentWindow):

    def __init__(self):
        logger.info('Initializing main window')
        super().__init__()
        self.initWindow()

        # TODO: create sub interface
        # self.homeInterface = HomeInterface(self)
        self.settingInterface = SettingInterface(self)
        self.deckInterface = DeckInterface(self)
        self.cardsInterface = CardsInterface(self)
        self.toolInterface = ToolInterface(self)

        self.connectSignalToSlot()
        # add items to navigation interface
        self.initNavigation()
        self.stackedWidget

        self.showNormal()
    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)

    def initNavigation(self):
        logger.info('Initializing navigation')
        # self.navigationInterface.setAcrylicEnabled(True)

        # TODO: add navigation items
        # self.addSubInterface(self.homeInterface, FIF.HOME, self.tr('Home'))
        # add custom widget to bottom
        self.addSubInterface(
            self.deckInterface,
            FIF.DICTIONARY,
            self.tr("Deck"),
            isTransparent=True,)
        self.addSubInterface(
            self.cardsInterface,
            FIF.DOCUMENT,
            self.tr("Cards"),
            isTransparent=True,
        )
        self.addSubInterface(
            self.toolInterface, FIF.UNIT, self.tr("Tool"), isTransparent=True
        )

        self.addSubInterface(
            self.settingInterface, Icon.SETTINGS, self.tr('Settings'), Icon.SETTINGS_FILLED, NavigationItemPosition.BOTTOM)
        self.splashScreen.finish()
        
        # 检查启动时自动更新设置
        self.check_startup_update()

    def check_startup_update(self):
        """检查启动时是否需要自动检查更新"""
        if cfg.get(cfg.checkUpdateAtStartUp):
            logger.info('Auto-checking for updates on startup')
            # 使用设置界面的更新管理器进行检查
            checker = self.settingInterface.update_manager.check_for_updates()
            if checker:
                # 只在有更新时显示提示，没有更新时静默处理
                checker.updateAvailable.connect(self._on_startup_update_available)
                checker.noUpdateAvailable.connect(lambda: logger.info('No updates available on startup'))
                checker.checkFailed.connect(lambda error: logger.warning(f'Startup update check failed: {error}'))

    def _on_startup_update_available(self, update_info: dict):
        """启动时发现更新的处理"""
        logger.info(f'Update available on startup: {update_info["version"]}')
        # 切换到设置页面并触发更新对话框
        self.stackedWidget.setCurrentWidget(self.settingInterface)
        self.settingInterface._on_update_available(update_info)

    def initWindow(self):
        logger.info('Configuring main window')
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(':/app/images/logo.png'))
        self.setWindowTitle('B4BA')

        self.setCustomBackgroundColor(QColor(240, 244, 249), QColor(32, 32, 32))
        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        # create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.show()
        QApplication.processEvents()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())
