from .calculated import *
import cv2 as cv
import pyautogui
import time


class map:
    def __init__(self):
        self.calculated = calculated()
        self.win32api = win32api
        self.win32con = win32con

    def map_init(self):

        # 进行地图初始化，把地图缩小,需要缩小5次

        target = cv.imread('./temp/contraction.jpg')
        while True:
            result = self.calculated.scan_screenshot(target)
            if result['max_val'] > 0.98:
                points = self.calculated.calculated(result, target.shape)
                print(points)
                pyautogui.click(points, clicks=5, interval=0.1)
                break

    def fighting(self):
        start_time = time.time()
        target = cv.imread('./temp/attack.jpg')
        while True:
            print("识别中")
            result = self.calculated.scan_screenshot(target)
            if result['max_val'] > 0.98:
                points = self.calculated.calculated(result, target.shape)
                print(points)
                self.calculated.Click(points)
                break
            elif time.time() - start_time > 30:  # 如果已经识别了30秒还未找到目标图片，则退出循环
                print("识别超时,此处可能无敌人")
                break

        time.sleep(5)
        target = cv.imread('./temp/auto.jpg')
        start_time = time.time()
        while True:
            result = self.calculated.scan_screenshot(target)
            if result['max_val'] > 0.98:
                points = self.calculated.calculated(result, target.shape)
                print(points)
                self.calculated.Click(points)
                print("开启自动战斗")
                break
            elif time.time() - start_time > 30:
                break

        start_time = time.time()  # 开始计算战斗时间
        target = cv.imread('./temp/finish_fighting.jpg')
        while True:
            result = self.calculated.scan_screenshot(target)
            if result['max_val'] > 0.95:
                points = self.calculated.calculated(result, target.shape)
                print(points)
                print("完成自动战斗")
                time.sleep(3)
                break

    def auto_map_1(self):

        # 选择地图
        pyautogui.keyDown("m")
        pyautogui.keyUp("m")
        time.sleep(1)
        self.map_init()

        points = self.calculated.click_target('./temp/orientation_1.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        points = self.calculated.click_target('./temp/orientation_2.jpg', 0.85)
        if points:
            self.calculated.Click(points)
            time.sleep(1)
            self.calculated.Click(points)
            points = None

        points = self.calculated.click_target('./temp/map_1.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        points = self.calculated.click_target('./temp/map_1_point.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        points = self.calculated.click_target('./temp/transfer.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        # 选择完地图，开始寻路
        print("选择完地图，开始寻路")
        time.sleep(5)
        self.calculated.Mouse_move(4650)  # 4650
        pyautogui.keyDown("w")
        time.sleep(2)
        pyautogui.keyUp("w")

        # 进入路径点一
        self.fighting()
        print("完成基座舱段刷怪")

    def auto_map_2(self):
        # 选择地图
        pyautogui.keyDown("m")
        pyautogui.keyUp("m")
        time.sleep(1)
        self.map_init()

        points = self.calculated.click_target('./temp/orientation_1.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        points = self.calculated.click_target('./temp/orientation_2.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            time.sleep(1)
            self.calculated.Click(points)
            points = None

        points = self.calculated.click_target('./temp/map_2.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        points = self.calculated.click_target('./temp/map_2_point_1.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        points = self.calculated.click_target('./temp/transfer.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        # 开始寻路

        time.sleep(5)
        self.calculated.Mouse_move(2300)  # 2300
        pyautogui.keyDown("w")
        time.sleep(3.6)
        pyautogui.keyUp("w")
        self.calculated.Mouse_move(-2300)  # -2300

        pyautogui.keyDown("w")
        time.sleep(4)
        pyautogui.keyUp("w")

        # 已到达第一个点位
        self.fighting()

        # 继续寻路
        self.calculated.Mouse_move(2300)  # 2300
        pyautogui.keyDown("w")
        time.sleep(3)
        pyautogui.keyUp("w")

        self.calculated.Mouse_move(2300)  # 2300
        pyautogui.keyDown("w")
        time.sleep(6.5)
        pyautogui.keyUp("w")

        self.calculated.Mouse_move(-2300)  # -2300
        pyautogui.keyDown("w")
        time.sleep(1.8)
        pyautogui.keyUp("w")

        self.calculated.Mouse_move(-2000)  # -2000
        pyautogui.keyDown("w")
        time.sleep(4)
        pyautogui.keyUp("w")

        # 已到达第二个点位
        self.fighting()

        # 继续寻路
        pyautogui.keyDown("m")
        pyautogui.keyUp("m")
        time.sleep(1)
        points = self.calculated.click_target('./temp/map_2_point_2.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        points = self.calculated.click_target('./temp/transfer.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        time.sleep(5)
        self.calculated.Mouse_move(4650)  # 4650
        pyautogui.keyDown("w")
        time.sleep(2)
        pyautogui.keyUp("w")

        # 已到达第三个点位
        self.fighting()

        # 继续寻路
        self.calculated.Mouse_move(4650)  # 4650
        pyautogui.keyDown("w")
        time.sleep(4.5)
        pyautogui.keyUp("w")

        self.calculated.Mouse_move(-1000)  # -1000
        pyautogui.keyDown("w")
        time.sleep(3)
        pyautogui.keyUp("w")

        self.calculated.Mouse_move(-1600)  # -1600
        pyautogui.keyDown("w")
        time.sleep(1.5)
        pyautogui.keyUp("w")

        # 已到达第四个点位
        self.fighting()

        # 继续寻路
        pyautogui.keyDown("m")
        pyautogui.keyUp("m")
        time.sleep(1)
        points = self.calculated.click_target('./temp/map_2_point_3.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        points = self.calculated.click_target('./temp/map_2_point_4.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        points = self.calculated.click_target('./temp/transfer.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        time.sleep(5)
        self.calculated.Mouse_move(4000)  # 4000
        pyautogui.keyDown("w")
        time.sleep(2.3)
        pyautogui.keyUp("w")

        # 已到达第五个点位
        self.fighting()

        # 继续寻路
        pyautogui.keyDown("m")
        pyautogui.keyUp("m")
        time.sleep(1)
        points = self.calculated.click_target('./temp/map_2_point_3.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        points = self.calculated.click_target('./temp/map_2_point_4.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        points = self.calculated.click_target('./temp/transfer.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        time.sleep(5)
        self.calculated.Mouse_move(-3000)  # -3000
        pyautogui.keyDown("w")
        time.sleep(1.8)
        pyautogui.keyUp("w")

        self.calculated.Mouse_move(1300)  # 1300
        pyautogui.keyDown("w")
        time.sleep(2)
        pyautogui.keyUp("w")

        self.calculated.Mouse_move(-1000)  # -1000
        pyautogui.keyDown("w")
        time.sleep(3)
        pyautogui.keyUp("w")

        # 已到达第六个点位
        self.fighting()
        print("完成收容舱段清怪")

    def auto_map_3(self):
        # 选择地图
        pyautogui.keyDown("m")
        pyautogui.keyUp("m")
        time.sleep(1)
        self.map_init()

        points = self.calculated.click_target('./temp/orientation_1.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        points = self.calculated.click_target('./temp/orientation_2.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            time.sleep(1)
            self.calculated.Click(points)
            points = None

        points = self.calculated.click_target('./temp/map_3.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        points = self.calculated.click_target('./temp/map_3_point_1.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        points = self.calculated.click_target('./temp/map_3_point_2.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        points = self.calculated.click_target('./temp/transfer.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        # 开始寻路
        time.sleep(5)
        pyautogui.keyDown("w")
        time.sleep(3.8)
        pyautogui.keyUp("w")

        # 已到达第一个检查点
        self.fighting()

        # 继续寻路
        pyautogui.keyDown("w")
        time.sleep(4)
        pyautogui.keyUp("w")
        self.calculated.Mouse_move(-2300)  # -2300
        pyautogui.keyDown("w")
        time.sleep(3.5)
        pyautogui.keyUp("w")
        self.calculated.Mouse_move(2300)  # 2300
        pyautogui.keyDown("w")
        time.sleep(1.5)
        pyautogui.keyUp("w")

        # 已到达第二个检查点
        self.fighting()

        # 继续寻路
        print("继续寻路")
        pyautogui.keyDown("m")
        pyautogui.keyUp("m")

        points = self.calculated.click_target('./temp/map_3_point_3.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        points = self.calculated.click_target('./temp/transfer.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        time.sleep(5)

        self.calculated.Mouse_move(-3800)  # -3800
        pyautogui.keyDown("w")
        time.sleep(3)
        pyautogui.keyUp("w")
        self.calculated.Mouse_move(-2000)  # -2000
        pyautogui.keyDown("w")
        time.sleep(0.8)
        pyautogui.keyUp("w")
        pyautogui.keyDown("f")
        pyautogui.keyUp("f")
        time.sleep(1)  # 等待传送

        # 继续寻路
        pyautogui.keyDown("w")
        time.sleep(0.6)
        pyautogui.keyUp("w")
        self.calculated.Mouse_move(2300)  # 2300
        pyautogui.keyDown("w")
        time.sleep(5)
        pyautogui.keyUp("w")

        # 已到达第三个检查点
        self.fighting()

        # 继续寻路
        self.calculated.Mouse_move(4650)  # 4650
        pyautogui.keyDown("w")
        time.sleep(11)
        pyautogui.keyUp("w")
        self.calculated.Mouse_move(2300)  # 2300
        pyautogui.keyDown("w")
        time.sleep(3.5)
        pyautogui.keyUp("w")

        # 已到达第四个检查点
        self.fighting()

        # 继续寻路
        pyautogui.keyDown("m")
        pyautogui.keyUp("m")

        points = self.calculated.click_target('./temp/map_3_point_4.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        points = self.calculated.click_target('./temp/transfer.jpg', 0.98)
        if points:
            self.calculated.Click(points)
            points = None

        time.sleep(5)
        pyautogui.keyDown("w")
        time.sleep(5.9)
        pyautogui.keyUp("w")

        # 已到达第五个检查点
        self.fighting()
