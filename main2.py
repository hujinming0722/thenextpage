import sys
import os
import json
import win32gui
import win32con
import winreg
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QSystemTrayIcon, QMenu, QMessageBox, QStyle
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QAction,QMouseEvent
import psutil
import pyautogui
class FloatWindow(QWidget):
    def __init__(self, side='left'):
        super().__init__()
        self.draggable = False  # 控制窗口是否可拖拽
        self.init_ui()
        self.side = side
        self.setup_window()
        self.load_position()  # 加载保存的位置
        self.drag_position = None  # 用于窗口拖拽
    def init_ui(self):
        # 加载UI文件
        loader = QUiLoader()
        ui_file = os.path.join(os.path.dirname(__file__), "ui","floatWindow2.ui")
        self.ui_widget = loader.load(ui_file, self)
        
        # 获取按钮引用
        self.pushButton = self.ui_widget.findChild(QPushButton, "pushButton")
        self.pushButton_2 = self.ui_widget.findChild(QPushButton, "pushButton_2")
        
        # 连接按钮信号与槽
        self.pushButton.clicked.connect(self.simulate_up_key)
        self.pushButton_2.clicked.connect(self.simulate_down_key)
        
        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # 调整窗口大小以适应内容
        self.resize(self.ui_widget.size())
         
    def setup_window(self):
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()
        
        # 计算窗口位置
        window_width = self.width()
        window_height = self.height()
        # 垂直居中
        y = (screen_height - window_height) // 2
        #只能说基本功不扎实是这样的，ai写的代码根本看不懂啊喂，参数往哪边传都不知道，只知道从某个地方调用他时加r或l可以输出不同位置
        if self.side == 'left':
            x = 0
        else:  # 右边的
            x = screen_width - window_width
            
        self.move(x, y)
    def mousePressEvent(self, event):
        """处理鼠标按下事件，用于窗口拖拽"""
        if self.draggable and event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)  # 让子控件处理事件
            
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件，用于窗口拖拽"""
        if self.draggable and event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        else:
            super().mouseMoveEvent(event)  # 让子控件处理事件
            
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件，保存窗口位置"""
        if self.draggable and event.button() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            self.drag_position = None
            self.save_position()  # 保存当前位置
            event.accept()
        else:
            super().mouseReleaseEvent(event)  # 让子控件处理事件
        
