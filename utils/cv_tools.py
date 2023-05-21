'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-05-21 21:12:13
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-05-21 22:24:12
Description: 

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Created by Xe-No at 2023/5/17
# 一些cv工具

from utils.switch_window import switch_window
from utils.get_angle import get_angle
import os
import time 
import cv2 as cv
import numpy as np
import win32gui, win32api, win32con
import pyautogui
from PIL import ImageGrab, Image

def get_binary(img, threshold=200):
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    _, binary = cv.threshold(gray, threshold, 255, cv.THRESH_BINARY)
    return binary

def show_img(img, scale=1, title='Image'):
    # cv.namedWindow('image', cv.WINDOW_NORMAL)
    h, w = img.shape[:2]
    img = cv.resize( img ,(int(w*scale), int(h*scale))  )
    cv.imshow(title, img)
    cv.waitKey(0)
    cv.destroyAllWindows()  

def show_imgs(imgs, title='Image'):
    cv.imshow(title, np.hstack(imgs))
    cv.waitKey(0)
    cv.destroyAllWindows()  

def get_loc(im, imt):
    result = cv.matchTemplate(im, imt, cv.TM_CCORR_NORMED)
    return cv.minMaxLoc(result)

def take_screenshot(rect, platform="PC", order="127.0.0.1:62001"):
    # 返回RGB图像
    if platform == "PC":
        hwnd = win32gui.FindWindow("UnityWndClass", "崩坏：星穹铁道")
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        #temp = pyautogui.screenshot(region=rect1)
        #print((rect[0],rect[1],rect[3],rect[2]))
        temp = ImageGrab.grab((rect[0]+left,rect[1]+top,rect[3]+left,rect[2]+top))
    elif platform == "模拟器":
        os.system(f"adb -s {order} shell screencap -p /sdcard/Pictures/screencast.png")
        os.system(f"adb -s {order} pull /sdcard/Pictures/screencast.png")
        img_fp = Image.open("./screencast.png")
        left, top = img_fp.size
        temp = img_fp.crop((rect[0],rect[1],rect[3],rect[2]))
    screenshot = np.array(temp)
    screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2RGB)
    #show_img(screenshot)
    return screenshot

def take_minimap(rect = [47,58,187,187]):
    return take_screenshot(rect)

def take_fine_screenshot(rect = [47,58,187,187], platform="PC", order="127.0.0.1:62001"):
    total = take_screenshot(rect, platform, order)
    n = 5
    for i in range(n):
        if platform == "PC":
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, -200, 0, 0)
        elif platform == "模拟器":
            os.system(f"adb -s {order} shell input swipe 636 359 636 184 50")
        mask = cv.compare(total, take_screenshot(rect, platform, order), cv.CMP_EQ )
        total = cv.bitwise_and(total, mask )
        time.sleep(0.01)
    time.sleep(0.1)
    for i in range(n):
        if platform == "PC":
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, -200, 0, 0)
        elif platform == "模拟器":
            os.system(f"adb -s {order} shell input swipe 636 362 636 495 50")
        mask = cv.compare(total, take_screenshot(rect, platform, order), cv.CMP_EQ )
        total = cv.bitwise_and(total, mask )
        time.sleep(0.01)
    minimap = cv.bitwise_and(total, mask )
    return minimap

def get_mask(img, color_range):
    lower, upper = color_range
    return cv.inRange(img, lower, upper)

def get_camera_fan(color = [130, 130, 60],angle=0, w=187, h=187, delta=90):
    center = (w//2, h//2)
    radius = min(h, w)//2
    fan = np.zeros((h, w, 3), np.uint8)
    # 计算圆心位置
    cx, cy = w // 2, h // 2
    axes = (w // 2, h // 2) 
    
    startAngle, endAngle = angle -45, angle +45 # 画90度

    cv.ellipse(fan, (cx, cy), axes, 0, startAngle, endAngle, color , -1)
    return fan

def get_gradient_mask(w,h):
    center = [w // 2, h // 2]
    radius = 0.8 *w
    # 创建渐变掩码
    gradient_mask = np.zeros((w, h), dtype=np.uint8)
    for r in range(gradient_mask.shape[0]):
        for c in range(gradient_mask.shape[1]):
            dist = np.sqrt((r-center[1])**2 + (c-center[0])**2)
            value =  max(0, min(1 - 2*dist/radius, 1))
            gradient_mask[r,c] = int(value * 255)
    return gradient_mask


def filter_contours_surround_point(gray, point):
    """过滤掉不包围指定点的轮廓"""
    contours, hierarchy = cv.findContours(gray, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    # 过滤掉所有不包含指定点的轮廓
    filtered_contours = []
    for i in range(len(contours)):
        if cv.pointPolygonTest(contours[i], point, False) < 0:
            filtered_contours.append(contours[i])
            
    # 过滤掉所有不包围指定点的轮廓
    surrounded_contours = []
    for i in range(len(filtered_contours)):
        rect = cv.boundingRect(filtered_contours[i])
        if rect[0] <= point[0] <= rect[0] + rect[2] and \
           rect[1] <= point[1] <= rect[1] + rect[3]:
            surrounded_contours.append(filtered_contours[i])
            
    return surrounded_contours


