import sys
import os
import json
import win32gui
import win32con
import winreg
from typing import Optional, List
from PySide6.QtWidgets import (QApplication, QWidget, QPushButton, QSystemTrayIcon, QMenu, QStyle)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import (Qt, QTimer, QEvent, QPoint)
from PySide6.QtGui import (QIcon, QAction, QGuiApplication, QMouseEvent)
import psutil
import pyautogui


class FloatWindow(QWidget):
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
        # 加载UI文件
        loader = QUiLoader()
        ui_file = os.path.join(os.path.dirname(__file__), "ui", "floatWindow2.ui")
        
        self.ui_widget = loader.load(ui_file, self)

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


class PPTController:
    def __init__(self, app: QApplication):
        self.app = app
        self.left_window: Optional[FloatWindow] = None
        self.right_window: Optional[FloatWindow] = None
        self.presentation_mode_active: bool = False  # 标记是否处于演示模式
        self.startup_enabled: bool = self.is_auto_startup_enabled()  # 开机自启动状态
        self.last_process_check: set = set()  # 上次检查时的进程列表
        self.position_adjust_mode: bool = False
        self.process_timer: Optional[QTimer] = None
        self.tray_icon: Optional[QSystemTrayIcon] = None
        self.startup_action: Optional[QAction] = None
        self.tray_menu: Optional[QMenu] = None  # 保存托盘菜单引用
        
        # 创建系统托盘图标
        self.create_system_tray_icon()
        self.setup_process_monitoring()
        
    def setup_process_monitoring(self) -> None:
        """设置进程监控"""
        # 使用定时器定期检查进程
        self.process_timer = QTimer()
        self.process_timer.timeout.connect(self.check_presentation_processes)
        self.process_timer.start(2000)  # 每2秒检查一次
        
    def create_system_tray_icon(self) -> None:
        """创建系统托盘图标"""
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(self.app)
        
        # 设置图标（使用自定义图标）
        icon_path = os.path.join(os.path.dirname(__file__), "ui", "icon.png")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # 如果图标文件不存在，则使用默认的应用图标
            style = self.app.style()
            standard_icon = style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
            self.tray_icon.setIcon(standard_icon)
        
        # 创建右键菜单
        self.tray_menu = QMenu()
        
        # 添加菜单项
        show_action = QAction("显示窗口", self.app)
        show_action.triggered.connect(self.show_windows)
        self.tray_menu.addAction(show_action)
        
        hide_action = QAction("隐藏窗口", self.app)
        hide_action.triggered.connect(self.hide_windows)
        self.tray_menu.addAction(hide_action)
        
        # 添加开机自启动复选框
        self.startup_action = QAction("开机自启动", self.app)
        self.startup_action.setCheckable(True)
        self.startup_action.setChecked(self.startup_enabled)
        self.startup_action.triggered.connect(self.toggle_startup)
        self.tray_menu.addAction(self.startup_action)
        
        exit_action = QAction("退出", self.app)
        exit_action.triggered.connect(self.exit_app)
        self.tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        
        # 显示系统托盘图标
        self.tray_icon.show()
        
        # 连接系统托盘图标激活信号
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        
    def on_tray_icon_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """处理系统托盘图标被点击事件"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # 单击托盘图标时显示/隐藏窗口
            if self.left_window and self.left_window.isVisible():
                self.hide_windows()
            else:
                self.show_windows()
                
    def check_presentation_processes(self) -> None:
        """检查演示进程并控制窗口显示"""
        presentation_detected = False
        
        # 检查PowerPoint或WPS进程
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info.get('name', '') or ""
                # 增加空值检查后再调用lower()
                proc_name_lower = proc_name.lower()
                
                # 检查是否为PowerPoint或WPS演示相关进程
                if any(keyword in proc_name_lower for keyword in ['powerpnt', 'wpp', 'wps']):
                    presentation_detected = True
                    break
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # 根据检测结果显示或隐藏窗口
        if presentation_detected and not self.presentation_mode_active:
            self.presentation_mode_active = True
            self.show_windows()
        elif not presentation_detected and self.presentation_mode_active:
            self.presentation_mode_active = False
            self.hide_windows()
            
    def show_windows(self) -> None:
        """显示悬浮窗口"""
        if self.left_window is None:
            self.left_window = FloatWindow('left')
            # 为悬浮窗设置右键菜单
            if self.tray_menu:
                self.left_window.set_context_menu(self.tray_menu)
                
        if self.right_window is None:
            self.right_window = FloatWindow('right')
            # 为悬浮窗设置右键菜单
            if self.tray_menu:
                self.right_window.set_context_menu(self.tray_menu)
            
        self.left_window.show()
        self.right_window.show()
        
    def hide_windows(self) -> None:
        """隐藏悬浮窗口"""
        if self.left_window:
            self.left_window.hide()
        if self.right_window:
            self.right_window.hide()
            
    def toggle_startup(self, checked: bool) -> None:
        """切换开机自启动"""
        success = self.set_auto_startup(checked)
        if not success and self.startup_action:
            # 如果设置失败，恢复复选框状态
            self.startup_action.setChecked(not checked)
            # 显示错误消息
            if self.tray_icon:
                self.tray_icon.showMessage(
                    "错误", 
                    "设置开机自启动失败", 
                    QSystemTrayIcon.MessageIcon.Critical
                )
    
    def exit_app(self) -> None:
        """退出应用程序"""
        self.hide_windows()
        if self.tray_icon:
            self.tray_icon.hide()
        self.app.quit()
        
    def get_startup_key(self) -> str:
        """获取Windows启动项注册表键"""
        return r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    def get_exe_full_path(self) -> str:
        """获取打包后EXE的绝对路径（适配开发/打包环境）"""
        if getattr(sys, 'frozen', False):
            # 打包为EXE的环境（PyInstaller）
            exe_path = sys.executable  # 直接指向EXE文件
        else:
            # 开发环境（脚本）
            exe_path = os.path.abspath(sys.argv[0])
        # 转为绝对路径并处理空格（避免注册表命令出错）
        return os.path.normpath(exe_path)
        
    def is_auto_startup_enabled(self) -> bool:
        """检查是否已设置开机自启动"""
        try:
            # 打开注册表键
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, 
                self.get_startup_key(), 
                0, 
                winreg.KEY_READ
            )
            # 尝试读取值
            winreg.QueryValueEx(key, "PPTController")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            # 键不存在
            return False
        except Exception as e:
            print(f"检查自启动状态失败: {e}")
            return False
            
    def set_auto_startup(self, enable: bool = True) -> bool:
        """设置开机自启动（适配EXE/脚本）"""
        try:
            # 打开注册表键
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, 
                self.get_startup_key(), 
                0, 
                winreg.KEY_WRITE
            )
            
            if enable:
                # 获取EXE/脚本的绝对路径（核心修改）
                exe_path = self.get_exe_full_path()
                # 注册表写入格式：带引号的路径（处理含空格的路径）
                startup_cmd = f'"{exe_path}"'
                # 写入注册表
                winreg.SetValueEx(key, "PPTController", 0, winreg.REG_SZ, startup_cmd)
            else:
                # 从启动项中删除
                try:
                    winreg.DeleteValue(key, "PPTController")
                except FileNotFoundError:
                    # 值不存在，忽略错误
                    pass
                    
            winreg.CloseKey(key)
            self.startup_enabled = enable
            return True
        except Exception as e:
            print(f"设置开机自启动失败: {e}")
            return False
        
    def run(self) -> None:
        """运行应用程序"""
        # 初始检查
        self.check_presentation_processes()
        sys.exit(self.app.exec())


if __name__ == "__main__":
    # 解决高DPI显示问题
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关闭最后一个窗口时不退出应用
    controller = PPTController(app)
    controller.run()