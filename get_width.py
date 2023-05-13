'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-05-13 23:45:35
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-05-14 01:18:24
FilePath: \Honkai-Star-Rail-beta-2.4h:\Download\Zip\Honkai-Star-Rail-beta-2.7\get_width.py
Description: 

Copyright (c) 2023 by ${git_name_email}, All Rights Reserved. 
'''
import time


import win32con
import win32gui
import win32print

from tools.config import init_config_file, modify_json_file, normalize_file_path, CONFIG_FILE_NAME
from tools.log import log


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

    if not normalize_file_path(CONFIG_FILE_NAME):
        init_config_file(real_width=real_width, real_height=real_height)

    log.info(f"Real resolution: {real_width} x {real_height}")

    modify_json_file(CONFIG_FILE_NAME, "real_width", real_width)
    modify_json_file(CONFIG_FILE_NAME, "real_height", real_height)
