import sys
import os
import json
import win32gui
import win32con
import winreg
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QSystemTrayIcon, QMenu, QMessageBox, QStyle
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QKeySequence, QShortcut, QIcon, QAction
import psutil
import pyautogui


class FloatWindow(QWidget):
    def __init__(self, side='left'):
        super().__init__()
        self.side = side  # 'left' 或 'right'
        self.draggable = False  # 控制窗口是否可拖拽
        self.init_ui()
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
        
        if self.side == 'left':
            x = 0
        else:  # right
            x = screen_width - window_width
            
        self.move(x, y)
        
    def mousePressEvent(self, event):
        """处理鼠标按下事件，用于窗口拖拽"""
        if self.draggable and event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)  # 让子控件处理事件
            
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件，用于窗口拖拽"""
        if self.draggable and event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        else:
            super().mouseMoveEvent(event)  # 让子控件处理事件
            
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件，保存窗口位置"""
        if self.draggable and event.button() == Qt.LeftButton and self.drag_position is not None:
            self.drag_position = None
            self.save_position()  # 保存当前位置
            event.accept()
        else:
            super().mouseReleaseEvent(event)  # 让子控件处理事件
        
    def get_position_file_path(self):
        """获取位置信息文件路径"""
        return os.path.join(os.path.dirname(__file__), f"window_position_{self.side}.json")
        
    def save_position(self):
        """保存窗口位置和屏幕分辨率到JSON文件"""
        # 获取当前屏幕信息
        screen = QApplication.primaryScreen().geometry()
        screen_info = {
            "width": screen.width(),
            "height": screen.height()
        }
        
        # 获取当前窗口位置
        position = {
            "x": self.x(),
            "y": self.y()
        }
        
        # 保存到JSON文件
        data = {
            "screen": screen_info,
            "position": position
        }
        
        try:
            with open(self.get_position_file_path(), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存位置信息失败: {e}")
            
    def load_position(self):
        """从JSON文件加载窗口位置信息"""
        try:
            file_path = self.get_position_file_path()
            if not os.path.exists(file_path):
                return False
                
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 获取当前屏幕信息
            screen = QApplication.primaryScreen().geometry()
            current_screen = {
                "width": screen.width(),
                "height": screen.height()
            }
            
            # 检查屏幕分辨率是否匹配
            saved_screen = data.get("screen", {})
            if saved_screen.get("width") == current_screen["width"] and \
               saved_screen.get("height") == current_screen["height"]:
                # 分辨率匹配，应用保存的位置
                position = data.get("position", {})
                x = position.get("x", 0)
                y = position.get("y", 0)
                self.move(x, y)
                return True
            else:
                # 分辨率不匹配，使用默认位置
                return False
                
        except Exception as e:
            print(f"加载位置信息失败: {e}")
            return False
    
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
    def __init__(self, app):
        self.app = app
        self.left_window = None
        self.right_window = None
        self.presentation_mode_active = False  # 标记是否处于演示模式
        self.startup_enabled = self.is_auto_startup_enabled()  # 开机自启动状态
        self.last_process_check = set()  # 上次检查时的进程列表
        
        # 创建系统托盘图标
        self.create_system_tray_icon()
        self.setup_process_monitoring()
        
    def setup_process_monitoring(self):
        """设置进程监控"""
        # 使用定时器定期检查进程
        self.process_timer = QTimer()
        self.process_timer.timeout.connect(self.check_presentation_processes)
        self.process_timer.start(2000)  # 每2秒检查一次
        
    def create_system_tray_icon(self):
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon()
        
        # 设置图标（使用自定义图标）
        icon_path = os.path.join(os.path.dirname(__file__),"ui","icon.png")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # 如果图标文件不存在，则使用默认的应用图标
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
        
        # 添加位置调整模式复选框
        self.position_adjust_action = QAction("调整悬浮窗位置", self.app)
        self.position_adjust_action.setCheckable(True)
        self.position_adjust_action.triggered.connect(self.toggle_position_adjust_mode)
        tray_menu.addAction(self.position_adjust_action)
        
        # 添加开机自启动复选框
        self.startup_action = QAction("开机自启动", self.app)
        self.startup_action.setCheckable(True)
        self.startup_action.setChecked(self.startup_enabled)
        self.startup_action.triggered.connect(self.toggle_startup)
        tray_menu.addAction(self.startup_action)
        
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
                
    def check_presentation_processes(self):
        """检查演示进程并控制窗口显示"""
        presentation_detected = False
        
        # 检查PowerPoint或WPS进程
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name'].lower()
                
                # 检查是否为PowerPoint或WPS演示相关进程
                if any(keyword in proc_name for keyword in ['powerpnt', 'wpp', 'wps']):
                    presentation_detected = True
                    break
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # 根据检测结果显示或隐藏窗口
        if presentation_detected and not self.presentation_mode_active:
            self.presentation_mode_active = True
            self.show_windows()
        elif not presentation_detected and self.presentation_mode_active:
            self.presentation_mode_active = False
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
            
    def toggle_position_adjust_mode(self, checked):
        """切换悬浮窗位置调整模式"""
        self.show_windows()
        self.position_adjust_mode = checked
        
        # 更新悬浮窗的拖拽状态
        if self.left_window:
            self.left_window.draggable = checked
            # 根据模式设置窗口属性
            if checked:
                # 调整位置模式：窗口可拖拽，按钮不可点击
                self.left_window.setWindowOpacity(0.7)  # 半透明效果提示用户处于调整模式
                # 禁用按钮
                self.left_window.pushButton.setEnabled(False)
                self.left_window.pushButton_2.setEnabled(False)
            else:
                # 正常操作模式：按钮可点击，窗口不可拖拽
                self.left_window.setWindowOpacity(1.0)
                # 启用按钮
                self.left_window.pushButton.setEnabled(True)
                self.left_window.pushButton_2.setEnabled(True)
                
        if self.right_window:
            self.right_window.draggable = checked
            # 根据模式设置窗口属性
            if checked:
                # 调整位置模式：窗口可拖拽，按钮不可点击
                self.right_window.setWindowOpacity(0.7)  # 半透明效果提示用户处于调整模式
                # 禁用按钮
                self.right_window.pushButton.setEnabled(False)
                self.right_window.pushButton_2.setEnabled(False)
            else:
                # 正常操作模式：按钮可点击，窗口不可拖拽
                self.right_window.setWindowOpacity(1.0)
                # 启用按钮
                self.right_window.pushButton.setEnabled(True)
                self.right_window.pushButton_2.setEnabled(True)
                
    def toggle_startup(self, checked):
        """切换开机自启动"""
        success = self.set_auto_startup(checked)
        if not success:
            # 如果设置失败，恢复复选框状态
            self.startup_action.setChecked(not checked)
            # 显示错误消息
            self.tray_icon.showMessage("错误", "设置开机自启动失败", QSystemTrayIcon.Critical)
    
    def exit_app(self):
        # 退出应用程序
        self.hide_windows()
        self.tray_icon.hide()
        self.app.quit()
        
    def get_startup_key(self):
        """获取Windows启动项注册表键"""
        return r"Software\Microsoft\Windows\CurrentVersion\Run"
        
    def is_auto_startup_enabled(self):
        """检查是否已设置开机自启动"""
        try:
            # 打开注册表键
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.get_startup_key(), 0, winreg.KEY_READ)
            # 尝试读取值
            winreg.QueryValueEx(key, "PPTController")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            # 键不存在
            return False
        except Exception:
            # 其他错误
            return False
            
    def set_auto_startup(self, enable=True):
        """设置开机自启动"""
        try:
            # 打开注册表键
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.get_startup_key(), 0, winreg.KEY_WRITE)
            
            if enable:
                # 获取当前Python脚本的路径
                script_path = os.path.abspath(sys.argv[0])
                # 添加到启动项
                winreg.SetValueEx(key, "PPTController", 0, winreg.REG_SZ, f'"{sys.executable}" "{script_path}"')
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
        
    def run(self):
        # 初始检查
        self.check_presentation_processes()
        sys.exit(self.app.exec())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = PPTController(app)
    controller.run()