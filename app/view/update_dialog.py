# coding:utf-8
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QProgressBar, QTextEdit, QFrame)
from PySide6.QtGui import QFont, QPixmap, QIcon
from qfluentwidgets import (PrimaryPushButton, PushButton, ProgressBar, 
                           MessageBox, InfoBar, BodyLabel, TitleLabel,
                           ScrollArea, ElevatedCardWidget)

from ..common.logger import Logger

logger = Logger.get_logger('update_dialog')


class UpdateDialog(QDialog):
    """更新对话框"""
    
    def __init__(self, update_info: dict, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.setupUI()
        
    def setupUI(self):
        self.setWindowTitle(self.tr("New Version Available"))
        self.setFixedSize(500, 600)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title_label = TitleLabel(self.tr("🚀 New Version Available!"))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 版本信息卡片
        info_card = ElevatedCardWidget()
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(20, 20, 20, 20)
        
        # 版本号
        version_label = BodyLabel(f"{self.tr('New Version')}: {self.update_info['version']}")
        version_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #0078d4;")
        info_layout.addWidget(version_label)
        
        # 发布时间
        if self.update_info.get('published_at'):
            date_str = self.update_info['published_at'][:10]  # 只取日期部分
            date_label = BodyLabel(f"{self.tr('Release Date')}: {date_str}")
            date_label.setStyleSheet("color: #666666;")
            info_layout.addWidget(date_label)
        
        # 文件大小
        if self.update_info.get('size'):
            size_mb = self.update_info['size'] / (1024 * 1024)
            size_label = BodyLabel(f"{self.tr('Download Size')}: {size_mb:.1f} MB")
            size_label.setStyleSheet("color: #666666;")
            info_layout.addWidget(size_label)
        
        layout.addWidget(info_card)
        
        # 更新内容
        if self.update_info.get('description'):
            desc_label = BodyLabel(self.tr("Update Details:"))
            desc_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            layout.addWidget(desc_label)
            
            desc_scroll = ScrollArea()
            desc_text = QTextEdit()
            desc_text.setPlainText(self.update_info['description'])
            desc_text.setReadOnly(True)
            desc_text.setMaximumHeight(200)
            desc_text.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 10px;
                    background-color: #f9f9f9;
                }
            """)
            layout.addWidget(desc_text)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.later_button = PushButton(self.tr("Remind Me Later"))
        self.update_button = PrimaryPushButton(self.tr("Update Now"))
        
        button_layout.addWidget(self.later_button)
        button_layout.addWidget(self.update_button)
        
        layout.addLayout(button_layout)
        
        # 连接信号
        self.later_button.clicked.connect(self.reject)
        self.update_button.clicked.connect(self.accept)


class ProgressDialog(QDialog):
    """下载进度对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()
        
    def setupUI(self):
        self.setWindowTitle(self.tr("Updating"))
        self.setFixedSize(400, 200)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title_label = TitleLabel(self.tr("Downloading update..."))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 进度条
        self.progress_bar = ProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = BodyLabel(self.tr("Preparing download..."))
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 取消按钮
        self.cancel_button = PushButton(self.tr("Cancel"))
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button)
        
    def update_progress(self, downloaded: int, total: int):
        """更新进度"""
        if total > 0:
            progress = int((downloaded / total) * 100)
            self.progress_bar.setValue(progress)
            
            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total / (1024 * 1024)
            self.status_label.setText(f"{self.tr('Downloaded')}: {downloaded_mb:.1f} MB / {total_mb:.1f} MB")
        
    def set_status(self, status: str):
        """设置状态文本"""
        self.status_label.setText(status)


class UpdateCompleteDialog(QDialog):
    """更新完成对话框"""
    
    def __init__(self, success: bool, message: str = "", parent=None):
        super().__init__(parent)
        self.success = success
        self.message = message
        self.setupUI()
        
    def setupUI(self):
        self.setWindowTitle(self.tr("Update Complete") if self.success else self.tr("Update Failed"))
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 图标和标题
        if self.success:
            title_label = TitleLabel(self.tr("✅ Update Complete!"))
            title_label.setStyleSheet("color: #28a745;")
            message = self.tr("The application has been successfully updated to the latest version.\nPlease restart the application to apply changes.")
        else:
            title_label = TitleLabel(self.tr("❌ Update Failed"))
            title_label.setStyleSheet("color: #dc3545;")
            message = f"{self.tr('An error occurred during the update process')}:\n{self.message}"
        
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 消息
        message_label = BodyLabel(message)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        if self.success:
            self.later_button = PushButton(self.tr("Restart Later"))
            self.restart_button = PrimaryPushButton(self.tr("Restart Now"))
            
            button_layout.addWidget(self.later_button)
            button_layout.addWidget(self.restart_button)
            
            self.later_button.clicked.connect(self.reject)
            self.restart_button.clicked.connect(self.accept)
        else:
            self.ok_button = PrimaryPushButton(self.tr("OK"))
            button_layout.addWidget(self.ok_button)
            self.ok_button.clicked.connect(self.reject)
        
        layout.addLayout(button_layout)
