from PySide6.QtWidgets import (QWidget, QDialog, QLabel, QGridLayout,
                              QListWidget, QMessageBox)  # 添加 QMessageBox / Add QMessageBox
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPixmap, QCursor
import os
import json
from .ui.cards_ui import Ui_Cards
from .ui.filter_ui import Ui_Filter
from ..common.logger import Logger

logger = Logger.get_logger('cards_interface')

class HoverLabel(QLabel):
    def __init__(self, pixmap, name, parent=None):
        super().__init__(parent)
        self.setPixmap(pixmap)
        self.name = name
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                padding: 10px;
                background: transparent;
            }
            QLabel:hover {
                background: rgba(0, 0, 0, 0.1);
                border-radius: 5px;
            }
        """)
        self.setCursor(QCursor(Qt.PointingHandCursor))

        # 初始化动画 / Initialize animation
        self._scale = 1.0
        self.animation = QPropertyAnimation(self, b"scale", self)
        self.animation.setDuration(200)  # 200ms
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        # ----------------------

    def getScale(self):
        return self._scale

    def setScale(self, scale):
        self._scale = scale
        self.update()

    scale = Property(float, getScale, setScale) # type: ignore

    def enterEvent(self, event):
        self.animation.setEndValue(1.05)
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animation.setEndValue(1.0)
        self.animation.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 获取父窗口(CardsInterface)实例 / Get parent window (CardsInterface) instance
            cards_interface = self.parent().parent().parent().parent().parent()
            if isinstance(cards_interface, CardsInterface):
                cards_interface.add_to_list(self.name)

class FilterInterface(QDialog, Ui_Filter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

class CardsInterface(QWidget, Ui_Cards):
    def __init__(self, parent=None):
        logger.info('Initializing cards interface')
        super().__init__(parent)
        self.main_window = self.parent()
        self.setupUi(self)

        # 连接保存按钮的信号 / Connect save button signal
        self.PushButton.clicked.connect(self.save_deck)

        # 添加过滤条件状态 / Add filter condition states
        self.filter_states = {
            'colors': [],
            'tags': []
        }

        # 设置widget的布局 / Set widget layout
        self.widget.setLayout(QGridLayout())
        self.grid_layout = self.widget.layout()
        self.grid_layout.setSpacing(20)  # type: ignore
        self.grid_layout.setContentsMargins(20, 20, 20, 20)  # type: ignore

        # 加载图片 / Load images
        self.images = []
        self.load_image_list()
        self.load_images()

        # 加载卡牌数据 / Load card data
        self.cards_data = self.load_cards_data()

        # 连接信号和槽 / Connect signals and slots
        self.PushButton_2.clicked.connect(self.show_filter_dialog)
        self.SearchLineEdit.textChanged.connect(self.filter_images)

        # 设置ListWidget鼠标事件 / Set ListWidget mouse event
        self.ListWidget_cards.mousePressEvent = self.list_widget_mouse_press

        self.filtered_images = self.images  # 添加一个属性来存储过滤后的结果 / Add a property to store filtered results

        self.MAX_CARDS = 15  # 添加卡牌上限常量 / Add card limit constant

        # -------------------------

    def load_image_list(self):
        """加载图片列表 / Load image list"""
        image_dir = "AppData/images/cards/zh"
        self.images = [
            {"path": os.path.join(image_dir, filename), 
             "name": os.path.splitext(filename)[0]}
            for filename in os.listdir(image_dir)
            if filename.lower().endswith(('.png', '.jpg', '.jpeg'))
        ]

    def load_images(self, images=None):
        """加载图片 / Load images"""
        logger.debug('Loading card images')
        if images is None:
            images = self.images

        # 清除现有图片 / Clear existing images
        for i in reversed(range(self.grid_layout.count())):  # type: ignore
            widget = self.grid_layout.itemAt(i).widget()  # type: ignore
            if widget is not None:
                widget.deleteLater()

        # 固定每行2个图片 / Fix 2 images per row
        for i, image in enumerate(images):
            row = i // 2  # 修改为2列 / Change to 2 columns
            col = i % 2

            # 加载原始图片 / Load original image
            pixmap = QPixmap(image["path"])

            # 创建可悬停的标签 / Create hoverable label
            image_label = HoverLabel(pixmap, image["name"], self.widget)
            self.grid_layout.addWidget(image_label, row, col, Qt.AlignCenter)  # type: ignore

    def filter_images(self):
        """过滤图片 / Filter images"""
        search_text = self.SearchLineEdit.text().lower()
        logger.debug(f'Filtering images with search text: {search_text}')
        # 如果搜索框为空,显示所有过滤后的图片 / If search box is empty, show all filtered images
        if not search_text:
            self.load_images(self.filtered_images)
            return

        # 在已过滤的结果中搜索名称和描述信息 / Search name and description in filtered results
        searched_images = []
        for image in self.filtered_images:
            # 查找对应的卡牌数据 / Find corresponding card data
            card_info = next((card for card in self.cards_data if card['name'] == image['name']), None)
            if card_info:
                # 搜索名称和描述信息 / Search name and description
                if (search_text in image["name"].lower() or 
                    search_text in card_info.get('info', '').lower()):
                    searched_images.append(image)

        self.load_images(searched_images)

    def show_filter_dialog(self):
        """显示过滤对话框 / Show filter dialog"""
        logger.debug('Opening filter dialog')
        dialog = FilterInterface(self)

        # 根据上次的状态设置选中状态 / Set selected state based on last state
        dialog.ToggleButton_blue.setChecked('blue' in self.filter_states['colors'])
        dialog.ToggleButton_red.setChecked('red' in self.filter_states['colors'])
        dialog.ToggleButton_green.setChecked('green' in self.filter_states['colors'])
        dialog.ToggleButton_yellow.setChecked('yellow' in self.filter_states['colors'])

        dialog.ToggleButton_offense.setChecked('offense' in self.filter_states['tags'])
        dialog.ToggleButton_defense.setChecked('defense' in self.filter_states['tags'])
        dialog.ToggleButton_utility.setChecked('utility' in self.filter_states['tags'])
        dialog.ToggleButton_mobility.setChecked('mobility' in self.filter_states['tags'])

        if dialog.exec() == QDialog.Accepted:
            # 获取并保存新的过滤条件 / Get and save new filter conditions
            colors = []
            if dialog.ToggleButton_blue.isChecked(): colors.append("blue")
            if dialog.ToggleButton_red.isChecked(): colors.append("red") 
            if dialog.ToggleButton_green.isChecked(): colors.append("green")
            if dialog.ToggleButton_yellow.isChecked(): colors.append("yellow")

            tags = []
            if dialog.ToggleButton_offense.isChecked(): tags.append("offense")
            if dialog.ToggleButton_defense.isChecked(): tags.append("defense")
            if dialog.ToggleButton_utility.isChecked(): tags.append("utility")
            if dialog.ToggleButton_mobility.isChecked(): tags.append("mobility")

            # 更新状态并应用过滤 / Update state and apply filters
            self.filter_states['colors'] = colors
            self.filter_states['tags'] = tags
            self.apply_filters(colors, tags)

    def apply_filters(self, colors, tags):
        """应用过滤条件 / Apply filters"""
        logger.debug(f'Applying filters - colors: {colors}, tags: {tags}')
        # 如果没有选择任何过滤条件，显示所有卡牌 / If no filters are selected, show all cards
        if not colors and not tags:
            self.filtered_images = self.images
            self.load_images()
            return

        # 过滤卡牌 / Filter cards
        filtered_cards = []
        for card in self.cards_data:
            if (not colors or card['color'] in colors) and \
               (not tags or card['tag'] in tags):
                # 找到对应的图片数据 / Find corresponding image data
                for image in self.images:
                    if image['name'] == card['name']:
                        filtered_cards.append(image)
                        break

        self.filtered_images = filtered_cards  # 保存过滤后的结果 / Save filtered results
        self.load_images(filtered_cards)
        # 重新应用搜索 / Reapply search
        self.filter_images()

    def load_cards_data(self):
        """加载卡牌数据 / Load card data"""
        try:
            with open('AppData/cards/cards_info_zh.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f'Successfully loaded {len(data)} cards')
                return data
        except Exception as e:
            logger.error(f"Error loading cards data: {e}", exc_info=True)
            return []

    def add_to_list(self, name):
        """添加卡牌到列表 / Add card to list"""
        if self.ListWidget_cards.count() >= self.MAX_CARDS:
            logger.warning(f'Attempted to add card beyond limit of {self.MAX_CARDS}')
            QMessageBox.warning(self, self.tr("Warning"), self.tr("Maximum 15 cards allowed in deck!"))  # type: ignore
            return

        # 检查是否已经存在 / Check if it already exists
        items = self.ListWidget_cards.findItems(name, Qt.MatchExactly)
        if not items:
            logger.debug(f'Adding card to list: {name}')
            self.ListWidget_cards.addItem(name)

    def list_widget_mouse_press(self, event):
        """ListWidget鼠标按下事件 / ListWidget mouse press event"""
        if event.button() == Qt.RightButton:
            item = self.ListWidget_cards.itemAt(event.pos())
            if item:
                self.ListWidget_cards.takeItem(self.ListWidget_cards.row(item))
        # 保持左键点击的默认行为 / Keep default behavior for left click
        super(QListWidget, self.ListWidget_cards).mousePressEvent(event)

    def save_deck(self):
        """保存卡组 / Save deck"""
        deck_name = self.LineEdit_deckname.text().strip()
        if not deck_name:
            logger.warning('Attempted to save deck without name')
            QMessageBox.warning(self, self.tr("Warning"), self.tr("Please enter a deck name!"))  # type: ignore
            return

        # 获取所有卡牌 / Get all cards
        cards = []
        for i in range(self.ListWidget_cards.count()):
            cards.append(self.ListWidget_cards.item(i).text())

        logger.info(f'Saving deck: {deck_name} with {len(cards)} cards')

        try:
            # 读取现有卡组 / Read existing decks
            decks = []
            try:
                with open('AppData/deck.json', 'r', encoding='utf-8') as f:
                    decks = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logger.warning(f'No existing decks file found or invalid format: {e}')
                decks = []

            # 准备新的卡组数据 / Prepare new deck data
            new_deck = {"name": deck_name, "cards": cards}
            deck_updated = False

            for i, deck in enumerate(decks):
                if deck['name'] == deck_name:
                    if (
                        QMessageBox.question(
                            self,
                            self.tr("Deck Exists"),
                            self.tr('Deck')+ deck["name"] + self.tr('already exists, overwrite?'),
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No,
                        )
                        == QMessageBox.No
                    ):
                        return
                    decks[i] = new_deck
                    deck_updated = True
                    logger.info(f'Updated existing deck: {deck_name}')
                    break

            # 如果不存在同名卡组，则添加新卡组 / If no deck with the same name exists, add a new deck
            if not deck_updated:
                decks.append(new_deck)
                logger.info(f'Added new deck: {deck_name}')

            # 保存到文件 / Save to file
            with open('AppData/deck.json', 'w', encoding='utf-8') as f:
                json.dump(decks, f, ensure_ascii=False, indent=4)

            deckInterface = self.main_window.deckInterface
            deckInterface.load_decks()
            deckInterface.load_cards_info()
            deckInterface.ComboBox_decks.setCurrentText(deck_name)
            logger.info(f'Successfully saved deck: {deck_name}')
            QMessageBox.information(self, self.tr("Success"), self.tr("Deck saved successfully!"))
            self.main_window.switchTo(deckInterface)

        except Exception as e:
            logger.error(f"Error saving deck: {e}", exc_info=True)
            QMessageBox.critical(self, self.tr("Error"), self.tr("Failed to save deck: ")+str(e))  # type: ignore
