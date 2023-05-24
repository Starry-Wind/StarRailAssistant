'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-05-23 17:39:27
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-05-24 20:51:37
Description: 

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
import ctypes
import pygetwindow as gw
from PIL import ImageGrab

from utils.config import init_config_file, modify_json_file, normalize_file_path, CONFIG_FILE_NAME
from utils.log import log


def get_width():
    window = gw.getWindowsWithTitle('崩坏：星穹铁道')[0]
    hwnd = window._hWnd

    # 获取活动窗口的大小
    window_rect = window.width, window.height

    user32 = ctypes.windll.user32
    desktop_width = user32.GetSystemMetrics(0)
    desktop_height = user32.GetSystemMetrics(1)
    
    #单显示器屏幕宽度和高度:
    img = ImageGrab.grab()
    width, height=img.size

    scaling = round(width/desktop_width*10)/10
    print(scaling)
    """    
    # 获取当前显示器的缩放比例
    dc = win32gui.GetWindowDC(hwnd)
    dpi_x = win32print.GetDeviceCaps(dc, win32con.LOGPIXELSX)
    dpi_y = win32print.GetDeviceCaps(dc, win32con.LOGPIXELSY)
    win32gui.ReleaseDC(hwnd, dc)
    scale_x = dpi_x / 96
    scale_y = dpi_y / 96
    log.info(f"Real : {width} x {height} {dc} x {dc}")
    """

    # 计算出真实分辨率
    real_width = int(window_rect[0])
    real_height = int(window_rect[1])

    if not normalize_file_path(CONFIG_FILE_NAME):
        init_config_file(real_width=real_width, real_height=real_height)

    log.info(f"Real resolution: {real_width} x {real_height} x {scaling}")

    modify_json_file(CONFIG_FILE_NAME, "real_width", real_width)
    modify_json_file(CONFIG_FILE_NAME, "real_height", real_height)
    modify_json_file(CONFIG_FILE_NAME, "scaling", scaling)