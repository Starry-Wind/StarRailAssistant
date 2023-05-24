'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-05-24 10:56:11
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-05-24 10:57:36
Description: 

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
import time

import cv2 as cv
import numpy as np
import pyautogui
import win32api
import win32con
import win32gui
from PIL import ImageGrab
from pynput.keyboard import Controller as KeyboardController

from .config import read_json_file, CONFIG_FILE_NAME
from .exceptions import Exception
from .log import log


class Calculated:
    def __init__(self):
        self.CONFIG = read_json_file(CONFIG_FILE_NAME)
        self.keyboard = KeyboardController()

    def click(self, points):
        """
        说明：
            点击坐标
        参数：
            :param points: 坐标
        """
        x, y = int(points[0]), int(points[1])
        log.debug((x, y))
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        # pyautogui.click(x,y, clicks=5, interval=0.1)
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    def relative_click(self, points):
        """
        说明：
            点击相对坐标
        参数：
            :param points: 百分比坐标
        """
        hwnd = win32gui.FindWindow("UnityWndClass", "崩坏：星穹铁道")
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        real_width = self.CONFIG["real_width"]
        real_height = self.CONFIG["real_height"]
        x, y = int(left + (right - left) / 100 * points[0]), int(
            top + (bottom - top) / 100 * points[1]
        )
        log.info((x, y))
        log.debug((x, y))
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    def take_screenshot(self):
        # 返回RGB图像
        hwnd = win32gui.FindWindow("UnityWndClass", "崩坏：星穹铁道")
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        temp = ImageGrab.grab((left, top, right, bottom), all_screens=True)
        screenshot = np.array(temp)
        screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2RGB)
        return screenshot, left, top, right, bottom

    def scan_screenshot(self, prepared) -> dict:
        """
        说明：
            比对图片
        参数：
            :param prepared: 比对图片地址
        """
        screenshot, left, top, right, bottom = self.take_screenshot()
        result = cv.matchTemplate(screenshot, prepared, cv.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        return {
            "screenshot": screenshot,
            "min_val": min_val,
            "max_val": max_val,
            "min_loc": (min_loc[0] + left, min_loc[1] + top),
            "max_loc": (max_loc[0] + left, max_loc[1] + top),
        }

    def calculated(self, result, shape):
        mat_top, mat_left = result["max_loc"]
        prepared_height, prepared_width, prepared_channels = shape

        x = int((mat_top + mat_top + prepared_width) / 2)

        y = int((mat_left + mat_left + prepared_height) / 2)

        return x, y

    # flag为true一定要找到
    def click_target(self, target_path, threshold, flag=True):
        target = cv.imread(target_path)
        while True:
            result = self.scan_screenshot(target)
            if result["max_val"] > threshold:
                points = self.calculated(result, target.shape)
                self.click(points)
                return
            if not flag:
                return

    def fighting(self):
        start_time = time.time()
        attack = cv.imread("./temp/attack.jpg")
        doubt = cv.imread("./temp/doubt.jpg")
        warn = cv.imread("./temp/warn.jpg")
        while True:
            log.info("识别中")
            attack_result = self.scan_screenshot(attack)
            doubt_result = self.scan_screenshot(doubt)
            warn_result = self.scan_screenshot(warn)
            if attack_result["max_val"] > 0.98:
                points = self.calculated(attack_result, attack.shape)
                self.click(points)
                break
            elif doubt_result["max_val"] > 0.9 or warn_result["max_val"] > 0.95:
                log.info("識別到疑問或警告，等待怪物開戰")
                time.sleep(3)
                target = cv.imread("./temp/finish_fighting.jpg")  # 識別是否已進入戰鬥，若已進入則跳出迴圈
                result = self.scan_screenshot(target)
                if result["max_val"] < 0.95:
                    break
            elif time.time() - start_time > 10:  # 如果已经识别了10秒还未找到目标图片，则退出循环
                log.info("识别超时,此处可能无敌人")
                return
        time.sleep(6)
        target = cv.imread("./temp/auto.jpg")
        start_time = time.time()
        if self.CONFIG["auto_battle_persistence"] != 1:
            while True:
                result = self.scan_screenshot(target)
                if result["max_val"] > 0.9:
                    points = self.calculated(result, target.shape)
                    self.click(points)
                    log.info("开启自动战斗")
                    break
                elif time.time() - start_time > 15:
                    break
        else:
            log.info("跳过开启自动战斗（沿用设置）")
            time.sleep(5)

        start_time = time.time()  # 开始计算战斗时间
        target = cv.imread("./temp/finish_fighting.jpg")
        while True:
            result = self.scan_screenshot(target)
            if result["max_val"] > 0.95:
                points = self.calculated(result, target.shape)
                log.debug(points)
                log.info("完成自动战斗")
                time.sleep(3)
                break

    def auto_map(self, map, old=True):
        map_data = (
            read_json_file(f"map\\old\\{map}.json")
            if old
            else read_json_file(f"map\\{map}.json")
        )
        map_filename = map
        # 开始寻路
        log.info("开始寻路")
        for map_index, map in enumerate(map_data["map"]):
            log.info(f"执行{map_filename}文件:{map_index + 1}/{len(map_data['map'])} {map}")
            key = list(map.keys())[0]
            value = map[key]
            if key in ["w", "s", "a", "d", "f"]:
                self.keyboard.press(key)
                start_time = time.perf_counter()
                while time.perf_counter() - start_time < value:
                    pass
                self.keyboard.release(key)
            elif key == "mouse_move":
                self.mouse_move(value)
            elif key == "fighting":
                if value == 1:  # 进战斗
                    self.fighting()
                elif value == 2:  # 障碍物
                    self.click(win32api.GetCursorPos())
                    time.sleep(1)
                else:
                    raise Exception((f"map数据错误, fighting参数异常:{map_filename}", map))
            elif key == "scroll":
                self.scroll(value)
            else:
                raise Exception((f"map数据错误,未匹配对应操作:{map_filename}", map))

    def mouse_move(self, x):
        real_width = self.CONFIG["real_width"]
        # 该公式为不同缩放比之间的转化
        dx = int(x * 1295 / real_width)
        i = int(dx / 200)
        last = dx - i * 200
        for ii in range(abs(i)):
            if dx > 0:
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 200, 0)  # 进行视角移动
            else:
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, -200, 0)  # 进行视角移动
            time.sleep(0.1)
        if last != 0:
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, last, 0)  # 进行视角移动
        time.sleep(0.5)

    def scroll(self, clicks: float):
        """
        说明：
            控制鼠标滚轮滚动
        参数：
            :param clicks 滚动单位，正数为向上滚动
        """
        pyautogui.scroll(clicks)
        time.sleep(0.5)

    def is_blackscreen(self, threshold=30):
        # 判断是否为黑屏，避免光标、加载画面或其他因素影响，不设为0，threshold范围0-255
        screenshot = cv.cvtColor(self.take_screenshot()[0], cv.COLOR_BGR2GRAY)
        return cv.mean(screenshot)[0] < threshold
