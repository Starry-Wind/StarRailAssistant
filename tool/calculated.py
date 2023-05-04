import pyautogui
import cv2 as cv
import numpy as np
import time
import win32api
import win32con
import win32gui
import win32print


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

    def click_target(self, target_path, threshold):
        target = cv.imread(target_path)
        while True:
            result = self.scan_screenshot(target)
            if result['max_val'] > threshold:
                points = self.calculated(result, target.shape)
                print(points)
                return points

    def Mouse_move(self, x):
        dx = int(x * 1295 / 1295)  # 此处若修改请将除号后面的数字修改为你得到的real_width的值
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, 0)  # 进行视角移动
