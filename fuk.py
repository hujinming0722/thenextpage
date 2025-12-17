import sys
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QPen, QColor, QBrush


class AnnotationWidget(QWidget):
    """可进行批注的透明窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 设置窗口属性
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
        )
        
        # 设置窗口半透明背景
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 设置窗口为全屏
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)
        
        # 批注相关变量
        self.drawing = False
        self.paths = []  # 存储所有绘制的路径
        self.current_path = []  # 当前正在绘制的路径
        self.pen_width = 5
        self.pen_color = QColor(255, 0, 0)  # 红色
        self.annotation_mode = True  # 批注模式
        
        # 确保能接收键盘和鼠标事件
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        
        # 显示指令提示
        print("指令:")
        print("  鼠标左键: 绘制")
        print("  ESC: 退出")
        print("  C: 清除所有批注")
        print("  R: 切换红色笔")
        print("  G: 切换绿色笔")
        print("  B: 切换蓝色笔")
        print("  +: 增大笔宽")
        print("  -: 减小笔宽")
        
    def paintEvent(self, event):
        """绘制批注内容"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制所有已保存的路径
        for path_info in self.paths:
            pen = QPen(path_info['color'], path_info['width'])
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)
            
            path_points = path_info['points']
            if len(path_points) > 1:
                for i in range(len(path_points) - 1):
                    painter.drawLine(path_points[i], path_points[i+1])
        
        # 绘制当前路径
        if self.current_path and len(self.current_path) > 1:
            pen = QPen(self.pen_color, self.pen_width)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)
            
            for i in range(len(self.current_path) - 1):
                painter.drawLine(self.current_path[i], self.current_path[i+1])
        
        # 绘制当前画笔位置（圆形光标）
        if self.drawing:
            painter.setBrush(QBrush(self.pen_color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(self.current_path[-1], 
                              self.pen_width//2, 
                              self.pen_width//2)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton and self.annotation_mode:
            self.drawing = True
            point = event.position().toPoint()
            self.current_path = [point]
            self.update()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.drawing and event.buttons() & Qt.LeftButton:
            point = event.position().toPoint()
            self.current_path.append(point)
            self.update()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            if self.current_path and len(self.current_path) > 1:
                # 保存当前路径
                self.paths.append({
                    'points': self.current_path.copy(),
                    'color': self.pen_color,
                    'width': self.pen_width
                })
                self.current_path.clear()
                self.update()
    
    def keyPressEvent(self, event):
        """键盘事件处理"""
        key = event.key()
        
        if key == Qt.Key_Escape:
            # ESC键退出
            self.close()
            
        elif key == Qt.Key_C:
            # C键清除所有批注
            self.paths.clear()
            self.current_path.clear()
            self.update()
            print("已清除所有批注")
            
        elif key == Qt.Key_R:
            # R键切换红色笔
            self.pen_color = QColor(255, 0, 0)
            print("切换到红色笔")
            
        elif key == Qt.Key_G:
            # G键切换绿色笔
            self.pen_color = QColor(0, 255, 0)
            print("切换到绿色笔")
            
        elif key == Qt.Key_B:
            # B键切换蓝色笔
            self.pen_color = QColor(0, 0, 255)
            print("切换到蓝色笔")
            
        elif key == Qt.Key_Plus or key == Qt.Key_Equal:
            # +键增大笔宽
            self.pen_width = min(50, self.pen_width + 2)
            print(f"笔宽增大到: {self.pen_width}")
            
        elif key == Qt.Key_Minus or key == Qt.Key_Underscore:
            # -键减小笔宽
            self.pen_width = max(1, self.pen_width - 2)
            print(f"笔宽减小到: {self.pen_width}")
            
        elif key == Qt.Key_W:
            # W键切换笔/橡皮擦模式
            if self.pen_color == QColor(255, 255, 255):
                self.pen_color = QColor(255, 0, 0)
                print("切换到笔模式（红色）")
            else:
                self.pen_color = QColor(255, 255, 255)
                self.pen_width = 20
                print("切换到橡皮擦模式")
        
        elif key == Qt.Key_P:
            # P键打印当前状态
            print(f"当前笔颜色: RGB({self.pen_color.red()}, {self.pen_color.green()}, {self.pen_color.blue()})")
            print(f"当前笔宽: {self.pen_width}")
            print(f"批注数量: {len(self.paths)}")


def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle("Fusion")
    
    # 创建批注窗口
    window = AnnotationWidget()
    window.setWindowTitle("屏幕批注工具")
    
    # 显示窗口
    window.show()
    
    # 确保窗口获得焦点
    window.raise_()
    window.activateWindow()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()