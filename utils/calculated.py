"""
系统控制项
"""
import time
import cv2 as cv
import numpy as np
import pygetwindow as gw

from cnocr import CnOcr
from PIL import ImageGrab, Image
from pynput import mouse
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController
from typing import Dict, Optional, Any, Union, Tuple, List, Literal

from .config import read_json_file, CONFIG_FILE_NAME
from .exceptions import Exception
from .log import log
from .adb import ADB
from .cv_tools import show_img
from .exceptions import Exception

class calculated:

    def __init__(self, platform="PC", order="127.0.0.1:62001"):
        """
        参数: 
            :param platform: 运行设备
            :param order: ADB端口
        """
        self.platform = platform
        self.order = order

        self.adb = ADB(order)
        self.CONFIG = read_json_file(CONFIG_FILE_NAME)
        self.scaling = self.CONFIG.get("scaling", 1)
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.ocr = CnOcr(det_model_name='ch_PP-OCRv2_det', rec_model_name='densenet_lite_114-fc')
        if platform == "PC":
            self.window = gw.getWindowsWithTitle('崩坏：星穹铁道')
            if not self.window:
                raise Exception("你游戏没开，我真服了")
            self.window = self.window[0]
        self.hwnd = self.window._hWnd  if platform == "PC" else None

    def Click(self, points = None):
        """
        说明：
            点击坐标
        参数：
            :param points: 坐标
        """
        if not points:
            points = self.mouse.position
        x, y = int(points[0]), int(points[1])
        if self.platform == "PC":
            '''
            win32api.SetCursorPos((x, y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            #pyautogui.click(x,y, clicks=5, interval=0.1)
            time.sleep(0.5)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            '''
            #x = x - (self.window.width-1920)/2
            #y = y - (self.window.height-1070)/2
            self.mouse.position = (x, y)
            self.mouse.press(mouse.Button.left)
            time.sleep(0.5)
            self.mouse.release(mouse.Button.left)
        elif self.platform == "模拟器":
            self.adb.input_tap((x, y))

    def appoint_click(self, points, appoint_points, hsv = [18, 18, 18]):
        """
        说明：
            点击坐标直到指定指定点位变成指定颜色
        参数：
            :param points: 坐标
            :param appoint_points: 指定坐标
            :param hsv: 三色值
        """
        start_time = time.time()
        while True:
            x, y = int(points[0]), int(points[1])
            log.debug((x, y))
            if self.platform == "PC":
                """
                win32api.SetCursorPos((x, y))
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
                #pyautogui.click(x,y, clicks=5, interval=0.1)
                time.sleep(0.5)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
                """
                self.mouse.position = (x, y)
                self.mouse.press(mouse.Button.left)
                time.sleep(0.5)
                self.mouse.release(mouse.Button.left)
            elif self.platform == "模拟器":
                self.adb.input_tap((x, y))
            result = self.get_pix_bgr(appoint_points)
            if result == hsv:
                break
            if time.time() - start_time > 5:
                log.info("识别超时")
                break

    def Relative_click(self, points):
        """
        说明：
            点击相对坐标
        参数：
            :param points: 百分比坐标
        """

        scaling = self.CONFIG["scaling"]
        left, top, right, bottom = self.window.left, self.window.top, self.window.right, self.window.bottom
        real_width = self.CONFIG["real_width"]
        real_height = self.CONFIG["real_height"]
        x, y = int(left + (right - left) / 100 * points[0]), int(
            top + (bottom - top) / 100 * points[1]
        )
        log.info((x, y))
        log.debug((x, y))
        if self.platform == "PC":
            """
            win32api.SetCursorPos((x, y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            #pyautogui.click(x,y, clicks=5, interval=0.1)
            time.sleep(0.5)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            """
            self.mouse.position = (x, y)
            self.mouse.press(mouse.Button.left)
            time.sleep(0.5)
            self.mouse.release(mouse.Button.left)
        elif self.platform == "模拟器":
            self.adb.input_tap((x, y))

    def img_click(self, points):
        """
        说明：
            点击图片坐标
        参数：
            :param points: 坐标
        """
        if self.platform == "PC":
            scaling = self.CONFIG["scaling"]
            left, top, right, bottom = self.window.left, self.window.top, self.window.right, self.window.bottom
            x, y = int(left + points[0]), int(top + points[1])
        elif self.platform == "模拟器":
            x, y = int(points[0]), int(points[1])
        log.debug((x, y))
        if self.platform == "PC":
            """
            win32api.SetCursorPos((x, y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            time.sleep(0.5)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            """
            self.mouse.position = (x, y)
            self.mouse.press(mouse.Button.left)
            time.sleep(0.5)
            self.mouse.release(mouse.Button.left)
        elif self.platform == "模拟器":
            self.adb.input_tap((x, y))

    def ocr_click(self, characters, overtime = 10, frequency = 1):
        """
        说明：
            点击文字坐标
        参数：
            :param characters: 识别的文字
            :param overtime: 超时
        """
        for i in range(frequency):
            start_time = time.time()
            while True:
                img_fp, left, top, right, bottom, width, length = self.take_screenshot()
                text, pos = self.ocr_pos(img_fp, characters)
                if pos:
                    if self.platform == "PC":
                        self.Click((left+pos[0], top+pos[1]))
                    elif self.platform == "模拟器":
                        self.adb.input_tap(pos)
                    return True
                if time.time() - start_time > overtime:
                    log.info("识别超时")
                    return False
                
    def take_screenshot(self,points=(0,0,0,0)):
        """
        说明:
            返回RGB图像
        参数:
            :param points: 图像截取范围
        """
        if self.platform == "PC":
            left, top, right, bottom = self.window.left, self.window.top, self.window.right, self.window.bottom
            temp = ImageGrab.grab((left, top, right, bottom))
            width, length = temp.size
        elif self.platform == "模拟器":
            left, top, right, bottom = 0,0,0,0
            temp = self.adb.screencast("/sdcard/Pictures/screencast1.png")
            width, length = temp.size
        if points != (0,0,0,0):
            #points = (points[0], points[1]+5, points[2], points[3]+5) if self.platform == "PC" else points
            temp = temp.crop((width/100*points[0], length/100*points[1], width/100*points[2], length/100*points[3]))
        screenshot = np.array(temp)
        screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2RGB)
        return (screenshot, left, top, right, bottom, width, length)

    def scan_screenshot(self, prepared:np, screenshot1 = None) -> dict:
        """
        说明：
            比对图片
        参数：
            :param prepared: 比对图片地址
            :param prepared: 被比对图片地址
        """
        if screenshot1:
            screenshot, left, top, right, bottom, width, length = self.take_screenshot()
            screenshot = np.array(screenshot1)
            screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2RGB)
        else:
            screenshot, left, top, right, bottom, width, length = self.take_screenshot()
        result = cv.matchTemplate(screenshot, prepared, cv.TM_CCORR_NORMED)
        length, width, _ = prepared.shape
        length = int(length)
        width = int(width)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        return {
            "screenshot": screenshot,
            "min_val": min_val,
            "max_val": max_val,
            "min_loc": (min_loc[0] + left+(width/2), min_loc[1] + top+(length/2)),
            "max_loc": (max_loc[0] + left+(width/2), max_loc[1] + top+(length/2)),
        }

    def calculated(self, result, shape):
        mat_top, mat_left = result["max_loc"]
        prepared_width, prepared_height, prepared_channels = shape

        x = int((mat_top + mat_top + prepared_width) / 2)

        y = int((mat_left + mat_left + prepared_height) / 2)

        return x, y

    # flag为true一定要找到
    def click_target(self, target_path: str, threshold, flag=True):
        """
        说明:
            识别图片并点击
        参数:
            :param target_path: 需要识别的图片地址
            :param threshold: 可信度阈值
            :param flag: 是否必须找到
        """
        target_path = target_path.replace("temp\\","temp\\pc\\") if self.platform == "PC" else target_path.replace("temp\\","temp\\mnq\\")
        temp_name = target_path.split("\\")[-1].split(".")[0]
        temp_ocr = {
            "orientation_1": "星轨航图",
            "orientation_2": "空间站「黑塔",
            "map_1": "基座舱段",
            "map_1_point" : [(593, 346),(593, 556)],
            "transfer": "传送",
            "map_1-2": "收容舱段",
            "map_1-3": "支援舱段",
        }
        if temp_name in temp_ocr:
            if "map" not in temp_name:
                self.ocr_click(temp_ocr[temp_name])
                while True:
                    if not self.is_blackscreen():
                        break
            elif "point" in temp_name and self.platform == "模拟器":
                self.adb.input_swipe(temp_ocr[temp_name][0],temp_ocr[temp_name][1],100)
                temp_ocr.pop(temp_name)
                time.sleep(0.5)
            else:
                if type(temp_ocr[temp_name]) == str:
                    ocr_data = self.part_ocr((77,10,85,97)) if self.platform == "PC" else self.part_ocr((72,18,80,97))
                    pos = ocr_data[temp_ocr[temp_name]]
                    self.appoint_click(pos,(pos[0]+60, pos[1]), [40,40,40])
                elif type(temp_ocr[temp_name]) == tuple:
                    self.img_click(temp_ocr[temp_name])
        if temp_name not in temp_ocr:
            target = cv.imread(target_path)
            while True:
                result = self.scan_screenshot(target)
                if result["max_val"] > threshold:
                    #points = self.calculated(result, target.shape)
                    self.Click(result["max_loc"])
                    break
                if flag == False:
                    break

    def fighting(self, type: int=0):
        """
        说明：
            攻击
        参数：
            :param type: 类型 大世界/模拟宇宙
        """
        start_time = time.time()
        target = cv.imread("./temp/pc/attack.jpg") if self.platform == "PC" else cv.imread("./temp/mnq/attack.jpg")
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
        target = cv.imread("./temp/pc/auto.jpg") if self.platform == "PC" else cv.imread("./temp/mnq/auto.jpg")
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
        target = cv.imread("./temp/pc/finish_fighting.jpg") if self.platform == "PC" else cv.imread("./temp/mnq/finish_fighting.jpg")
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

    def Mouse_move(self, x):
        """
        说明:
            视角转动
        """
        # 该公式为不同缩放比之间的转化
        real_width = self.CONFIG["real_width"]
        dx = int(x * 1295 / real_width)
        i = int(dx/200)
        last = dx - i*200
        for ii in range(abs(i)):
            if dx >0:
                if self.platform == "PC":
                    #win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 200, 0)  # 进行视角移动
                    self.mouse.move(200, 0)
                else:
                    self.adb.input_swipe((919, 394), (1119, 394), 200)
            else:
                if self.platform == "PC":
                    #win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, -200, 0)  # 进行视角移动
                    self.mouse.move(-200, 0)
                else:
                    self.adb.input_swipe((919, 394), (719, 394), 200)
            time.sleep(0.1)
        if last != 0:
            if self.platform == "PC":
                #win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, last, 0)  # 进行视角移动
                self.mouse.move(last, 0)
            else:
                self.adb.input_swipe((919, 394), (919-last, 394), 200)
        time.sleep(0.5)

    def move(self, com = ["w","a","s","d","f"], time1=1):
        '''
        说明:
            移动
        参数:
            :param com: 键盘操作 wasdf
            :param time 操作时间,单位秒
        '''
        if self.platform == "PC":
            self.keyboard.press(com)
            start_time = time.perf_counter()
            while time.perf_counter() - start_time < time1:
                pass
            self.keyboard.release(com)
        elif self.platform == "模拟器":
            time1 = time1*1000
            if com == "w":
                self.adb.input_swipe((213, 512), (213, 409), time1)
            elif com == "a":
                self.adb.input_swipe((170, 560), (107, 560), time1)
            elif com == "s":
                self.adb.input_swipe((208, 625), (208, 684), time1)
            elif com == "d":
                self.adb.input_swipe((242, 557), (320, 557), time1)
            elif com == "f":
                self.adb.input_swipe((880, 362))

    def path_move(self, path: List):
        '''
        说明:
            根据路径移动
        参数:
            :param path: 路径列表
        '''
        fast_com = path.pop(0)
        com_data = []
        for com in path:
            if com[0]-fast_com[0] >= 0:
                if com[0]-fast_com[0] > com[1]-fast_com[1]:
                    # <
                    if com_data:
                        if list(com_data[-1].keys())[0] == "a":
                            com_data[-1]["a"] += 1
                        else:
                            com_data.append({"a": 1})
                    else:
                        com_data.append({"a": 1})
                    #self.move("a", 1, platform)
                else:
                    # /
                    if com_data:
                        if list(com_data[-1].keys())[0] == "w":
                            com_data[-1]["w"] += 1
                        else:
                            com_data.append({"w": 1})
                    else:
                        com_data.append({"w": 1})
                    #self.move("w", 1, platform)
            else:
                if com[0]-fast_com[0] > com[1]-fast_com[1]:
                    # >
                    if com_data:
                        if list(com_data[-1].keys())[0] == "d":
                            com_data[-1]["d"] += 1
                        else:
                            com_data.append({"d": 1})
                    else:
                        com_data.append({"d": 1})
                    #self.move("d", 1, platform)
                else:
                    # \
                    if com_data:
                        if list(com_data[-1].keys())[0] == "s":
                            com_data[-1]["s"] += 1
                        else:
                            com_data.append({"s": 1})
                    else:
                        com_data.append({"s": 1})
                    #self.move("s", 1, platform)
            fast_com = com
            com = ''
        log.info(com_data)
        for com in com_data:
            move_com = list(com.keys())[0]
            self.move(move_com, com[move_com])

    def scroll(self, clicks: float):
        """
        说明：
            控制鼠标滚轮滚动
        参数：
            :param clicks 滚动单位，正数为向上滚动
        """
        self.mouse.scroll(0, clicks)
        time.sleep(0.5)

    def is_blackscreen(self, threshold = 30):
        """
        说明:
            判断是否为黑屏，避免光标、加载画面或其他因素影响，不设为0，threshold范围0-255
        """
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
        if self.platform == "模拟器":
            pos = ((data[characters][2][0]+data[characters][0][0])/2, (data[characters][2][1]+data[characters][0][1])/2) if characters in data else None
        elif self.platform == "PC":
            pos = (data[characters][0][0], data[characters][0][1]) if characters in data else None
        return characters, pos
    
    def part_ocr(self,points = (0,0,0,0)):
        """
        说明：
            返回图片文字和坐标
        参数：
            :param points: 图像截取范围
        返回:
            :return data: 文字: 坐标
        """
        img_fp, left, top, right, bottom, width, length = self.take_screenshot(points)
        x, y = width/100*points[0], length/100*points[1]
        out = self.ocr.ocr(img_fp)
        data = {i['text']: (left+x+(i['position'][2][0]+i['position'][0][0])/2,top+y+(i['position'][2][1]+i['position'][0][1])/2) for i in out}
        return data

    def get_pix_bgr(self, pos):
        """
        说明：
            获取指定坐标的颜色
        参数：
            :param pos: 坐标
        返回:
            :return 三色值
        """
        img, left, top, right, bottom, width, length = self.take_screenshot()
        img = np.array(img)
        if self.platform == "PC":
            x = int(pos[0])-int(left)
            y = int(pos[1])-int(top)
        else:
            x = int(pos[0])
            y = int(pos[1])
        px = img[y, x]
        blue = img[y, x, 0]
        green = img[y, x, 1]
        red = img[y, x, 2]
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

    def wait_join(self):
        """
        说明：
            等待进入地图
        返回:
            进入地图的时间
        """
        start_time = time.time()
        while True:
            result = self.get_pix_bgr((119, 86))
            endtime = time.time() - start_time
            if result != [18, 18, 18]:
                log.info("已进入地图")
                return endtime
            if endtime > 30:
                log.info("识别超时")
                return endtime

    def switch_window(self,title = '崩坏：星穹铁道'):
        if self.platform == "PC":
            ws = gw.getWindowsWithTitle(title)
            
            if len(ws) >= 1 :
                for w in ws:
                    # 避免其他窗口也包含崩坏：星穹铁道，比如正好开着github脚本页面
                    # log.debug(w.title)
                    if w.title == title:
                        #client.Dispatch("WScript.Shell").SendKeys('%')
                        w.activate()
                        break
            else:
                log.info(f'没找到窗口{title}')

    def open_map(self, open_key):
        start_time = time.time()
        while True:
            if self.platform == "PC":
                self.keyboard.press(open_key)
                self.keyboard.release(open_key)
                #pyautogui.keyDown(open_key)
                #pyautogui.keyUp(open_key)
                time.sleep(1)
            elif self.platform == "模拟器":
                self.img_click((116, 128))
            time.sleep(0.5)
            map_status = self.part_ocr((5,7,10,10)) if self.platform == "PC" else self.part_ocr((6,2,10,5))
            if "导航" in map_status:
                log.info("进入地图")
                break
            if time.time() - start_time > 10:
                log.info("识别超时")
                break
        
