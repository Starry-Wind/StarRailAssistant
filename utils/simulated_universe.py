'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-05-19 16:04:28
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-05-21 22:26:37
Description: 

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
import re
import os
import math
import cn2an
import questionary

from xpinyin import Pinyin
from questionary import Validator, ValidationError
from typing import List
from pynput.keyboard import Controller as KeyboardController
from threading import Thread
from ultralytics.nn.tasks import  attempt_load_weights

from .calculated import *
from .config import get_file, read_json_file, modify_json_file, CONFIG_FILE_NAME
from .log import log
from .requests import webhook_and_log
from .yolo import predict
from .cv_tracker import get_rolepos

class Simulated_Universe:

    def __init__(self):
        self.calculated = calculated()
        self.win32api = win32api
        self.win32con = win32con
        self.open_map = read_json_file(CONFIG_FILE_NAME).get("open_map", "m")
        self.hwnd = win32gui.FindWindow("UnityWndClass", "崩坏：星穹铁道")
        self.map_list = []
        self.map_list_map = {}
        self.p = Pinyin()
        self.keyboard = KeyboardController()
        self.model = attempt_load_weights("./temp/model/best.pt")
        self.view_target = False
        self.order="127.0.0.1:62001"

    def read_role(self):
        """
        说明：
            读取角色
        返回:
            角色列表
        """
        self.role_list = get_file('./temp/Simulated_Universe/role')
        self.role_list = [i.split('.jpg')[0] for i in self.role_list]
        log.debug(self.role_list)
        return self.role_list
    
    def choose_level(self, level: int, start: int, pos, platform = "PC"):
        """
        说明：
            选择关卡
        参数：
            :param level: 第几个世界
            :param start: 当前世界
            :param pos: 文字坐标
        """
        if level > start:
            for i in range(abs(level - start)):
                if platform == "PC":
                    self.calculated.scroll(1)
                elif platform == "模拟器":
                    os.system(f"adb -s {self.order} shell input swipe 919 617 919 908 100")
        elif level < start:
            for i in range(abs(level - start)):
                if platform == "PC":
                    self.calculated.scroll(-1)
                elif platform == "模拟器":
                    os.system(f"adb -s {self.order} shell input swipe 925 650 925 394 100")
        if platform == "PC":
            time.sleep(0.5)
            self.calculated.Relative_click((60, 50))
        elif platform == "模拟器":
            time.sleep(0.5)
            os.system(f"adb -s {self.order} shell input tap 895 394")
        start_time = time.time()
        while True:
            if platform == "PC":
                left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
                img_fp = ImageGrab.grab((left, top, right, bottom))
                text, pos = self.calculated.ocr_pos(img_fp, "下载初始角色")
                if pos:
                    self.calculated.Click((left+pos[0], top+pos[1]))
                    break
            elif platform == "模拟器":
                os.system(f"adb -s {self.order} shell screencap -p /sdcard/Pictures/screencast.png")
                os.system(f"adb -s {self.order} pull /sdcard/Pictures/screencast.png")
                img_fp = Image.open("./screencast.png")
                text, pos = self.calculated.ocr_pos(img_fp, "下载初始角色")
                if pos:
                    os.system(f"adb -s {self.order} shell input tap {pos[0]} {pos[1]}")
                    break
            if time.time() - start_time > 10:
                log.info("识别超时")
                break

    def choose_role(self, roles: list, platform = "PC"):
        """
        说明：
            选择角色
        参数：
            :param roles: 角色列表
        """
        time.sleep(1)
        if platform == "PC":
            left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
            img_fp = ImageGrab.grab((left, top, right-(right-left)/100*70, bottom))
        elif platform == "模拟器":
            os.system(f"adb -s {self.order} shell screencap -p /sdcard/Pictures/screencast.png")
            os.system(f"adb -s {self.order} pull /sdcard/Pictures/screencast.png")
            img_fp = Image.open("./screencast.png")
        start_time = time.time()
        while True:
            for role in roles:
                role_py = self.p.get_pinyin(role,'')
                target = cv.imread(f"./temp/Simulated_Universe/role/mnq/{role_py}.png")
                result = self.calculated.scan_screenshot(target, img_fp, platform=platform)
                print(role+":"+str(result['max_val']))
                if result['max_val'] > 0.90:
                    roles.remove(role)
                    #points = self.calculated.calculated(result, img.shape)
                    if platform == "PC":
                        self.calculated.Click((result['max_loc'][0]+10, result['max_loc'][1]+10))
                    elif platform == "模拟器":
                        os.system(f"adb -s {self.order} shell input tap {result['max_loc'][0]+10} {result['max_loc'][1]+10}")
                    time.sleep(0.1)
            if len(roles) == 0:
                break
            elif time.time() - start_time > 15:
                log.info("识别超时")
                break

    def choose_presets(self, choose_presets):
        """
        说明：
            设置预设
        参数：
            :param choose_presets: 选项
        """
        presets_list = read_json_file(CONFIG_FILE_NAME).get("presets", [])
        if choose_presets == '设置预设':
            role_presets_num = int(questionary.text("请输入预设数量：").ask())
            for r in range(1, role_presets_num + 1):
                log.info(f'当前是第{r}只队伍预设')
                roles = ['三月七', '丹恒', '佩拉', '姬子', '娜塔莎', '婷云', '布洛尼亚', '希儿', '希露瓦', '彦卿', '景元', '杰帕德', '桑博', '火主', '火主1', '物主', '瓦尔特', '素裳', '艾丝妲', '虎克', '阿兰', '青雀', '黑塔']
                role_list = questionary.checkbox('请选择角色',choices=roles,validate=lambda a: (
                                            True if len(a) == 5 else "请选择5名角色"
                                        )).ask()
                presets_list.append(role_list)
                modify_json_file(CONFIG_FILE_NAME, "presets", presets_list)

    def choose_bless(self, bless:str = "巡猎", platform="PC"):
        """
        说明：
            选择祝福
        参数：
            :param bless: 命途
        """
        start_time = time.time()
        while True:
            result = self.calculated.ocr_click(f"「{bless}」", 3, 2, platform=platform, order=self.order)
            if not result:
                bless_list = ['「存护」', '「记忆」', '「虚无」', '「丰饶」', '「巡猎」', '「毁灭」', '「欢愉」']
                bless_list.remove(f"「{bless}」")
                for bless in bless_list:
                    result = self.calculated.ocr_click(bless, 3, 2)
                    if result:
                        break
            result = self.calculated.part_ocr((6,10,89,88), platform=platform, order=self.order)
            if "选择祝福" not in result:
                break
            elif time.time() - start_time > 15:
                log.info("识别超时")
                break

    def choose_event(self):
        """
        说明：
            选择事件
        """
        start_time = time.time()
        while True:
            result = self.calculated.ocr_click("「巡猎」", 3, 2)
            if not result:
                event_choose_list = ["选择","进入战斗"]
                event = ["选择"]
                log.info(set(event_choose_list).intersection(set(event)))
            result = self.calculated.part_ocr((6,10,89,88))
            if "选择事件" not in result:
                break
            elif time.time() - start_time > 15:
                log.info("识别超时")
                break

    def path_move(self, path: List, platform = "PC"):
        '''
        说明:
            移动
        '''
        fast_com = path.pop(0)
        for com in path:
            if com[0]-fast_com[0] >= 0:
                if com[0]-fast_com[0] > com[1]-fast_com[1]:
                    # <
                    self.move("a", 1, platform)
                else:
                    # /
                    self.move("w", 1, platform)
            else:
                if com[0]-fast_com[0] > com[1]-fast_com[1]:
                    # >
                    self.move("d", 1, platform)
                else:
                    # \
                    self.move("s", 1, platform)
            com = ''
            fast_com = com

    def Mouse_move(self, x, platform = "PC"):
        # 该公式为不同缩放比之间的转化
        dx = int(x * 1295 / 1295)
        i = int(dx/200)
        last = dx - i*200
        for ii in range(abs(i)):
            if dx >0:
                if platform == "PC":
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 200, 0)  # 进行视角移动
                else:
                    os.system(f"adb -s {self.order} shell input swipe 919 394 1119 394 200")
            else:
                if platform == "PC":
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, -200, 0)  # 进行视角移动
                else:
                    os.system(f"adb -s {self.order} shell input swipe 919 394 719 394 200")
            time.sleep(0.1)
        if last != 0:
            if platform == "PC":
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, last, 0)  # 进行视角移动
            else:
                os.system(f"adb -s {self.order} shell input swipe 919 394 {919-last} 394 200")
        time.sleep(0.5)

    def start_predict(self):
        last_name = ""
        while True:
            left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
            temp = ImageGrab.grab((left, top, right, bottom))
            img = np.array(temp)
            name = ['boss', 'destructible1', 'destructible2', 'destructible3', 'door1', 'door2', 'event1', 'monster1', 'monster2', 'monster3', 'monster4', 'monster5', 'role', 'transfer1', 'transfer2', 'transfer3']
            res = predict(self.model, img, name)
            log.info(res)
            for r in res:
                if r['name'] in ["destructible2","monster1"] and r['credibility'] > 0.7:
                    self.view_target = True
                    other = (r["pos"][0] + r["pos"][2])/2
                    role = (right-left)/2
                    jl1 = other-role
                    angle = math.atan(jl1/((right-left)/2 * math.tan(math.radians(60)))) * 180 / math.pi
                    xz = 10000/360
                    log.info(f'角度: {angle}')
                    log.info(angle*xz)
                    self.Mouse_move(angle*xz)
                    self.keyboard.press("w")
                    start_time = time.perf_counter()
                    while time.perf_counter() - start_time < 1:
                        pass
                    self.keyboard.release("w")
                    last_name = r['name']
                if  (r['name'] != "destructible2" or (r['name'] == "destructible2" and r['credibility'] < 0.7)) and last_name == "destructible2":
                    self.calculated.Click(win32api.GetCursorPos())
                    last_name = ""
                    self.view_target = False
                if  (r['name'] != "monster1" or (r['name'] == "monster1" and r['credibility'] < 0.7)) and last_name == "monster1":
                    self.calculated.Click(win32api.GetCursorPos())
                    last_name = ""
                    self.view_target = False

    def move(self, com, time, platform="PC"):
        '''
        说明:
            移动
        '''
        time = time*100
        if platform == "PC":
            ...
        elif platform == "模拟器":
            if com == "w":
                os.system(f"adb -s {self.order} shell input swipe 213 512 213 409 {time}")
            elif com == "a":
                os.system(f"adb -s {self.order} shell input swipe 170 560 107 560 {time}")
            elif com == "s":
                os.system(f"adb -s {self.order} shell input swipe 208 593 208 635 {time}")
            elif com == "d":
                os.system(f"adb -s {self.order} shell input swipe 242 557 320 557 {time}")
            elif com == "f":
                os.system(f"adb -s {self.order} shell input tap 880 362")

    def wait_join(self, platform="PC"):
        """
        说明：
            等待进入地图
        """
        start_time = time.time()
        while True:
            result = self.calculated.get_pix_bgr((119, 86), platform=platform, order=self.order)
            print(result)
            if result != [18, 18, 18]:
                log.info("已进入地图")
                break
            if time.time() - start_time > 30:
                log.info("识别超时")
                break

    def auto_map(self, start = 1, choose_list = [], platform = "PC"):
        #self.calculated.part_ocr((6,10,89,88))
        #self.calculated.fighting(type=1)
        roles = choose_list[0]
        fate = choose_list[1]
        if platform == "PC":
            left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
            img_fp = ImageGrab.grab((left+(right-left)/100*40, top+(bottom-top)/100*45, right-(right-left)/100*45, bottom-(bottom-top)/100*40))
        elif platform == "模拟器":
            os.system(f"adb -s {self.order} shell screencap -p /sdcard/Pictures/screencast.png")
            os.system(f"adb -s {self.order} pull /sdcard/Pictures/screencast.png")
            img_fp = Image.open("./screencast.png")
            left, top = img_fp.size
            img_fp = img_fp.crop((left/100*40, top/100*50, left/100*50, top/100*54))
        text, pos = self.calculated.ocr_pos(img_fp)
        level = cn2an.cn2an(re.findall(r"第(.*)世界", text)[0])
        self.choose_level(level, start, pos, platform)
        self.choose_role(roles, platform)
        if platform == "PC":
            self.calculated.Relative_click((85, 90))
        elif platform == "模拟器":
            os.system(f"adb -s {self.order} shell input tap 1020 654")
        self.calculated.ocr_click("O确认", 2, platform=platform, order=self.order)
        time.sleep(0.5)
        self.calculated.ocr_click(fate, 3, 2, platform=platform, order=self.order)
        time.sleep(1)
        self.calculated.ocr_click("确认命途", 3, 2, platform=platform, order=self.order)
        time.sleep(5)
        self.wait_join(platform=platform)
        self.calculated.ocr_click("获得150宇宙碎片", 3, 2, platform=platform, order=self.order)
        self.calculated.ocr_click("确认", 3, 3, platform=platform, order=self.order)
        self.choose_bless(fate, platform=platform)
        log.info(get_rolepos("44.png", platform=platform))
        '''
        t1 = Thread(target=self.start_predict)
        t1.start()
        '''


