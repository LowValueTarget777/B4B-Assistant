import win32api, win32con, win32gui, win32process
import time
from .ocr import OCRProcessor
import win32clipboard
import win32com.client
import json
import os
from .logger import Logger

logger = Logger.get_logger('game_controller')

class GameController:
    def __init__(self, process_name="Back4Blood.exe"):
        logger.info('Initializing game controller')
        # 获取屏幕分辨率 / Get screen resolution
        self.process_name = process_name
        self.screen_width = win32api.GetSystemMetrics(0)
        self.screen_height = win32api.GetSystemMetrics(1)
        self.ocr = OCRProcessor()
        self.positions = {}
        self.card_positions = 530
        self.shell = win32com.client.Dispatch("WScript.Shell")  # 添加shell作为类属性 / Add shell as class attribute
        self.positions_file = 'AppData/game_positions.json'
        self.load_positions()

    def get_absolute_position(self, rel_x, rel_y):
        """将相对坐标转换为绝对坐标 / Convert relative coordinates to absolute coordinates"""
        return (
            int(rel_x * self.screen_width),
            int(rel_y * self.screen_height)
        )

    def locate_elements(self):
        """定位所有需要的元素 / Locate all required elements"""
        targets = {
            "create_deck": "创建牌组",
            "save_deck": "保存牌组",
            "search": "寻找",
            "custom_deck": "自定义牌组",
        }


        # 获取当前屏幕的OCR结果 / Get the current screen OCR results
        results = self.ocr.process_image(target=list(targets.values()))

        for result in results:
            try:
                text = result['text']
                # 找到当前文本对应的key / Find the key corresponding to the current text
                for key, value in targets.items():
                    if value in text:
                        # 转换为相对坐标并存储 / Convert to relative coordinates and store
                        center_x = result['center'][0] / self.screen_width
                        center_y = result['center'][1] / self.screen_height
                        self.positions[key] = {
                            'x': center_x,
                            'y': center_y
                        }
                        logger.info(f"Found element {text} at position: {center_x:.3f}, {center_y:.3f}")

                        # 如果找到创建牌组，同时设置保存牌组的位置 / If the create deck is found, set the save deck position
                        if key == 'create_deck':
                            self.positions['save_deck'] = {
                                'x': center_x,
                                'y': center_y
                            }
                        # 如果找到保存牌组，同时设置创建牌组的位置 / If the save deck is found, set the create deck position
                        elif key == 'save_deck':
                            self.positions['create_deck'] = {
                                'x': center_x,
                                'y': center_y
                            }
            except Exception as e:
                logger.error(f"Error processing result: {e}")
                continue

        return bool(self.positions)

    def move_to(self, x, y):
        """移动鼠标到指定位置 / Move the mouse to the specified position"""
        win32api.SetCursorPos((x, y))

    def click(self):
        """在当前鼠标位置点击 / Click at the current mouse position"""
        x, y = win32api.GetCursorPos()
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    def click_position(self, position_key, tick=0.1):
        """移动到指定位置并点击 / Move to the specified position and click"""
        if position_key in self.positions:
            pos = self.positions[position_key]
            abs_x, abs_y = self.get_absolute_position(pos['x'], pos['y'])
            self.move_to(abs_x, abs_y)
            time.sleep(tick)  # 等待移动完成 / Wait for the move to complete
            self.click()
            return True
        return False

    def load_positions(self):
        """从文件加载已保存的坐标 / Load saved positions from file"""
        try:
            if os.path.exists(self.positions_file):
                with open(self.positions_file, 'r', encoding='utf-8') as f:
                    self.positions = json.load(f)
                logger.info("Loaded saved positions")
                return True
        except Exception as e:
            logger.error(f"Failed to load position data: {e}")
        return False

    def save_positions(self):
        """保存坐标到文件 / Save positions to file"""
        try:
            os.makedirs(os.path.dirname(self.positions_file), exist_ok=True)
            with open(self.positions_file, 'w', encoding='utf-8') as f:
                json.dump(self.positions, f, ensure_ascii=False, indent=4)
            logger.info("Positions saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save positions: {e}")
            return False

    def verify_positions(self):
        """验证已保存的坐标是否仍然有效 / Verify if the saved positions are still valid"""
        if not self.positions:
            return False

        # 获取搜索按钮的当前位置，限定识别区域 / Get the current position of the search button, limit the recognition area
        results = self.ocr.process_image(target=['寻找'])
        if not results:
            return False

        for result in results:
            if '寻找' in result['text']:
                current_x = result['center'][0] / self.screen_width
                current_y = result['center'][1] / self.screen_height

                # 检查当前位置与保存的位置是否接近（允许5%的误差） / Check if the current position is close to the saved position (allow 5% error)
                if 'search' in self.positions:
                    saved_x = self.positions['search']['x']
                    saved_y = self.positions['search']['y']

                    if (abs(current_x - saved_x) < 0.05 and 
                        abs(current_y - saved_y) < 0.05):
                        logger.info("Position verification successful")
                        return True
                break

        logger.warning("Position verification failed, need to relocate")
        return False

    def initialize_game_positions(self):
        """初始化游戏中的关键位置 / Initialize key positions in the game"""
        # 首先尝试验证已保存的坐标 / First try to verify the saved positions
        if self.verify_positions():
            return True

        # 如果验证失败，重新定位所有元素 / If verification fails, relocate all elements
        if self.locate_elements():
            self.save_positions()  # 保存新的坐标 / Save new positions
            logger.info("All positions located and saved successfully")
            return True
        else:
            logger.error("Failed to locate required elements")
            return False

    def select_all_and_clear(self, tick=0.1):
        """全选并清除文本框内容 / Select all and clear the text box content"""
        # 模拟Ctrl+A全选 / Simulate Ctrl+A to select all
        time.sleep(tick)
        self.shell.SendKeys("^a")
        time.sleep(tick)

        # 模拟Delete键删除 / Simulate Delete key to delete
        self.shell.SendKeys("{DELETE}")
        time.sleep(tick)

    def send_text(self, text, clear_first=True):
        """
        模拟键盘输入文本 / Simulate keyboard input text
        Args:
            text: 要输入的文本 / Text to input
            clear_first: 是否先清除现有文本 / Whether to clear existing text first
        """
        if clear_first:
            self.select_all_and_clear()

        # 将文本复制到剪贴板 / Copy text to clipboard
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()

        # 模拟Ctrl+V / Simulate Ctrl+V
        time.sleep(0.1)
        self.shell.SendKeys("^v")
        time.sleep(0.1)

    def click_with_offset(self, base_position_key, offset_x_1920, offset_y=0, tick=0.1):
        """
        移动到基准位置的偏移处并点击 / Move to the offset position of the base position and click
        """
        if base_position_key not in self.positions:
            return False

        base_pos = self.positions[base_position_key]

        # 计算当前屏幕与1920的比例，并据此调整偏移量 / Calculate the ratio of the current screen to 1920 and adjust the offset accordingly
        screen_ratio = self.screen_width / 1920
        actual_offset_x = offset_x_1920 * screen_ratio

        # 将实际偏移转换为相对值 / Convert the actual offset to relative value
        offset_x_ratio = actual_offset_x / self.screen_width
        offset_y_ratio = offset_y / self.screen_height if offset_y else 0

        # 计算最终的相对坐标 / Calculate the final relative coordinates
        final_x = base_pos['x'] + offset_x_ratio
        final_y = base_pos['y'] + offset_y_ratio

        # 转换为绝对坐标并移动、点击 / Convert to absolute coordinates and move, click
        abs_x, abs_y = self.get_absolute_position(final_x, final_y)
        self.move_to(abs_x, abs_y)
        time.sleep(tick)  # 等待移动完成 / Wait for the move to complete
        self.click()
        return True

    def find_window_by_process_name(self):
        """根据进程名查找窗口句柄 / Find window handle by process name"""
        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    process = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, pid)
                    exe_name = win32process.GetModuleFileNameEx(process, 0)
                    if self.process_name.lower() in exe_name.lower():
                        hwnds.append(hwnd)
                except Exception as e:
                    pass
            return True

        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        self.hwnd = hwnds[0]
        return hwnds

    def activate_window(self):
        """激活窗口 / Activate window"""
        win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(self.hwnd)

    def get_window_resolution(self):
        """获取窗口分辨率 / Get window resolution"""
        rect = win32gui.GetWindowRect(self.hwnd)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        return width, height

    def apply_deck(self, deck_name, cards):
        """应用卡组到游戏中 / Apply deck to the game"""
        logger.info(f'Applying deck: {deck_name}')
        self.find_window_by_process_name()
        self.activate_window()
        time.sleep(0.5)

        # 检查是否有保存的坐标 / Check if there are saved positions
        if not self.positions:
            logger.warning("No saved positions found, starting element location")
            if not self.initialize_game_positions():
                logger.error("Failed to locate game elements, operation aborted")
                return False
        else:
            # 验证已保存坐标是否有效 / Verify if the saved positions are valid
            logger.info("Verifying saved positions")
            if not self.verify_positions():
                logger.warning("Position verification failed, relocating")
                if not self.initialize_game_positions():
                    logger.error("Failed to locate game elements, operation aborted")
                    return False
            else:
                logger.info("Using saved positions")

        # 检查是否找到自定义牌组 / Check if custom deck is found
        while 'custom_deck' not in self.positions:
            if 'create_deck' in self.positions:
                logger.info("Custom deck not found, clicking create deck")
                self.click_position('create_deck', tick=0.5)
                time.sleep(0.5)
                self.locate_elements()
                self.save_positions()  # 保存新获取的坐标 / Save newly obtained positions
            else:
                logger.error("Create deck button not found, exiting")
                return False

        if 'custom_deck' in self.positions:
            # 点击搜索并输入卡组名称 / Click search and enter deck name
            self.click_position('create_deck', tick=0.5)
            time.sleep(0.5)
            self.click_position('custom_deck', tick=0.1)
            self.send_text(deck_name, clear_first=True)

            # 添加卡牌 / Add cards
            for card in cards:
                self.click_position('search')
                time.sleep(0.2)
                self.send_text(card, clear_first=True)
                self.click_with_offset("custom_deck", self.card_positions, tick=0.3)
            self.click_position("search")
            self.select_all_and_clear()
            logger.info('Deck application complete')
            return True
        return False
