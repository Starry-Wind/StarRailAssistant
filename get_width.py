import win32gui
import win32print
import win32con
import time
from tool.config import modify_json_file
from tool.log import log

def get_width():
    hwnd = win32gui.GetForegroundWindow()  # 根据当前活动窗口获取句柄
    log.info(hwnd)
    Text = win32gui.GetWindowText(hwnd)
    log.info(Text)

    # 获取活动窗口的大小
    window_rect = win32gui.GetWindowRect(hwnd)
    width = window_rect[2] - window_rect[0]
    height = window_rect[3] - window_rect[1]

    # 获取当前显示器的缩放比例
    dc = win32gui.GetWindowDC(hwnd)
    dpi_x = win32print.GetDeviceCaps(dc, win32con.LOGPIXELSX)
    dpi_y = win32print.GetDeviceCaps(dc, win32con.LOGPIXELSY)
    win32gui.ReleaseDC(hwnd, dc)
    scale_x = dpi_x / 96
    scale_y = dpi_y / 96

    # 计算出真实分辨率
    real_width = int(width * scale_x)
    real_height = int(height * scale_y)

    log.info(f"Real resolution: {real_width} x {real_height}")

    modify_json_file('config.json', 'real_width', real_width)
    modify_json_file('config.json', 'real_height', real_height)
