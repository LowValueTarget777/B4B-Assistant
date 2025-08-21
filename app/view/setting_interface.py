# coding:utf-8
from qfluentwidgets import (SwitchSettingCard,
                            HyperlinkCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout,
                            setFont,
                            InfoBar, MessageBox)
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import SettingCardGroup as CardGroup
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QFont
from PySide6.QtWidgets import QWidget, QLabel, QDialog

from ..common.config import cfg, isWin11
from ..common.setting import HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR
from ..common.signal_bus import signalBus
from ..common.style_sheet import StyleSheet
from ..common.logger import Logger
from ..common.updater import UpdateManager
from .update_dialog import UpdateDialog, ProgressDialog, UpdateCompleteDialog

logger = Logger.get_logger('setting_interface')

class SettingCardGroup(CardGroup):

   def __init__(self, title: str, parent=None):
       super().__init__(title, parent)
       setFont(self.titleLabel, 14, QFont.Weight.DemiBold)



class SettingInterface(ScrollArea):
    """ Setting interface """

    def __init__(self, parent=None):
        logger.info('Initializing setting interface')
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.settingLabel = QLabel(self.tr("Settings"), self)

        # personalization
        self.personalGroup = SettingCardGroup(
            self.tr('Personalization'), self.scrollWidget)
        self.micaCard = SwitchSettingCard(
            FIF.TRANSPARENT,
            self.tr('Mica effect'),
            self.tr('Apply semi transparent to windows and surfaces'),
            cfg.micaEnabled,
            self.personalGroup
        )
        self.zoomCard = ComboBoxSettingCard(
            cfg.dpiScale,
            FIF.ZOOM,
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("Use system setting")
            ],
            parent=self.personalGroup
        )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            self.tr('Language'),
            self.tr('Set your preferred language for UI'),
            texts=['简体中文', 'English', self.tr('Use system setting')],
            parent=self.personalGroup
        )

        # update software
        self.updateSoftwareGroup = SettingCardGroup(
            self.tr("Software update"), self.scrollWidget)
        self.updateOnStartUpCard = SwitchSettingCard(
            FIF.UPDATE,
            self.tr('Check for updates when the application starts'),
            self.tr('The new version will be more stable and have more features'),
            configItem=cfg.checkUpdateAtStartUp,
            parent=self.updateSoftwareGroup
        )
        
        # 手动检查更新卡片
        self.checkUpdateCard = PrimaryPushSettingCard(
            self.tr('Check for updates'),
            FIF.SYNC,
            self.tr('Check for updates'),
            self.tr('Manually check for the latest version'),
            self.updateSoftwareGroup
        )

        # application
        self.aboutGroup = SettingCardGroup(self.tr('About'), self.scrollWidget)
        self.helpCard = HyperlinkCard(
            HELP_URL,
            self.tr('Open help page'),
            FIF.HELP,
            self.tr('Help'),
            self.tr(
                'Discover new features and learn useful tips about B4BA'),
            self.aboutGroup
        )
        self.feedbackCard = PrimaryPushSettingCard(
            self.tr('Provide feedback'),
            FIF.FEEDBACK,
            self.tr('Provide feedback'),
            self.tr('Help us improve B4BA by providing feedback'),
            self.aboutGroup
        )
        self.aboutCard = PrimaryPushSettingCard(
            self.tr('About'),
            ":/qfluentwidgets/images/logo.png",
            self.tr('About'),
            '© ' + self.tr('Copyright') + f" {YEAR}, {AUTHOR}. " +
            self.tr('Version') + " " + VERSION,
            self.aboutGroup
        )

        # 初始化更新管理器
        self.update_manager = UpdateManager(VERSION, self)
        self.progress_dialog = None

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 100, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface')

        # initialize style sheet
        setFont(self.settingLabel, 23, QFont.Weight.DemiBold)
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)
        self.scrollWidget.setStyleSheet("QWidget{background:transparent}")

        self.micaCard.setEnabled(isWin11())

        # initialize layout
        self.__initLayout()
        self._connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(36, 50)

        self.personalGroup.addSettingCard(self.micaCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        self.personalGroup.addSettingCard(self.languageCard)

        self.updateSoftwareGroup.addSettingCard(self.updateOnStartUpCard)
        self.updateSoftwareGroup.addSettingCard(self.checkUpdateCard)

        self.aboutGroup.addSettingCard(self.helpCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.updateSoftwareGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def _showRestartTooltip(self):
        logger.info('Configuration updated, restart required')
        InfoBar.success(
            self.tr('Updated successfully'),
            self.tr('Configuration takes effect after restart'),
            duration=1500,
            parent=self
        )

    def _connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self._showRestartTooltip)

        # personalization
        self.micaCard.checkedChanged.connect(signalBus.micaEnableChanged)

        # check update
        self.checkUpdateCard.clicked.connect(self.check_for_updates)
        self.aboutCard.clicked.connect(lambda: self.show_about_dialog())

        # about
        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))

    def check_for_updates(self):
        """检查更新"""
        logger.info('Manual update check triggered')
        
        # 显示检查中的提示
        InfoBar.info(
            self.tr('Checking for updates'),
            self.tr('Please wait while we check for updates...'),
            duration=2000,
            parent=self
        )
        
        # 开始检查更新
        checker = self.update_manager.check_for_updates()
        if checker:
            checker.updateAvailable.connect(self._on_update_available)
            checker.noUpdateAvailable.connect(self._on_no_update_available)
            checker.checkFailed.connect(self._on_check_failed)

    def _on_update_available(self, update_info: dict):
        """发现更新时的处理"""
        logger.info(f'Update available: {update_info["version"]}')
        
        # 显示更新对话框
        dialog = UpdateDialog(update_info, self)
        if dialog.exec() == QDialog.Accepted:
            self._start_download(update_info)

    def _on_no_update_available(self):
        """没有更新时的处理"""
        logger.info('No updates available')
        InfoBar.success(
            self.tr('No updates available'),
            self.tr('You are already using the latest version'),
            duration=3000,
            parent=self
        )

    def _on_check_failed(self, error: str):
        """检查失败时的处理"""
        logger.error(f'Update check failed: {error}')
        InfoBar.error(
            self.tr('Update check failed'),
            error,
            duration=5000,
            parent=self
        )

    def _start_download(self, update_info: dict):
        """开始下载更新"""
        download_url = update_info.get('download_url')
        if not download_url:
            InfoBar.error(
                self.tr('Download failed'),
                self.tr('Download URL not found'),
                duration=3000,
                parent=self
            )
            return

        # 显示进度对话框
        self.progress_dialog = ProgressDialog(self)
        self.progress_dialog.show()

        # 开始下载
        downloader = self.update_manager.download_update(download_url)
        downloader.downloadProgress.connect(self.progress_dialog.update_progress)
        downloader.downloadFinished.connect(self._on_download_finished)
        downloader.downloadFailed.connect(self._on_download_failed)
        
        # 连接取消信号
        self.progress_dialog.rejected.connect(lambda: downloader.cancel())

    def _on_download_finished(self, file_path: str):
        """下载完成的处理"""
        logger.info(f'Download completed: {file_path}')
        
        if self.progress_dialog:
            self.progress_dialog.set_status(self.tr("Installing update..."))
        
        # 安装更新
        success = self.update_manager.install_update(file_path)
        
        if self.progress_dialog:
            self.progress_dialog.close()
            
        # 显示安装结果
        if success:
            dialog = UpdateCompleteDialog(True, parent=self)
            if dialog.exec() == QDialog.Accepted:
                self.update_manager.restart_app()
        else:
            dialog = UpdateCompleteDialog(False, self.tr("An error occurred while installing the update"), parent=self)
            dialog.exec()

    def _on_download_failed(self, error: str):
        """下载失败的处理"""
        logger.error(f'Download failed: {error}')
        
        if self.progress_dialog:
            self.progress_dialog.close()
            
        InfoBar.error(
            self.tr('Download failed'),
            error,
            duration=5000,
            parent=self
        )

    def show_about_dialog(self):
        """显示关于对话框"""
        MessageBox(
            self.tr('About'),
            f'B4B Assistant\n'
            f'{self.tr("Version")}: {VERSION}\n'
            f'© {YEAR} {AUTHOR}\n\n'
            f'{self.tr("A helpful tool for Back 4 Blood players.")}',
            self
        ).exec()
