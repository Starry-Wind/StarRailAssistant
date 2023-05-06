from pickle import FALSE
import pyautogui
import cv2 as cv
import numpy as np
import time
import win32api
import win32con
import json


class calculated:

    def __init__(self):
        pass

    def Click(self, points):
        x, y = points
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    def scan_screenshot(self, prepared):
        temp = pyautogui.screenshot()
        screenshot = np.array(temp)
        screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2RGB)
        result = cv.matchTemplate(screenshot, prepared, cv.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        return {'screenshot': screenshot, 'min_val': min_val, 'max_val': max_val, 'min_loc': min_loc, 'max_loc': max_loc}

    def calculated(self, result, shape):
        mat_top, mat_left = result['max_loc']
        prepared_height, prepared_width, prepared_channels = shape

        x = int((mat_top + mat_top + prepared_width) / 2)

        y = int((mat_left + mat_left + prepared_height) / 2)

        return x, y

    # flag为true一定要找到
    def click_target(self, target_path, threshold, flag=True):
        target = cv.imread(target_path)
        while True:
            result = self.scan_screenshot(target)
            if result['max_val'] > threshold:
                points = self.calculated(result, target.shape)
                print(points)
                self.Click(points)
                return
            if flag == False:
                return

    def fighting(self):
        start_time = time.time()
        target = cv.imread('./temp/attack.jpg')
        while True:
            print("识别中")
            result = self.scan_screenshot(target)
            if result['max_val'] > 0.98:
                points = self.calculated(result, target.shape)
                print(points)
                self.Click(points)
                break
            elif time.time() - start_time > 10:  # 如果已经识别了10秒还未找到目标图片，则退出循环
                print("识别超时,此处可能无敌人")
                break
        time.sleep(5)
        target = cv.imread('./temp/auto.jpg')
        start_time = time.time()
        while True:
            result = self.scan_screenshot(target)
            if result['max_val'] > 0.98:
                points = self.calculated(result, target.shape)
                print(points)
                self.Click(points)
                print("开启自动战斗")
                break
            elif time.time() - start_time > 15:
                break

        start_time = time.time()  # 开始计算战斗时间
        target = cv.imread('./temp/finish_fighting.jpg')
        while True:
            result = self.scan_screenshot(target)
            if result['max_val'] > 0.95:
                points = self.calculated(result, target.shape)
                print(points)
                print("完成自动战斗")
                time.sleep(3)
                break

    def auto_map(self, map):
        with open(f"map\\{map}.json", 'r', encoding='utf8') as f:
            map_data = json.load(f)
        # 开始寻路
        print("开始寻路")
        for map in map_data['map']:
            print(map)
            key = list(map.keys())[0]
            value = map[key]
            if key in ['w', 's', 'a', 'd', 'f']:
                pyautogui.keyDown(key)
                time.sleep(value)
                pyautogui.keyUp(key)
            elif key == "mouse_move":
                self.Mouse_move(value)
            else:
                self.fighting()

    def Mouse_move(self, x):
        with open('./real_width.json', 'r', encoding='utf8') as f:
            real_width = json.load(f)['real_width']
        # 该公式为不同缩放比之间的转化
        dx = int(x * 1295 / real_width)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, 0)  # 进行视角移动
