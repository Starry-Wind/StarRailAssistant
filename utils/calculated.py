"""
系统控制项，以及玩家控制
"""
import itertools
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import cv2 as cv
import numpy as np
import pywinctl as pwc  # 跨平台支持
import win32api
import hashlib
import pprint
from cnocr import CnOcr
from PIL import Image, ImageGrab
from pynput import mouse
from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Key
from pynput.mouse import Controller as MouseController

from .config import CONFIG_FILE_NAME, _, get_file, sra_config_obj
from .cv_tools import CV_Tools, show_img
from .exceptions import Exception
from .log import log

#from .get_angle import Point

class calculated(CV_Tools):

    def __init__(self, title=_("崩坏：星穹铁道"), det_model_name="ch_PP-OCRv3_det", rec_model_name= "densenet_lite_114-fc", number=False, start=True):
        """
        参数: 
            :param det_model_name: 文字定位模型
            :param rec_model_name: 文字识别模型
            :param number: 是否只考虑数字
            :param start: 是否开始运行脚本 如果为False则不加载OCR等模型
        """
        super().__init__(title)
        self.title = title

        self.scaling = sra_config_obj.scaling
        self.DEBUG = sra_config_obj.debug
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        #self.point = Point(title)

        self.pos = (100, 100)

        if start:
            if getattr(sys, 'frozen', None):
                dir = sys._MEIPASS
            else:
                dir = Path()
            det_root, rec_root = os.path.join(dir, "model/cnstd"), os.path.join(dir, "model/cnocr")
            self.ocr = CnOcr(det_model_name=det_model_name, rec_model_name=rec_model_name, rec_vocab_fp="model/cnocr/label_cn.txt", det_root=det_root, rec_root=rec_root) if not number else CnOcr(det_model_name=det_model_name, rec_model_name=rec_model_name,det_root="./model/cnstd", rec_root="./model/cnocr", cand_alphabet='0123456789')
            self.number_ocr = CnOcr(det_model_name=det_model_name, rec_model_name=rec_model_name, det_root=det_root, rec_root=rec_root, cand_alphabet='0123456789.+%')
            #self.ocr = CnOcr(det_model_name='db_resnet34', rec_model_name='densenet_lite_114-fc')
        self.check_list = lambda x,y: re.match(x, str(y)) != None
        self.compare_lists = lambda a, b: all(x <= y for x, y in zip(a, b))

        # 初始化
        self.attack = cv.imread("./picture/pc/attack.png")
        self.doubt = cv.imread("./picture/pc/doubt.png")
        self.warn = cv.imread("./picture/pc/warn.png")
        # tagz = cv.imread("./picture/pc/tagz.jpg")
        self.finish = cv.imread("./picture/pc/finish_fighting.jpg")
        self.auto = cv.imread("./picture/pc/auto.jpg")

        self.end_list = ["Tab", _("轮盘"), _("唤起鼠标"), _("手机"), _("退出")]

    def rp2ap(self, points):
        """
        说明:
            相对坐标转绝对坐标
        参数：
            :param points: 百分比坐标
        """      
        borderless = sra_config_obj.borderless
        left_border = sra_config_obj.left_border
        up_border = sra_config_obj.up_border
        #points = (points[0]*1.5/scaling,points[1]*1.5/scaling,points[2]*1.5/scaling,points[3]*1.5/scaling)
        if borderless:
            left, top, right, bottom = self.window.left, self.window.top, self.window.right, self.window.bottom
        else:
            left, top, right, bottom = self.window.left+left_border, self.window.top+up_border, self.window.right-left_border, self.window.bottom-left_border
        # log.info(f"{left}, {top}, {right}, {bottom}")
        x, y = int(left + (right - left) / 100 * points[0]), \
                int(top + (bottom - top) / 100 * points[1])
        log.debug((x, y))
        return (x, y)

    def click(self, points = None, click_time=0.5):
        """
        说明：
            点击坐标
        参数：
            :param points: 坐标
        """
        if not points:
            points = self.mouse.position
        x, y = int(points[0]), int(points[1])
        self.mouse.position = (x, y)
        self.mouse.press(mouse.Button.left)
        time.sleep(click_time)
        self.mouse.release(mouse.Button.left)

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
            self.mouse.position = (x, y)
            self.mouse.press(mouse.Button.left)
            time.sleep(0.5)
            self.mouse.release(mouse.Button.left)
            result = self.get_pix_r(appoint_points)
            log.debug(result)
            if result == hsv:
                break
            if time.time() - start_time > 5:
                log.info(_(_("识别超时")))
                break

    def relative_click(self, points, click_time=0.5):
        """
        说明：
            点击相对坐标
        参数：
            :param points: 百分比坐标
        """
        return self.click(self.rp2ap(points), click_time)

    def img_click(self, points):
        """
        说明：
            点击图片坐标
        参数：
            :param points: 坐标
        """
        left, top, __, __ = self.window.left, self.window.top, self.window.right, self.window.bottom
        x, y = int(left + points[0] + sra_config_obj.left_border), int(top + points[1] + sra_config_obj.up_border)
        log.info((x, y))
        self.mouse.position = (x, y)
        self.mouse.press(mouse.Button.left)
        time.sleep(0.5)
        self.mouse.release(mouse.Button.left)

    def ocr_click(self, characters, overtime = 10, frequency = 1, points = (0, 0, 0, 0)):
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
                #img_fp, left, top, __, __, __, __ = self.take_screenshot()
                #show_img(img_fp)
                __, pos = self.ocr_pos(characters, points)
                log.debug(characters)
                if pos:
                    self.click(pos)
                    time.sleep(0.3)
                    return pos
                if time.time() - start_time > overtime:
                    log.info(_("识别超时")) if overtime != 0 else None
                    return False

    def hsv_click(self, hsv_color, points=(0,0,0,0), offset=(0,0), flag=True, tolerance = 5):
        """
        说明：
            点击指定hsv颜色，允许偏移
        参数：
            :param hsv_color: hsv颜色
            :param points: 百分比截取范围
            :param offset: 坐标偏移
        """
        start_time = time.time()
        while True:
            if time.time() - start_time > 10:
                log.info(_("识别超时"))
                return False
            img_fp, left, top, __, __, width, length = self.take_screenshot(points)
            #cv.imwrite('scr.png', img_fp)
            x, y = left + width/100*points[0], top + length/100*points[1]
            pos = self.hsv2pos(img_fp, hsv_color, tolerance)
            if pos == None:
                time.sleep(0.1)
                if flag == True:
                    continue
                else:
                    break
            ret = [x + pos[0] + offset[0] , y + pos[1] + offset[1] ]
            log.info(_('点击坐标{ret}').format(ret=ret))
            self.click(ret)
            return True
        
    def swipe(self, pos1, pos2, time_=1):
        """
        说明:
            滑动屏幕
            相较scroll方法，提高精度与可控性
            (注意此方法在部分场景中，页面会有滑动惯性造成的动态延迟)
        参数:
            :param pos1: 坐标1
            :param pos2: 坐标2
            :param time_: 操作时间
        """
        import pyautogui
        pyautogui.moveTo(pos1[0], pos1[1])
        pyautogui.mouseDown()
        pyautogui.moveTo(pos2[0], pos2[1], duration=time_)
        pyautogui.mouseUp()

    def relative_swipe(self, pos1, pos2, time_=1):
        """
        说明:
            相对坐标滑动屏幕
        参数:
            :param pos1: 相对坐标1
            :param pos2: 相对坐标2
            :param time_: 操作时间
        """
        self.swipe(self.rp2ap(pos1), self.rp2ap(pos2), time_)

    def remove_non_white_pixels(self, image):
        """
        说明:
            移除非白色像素
        参数:
            :param image: 图像
        """
        # 定义白色的HSV范围
        lower_white = np.array([0, 0, 200], dtype=np.uint8)
        upper_white = np.array([180, 25, 255], dtype=np.uint8)
        # 将图像转换为HSV颜色空间
        hsv_image = cv.cvtColor(image, cv.COLOR_BGR2HSV)
        # 创建掩膜，将非白色区域设置为黑色
        mask = cv.inRange(hsv_image, lower_white, upper_white)
        # 将掩膜应用到原始图像上
        result = cv.bitwise_and(image, image, mask=mask)
        return result

    def scan_screenshot(self, prepared:np, points = None) -> dict:
        """
        说明：
            比对图片
        参数：
            :param prepared: 比对图片地址
            :param pos: 游戏局部截图的坐标
        """
        screenshot, left, top, __, __, game_width, game_length = self.take_screenshot(points if points else (0,0,0,0))
        result = cv.matchTemplate(screenshot, prepared, cv.TM_CCORR_NORMED)
        length, width, __ = prepared.shape
        length = int(length)
        width = int(width)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        if points:
            min_loc = (min_loc[0]+game_width/100*points[0], min_loc[1]+game_length/100*points[1])
            max_loc = (max_loc[0]+game_width/100*points[0], max_loc[1]+game_length/100*points[1])
        return {
            "screenshot": screenshot,
            "min_val": min_val,
            "max_val": max_val,
            "min_loc": (min_loc[0] + left+(width/2), min_loc[1] + top+(length/2)),
            "max_loc": (max_loc[0] + left+(width/2), max_loc[1] + top+(length/2)),
        }

    # flag为true一定要找到
    def click_target(self, target_path: str, threshold, flag:bool=True, check:bool=False, map=""):
        """
        说明:
            识别图片并点击
        参数:
            :param target_path: 需要识别的图片地址
            :param threshold: 可信度阈值
            :param flag: 是否必须找到
        """
        target_path = target_path.replace("picture\\","").replace("temp\\","").replace("picture\\pc\\","")
        picture_path = "picture\\pc\\"+target_path
        temp_name = target_path.split(".")[0]
        join = False # 强制进行传统模板匹配
        '''
        map: 
            type为str时点击对应文字
            tyrpe为tuple时点击对应坐标
        map_*_point:
            type为dict时在points中点击name
        其他:
            type为dict时在points中点击name
            type为tuple时点击百分比坐标
            type为str时点击文字
        '''
        temp_ocr = {
            "orientation_1": {
                "name": _("星轨航图"),
                "points": (77, 11, 92, 15)
            },
            #"orientation_2": (18, 50), #  _("空间站「黑塔")
            "map_1": _("基座舱段"),
            "transfer": _("传送"),
            "map_1-2": _("收容舱段"),
            "map_1-3": _("支援舱段"),
            "map_1-3_point_2": {
                "name": _("电力室"),
                "points": (40, 67, 63, 79)
            },
            #"orientation_3": (52, 23), # _("雅利洛-VI")
            "map_2-1": _("城郊雪原"),
            "map_2-2": _("边缘通路"),
            "map_2-3": _("残响回廊"),
            "map_2-4": _("永冬岭"),
            "map_2-5": _("大矿区"),
            "map_2-6": _("铆钉镇"),
            "map_2-7": _("机械聚落"),
            #"orientation_4": (79, 80), # _("仙舟「罗浮")
            "map_3-1": _("流云渡"),
            "map_3-2": _("迴星港"),
            "map_3-3": _("太卜司"),
            "map_3-4": _("工造司"),
            "map_3-5": _("丹鼎司"),
            "map_3-6": _("鳞渊境"),
            "change_team": _("更换队伍"),
        }

        if temp_name in temp_ocr:
            log.info(temp_name)
            if "orientation" in temp_name:
                log.info(_("选择星球"))
            elif "point" in temp_name:
                log.info(_("选择传送锚点"))
            elif "map" in temp_name:
                log.info(_("选择地图"))
            if "orientation" in temp_name or "transfer" in temp_name:
                if type(temp_ocr[temp_name]) == dict:
                    result = self.ocr_click(temp_ocr[temp_name]["name"], points=temp_ocr[temp_name]["points"])
                elif type(temp_ocr[temp_name]) == tuple:
                    self.relative_click(temp_ocr[temp_name])
                    result = True
                else:
                    result = self.ocr_click(temp_ocr[temp_name])
                while True:
                    if not result:
                        log.info(_("使用图片识别兜底"))
                        join = True
                        break
                    if not self.is_blackscreen():
                        break
            elif "change_team" in temp_name:
                self.change_team()
            elif "point" in temp_name and "map" in temp_name:
                start_time = time.time()
                while True:
                    if type(temp_ocr[temp_name]) == dict:
                        result = self.ocr_click(temp_ocr[temp_name]["name"], points=temp_ocr[temp_name]["points"])
                        if result:
                            break
            else:
                if type(temp_ocr[temp_name]) == str:
                    start_time = time.time()
                    first_timeout = True
                    while True:
                        ocr_data = self.part_ocr((77,20,95,97))
                        log.debug(temp_ocr[temp_name])
                        check_dict = list(filter(lambda x: re.match(f'.*{temp_ocr[temp_name]}.*', x) != None, list(ocr_data.keys())))
                        pos = ocr_data.get(check_dict[0], None) if check_dict else None
                        log.debug(pos)
                        if pos:
                            self.appoint_click(pos,(pos[0]+60, pos[1]), [40,40,40])
                            break
                        if time.time() - start_time > 5:
                            # 右边列表太长了 尝试向下滚动5秒 再向上滚动5秒
                            # scroll内部sleep 0.5s 大概能10次 目前最长在雅利洛需要向下滚动7次
                            if first_timeout:  # 点击右边的地图列表
                                self.relative_click((80, 50))
                                first_timeout = False
                            if time.time() - start_time < 10:
                                self.scroll(-10)
                            else:
                                self.scroll(10)

                        if time.time() - start_time > 15:
                            log.info(_("地图识别超时"))
                            # join = True
                            break
                elif type(temp_ocr[temp_name]) == tuple:
                    self.img_click(temp_ocr[temp_name])
        if temp_name not in temp_ocr or join:
            log.info(temp_name)
            target = cv.imread(picture_path)
            start_time = time.time()
            first_timeout = True
            distance_iter = itertools.cycle([300, -300, -300])
            level_iter = itertools.cycle([(3, 81), (3, 89), (3, 75)])
            move_num = 0
            while True:
                result = self.scan_screenshot(target)
                log.info(result["max_val"])
                if result["max_val"] > threshold:
                    #points = self.calculated(result, target.shape)
                    self.click(result["max_loc"])
                    break
                if time.time() - start_time > 5 and "point" in temp_name:
                    start_x = (self.window.left+self.window.right) // 2
                    start_y = (self.window.top+self.window.bottom) // 2
                    log.info(move_num%3)
                    if move_num%3 == 0 and move_num != 0:
                        self.relative_click(next(level_iter))
                        time.sleep(0.2)
                    self.swipe((start_x, start_y), (start_x, start_y+next(distance_iter)), 1)
                    move_num+=1
                if ((time.time() - start_time > 15  and "point" not in temp_name) \
                    or (time.time() - start_time > 30  and "point" in temp_name)): #防止卡死.重启线程
                    log.info(_("传送识别超时"))
                    #self.keyboard.press(Key.esc)
                    #time.sleep(0.1)
                    #self.keyboard.release(Key.esc)
                    break
                if flag == False:
                    break
                time.sleep(0.5)

    def fighting(self):
        start_time = time.time()
        self.click()
        time.sleep(0.1)
        if self.has_red((4, 7, 10, 19)):
            while True:
                result = self.get_pix_rgb(pos=(40, 62))
                log.debug(f"进入战斗取色: {result}")
                if self.compare_lists([0, 0, 222], result) and self.compare_lists(result, [0, 0, 255]):
                    self.click()
                else:
                    break
                time.sleep(0.1)
                if time.time() - start_time > 10:  # 如果已经识别了10秒还未找到目标，则退出循环
                    log.info(_("识别超时,此处可能漏怪!"))
                    return False
            self.wait_fight_end()
            return True
        time.sleep(0.2)
        result = self.get_pix_rgb(pos=(40, 62))
        log.debug(f"进入战斗取色: {result}")
        if not (self.compare_lists([0, 0, 225], result) and self.compare_lists(result, [0, 0, 255])):
            self.wait_fight_end() # 无论是否识别到敌人都判断是否结束战斗，反正怪物袭击
        return True

    def check_fighting(self):
        while True:
            if (
                self.compare_lists([0, 0, 222], self.get_pix_rgb(pos=(1435, 58))) and
                self.compare_lists(self.get_pix_rgb(pos=(1435, 58)), [0, 0, 240]) and
                self.compare_lists([20, 90, 80], self.get_pix_rgb(pos=(88, 979))) and
                self.compare_lists(self.get_pix_rgb(pos=(88, 979)), [25, 100, 90])
            ):
                log.info(_("未在战斗状态"))
                break
            else:
                log.info(_("未知状态,可能遇袭处于战斗状态"))
            time.sleep(1) # 避免长时间ocr

    def wait_fight_end(self, type=0):
        """
        说明:
            等待战斗结束
        参数:
            :param type: 0: 大世界 1:副本
        """
        #进入战斗
        start_time = time.time()
        if sra_config_obj.auto_battle_persistence != 1:  #这个设置建议放弃,看了看浪费性能加容易出问题
            while True:
                result = self.scan_screenshot(self.auto, points=(90, 0, 100, 10))
                if result["max_val"] > 0.95:
                    time.sleep(0.3)
                    self.keyboard.press("v")
                    self.keyboard.release("v")
                    log.info(_("开启自动战斗"))
                    break
                elif time.time() - start_time > 15:
                    break
                time.sleep(0.1)
        else:
            log.info(_("跳过开启自动战斗（沿用设置）"))
            time.sleep(5)
        start_time = time.time()  # 开始计算战斗时间
        while True:
            if type == 0:
                if (
                    self.compare_lists([0, 0, 222], self.get_pix_rgb(pos=(1435, 58))) and
                    self.compare_lists(self.get_pix_rgb(pos=(1435, 58)), [0, 0, 240]) and
                    self.compare_lists([20, 90, 80], self.get_pix_rgb(pos=(88, 979))) and
                    self.compare_lists(self.get_pix_rgb(pos=(88, 979)), [25, 100, 90])
                ):
                    log.info(_("完成自动战斗"))
                    break
            elif type == 1:
                end_str = str(self.part_ocr((32, 85, 56, 89)))
                if self.ocr_click("退出关卡", overtime=0, points=(32, 85, 42, 89)):
                    log.info(_("完成自动战斗"))
                    break
                if self.ocr_click("返回忘却之庭", overtime=0, points=(44, 85, 56, 89)):
                    log.info(_("完成自动战斗"))
                    break
            time.sleep(1.0) # 缓冲
            fight_time = sra_config_obj.fight_time
            if time.time() - start_time > fight_time: # 避免卡死
                log.info(_("战斗超时"))
                break
            time.sleep(1) # 避免长时间ocr

    def mouse_move(self, x):
        """
        说明:
            视角转动
        """
        # 该公式为不同缩放比之间的转化
        scaling = sra_config_obj.scaling
        dx = x * scaling
        i = int(dx/200)
        last = int(dx - i*200)
        for ii in range(abs(i)):
            if dx >0:
                win32api.mouse_event(1, 200, 0)  # 进行视角移动
            else:
                win32api.mouse_event(1, -200, 0)  # 进行视角移动
            time.sleep(0.1)
        if last != 0:
            win32api.mouse_event(1, last, 0)  # 进行视角移动
        #time.sleep(0.5)

    def move(self, com: str = ["w","a","s","d","f"], sleep_time=1, map_name=""):
        '''
        说明:
            移动
        参数:
            :param com: 键盘操作 wasdf
            :param time 操作时间,单位秒
        '''
        loc = self.get_loc(map_name=map_name) if self.DEBUG else (0, 0)
        log.info(loc)
        if type(sleep_time) == list:
            set_loc = sleep_time[1]
            sleep_time = sleep_time[0]
            self.move_com(com, sleep_time)
            loc = self.get_loc(map_name=map_name) if self.DEBUG else (0, 0)
            log.info(loc)
            com_num = abs(loc[1] - set_loc[1])
            if com_num > 16:
                self.move_com(com, com_num/16)
        else:
            self.move_com(com, sleep_time)
            loc = (0, 0)
        return loc

    def move_com(self, com, sleep_time=1):
        move_excursion = sra_config_obj.move_excursion
        move_division_excursion = sra_config_obj.move_division_excursion
        self.keyboard.press(com)
        start_time = time.perf_counter()
        if sra_config_obj.sprint:
            result = self.get_pix_r(pos=(1712, 958))
            if (self.compare_lists(result, [130, 160, 180]) or self.compare_lists([200, 200, 200], result)):
                time.sleep(0.05)
                log.info("疾跑")
                self.mouse.press(mouse.Button.right)
                self.mouse.release(mouse.Button.right)
        while time.perf_counter() - start_time < (sleep_time/move_division_excursion+move_excursion):
            pass
        self.keyboard.release(com)

    def scroll(self, clicks: float):
        """
        说明：
            控制鼠标滚轮滚动
        参数：
            :param clicks 滚动单位，正数为向上滚动
        """
        self.mouse.scroll(0, clicks)
        time.sleep(0.1)

    def is_blackscreen(self, threshold = 30):
        """
        说明:
            判断是否为黑屏，避免光标、加载画面或其他因素影响，不设为0，threshold范围0-255
        """
        screenshot = cv.cvtColor(self.take_screenshot()[0], cv.COLOR_BGR2GRAY)
        return cv.mean(screenshot)[0] < threshold

    def ocr_pos(self, characters:str = None, points = (0,0,0,0)):
        """
        说明：
            获取指定文字的坐标
        参数：
            :param points: 百分比坐标
        返回:
            :return text: 文字
            :return pos: 坐标
        """
        #img_fp = self.take_screenshot(points)
        #out = self.ocr.ocr(img_fp)
        #data = {i['text']: i['position'] for i in out}
        data = self.part_ocr(points)
        log.debug(data)
        if not characters:
            characters = list(data.keys())[0]
        check_list = list(filter(lambda x: re.match(f'.*{characters}.*', x) != None, list(data.keys())))
        characters = check_list[0] if check_list else None
        #pos = ((data[characters][2][0]+data[characters][0][0])/2, (data[characters][2][1]+data[characters][0][1])/2) if characters in data else None
        pos = data[characters] if characters in data else None
        return characters, pos

    def ocr_pos_for_singleLine(self, characters_list:list[str] = None, points = (0,0,0,0), number = False, debug = False, img_pk:tuple = None) -> Union[int, str]:
        """
        说明：
            获取指定坐标的单行文字
        参数：
            :param characters_list: 预选文字列表
            :param points: 图像截取范围
            :param img_pk: 图像数据包，由take_screenshot函数返回
            :param number: 设置OCR字符集为 '0123456789.+%'
        返回：
            :return index: 预选文字列表索引
            :return data: 文字
        """
        data = self.part_ocr(points, debug, number=number, img_pk=img_pk, is_single_line=True)
        if len(data) == 0:  # 字符串长度为零
            return None
        if not characters_list:
            return data   # 常用于返回单行数字
        # 在预选列表寻找第一个匹配项
        for index, characters in enumerate(characters_list):
            if re.match(f'.*{characters}.*', data):
                return index
        log.error(f"OCR失败，所识别的 '{data}' 不在指定预选项{characters_list}中")
        return -1

    def read_img(self, path, prefix='./picture/pc/'):
        """
        说明：
            读取图像
        参数：
            :param path: 路径
        返回:
            :return img: 图像
        """
        return cv.imread(f'{prefix}{path}')

    def part_ocr(self, points = (0,0,0,0), debug=False, left=False, number = False, img_pk:tuple = None, is_single_line = False, only_white=False
                       ) -> Union[str, dict[str, tuple[int, int]]]:
        """
        说明：
            返回图片文字和坐标(相对于桌面的坐标)
        参数：
            :param points: 图像截取范围
            :param left: 是否返回左上角坐标
            :param number: 设置OCR字符集为 '0123456789.+%'
            :param img_pk: 图像数据包，由take_screenshot函数返回
            :param is_single_line: 是否仅识别单行文字
        返回:
            :return data: 文字: 坐标(相对于桌面的坐标)
        """
        if img_pk:  # 支持对一次结果的多次OCR
            img_fp, game_left, game_top, __, __, width, length = img_pk   # 此时由take_screenshot返回的图片已消除窗口位置、窗口边框的影响
            if points != (0,0,0,0):
                # 通过切片对图片裁剪，shape(img)=(length, width, channal)
                img_fp = img_fp[int(length/100*points[1]):int(length/100*points[3]),
                                int(width/100*points[0]):int(width/100*points[2]), :] 
        else:
            img_fp, game_left, game_top, _, _, width, length = self.take_screenshot(points)
        if only_white:
            img_fp = self.remove_non_white_pixels(img_fp)
        x, y = width/100*points[0], length/100*points[1]
        if is_single_line:
            out = self.number_ocr.ocr_for_single_line(img_fp) if number else self.ocr.ocr_for_single_line(img_fp)
            data = out['text']
        else:
            out = self.ocr.ocr(img_fp) if number else self.ocr.ocr(img_fp)
            if left:
                data = {i['text'].replace(" ", ""): (int(game_left+x+i['position'][0][0]), int(game_top+y+i['position'][0][1])) for i in out}
            else:
                data = {i['text'].replace(" ", ""): (int(game_left+x+(i['position'][2][0]+i['position'][0][0])/2),int(game_top+y+(i['position'][2][1]+i['position'][0][1])/2)) for i in out}
        if debug:
            log.info(data)
            # show_img(img_fp)
            timestamp_str = str(int(datetime.timestamp(datetime.now())))
            cv.imwrite(f"log/image/relic_{str(points)}_{timestamp_str}.png", img_fp)
        else:
            log.debug(data)
        return data

    def get_pix_r(self, desktop_pos: Union[tuple, None]=None, pos: Union[tuple, None]=None, points: tuple=(0, 0, 0, 0)):
        """
        说明：
            获取指定坐标的颜色
        参数：
            :param desktop_pos: 包含桌面的坐标
            :param pos: 图片的坐标
        返回:
            :return rgb: 颜色
        """
        img, left, top, __, __, __, __ = self.take_screenshot(points)
        img = np.array(img)
        if desktop_pos:
            x = int(desktop_pos[0])-int(left)
            y = int(desktop_pos[1])-int(top)
        elif pos:
            x = int(pos[0])
            y = int(pos[1])
        rgb = img[y, x]
        blue = img[y, x, 0]
        green = img[y, x, 1]
        red = img[y, x, 2]
        return [blue,green,red]

    def get_pix_rgb(self, desktop_pos: Union[tuple, None]=None, pos: Union[tuple, None]=None, points: tuple=(0, 0, 0, 0)):
        """
        说明：
            获取指定坐标的颜色
        参数：
            :param desktop_pos: 包含桌面的坐标
            :param pos: 图片的坐标
        返回:
            :return rgb: 颜色
        """
        img, left, top, __, __, __, __ = self.take_screenshot(points)
        HSV=cv.cvtColor(img,cv.COLOR_BGR2HSV)
        if desktop_pos:
            x = int(desktop_pos[0])-int(left)
            y = int(desktop_pos[1])-int(top)
        elif pos:
            x = int(pos[0])
            y = int(pos[1])
        rgb = HSV[y, x]
        blue = HSV[y, x, 0]
        green = HSV[y, x, 1]
        red = HSV[y, x, 2]
        return [blue,green,red]

    def hsv2pos(self, img, color, tolerance = 0):
        """
        说明：
            获取指定颜色的坐标
        参数：
            :param img: 图片
            :param color: 颜色
            :param tolerance: 颜色误差容忍度 0-255
        返回:
            :return 坐标
        """
        HSV=cv.cvtColor(img,cv.COLOR_BGR2HSV)
        for index,x in enumerate(HSV):
            for index1,x1 in enumerate(HSV[index]):
                # 色相保持一致
                if abs(x1[0] - color[0])==0 and abs(x1[1] - color[1])<=tolerance and abs(x1[2] - color[2])<=tolerance:
                    return (index1, index)

    def has_red(self, points=(0,0,0,0)):
        """
        说明:
            判断游戏指定位置是否有红色
        参数:
            :param points: 图像截取范围
        """
        img = self.take_screenshot(points)[0]
        hsv_img = cv.cvtColor(img, cv.COLOR_BGR2HSV)

        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])
        lower_red2 = np.array([170, 100, 100])
        upper_red2 = np.array([180, 255, 255])

        mask1 = cv.inRange(hsv_img, lower_red, upper_red)
        mask2 = cv.inRange(hsv_img, lower_red2, upper_red2)
        mask = cv.bitwise_or(mask1, mask2)

        # 统计掩膜中的像素数目
        red_pixel_count = cv.countNonZero(mask)
        log.info(red_pixel_count)
        return red_pixel_count > 30

    def wait_join(self):
        """
        说明：
            等待进入地图
        返回:
            进入地图的时间
        """
        start_time = time.time()
        '''
        join1 = False
        join2 = False
        block_join1 = False
        block_join2 = False
        '''
        join_time = sra_config_obj.join_time
        while True:
            '''
            result = self.get_pix_r(pos=(960, 86))
            log.info(result)
            endtime = time.time() - start_time
            if self.compare_lists([222, 222, 116], result):
                block_join1 = True # 进入地图
            elif self.compare_lists([0, 0, 0], result) and self.compare_lists(result, [190, 190, 190]) and block_join1:
                block_join2 = True # 进入地图
            if not block_join2:
                if self.compare_lists([0, 0, 0], result) and self.compare_lists(result, [19, 19, 19]):
                    join1 = True # 开始传送
                elif self.compare_lists([19, 19, 19], result) and join1:
                    join2 = True # 进入地图
            if join1 and join2 or (block_join1 and block_join2):
                log.info(_("已进入地图"))
                return endtime
            '''
            endtime = time.time() - start_time
            result = self.get_pix_rgb(pos=(40, 62))
            log.debug(result)
            if self.compare_lists([0, 0, 222], result):
                log.info(_("已进入地图"))
                return endtime
            if endtime > join_time:
                log.info(_("识别超时"))
                return endtime
            time.sleep(0.1)

    def switch_window(self, dt=0.1):
        ws = pwc.getWindowsWithTitle(self.title)
        time.sleep(dt)
        if len(ws) >= 1:
            for w in ws:
                # 避免其他窗口也包含崩坏：星穹铁道，比如正好开着github脚本页面
                # log.debug(w.title)
                if w.title == self.title:
                    #client.Dispatch("WScript.Shell").SendKeys('%')
                    self.keyboard.press(Key.right)
                    self.keyboard.release(Key.right)                     
                    w.activate()
                    break
        else:
            log.info(_('没找到窗口{title}').format(title=self.title))
        time.sleep(dt)

    def open_map(self, open_key):
        while True:
            self.keyboard.press(open_key)
            time.sleep(0.3) # 修复地图无法打开的问题
            self.keyboard.release(open_key)
            time.sleep(1)
            map_status = self.part_ocr((3,2,10,10))
            if self.check_list(_(".*导.*"), map_status):
                log.info(_("进入地图"))
                break

    def teleport(self, key, value, threshold=0.95):
        """
            入画. 入画时ui会消失, 所以可以通过检测团队图标, 来判断是否结束入画
        param:
            - key 对应按键
            - value 操作时间,单位秒
        """
        self.move(key)
        time.sleep(1) # 等待进入入画
        log.info(_("等待入画结束"))
        time.sleep(0.3) # 缓冲
        while True:            
            if (
                self.compare_lists([0, 0, 222], self.get_pix_rgb(pos=(1435, 58))) and
                self.compare_lists(self.get_pix_rgb(pos=(1435, 58)), [0, 0, 240]) and
                self.compare_lists([20, 90, 80], self.get_pix_rgb(pos=(88, 979))) and
                self.compare_lists(self.get_pix_rgb(pos=(88, 979)), [25, 100, 90])
            ):
                log.info(_("完成入画"))
                break
            time.sleep(1.0) # 缓冲

    def monthly_pass(self):
        """
        说明：
            点击月卡
        """
        start_time = time.time()
        dt = datetime.now().strftime('%Y-%m-%d') + " 04:00:00"
        ts = int(time.mktime(time.strptime(dt, "%Y-%m-%d %H:%M:%S")))
        ns = int(start_time)
        if -60 < ns - ts <= 60:
            log.info(_("点击月卡"))
            pos = self.ocr_click(_("今日补给"))
            time.sleep(0.5)
            self.click(pos)

    def get_loc(self, map_name: str="", map_id: int=None):
        """
        说明:
            获取玩家坐标
        参数:
            :param map_name: 地图名称
            :param map_id: 地图ID
        返回:
            (x, y)
        """
        map_name2id = {
            "铁卫禁区": {
                "铁卫禁区-1": 7,
            },
            "丹鼎司": {
                "丹鼎司-1": 2,
                "丹鼎司-2": 3,
                "丹鼎司-3": 3,
                "丹鼎司-4": 3,
                "丹鼎司-5": 4,
                "丹鼎司-6": 4,
            }
        }
        map_id = map_name2id.get(map_name.split("-")[0], {}).get(map_name, None)
        if not map_id:
            return (0, 0)
        img = cv.imread(f"./picture/maps/{map_id}.png")
        template = self.take_screenshot((2.194802494802495, 4.509276437847866, 12.445738045738045, 23.283858998144712))[0]
        #img = img[self.pos[1]-100:img.shape[0]]
        max_scale_percent, max_val, max_loc, length, width = self.find_best_match(img, template, [100, 105, 124, 125])
        #max_val, max_loc = match_scaled(img, template,2.09)
        #log.info(max_scale_percent)
        #log.info(max_val)
        '''
        if max_scale_percent in [102, 103]:
            max_loc = (max_loc[0] + int(width/2)+17, max_loc[1] + int(length/2))
        else:
            max_loc = (max_loc[0] + int(width/2)+10, max_loc[1] + int(length/2))
        '''
        max_loc = (max_loc[0] + width//2 + 6, max_loc[1] + length//2 + 1)
        cv.rectangle(img, max_loc, (max_loc[0] + 5, max_loc[1] + 5), (0, 255, 0), 2)
        show_img(img, not_close=1)
        #max_loc = (max_loc[0], max_loc[1] + self.pos[1]-100)
        self.pos = max_loc
        return max_loc

    def change_team(self):
        """
        说明:
            切换队伍
        """
        if self.ocr_click("队伍", points = (4, 1, 9, 6), overtime=1):
            team_list = [(732, 79),(854, 83),(975, 77),(1091, 79),(1214, 81),(1333, 79)] # 队伍坐标
            self.img_click(team_list[sra_config_obj.team_number-1])
            return True
        else:
            return False

    def get_data_hash(self, data) -> str:
        """
        说明：
            求任意类型数据 (包括list和dict) 的哈希值
            首先将数据规范化输出为str，再计算md5转16进制
        """
        # pprint默认sort_dicts=True，对键值进行排序，以确保字典类型数据的唯一性
        return hashlib.md5(pprint.pformat(data).encode('utf-8')).hexdigest()
    