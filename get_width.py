'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-05-23 17:39:27
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-08-01 21:07:06
Description: 

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
from ctypes import windll
import pywinctl as pwc # 跨平台支持

from utils.config import sra_config_obj, normalize_file_path, CONFIG_FILE_NAME
from utils.log import log


def get_width(title):
    user32 = windll.user32
    desktop_width = user32.GetSystemMetrics(0) # 显示器原始宽度
    #desktop_height = user32.GetSystemMetrics(1)
    
    #单显示器屏幕宽度和高度:
    window = pwc.getWindowsWithTitle(title)[0]
    # 获取活动窗口的大小
    window_rect = window.width, window.height
    width, height = pwc.getScreenSize()# 显示器缩放后宽度
    print(width)
    print(desktop_width)
    scaling = round(width/desktop_width*100)/100
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
    real_width = int(window_rect[0]/scaling)
    real_height = int(window_rect[1]/scaling)
    borderless = True if real_width*scaling == 1920 else False
    left_border = (real_width*scaling-1920)/2
    up_border = (real_height*scaling-1080)-left_border
    real_width1 = 1920
    real_height1 = 1080

    log.info(f"Real resolution: {real_width} x {real_height} x {scaling} x {borderless}")

    sra_config_obj.real_width = real_width1
    sra_config_obj.real_height = real_height1
    sra_config_obj.scaling = scaling
    sra_config_obj.borderless = borderless
    sra_config_obj.left_border = left_border
    sra_config_obj.up_border = up_border

    # 排除缩放干扰
    #user32.SetProcessDPIAware()
    