
import win32gui
import win32con
from typing import Optional, List
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QMenu

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QMouseEvent
import pyautogui
import time
class UpDownWindow(QWidget):
    def __init__(self, side: str = 'left', parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.side: str = side  # 'left' 或 'right'
        self.ui_widget: Optional[QWidget] = None
        self.pushButton: Optional[QPushButton] = None
        self.pushButton_2: Optional[QPushButton] = None
        self.context_menu: Optional[QMenu] = None  # 右键菜单

        self.init_ui()
        self.setup_window()
        
    def init_ui(self) -> None:
        """初始化UI界面"""
        
        from ui.updownWindow import Ui_Form
        
        self.ui_widget = Ui_Form

        # 获取按钮引用（增加空值检查）
        if self.ui_widget:
            btn1 = self.ui_widget.findChild(QPushButton, "pushButton")
            btn2 = self.ui_widget.findChild(QPushButton, "pushButton_2")
            
            if btn1:
                self.pushButton = btn1
                self.pushButton.clicked.connect(self.simulate_up_key)
                
            if btn2:
                self.pushButton_2 = btn2
                self.pushButton_2.clicked.connect(self.simulate_down_key)
        
        # 设置窗口属性
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # 调整窗口大小以适应内容
        if self.ui_widget:
            self.resize(self.ui_widget.size())
        
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



class penWindow(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.ui_widget: Optional[QWidget] = None
        self.EraserButton: Optional[QPushButton] = None
        self.ExitButton: Optional[QPushButton] = None
        self.PenButton: Optional[QPushButton] = None
        self.context_menu: Optional[QMenu] = None  # 右键菜单

        self.init_ui()
        self.setup_window()
        
    def init_ui(self) -> None:
        """初始化UI界面"""
        from ui.penslot import Ui_Form
        
        self.ui_widget = Ui_Form

        # 获取按钮引用（增加空值检查）
        if self.ui_widget:
            btn1 = self.ui_widget.findChild(QPushButton, "PenButton")
            btn2 = self.ui_widget.findChild(QPushButton, "EraserButton")
            btn3 = self.ui_widget.findChild(QPushButton, "ExitButton")
            if btn1:
                self.PenButton = btn1
                self.PenButton.clicked.connect(self.simulate_Pen_key)
                
            if btn2:
                self.EraserButton = btn2
                self.EraserButton.clicked.connect(self.simulate_Eraser_key)
            
            if btn3:
                self.ExitButton = btn3
                self.ExitButton.clicked.connect(self.simulate_Esc_key)
        
        # 设置窗口属性
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # 调整窗口大小以适应内容
        if self.ui_widget:
            self.resize(self.ui_widget.size())
        
    def setup_window(self) -> None:
        """设置窗口初始位置"""
        # 获取屏幕尺寸
        screen = QGuiApplication.primaryScreen().geometry()
        #screen_width = screen.width()
        screen_height = screen.height()
        
        # 计算窗口位置
        #window_width = self.width()
        #window_height = self.height()
        
        # 居于屏幕右下方
        y = screen_height -100
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
        # 模拟按下向下键
        pyautogui.hotkey('ctrl','P')
       
    def simulate_Eraser_key(self) -> None:
        """模拟橡皮按键"""
        # 查找并激活演示窗口
        hwnd = self.find_presentation_window()
        if hwnd:
            # 激活窗口
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.3)    
        # 模拟按下向下键
        pyautogui.hotkey('ctrl','e')
    def simulate_Esc_key(self) -> None:
        """模拟esc按键"""
        # 查找并激活演示窗口
        hwnd = self.find_presentation_window()
        if hwnd:
            # 激活窗口
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            
        # 模拟按下向下键
        pyautogui.press('esc')