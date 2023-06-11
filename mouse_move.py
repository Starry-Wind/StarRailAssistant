'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-06-12 01:26:37
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-06-12 01:46:39
Description: 

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
from get_width import get_width
get_width("崩坏：星穹铁道")
import time
import win32api
from utils.config import read_json_file, CONFIG_FILE_NAME
import pygetwindow as gw
import pyautogui # 缩放纠正
from utils.calculated import calculated
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController
calculated = calculated()

def switch_window():
    ws = gw.getWindowsWithTitle("崩坏：星穹铁道")
    kc = KeyboardController()
    if len(ws) >= 1 :
        for w in ws:
            if w.title == "崩坏：星穹铁道":
                kc.press('%')
                kc.release('%')
                w.activate()
                break
    else:
        print('没找到窗口崩坏：星穹铁道')

switch_window()

def Mouse_move(x):
    """
    说明:
        视角转动
    """
    # 该公式为不同缩放比之间的转化
    real_width = read_json_file(CONFIG_FILE_NAME)["real_width"]
    dx = int(x * 1920 / real_width)
    i = int(dx/200)
    last = dx - i*200
    for ii in range(abs(i)):
        if dx >0:
            win32api.mouse_event(1, 200, 0)  # 进行视角移动
            #self.mouse.move(200, 0)
        else:
            win32api.mouse_event(1, -200, 0)  # 进行视角移动
            #self.mouse.move(-200, 0)
        time.sleep(0.1)
    if last != 0:
        win32api.mouse_event(1, last, 0)  # 进行视角移动
        #self.mouse.move(last, 0)
    time.sleep(0.5)

Mouse_move(1000)