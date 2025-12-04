# PPT翻页助手 (thenextpage)

这是一个基于PySide6开发的PPT翻页辅助工具。当检测到PowerPoint或WPS演示文稿程序运行时，会在屏幕左右两侧显示透明背景的控制窗口，通过点击按钮可以模拟键盘的上下方向键来实现PPT翻页。此程序也是EasyWriteWhiteboard的一部分，用于在演示过程中更方便地控制PPT翻页。

## 功能特点

- 自动检测PowerPoint或WPS进程
- 在屏幕左右两侧显示透明控制窗口
- 窗口始终保持置顶
- 上箭头按钮模拟键盘向上键（上一页）
- 下箭头按钮模拟键盘向下键（下一页）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

直接运行main.py文件：

```bash
python main.py
```

程序会自动在后台运行，当检测到PowerPoint或WPS运行时，会在屏幕左右两侧显示控制窗口。

## 按钮说明

- ↑ 按钮：模拟键盘向上键（上一页）
- ↓ 按钮：模拟键盘向下键（下一页）

## 技术实现

本程序使用以下技术：
- PySide6：用于创建GUI界面
- psutil：用于检测系统进程
- pyautogui：用于模拟键盘按键

## 注意事项

1. 首次运行可能需要允许Python访问屏幕录制权限（macOS）或管理员权限（Windows）
2. 程序会持续监控系统进程，可能会轻微增加CPU占用
3. 如果遇到按键无效，请确保PPT窗口处于活动状态