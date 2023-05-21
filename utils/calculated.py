import time
import os
from pickle import FALSE

import cv2 as cv
import numpy as np
import orjson
import pyautogui
import win32api
import win32con
import win32gui
from cnocr import CnOcr
from PIL import ImageGrab, Image
from pynput.keyboard import Controller as KeyboardController
from typing import Dict, Optional, Any, Union, Tuple, List, Literal

from .config import read_json_file, CONFIG_FILE_NAME

from .exceptions import Exception
from .log import log


class calculated:
    def __init__(self):
        self.CONFIG = read_json_file(CONFIG_FILE_NAME)
        self.keyboard = KeyboardController()
        self.ocr = CnOcr(det_model_name='ch_PP-OCRv3_det', rec_model_name='densenet_lite_114-fc')
        self.hwnd = win32gui.FindWindow("UnityWndClass", "崩坏：星穹铁道")

    def Click(self, points):
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
        #pyautogui.click(x,y, clicks=5, interval=0.1)
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    def Relative_click(self, points):
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

    def part_ocr_click(self, characters, overtime, frequency = 1):
        """
        说明：
            局部ocr点击坐标
        参数：
            :param characters: 识别的文字
            :param overtime: 超时
        """
        for i in range(frequency):
            start_time = time.time()
            while True:
                left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
                img_fp = ImageGrab.grab((left, top, right, bottom))
                text, pos = self.ocr_pos(img_fp, characters)
                if pos:
                    self.Click((left+pos[0], top+pos[1]))
                    return True
                if time.time() - start_time > overtime:
                    log.info("识别超时")
                    return False

    def ocr_click(self, characters, overtime, frequency = 1, platform = "PC", order = "127.0.0.1:62001"):
        """
        说明：
            点击坐标
        参数：
            :param characters: 识别的文字
            :param overtime: 超时
        """
        for i in range(frequency):
            start_time = time.time()
            while True:
                if platform == "PC":
                    left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
                    img_fp = ImageGrab.grab((left, top, right, bottom))
                elif platform == "模拟器":
                    left, top, right, bottom = 0,0,0,0
                    os.system(f"adb -s {order} shell screencap -p /sdcard/Pictures/screencast1.png")
                    os.system(f"adb -s {order} pull /sdcard/Pictures/screencast1.png")
                    img_fp = Image.open("./screencast1.png")
                text, pos = self.ocr_pos(img_fp, characters)
                print(text, pos)
                if pos:
                    if platform == "PC":
                        self.Click((left+pos[0], top+pos[1]))
                    elif platform == "模拟器":
                        os.system(f"adb -s {order} shell input tap {pos[0]} {pos[1]}")
                    return True
                if time.time() - start_time > overtime:
                    log.info("识别超时")
                    return False
                
    def take_screenshot(self, platform = "PC", order = "127.0.0.1:62001"):
        # 返回RGB图像
        if platform == "PC":
            left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
            temp = ImageGrab.grab((left, top, right, bottom))
        elif platform == "模拟器":
            left, top, right, bottom = 0,0,0,0
            os.system(f"adb -s {order} shell screencap -p /sdcard/Pictures/screencast1.png")
            os.system(f"adb -s {order} pull /sdcard/Pictures/screencast1.png")
            temp = Image.open("./screencast1.png")
        screenshot = np.array(temp)
        screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2RGB)
        return (screenshot, left, top, right, bottom)

    def scan_screenshot(self, prepared, screenshot1 = None, platform = "PC") -> dict:
        """
        说明：
            比对图片
        参数：
            :param prepared: 比对图片地址
            :param prepared: 被比对图片地址
        """
        if screenshot1:
            screenshot, left, top, right, bottom = self.take_screenshot(platform)
            screenshot = np.array(screenshot1)
            screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2RGB)
        else:
            screenshot, left, top, right, bottom = self.take_screenshot(platform)
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
        prepared_width, prepared_height, prepared_channels = shape

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
                self.Click(points)
                return
            if flag == False:
                return

    def fighting(self, type: int=0):
        """
        说明：
            攻击
        参数：
            :param type: 类型 大世界/模拟宇宙
        """
        start_time = time.time()
        target = cv.imread("./temp/attack.jpg")
        while True:
            log.info("识别中")
            result = self.scan_screenshot(target)
            if result["max_val"] > 0.98:
                points = self.calculated(result, target.shape)
                self.Click(points)
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
                    self.Click(points)
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
            if type == 0:
                result = self.scan_screenshot(target)
                if result["max_val"] > 0.95:
                    points = self.calculated(result, target.shape)
                    log.debug(points)
                    log.info("完成自动战斗")
                    time.sleep(3)
                    break
            elif type == 1:
                result = self.part_ocr((6,10,89,88))
                if "选择祝福" in result:
                    log.info("完成自动战斗")
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
            log.info(f"执行{map_filename}文件:{map_index+1}/{len(map_data['map'])} {map}")
            key = list(map.keys())[0]
            value = map[key]
            if key in ["w", "s", "a", "d", "f"]:
                self.keyboard.press(key)
                start_time = time.perf_counter()
                while time.perf_counter() - start_time < value:
                    pass
                self.keyboard.release(key)
            elif key == "mouse_move":
                self.Mouse_move(value)
            elif key == "fighting":
                if value == 1:  # 进战斗
                    self.fighting()
                elif value == 2:  # 障碍物
                    self.Click(win32api.GetCursorPos())
                    time.sleep(1)
                else:
                    raise Exception(f"map数据错误, fighting参数异常:{map_filename}", map)
            elif key == "scroll":
                self.scroll(value)
            else:
                raise Exception(f"map数据错误,未匹配对应操作:{map_filename}", map)

    def Mouse_move(self, x):
        real_width = self.CONFIG["real_width"]
        # 该公式为不同缩放比之间的转化
        dx = int(x * 1295 / real_width)
        i = int(dx/200)
        last = dx - i*200
        for ii in range(abs(i)):
            if dx >0:
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

    def is_blackscreen(self, threshold = 30):
        # 判断是否为黑屏，避免光标、加载画面或其他因素影响，不设为0，threshold范围0-255
        screenshot = cv.cvtColor(self.take_screenshot()[0], cv.COLOR_BGR2GRAY)
        return cv.mean(screenshot)[0] < threshold

    def ocr_pos(self,img_fp: Image, characters:str = None):
        """
        说明：
            获取指定文字的坐标
        参数：
            :param points: 百分比坐标
        返回:
            :return text: 文字
            :return pos: 坐标
        """
        out = self.ocr.ocr(img_fp)
        data = {i['text']: i['position'] for i in out}
        if not characters:
            characters = list(data.keys())[0]
        pos = ((data[characters][2][0]+data[characters][0][0])/2, (data[characters][2][1]+data[characters][0][1])/2) if characters in data else None
        return characters, pos
    
    def part_ocr(self,points = (100,100,100,100), platform="PC", order="127.0.0.1:62001"):
        """
        说明：
            返回图片文字和坐标
        参数：
            :param points: 坐标百分比
        返回:
            :return data: 文字: 坐标
        """
        if platform == "PC":
            left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
            img_fp = ImageGrab.grab((left+(right-left)/100*points[0], top+(bottom-top)/100*points[1], right-(right-left)/100*points[2], bottom-(bottom-top)/100*points[3]))
        elif platform == "模拟器":
            left, top, right, bottom = 0,0,0,0
            os.system(f"adb -s {order} shell screencap -p /sdcard/Pictures/screencast1.png")
            os.system(f"adb -s {order} pull /sdcard/Pictures/screencast1.png")
            img_fp = Image.open("./screencast1.png")
            left, top = img_fp.size
            img_fp = img_fp.crop((left/100**points[0], top/100*points[1], left/100*(1-points[2]), top/100*(1-points[3])))
            img_fp.show()
        out = self.ocr.ocr(img_fp)
        data = {i['text']: i['position'] for i in out}
        return data

    def get_pix_bgr(self, points, platform="PC", order="127.0.0.1:62001"):
        """
        说明：
            获取指定坐标的颜色
        参数：
            :param points: 坐标
        返回:
            :return 三色值
        """
        if platform == "PC":
            left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
            img = ImageGrab.grab((left, top, right, bottom))
        elif platform == "模拟器":
            left, top, right, bottom = 0,0,0,0
            os.system(f"adb -s {order} shell screencap -p /sdcard/Pictures/screencast1.png")
            os.system(f"adb -s {order} pull /sdcard/Pictures/screencast1.png")
            img = Image.open("./screencast1.png")
            img = np.array(img)
        x = points[0]
        y = points[1]
        px = img[x, y]
        blue = img[x, y, 0]
        green = img[x, y, 1]
        red = img[x, y, 2]
        return [blue, green, red]
    
    def hsv2pos(self, img, color):
        """
        说明：
            获取指定颜色的坐标
        参数：
            :param img: 图片
            :param color: 颜色
        返回:
            :return 坐标
        """
        HSV=cv.cvtColor(img,cv.COLOR_BGR2HSV)
        for index,x in enumerate(HSV):
            for index1,x1 in enumerate(HSV[index]):
                if x1[0] == color[0] and x1[1] == color[1] and x1[2] == color[2]:
                    return (index1, index1)
