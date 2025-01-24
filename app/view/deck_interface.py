import time
from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QPixmap, QClipboard
from .ui.deck_ui import Ui_Deck
from ..common.ocr import OCRProcessor
from ..common.applyingame import GameController
import json
import os
from ..common.logger import Logger

logger = Logger.get_logger('deck_interface')


class DeckInterface(QWidget, Ui_Deck):
    edit_deck_signal = Signal(dict)  # 添加信号 / Add signal

    def __init__(self, parent=None):
        logger.info('Initializing deck interface')
        super().__init__(parent)
        self.setupUi(self)

        # 初始化数据 / Initialize data
        self.decks = []
        self.current_deck = None
        self.cards_info = []
        self.main_window = self.parent()
        self.ocr = OCRProcessor(self.parent())  # 初始化OCRProcessor / Initialize OCRProcessor

        # 加载卡组和卡牌数据 / Load decks and card data
        self.load_decks()
        self.load_cards_info()

        # 连接信号和槽 / Connect signals and slots
        self.PushButton_edit.clicked.connect(self.edit_deck)
        self.PushButton_delete.clicked.connect(self.delete_deck)
        self.PushButton_importdeck.clicked.connect(self.import_deck)
        self.PushButton_ingame.clicked.connect(self.apply_deck)
        self.PushButton_new.clicked.connect(self.new_deck)
        self.PushButton_share.clicked.connect(self.share_deck)

        # 列表选择信号 / List selection signal
        self.ListWidget_decklist.itemClicked.connect(self.on_item_clicked)

        # 下拉框改变信号 / Combo box change signal
        self.ComboBox_decks.currentTextChanged.connect(self.on_combo_changed)

    def load_decks(self):
        logger.debug('Loading decks from file')
        """从deck.json加载卡组数据 / Load deck data from deck.json"""
        try:
            with open('AppData/deck.json', 'r', encoding='utf-8') as f:
                self.decks = json.load(f)

            # 更新ComboBox / Update ComboBox
            self.ComboBox_decks.clear()
            for deck in self.decks:
                self.ComboBox_decks.addItem(deck['name'])

            # 如果有卡组，选择第一个 / If there are decks, select the first one
            if self.decks:
                self.ComboBox_decks.setCurrentIndex(0)
                self.update_deck_list(self.decks[0])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f'Error loading decks: {e}', exc_info=True)
            self.decks = []

    def load_cards_info(self):
        """加载卡牌信息 / Load card information"""
        try:
            with open('AppData/cards/cards_info_zh.json', 'r', encoding='utf-8') as f:
                self.cards_info = json.load(f)
        except Exception as e:
            logger.error(f"Error loading cards info: {str(e)}")
            self.cards_info = []

    def update_deck_list(self, deck):
        """更新卡组列表显示 / Update deck list display"""
        self.ListWidget_decklist.clear()
        if deck and 'cards' in deck:
            self.ListWidget_decklist.addItems(deck['cards'])
            self.current_deck = deck

    def on_combo_changed(self, text):
        """当ComboBox选择改变时更新卡组列表 / Update deck list when ComboBox selection changes"""
        # 查找选中的卡组 / Find the selected deck
        selected_deck = next((deck for deck in self.decks if deck['name'] == text), None)
        if selected_deck:
            self.update_deck_list(selected_deck)

    def edit_deck(self):
        """编辑当前选中的卡组 / Edit the currently selected deck"""
        current_deck_name = self.ComboBox_decks.currentText()
        if not current_deck_name:
            return

        # 获取当前卡组数据 / Get current deck data
        current_deck = next((deck for deck in self.decks if deck['name'] == current_deck_name), None)
        if current_deck:
            # 获取主窗口实例 / Get main window instance
            main_window = self.main_window
            # 获取cards界面实例 / Get cards interface instance
            cards_interface = main_window.cardsInterface
            # 设置卡组数据 / Set deck data
            cards_interface.LineEdit_deckname.setText(current_deck['name'])
            cards_interface.ListWidget_cards.clear()
            cards_interface.ListWidget_cards.addItems(current_deck["cards"])
            # 切换到cards界面 / Switch to cards interface
            main_window.switchTo(cards_interface)

    def delete_deck(self):
        """删除当前选中的卡组 / Delete the currently selected deck"""
        current_deck_name = self.ComboBox_decks.currentText()
        if not current_deck_name:
            return

        # 确认删除 / Confirm deletion
        reply = QMessageBox.question(
            self,
            self.tr("Confirm Delete"),
            self.tr('Are you sure you want to delete deck ') + current_deck_name + '?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # 从数据中删除 / Remove from data
            self.decks = [deck for deck in self.decks if deck['name'] != current_deck_name]
            # 更新 ComboBox / Update ComboBox
            self.ComboBox_decks.removeItem(self.ComboBox_decks.currentIndex())
            # 清空列表 / Clear list
            self.ListWidget_decklist.clear()
            # 保存更新 / Save updates
            self.save_decks()
            self.load_decks()
            self.load_cards_info()
            # 获取 ComboBox 中选项的总数 / Get the total number of options in ComboBox
            total_items = self.ComboBox_decks.count()

            # 设置索引为最后一个选项 / Set index to the last option
            self.ComboBox_decks.setCurrentIndex(total_items - 1)
            self.on_combo_changed(self.ComboBox_decks.currentText())
            logger.info(f"delete deck {current_deck_name}")

    def import_deck(self):
        """导入卡组 / Import deck"""
        # 创建一个消息框 / Create a message box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(self.tr("Import Deck"))
        msg_box.setText(self.tr("Please select import method:"))

        # 添加两个按钮 / Add two buttons
        clipboard_button = msg_box.addButton(self.tr("Clipboard Import"), QMessageBox.ActionRole)
        ocr_button = msg_box.addButton(self.tr("OCR Import"), QMessageBox.ActionRole)
        cancel_button = msg_box.addButton(self.tr("Cancel"), QMessageBox.RejectRole)

        msg_box.exec()

        # 根据点击的按钮执行相应操作 / Perform corresponding operation based on the clicked button
        if msg_box.clickedButton() == clipboard_button:
            self.import_from_clipboard()
        elif msg_box.clickedButton() == ocr_button:
            self.import_from_ocr()

    def import_from_clipboard(self):
        """从剪贴板导入卡组 / Import deck from clipboard"""
        clipboard = QClipboard()
        deck_str = clipboard.text()

        try:
            deck_data = json.loads(deck_str)
            # 验证导入的数据格式是否正确（必须包含name和cards字段） / Verify if the imported data format is correct (must contain name and cards fields)
            if not isinstance(deck_data, dict) or 'name' not in deck_data or 'cards' not in deck_data:
                QMessageBox.warning(self, self.tr("Error"), self.tr("Invalid clipboard deck format!")) # type: ignore
                return

            # 验证name不为空且cards是列表 / Verify that name is not empty and cards is a list
            if not deck_data['name'] or not isinstance(deck_data['cards'], list):
                QMessageBox.warning(self, self.tr("Error"), self.tr("Invalid deck data!"))  # type: ignore
                return

            # 检查是否已存在同名卡组 / Check if a deck with the same name already exists
            if any(deck['name'] == deck_data['name'] for deck in self.decks):
                reply = QMessageBox.question(
                    self,
                    self.tr("deck exists"),
                    self.tr('deck') + deck_data["name"] + self.tr('exists,overwrite?'),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if reply == QMessageBox.No:
                    return
                # 删除旧卡组 / Delete old deck
                self.decks = [deck for deck in self.decks if deck['name'] != deck_data['name']]

            # 添加新卡组 / Add new deck
            self.decks.append(deck_data)
            self.save_decks()
            self.load_decks()
            self.ComboBox_decks.setText(deck_data["name"])
            self.on_combo_changed(deck_data["name"])
            QMessageBox.information(self, self.tr("Success"), self.tr("Deck imported successfully!"))

        except json.JSONDecodeError:
            QMessageBox.warning(self, self.tr("Error"), self.tr("Deck data is not valid JSON format!"))# type: ignore
        except Exception as e:
            QMessageBox.warning(self, self.tr("Error"), self.tr("Import failed: ")+str(e))  # type: ignore

    def import_from_ocr(self):
        """从OCR导入卡组 / Import deck from OCR"""
        try:
            # 最小化窗口 / Minimize window
            self.main_window.showMinimized()

            # 获取OCR识别结果 / Get OCR recognition results
            results = self.ocr.process_interactive_region(threshold=0.6)

            if not results:
                QMessageBox.warning(self, self.tr("Notice"), self.tr("No cards detected!")) # type: ignore
                self.main_window.showNormal()
                return

            # 提取匹配到的卡牌名称 / Extract matched card names
            matched_cards = [item["matched_cards"][0] for item in results]

            # 切换到cards界面 / Switch to cards interface
            self.main_window.cardsInterface.LineEdit_deckname.clear()
            self.main_window.cardsInterface.ListWidget_cards.clear()
            # 添加识别到的卡牌 / Add recognized cards
            self.main_window.cardsInterface.ListWidget_cards.addItems(matched_cards)
            # 切换界面 / Switch interface
            self.main_window.switchTo(self.main_window.cardsInterface)
            # 恢复窗口 / Restore window
            self.main_window.showNormal()

        except Exception as e:
            if hasattr(self, "progress"):
                self.main_window.showNormal()
            if "由于目标计算机积极拒绝" in str(e):
                QMessageBox.warning(self, self.tr("Error"), self.tr("OCR is initializing, please wait!")) # type: ignore
            else:
                QMessageBox.warning(self, self.tr("Error"), self.tr("OCR recognition failed:") + (str(e))) # type: ignore

    def apply_deck(self):
        """应用卡组 / Apply deck"""
        current_deck = self.ComboBox_decks.currentText()
        self.load_decks()
        cards = next((deck['cards'] for deck in self.decks if deck['name'] == current_deck), None)
        if cards:
            game_controller = GameController()
            game_controller.apply_deck(current_deck,cards)
        else:
            QMessageBox.warning(self, self.tr("Error"), self.tr("Invalid deck data!")) # type: ignore

        self.ComboBox_decks.setText(current_deck)
        self.on_combo_changed(current_deck)

    def new_deck(self):
        """创建新卡组 / Create new deck"""
        self.main_window.cardsInterface.LineEdit_deckname.clear()
        self.main_window.cardsInterface.ListWidget_cards.clear()
        self.main_window.switchTo(self.main_window.cardsInterface)

    def share_deck(self):
        """分享当前选中的卡组 / Share the currently selected deck"""
        current_deck_name = self.ComboBox_decks.currentText()
        if not current_deck_name:
            return

        # 获取当前卡组数据 / Get current deck data
        current_deck = next((deck for deck in self.decks if deck['name'] == current_deck_name), None)
        if current_deck:
            # 转换为字符串 / Convert to string
            deck_str = json.dumps(current_deck, ensure_ascii=False)
            # 复制到剪贴板 / Copy to clipboard
            clipboard = QClipboard()
            clipboard.setText(deck_str)
            QMessageBox.information(self, self.tr("Success"), self.tr("Deck data copied to clipboard!"))

    def on_item_clicked(self, item):
        """当列表项被点击时更新显示 / Update display when list item is clicked"""
        card_name = item.text()
        self.update_card_display(card_name)

    def update_card_display(self, card_name):
        """更新卡牌图片和信息显示 / Update card image and information display"""
        # 更新图片 / Update image
        image_path = f"AppData/images/cards/zh/{card_name}.jpg"
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():  # 检查图片是否成功加载 / Check if image is successfully loaded
                # 调整图片大小以适应 ImageLabel / Resize image to fit ImageLabel
                scaled_pixmap = pixmap.scaled(
                    self.ImageLabel_card.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.ImageLabel_card.setPixmap(scaled_pixmap)
            else:
                logger.error("Failed to load image: {image_path}")
        else:
            logger.error(f"Image file not found: {image_path}")
            self.ImageLabel_card.clear()  # 清除之前的图片 / Clear previous image

        # 更新信息 / Update information
        card_info = next((card for card in self.cards_info if card['name'] == card_name), None)
        if card_info:
            html_text = f"""<html><head/>
                <body>
                    <p align="center">
                        <span style="font-size:20pt;">{card_info['info']}</span>
                    </p>
                </body></html>"""
            self.DisplayLabel_cardinfo.setText(html_text)

    def save_decks(self):
        """保存卡组数据到文件 / Save deck data to file"""
        try:
            with open('AppData/deck.json', 'w', encoding='utf-8') as f:
                json.dump(self.decks, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Error saving decks: {e}")
