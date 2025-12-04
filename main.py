import sys
import os
import win32gui
import win32con
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QSystemTrayIcon, QMenu, QMessageBox, QStyle
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut, QIcon, QAction
import psutil
import pyautogui


class FloatWindow(QWidget):
    def __init__(self, side='left'):
        super().__init__()
        self.side = side  # 'left' 或 'right'
        self.init_ui()
        self.setup_window()
        
    def init_ui(self):
        # 加载UI文件
        loader = QUiLoader()
        ui_file = os.path.join(os.path.dirname(__file__), "floatWindow2.ui")
        widget = loader.load(ui_file, self)
        
        # 获取按钮引用
        self.pushButton = widget.findChild(QPushButton, "pushButton")
        self.pushButton_2 = widget.findChild(QPushButton, "pushButton_2")
        
        # 连接按钮信号与槽
        self.pushButton.clicked.connect(self.simulate_up_key)
        self.pushButton_2.clicked.connect(self.simulate_down_key)
        
        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # 调整窗口大小以适应内容
        self.resize(widget.size())
        
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
        
        if self.side == 'left':
            x = 0
        else:  # right
            x = screen_width - window_width
            
        self.move(x, y)
        
    def find_presentation_window(self):
        """查找WPS或PowerPoint的放映窗口"""
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                class_name = win32gui.GetClassName(hwnd)
                # 查找WPS或PowerPoint的放映窗口
                if any(keyword in window_text.lower() for keyword in ['wps', 'powerpoint', '演示']) or \
                   any(keyword in class_name.lower() for keyword in ['wpp', 'powerpnt', 'presentation']):
                    windows.append(hwnd)
            return True
        
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        return windows[0] if windows else None
    
    def simulate_up_key(self):
        # 查找并激活演示窗口
        hwnd = self.find_presentation_window()
        if hwnd:
            # 激活窗口
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            
        # 模拟按下向上键
        pyautogui.press('up')
        
    def simulate_down_key(self):
        # 查找并激活演示窗口
        hwnd = self.find_presentation_window()
        if hwnd:
            # 激活窗口
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            
        # 模拟按下向下键
        pyautogui.press('down')


class PPTController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.left_window = None
        self.right_window = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_ppt_processes)
        self.timer.start(1000)  # 每秒检查一次
        
        # 创建系统托盘图标
        self.create_system_tray_icon()
        
    def create_system_tray_icon(self):
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon()
        
        # 设置图标（使用默认的应用图标）
        self.tray_icon.setIcon(self.app.style().standardIcon(QStyle.SP_ComputerIcon))
        
        # 创建右键菜单
        tray_menu = QMenu()
        
        # 添加菜单项
        show_action = QAction("显示窗口", self.app)
        show_action.triggered.connect(self.show_windows)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("隐藏窗口", self.app)
        hide_action.triggered.connect(self.hide_windows)
        tray_menu.addAction(hide_action)
        
        exit_action = QAction("退出", self.app)
        exit_action.triggered.connect(self.exit_app)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        
        # 显示系统托盘图标
        self.tray_icon.show()
        
        # 连接系统托盘图标激活信号
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        
    def on_tray_icon_activated(self, reason):
        # 处理系统托盘图标被点击事件
        if reason == QSystemTrayIcon.Trigger:
            # 单击托盘图标时显示/隐藏窗口
            if self.left_window and self.left_window.isVisible():
                self.hide_windows()
            else:
                self.show_windows()
                
    def check_ppt_processes(self):
        # 检查是否有PowerPoint或WPS进程在运行
        ppt_running = False
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name'].lower()
                if 'powerpnt' in proc_name or 'wps' in proc_name:
                    ppt_running = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
                
        # 根据PPT是否运行来显示或隐藏窗口
        if ppt_running:
            self.show_windows()
        else:
            self.hide_windows()
            
    def show_windows(self):
        if self.left_window is None:
            self.left_window = FloatWindow('left')
        if self.right_window is None:
            self.right_window = FloatWindow('right')
            
        self.left_window.show()
        self.right_window.show()
        
    def hide_windows(self):
        if self.left_window:
            self.left_window.hide()
        if self.right_window:
            self.right_window.hide()
            
    def exit_app(self):
        # 退出应用程序
        self.hide_windows()
        self.tray_icon.hide()
        self.app.quit()
        
    def run(self):
        # 初始检查
        self.check_ppt_processes()
        sys.exit(self.app.exec())


if __name__ == "__main__":
    controller = PPTController()
    controller.run()