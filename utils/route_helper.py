from .get_angle import get_camera_angle, get_angle
# from .switch_window import switch_window
# from .calculated import *
import time
import pyautogui
import win32con, win32api
import numpy as np
import sys
import cv2 
# 分辨率1920x1080
# 角度，顺时针为正，东方为0
# 速度，正常情况下，跑动速度为25小地图像素/秒（停稳后），？大地图像素/秒

# ================基础操作




def move(t, run=True):
	print(f'前进{t}秒')
	pyautogui.keyDown("w")
	if run:
		pyautogui.keyDown("shift")
	time.sleep(t)
	pyautogui.keyUp("w")
	if run:
		pyautogui.keyUp("shift")
		time.sleep(0.5)



