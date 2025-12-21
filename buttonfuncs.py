import win32gui
import win32con
from typing import Optional, List
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QMenu
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QMouseEvent
import pyautogui
import time
import os

# 导入通过uic生成的UI类
from ui.design.updownWindow import Ui_Form
from ui.design.penslot import Ui_Form as penslots

class UpDownWindow(QWidget, Ui_Form):
    def __init__(self, side: str = 'left'):
        # 正确调用父类初始化
        super().__init__()
        
        self.side: str = side  # 'left' 或 'right'
        self.context_menu: Optional[QMenu] = None  # 右键菜单

        # 调用setupUi方法设置UI
        self.setupUi(self)
        
        self.init_ui()
        self.setup_window()
        
    def init_ui(self) -> None:
        """初始化UI界面"""
        # 按钮引用已经通过setupUi设置好了
        if hasattr(self, 'pushButton') and self.pushButton:
            self.pushButton.clicked.connect(self.simulate_up_key)
            
        if hasattr(self, 'pushButton_2') and self.pushButton_2:
            self.pushButton_2.clicked.connect(self.simulate_down_key)
        
        # 设置窗口属性
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
    def setup_window(self) -> None:
        """设置窗口初始位置"""
        # 获取屏幕尺寸
        screen = QGuiApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()
        
        # 计算窗口位置
        window_width = self.width()
        window_height = self.height()
        
        # 垂直居中
        y = (screen_height - window_height) // 2
        
        if self.side == 'left':
            x = 0
        else:  # right
            x = screen_width - window_width
            
        self.move(x, y)
    
    def set_context_menu(self, menu: QMenu) -> None:
        """设置右键菜单"""
        self.context_menu = menu
        
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """鼠标按下事件处理 - 捕获右键点击"""
        # 检测右键点击
        if event.button() == Qt.MouseButton.RightButton and self.context_menu:
            # 在鼠标位置显示右键菜单
            self.context_menu.exec(event.globalPosition().toPoint())
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def find_presentation_window(self) -> Optional[int]:
        """查找WPS或PowerPoint的放映窗口"""
        windows: List[int] = []
        
        def enum_windows_callback(hwnd: int, extra: List[int]) -> bool:
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd) or ""
                class_name = win32gui.GetClassName(hwnd) or ""
                # 查找WPS或PowerPoint的放映窗口
                if (any(keyword in window_text.lower() for keyword in ['wps', 'powerpoint', '演示']) or 
                    any(keyword in class_name.lower() for keyword in ['wpp', 'powerpnt', 'presentation'])):
                    extra.append(hwnd)
            return True
        
        win32gui.EnumWindows(enum_windows_callback, windows)
        return windows[0] if windows else None
    
    def simulate_up_key(self) -> None:
        """模拟上一页按键"""
        # 查找并激活演示窗口
        hwnd = self.find_presentation_window()
        if hwnd:
            # 激活窗口
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            
        # 模拟按下向上键
        pyautogui.press('up')
        
    def simulate_down_key(self) -> None:
        """模拟下一页按键"""
        # 查找并激活演示窗口
        hwnd = self.find_presentation_window()
        if hwnd:
            # 激活窗口
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            
        # 模拟按下向下键
        pyautogui.press('down')


class penWindow(QWidget, penslots):
    def __init__(self):
        # 正确调用父类初始化
        super().__init__()
        
        self.context_menu: Optional[QMenu] = None  # 右键菜单

        # 调用setupUi方法设置UI
        self.setupUi(self)
        
        self.init_ui()
        self.setup_window()
        
    def init_ui(self) -> None:
        """初始化UI界面"""
        # 按钮引用已经通过setupUi设置好了
        # 可以直接使用self.PenButton, self.EraserButton, self.ExitButton
        
        if hasattr(self, 'PenButton') and self.PenButton:
            self.PenButton.clicked.connect(self.simulate_Pen_key)
            
        if hasattr(self, 'EraserButton') and self.EraserButton:
            self.EraserButton.clicked.connect(self.simulate_Eraser_key)
            
        if hasattr(self, 'ExitButton') and self.ExitButton:
            self.ExitButton.clicked.connect(self.simulate_Esc_key)
        
        if hasattr(self, 'whiteBoardButton') and self.whiteBoardButton:
            self.whiteBoardButton.clicked.connect(self.open_sth)
        
        # 设置窗口属性
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowTitle("仅ppt可用")
        
    def setup_window(self) -> None:
        """设置窗口初始位置"""
        # 获取屏幕尺寸
        screen = QGuiApplication.primaryScreen().geometry()
        screen_height = screen.height()
        
        # 居于屏幕左下方
        y = screen_height - 350
        x = 0            
        self.move(x, y)
    
    def set_context_menu(self, menu: QMenu) -> None:
        """设置右键菜单"""
        self.context_menu = menu
        
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """鼠标按下事件处理 - 捕获右键点击"""
        # 检测右键点击
        if event.button() == Qt.MouseButton.RightButton and self.context_menu:
            # 在鼠标位置显示右键菜单
            self.context_menu.exec(event.globalPosition().toPoint())
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def find_presentation_window(self) -> Optional[int]:
        """查找WPS或PowerPoint的放映窗口"""
        windows: List[int] = []
        
        def enum_windows_callback(hwnd: int, extra: List[int]) -> bool:
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd) or ""
                class_name = win32gui.GetClassName(hwnd) or ""
                # 查找WPS或PowerPoint的放映窗口
                if (any(keyword in window_text.lower() for keyword in ['wps', 'powerpoint', '演示']) or 
                    any(keyword in class_name.lower() for keyword in ['wpp', 'powerpnt', 'presentation'])):
                    extra.append(hwnd)
            return True
            
        win32gui.EnumWindows(enum_windows_callback, windows)
        return windows[0] if windows else None
        
    def simulate_Pen_key(self) -> None:
        """模拟笔按键"""
        # 查找并激活演示窗口
        hwnd = self.find_presentation_window()
        if hwnd:
            # 激活窗口
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.3)    
        # 模拟按下Ctrl+P
        pyautogui.hotkey('ctrl', 'p')
       
    def simulate_Eraser_key(self) -> None:
        """模拟橡皮按键"""
        # 查找并激活演示窗口
        hwnd = self.find_presentation_window()
        if hwnd:
            # 激活窗口
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.3)    
        # 模拟按下Ctrl+E
        pyautogui.hotkey('ctrl', 'e')
    
        
    def simulate_Esc_key(self) -> None:
        """模拟esc按键"""
        # 查找并激活演示窗口
        hwnd = self.find_presentation_window()
        if hwnd:
            # 激活窗口
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            
        # 模拟按下Esc键
        pyautogui.press('esc')
    def open_sth(self) -> None:
        """打开希沃白板"""
        softDir = r'"C:\Program Files (x86)\Seewo\EasiNote5\swenlauncher\swenlauncher.exe"'
        os.system(softDir)