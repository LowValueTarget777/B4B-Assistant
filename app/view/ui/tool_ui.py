# -*- coding: utf-8 -*-

# Enhanced Tool UI with improved design and layout
# Manually enhanced for better user experience

from PySide6 import QtCore, QtGui, QtWidgets
from qfluentwidgets import (
    ElevatedCardWidget, 
    SmoothScrollArea, 
    FluentIcon,
    IconWidget,
    BodyLabel,
    SubtitleLabel,
    TitleLabel
)

class Ui_Tool(object):
    def setupUi(self, Tool):
        Tool.setObjectName("Tool")
        Tool.resize(847, 729)
        
        # 主布局
        self.main_layout = QtWidgets.QVBoxLayout(Tool)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        self.main_layout.setObjectName("main_layout")
        
        # 标题区域
        self.title_widget = QtWidgets.QWidget(Tool)
        self.title_widget.setObjectName("title_widget")
        self.title_widget.setMinimumHeight(80)  # 确保标题区域有足够高度
        self.title_layout = QtWidgets.QVBoxLayout(self.title_widget)
        self.title_layout.setContentsMargins(0, 10, 0, 20)
        self.title_layout.setSpacing(10)
        
        # 主标题
        self.title_label = TitleLabel(self.title_widget)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setObjectName("title_label")
        self.title_label.setText("🛠️ 工具箱")
        self.title_layout.addWidget(self.title_label)
        
        # 副标题
        self.subtitle_label = BodyLabel(self.title_widget)
        self.subtitle_label.setAlignment(QtCore.Qt.AlignCenter)
        self.subtitle_label.setObjectName("subtitle_label")
        self.subtitle_label.setText("Back 4 Blood 实用工具与资源集合")
        self.subtitle_label.setStyleSheet("color: #666666;")
        self.title_layout.addWidget(self.subtitle_label)
        
        self.main_layout.addWidget(self.title_widget)
        
        # 滚动区域
        self.scroll_area = SmoothScrollArea(Tool)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_area")
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        # 滚动内容容器
        self.scroll_content = QtWidgets.QWidget()
        self.scroll_content.setObjectName("scroll_content")
        
        # 网格布局
        self.grid_layout = QtWidgets.QGridLayout(self.scroll_content)
        self.grid_layout.setContentsMargins(20, 20, 20, 20)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setObjectName("grid_layout")
        
        # 创建工具卡片
        self._create_tool_cards()
        
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)
        
        # 设置伸缩
        self.main_layout.setStretch(1, 1)

    def _create_tool_cards(self):
        """创建工具卡片"""
        # 工具数据
        self.tool_data = [
            {
                'name': 'wiki_card',
                'title': 'WIKI',
                'description': 'Back 4 Blood 官方 Wiki',
                'icon': FluentIcon.BROOM,
                'row': 0, 'col': 0
            },
            {
                'name': 'codex_card', 
                'title': 'Card Codex',
                'description': 'B4B 卡牌大全与攻略指南',
                'icon': FluentIcon.LIBRARY,
                'row': 0, 'col': 1
            },
            {
                'name': 'supplylines_card',
                'title': 'Supply Lines',
                'description': '供应线路图表 (中文)',
                'icon': FluentIcon.CHECKBOX,
                'row': 1, 'col': 0
            },
            {
                'name': 'deckbuilder_card',
                'title': 'Deck Builder',
                'description': 'FortHope 卡组构建器',
                'icon': FluentIcon.TILES,
                'row': 1, 'col': 1
            },
            {
                'name': 'weapon_card',
                'title': 'Weapon Sheet',
                'description': 'Back 4 Blood 武器数据表',
                'icon': FluentIcon.TAG,
                'row': 2, 'col': 0
            },
            {
                'name': 'calculator_card',
                'title': 'Stat Calculator',
                'description': 'B4B 数据计算器',
                'icon': FluentIcon.CALORIES,
                'row': 2, 'col': 1
            },
            {
                'name': 'yanxin_card',
                'title': '是颜芯呀',
                'description': 'BiliBili UP主 - 游戏攻略视频',
                'icon': FluentIcon.VIDEO,
                'row': 3, 'col': 0
            },
            {
                'name': 'laorin_card',
                'title': 'LaoRin',
                'description': 'BiliBili UP主 - 游戏教程合集',
                'icon': FluentIcon.PLAY,
                'row': 3, 'col': 1
            }
        ]
        
        # 创建卡片
        for tool in self.tool_data:
            card = self._create_enhanced_card(tool)
            setattr(self, f"ElevatedCardWidget_{tool['name'].replace('_card', '')}", card)
            self.grid_layout.addWidget(card, tool['row'], tool['col'])

    def _create_enhanced_card(self, tool_info):
        """创建增强的卡片"""
        card = ElevatedCardWidget()
        card.setFixedHeight(120)
        card.setObjectName(tool_info['name'])
        
        # 卡片布局
        card_layout = QtWidgets.QHBoxLayout(card)
        card_layout.setContentsMargins(20, 15, 20, 15)
        card_layout.setSpacing(15)
        
        # 图标
        icon_widget = IconWidget(tool_info['icon'])
        icon_widget.setFixedSize(48, 48)
        card_layout.addWidget(icon_widget)
        
        # 文本区域
        text_widget = QtWidgets.QWidget()
        text_layout = QtWidgets.QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(5)
        
        # 标题
        title_label = SubtitleLabel(tool_info['title'])
        title_label.setObjectName(f"{tool_info['name']}_title")
        text_layout.addWidget(title_label)
        
        # 描述
        desc_label = BodyLabel(tool_info['description'])
        desc_label.setObjectName(f"{tool_info['name']}_desc")
        desc_label.setStyleSheet("color: #888888;")
        text_layout.addWidget(desc_label)
        
        text_layout.addStretch()
        card_layout.addWidget(text_widget)
        
        # 右侧箭头图标
        arrow_icon = IconWidget(FluentIcon.CHEVRON_RIGHT)
        arrow_icon.setFixedSize(16, 16)
        card_layout.addWidget(arrow_icon)
        
        # 设置卡片样式
        card.setStyleSheet("""
            ElevatedCardWidget {
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.8);
            }
            ElevatedCardWidget:hover {
                background-color: rgba(0, 120, 215, 0.1);
                border: 1px solid rgba(0, 120, 215, 0.3);
            }
        """)
        
        return card

    def retranslateUi(self, Tool):
        _translate = QtCore.QCoreApplication.translate
        Tool.setWindowTitle(_translate("Tool", "工具箱"))
        # 标题已经在 setupUi 中设置，这里可以覆盖（如果需要国际化）
        if hasattr(self, 'title_label'):
            self.title_label.setText(_translate("Tool", "🛠️ 工具箱"))
        if hasattr(self, 'subtitle_label'):
            self.subtitle_label.setText(_translate("Tool", "Back 4 Blood 实用工具与资源集合"))
