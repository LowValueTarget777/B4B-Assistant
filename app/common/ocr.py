import os
import json
import numpy as np
from PIL import Image, ImageGrab
import io
import logging
from typing import List, Dict, Union, Optional, Tuple
from difflib import SequenceMatcher
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QPainter, QColor, QPen, QImage
from PySide6.QtCore import Qt, Signal, QEventLoop, QRect, QPoint
from rapidocr_openvino import RapidOCR
from .logger import Logger

logger = Logger.get_logger('ocr')

class OCRProcessor:
    MAX_RESULTS = 15

    def __init__(self, mainwindo=None):
        logger.info('Initializing OCR processor')
        self.app = QApplication.instance()
        self.mainwindo = mainwindo

        # 设置模型路径 / Set model path
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.model_path = os.path.join(self.root_dir, "AppData", "model")
        self.det_model = os.path.join(self.model_path, "ch_PP-OCRv4_det_infer.onnx")
        self.rec_model = os.path.join(self.model_path, "ch_PP-OCRv4_rec_infer.onnx")

        # 确保模型文件存在 / Ensure model files exist
        self.ensure_model_files()

        # 初始化OCR / Initialize OCR
        self.ocr = RapidOCR(rec_model_path=self.rec_model, det_model_path=self.det_model)
        self.print_model_paths()

        # 加载卡牌数据 / Load card data
        json_path = os.path.join(self.root_dir, "AppData", "cards", "cards_info_zh.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            self.cards_data = json.load(f)

    def ensure_model_files(self):
        """确保模型文件存在 / Ensure model files exist"""
        required_files = [self.det_model, self.rec_model]
        for file in required_files:
            if not os.path.exists(file):
                raise FileNotFoundError(f"Model file not found: {file}")

    def print_model_paths(self):
        """打印模型文件信息 / Print model file information"""
        logger.info(f"Model directory: {self.model_path}")
        if os.path.exists(self.model_path):
            for root, dirs, files in os.walk(self.model_path):
                for file in files:
                    logger.info(os.path.join(root, file))

    def process_image(self, image: Optional[Image.Image] = None, target: Optional[Union[str, List[str]]] = None) -> List[Dict]:
        logger.debug('Processing image')
        """处理图片OCR识别 / Process image OCR recognition"""
        try:
            if image is None:
                image = self.capture_screen()

            img_array = np.array(image)
            result, elapse = self.ocr(img_array)
            ocr_results = self.parse_results(result)
            self.print_results(ocr_results, "识别结果 / Recognition Results")
            logger.debug(f'OCR results: {len(result) if result else 0} text regions found')

            if target:
                if isinstance(target, str):
                    target = [target]
                ocr_results = [res for res in ocr_results if any(t in res['text'] for t in target)]

            return ocr_results
        except Exception as e:
            logger.error(f'Error processing image: {e}', exc_info=True)
            return []

    def parse_results(self, results):
        """解析OCR结果 / Parse OCR results"""
        ocr_results = []
        for line in results:
            coords, text, confidence = line
            center_x = sum(point[0] for point in coords) / 4
            center_y = sum(point[1] for point in coords) / 4

            ocr_results.append({
                'text': text,
                'coordinates': coords,
                'center': (round(center_x, 2), round(center_y, 2)),
                'confidence': round(float(confidence), 4)
            })
        return ocr_results

    def _calculate_similarity(self, a: str, b: str) -> float:
        """计算相似度 / Calculate similarity"""
        return SequenceMatcher(None, a, b).ratio()

    def _find_similar_cards(self, text: str, threshold: float = 0.6) -> List[str]:
        """查找相似卡牌 / Find similar cards"""
        best_match = None
        best_similarity = threshold

        for card in self.cards_data:
            similarity = self._calculate_similarity(text, card['name'])
            if similarity >= best_similarity:
                best_similarity = similarity
                best_match = card['name']

        return [best_match] if best_match else []

    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> Image.Image:
        """截取屏幕区域 / Capture screen region"""
        return ImageGrab.grab(bbox=region)

    def capture_screen_interactive(self) -> Optional[Image.Image]:
        """使用交互式方式捕获屏幕区域 / Capture screen region interactively"""
        screenshot_widget = ScreenshotWidget()

        # 等待截图完成 / Wait for screenshot to complete
        loop = QEventLoop()
        screenshot_widget.finished.connect(loop.quit)
        screenshot_widget.finished.connect(lambda x: setattr(self, "_temp_screenshot", x))

        try:
            loop.exec()
            return getattr(self, "_temp_screenshot", None)
        except Exception as e:
            logger.error(f"截图出错: {e}")
            return None
        finally:
            if hasattr(self, "_temp_screenshot"):
                delattr(self, "_temp_screenshot")

    def process_interactive_region(self, threshold: float = 0.6) -> List[Dict]:
        """交互式框选识别 / Interactive region selection recognition"""
        screenshot = self.capture_screen_interactive()
        if self.mainwindo is not None:
            self.mainwindo.showNormal()
        if screenshot is None:
            return []

        results = self.process_image(screenshot)
        matched_results = []
        matched_cards_set = set()

        results.sort(key=lambda x: (x['center'][1], x['center'][0]))

        for result in results:
            if len(matched_cards_set) >= 15:
                break

            similar_cards = self._find_similar_cards(result['text'], threshold)
            if similar_cards:
                card_name = similar_cards[0]
                if card_name not in matched_cards_set:
                    matched_cards_set.add(card_name)
                    matched_results.append({
                        'original_text': result['text'],
                        'matched_cards': [card_name],
                        'position': result['center']
                    })
        return matched_results

    def print_results(self, results: List[Dict], title: str = "识别结果") -> None:
        """格式化打印OCR识别结果 / Format and print OCR recognition results"""
        print(f"\n=== {title} ===")
        if results:
            print(f"找到 {len(results)} 个匹配结果:")
            for idx, result in enumerate(results, 1):
                print(f"\n结果 {idx}:")
                print(f"文字: {result['text']}")
                print(f"中心点: {result['center']}")
                print(f"坐标: {result['coordinates']}")
                print(f"置信度: {result['confidence']}")
                print("-" * 50)
        else:
            print("未找到匹配的文字")

class ScreenshotWidget(QWidget):
    finished = Signal(object)

    def __init__(self):
        super().__init__()
        self.begin = QPoint()
        self.end = QPoint()
        self.is_drawing = False
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background-color:black;")
        self.setWindowState(Qt.WindowFullScreen)
        self.setWindowOpacity(0.6)
        self.setCursor(Qt.CrossCursor)
        self.show()

    def paintEvent(self, event):
        """绘制事件 / Paint event"""
        if self.is_drawing:
            painter = QPainter(self)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 120))

            if not self.begin.isNull() and not self.end.isNull():
                rect = QRect(self.begin, self.end)
                painter.setCompositionMode(QPainter.CompositionMode_Clear)
                painter.fillRect(rect, Qt.transparent)

                painter.setCompositionMode(QPainter.CompositionMode_Source)
                pen = QPen(Qt.red, 2)
                painter.setPen(pen)
                painter.drawRect(rect)

    def mousePressEvent(self, event):
        """鼠标按下事件 / Mouse press event"""
        if event.button() == Qt.LeftButton:
            self.begin = event.pos()
            self.end = self.begin
            self.is_drawing = True
            self.update()

    def mouseMoveEvent(self, event):
        """鼠标移动事件 / Mouse move event"""
        if self.is_drawing:
            self.end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件 / Mouse release event"""
        if event.button() == Qt.LeftButton:
            if self.begin and self.end:
                self.capture_screenshot()
            self.close()

    def keyPressEvent(self, event):
        """按键事件 / Key press event"""
        if event.key() == Qt.Key_Escape:
            self.close()

    def capture_screenshot(self):
        """捕获截图 / Capture screenshot"""
        if self.begin and self.end:
            rect = QRect(self.begin, self.end)
            rect = rect.normalized()

            if rect.width() < 10 or rect.height() < 10:
                return

            try:
                screen = QApplication.primaryScreen()
                pixmap = screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())
                image = pixmap.toImage()

                width = image.width()
                height = image.height()

                format = image.format()
                if format == QImage.Format_RGB32:
                    bits = image.bits()
                    arr = np.frombuffer(bits, np.uint8).reshape(height, width, 4)
                    arr = arr[:, :, :3]
                else:
                    image = image.convertToFormat(QImage.Format_RGB32)
                    bits = image.bits()
                    arr = np.frombuffer(bits, np.uint8).reshape(height, width, 4)
                    arr = arr[:, :, :3]

                pil_image = Image.fromarray(arr)
                self.finished.emit(pil_image)

            except Exception as e:
                print(f"截图错误: {e}")
            finally:
                self.close()
