#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Created by Xe-No at 2023/5/16
# 模拟宇宙自动脚本试作，基于群文件demo修改而成，感谢前人贡献

from tools.calculated import *
from tools.switch_window import *
from tools.route_helper import *
import os
import cv2 as cv
import numpy as np
import pyautogui
import time
import win32api
import win32con
# from tools.config import read_json_file
from universeAuto import Pathfinder
import pytesseract

# World_num = input('请输入数字!!!\n第()世界:')
# buff_num = input('-----选择命途-----\n1:存护 2:记忆 3:虚无 4:丰饶 5:巡猎 6:毁灭 7:欢愉\n请输入数字:')
# print('一定要用拼音输入角色名!!!(绝对不是因为我不会英语)\n' * 3, '举例:布洛妮娅=buluoniya,希儿=xier' * 3,
#       '\n主角是属性+主,如火主即huozhu,物主即wuzhu\n0代表女主,1代表男主')
# print('觉得拼音麻烦可以在 temp\\Simulated_Universe\\role 目录下自行修改对应角色头像文件名')
#
# role_list = []
# for role_num in range(1, 5):
#     choose_role = input(f'第{role_num}名角色:')
#     role_list.append(choose_role)
World_num = '6'
buff_num = '5'
# role_list = ['1','2','xier','aisida']
role_list = ['xier', 'natasha', 'jiepade', 'tingyun']
# time.sleep(3)




class SimulatedUniverse:
    def __init__(self):
        self.calculated = calculated()
        self.win32api = win32api
        self.win32con = win32con
        self.mapSize = 12
        self.miniMap = [70, 0, 165, 253]
        self.wishV1 = [1500, 30, 240, 60]
        self.select = [35, 21, 120, 80]
        self.battle = [1700, 1030, 200, 50]
        self.event_rect = [45, 15, 45+140, 15+60]
        self.level_rect = [56, 17, 56+110, 17+24]
        self.scene_rect = [1813, 15, 1813+65, 15+65]
        self.object = [1550, 40, 150, 45]
        # 1长战 2战斗 3分歧 4精英 5休整 
        # 6长战 7分歧 8精英 9休整 10战斗
        # 11分歧 12休整 13首领
        self.relax_levels = [5,9,12]
        self.long_levels = [1,6]
        self.elite_levels = [4,8,13]
        self.event_levels= [11]
        self.pf = Pathfinder()


    def start_init(self):
        pyautogui.keyDown("F4")
        pyautogui.keyUp("F4")
        # time.sleep(1)

        # self.calculated.click_target(
        #     'temp\\Simulated_Universe\\Interastral_Guide.jpg', 0.98)

        self.calculated.click_target(
            'temp\\Simulated_Universe\\transfer.jpg', 0.98)

        # 初始化模拟宇宙界面
        time.sleep(1)
        for i in range(6):
            pyautogui.click(x=1180, y=220)
            time.sleep(0.4)

        # 点击至对应世界
        time.sleep(1.5)
        for i in range(eval(World_num) - 1):
            pyautogui.click(x=1180, y=940)
            time.sleep(0.4)

    def start(self):
        self.calculated.click_target(
            f'temp\\Simulated_Universe\\World_{World_num}.jpg', 0.98)
        time.sleep(1)
        self.calculated.click_target(
            'temp\\Simulated_Universe\\start_1.jpg', 0.98)

        time.sleep(2)
        for role in role_list:
            self.calculated.click_target(
                f'temp\\Simulated_Universe\\role\\{role}.jpg', 0.95)  # 选择角色
            time.sleep(1)

        self.calculated.click_target(
            'temp\\Simulated_Universe\\start_2.jpg', 0.98)

        time.sleep(1)
        target = cv.imread('temp\\Simulated_Universe\\tips.jpg')  # 解决角色等级\数量不足弹窗
        result = self.calculated.scan_screenshot(target)
        if result['max_val'] > 0.95:
            self.calculated.click_target(
                'temp\\Simulated_Universe\\yes.jpg', 0.98)

        time.sleep(2)
        self.calculated.click_target(
            f'temp\\Simulated_Universe\\buff_{buff_num}.jpg', 0.90)  # 自选命途回响
        time.sleep(1)
        self.calculated.click_target(
            'temp\\Simulated_Universe\\choose_2.jpg', 0.95)

        time.sleep(2)
        target = cv.imread('temp\\Simulated_Universe\\choose_3.jpg')
        result = self.calculated.scan_screenshot(target)
        if result['max_val'] > 0.9:
            self.calculated.click_target(
                'temp\\Simulated_Universe\\choose_3.jpg', 0.98)
            time.sleep(1)

            target = cv.imread('temp\\Simulated_Universe\\choose_4.jpg')
            result = self.calculated.scan_screenshot(target)
            if result['max_val'] > 0.9:
                self.calculated.click_target(
                    'temp\\Simulated_Universe\\choose_4.jpg', 0.98)
            print("进入地图")
        time.sleep(5)

    def get_all_map_name(self) -> list:
        map_list = []
        map_name = "universe_21_"
        i = 0
        # 把mapName都加入一个list里
        for i in range(self.mapSize):
            map_list.append(map_name + str(i))
            i += 1
        return map_list

    def map_select(self) -> int:
        # 判断地图
        time.sleep(0.5)
        print("Start searching")
        map_list = self.get_all_map_name()
        cur_map = ''
        similarity_score_buffer = 0
        for map in map_list:
            path = './temp/Simulated_Universe/map/' + map + '.jpg'
            image_b = cv.imread(path)
            image_a = pyautogui.screenshot(region=(self.miniMap[0], self.miniMap[1], self.miniMap[2], self.miniMap[3]))
            similarity_score = self.pic_similarity(image_a, image_b, -1)
            print("The similarity of " + map + " is " + str(similarity_score))
            if similarity_score_buffer < similarity_score:
                screenS = image_a
                cur_map = map
                similarity_score_buffer = similarity_score
        print("The current map is " + cur_map)
        return cur_map

    def pic_similarity(self, image_a, image_b, threshold) -> float:

        result = cv.matchTemplate(np.array(image_a), image_b, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        similarity_score = max_val * 100
        if (threshold == -1):
            return similarity_score
        return threshold >= similarity_score

    def pathfinder(self, map):
        map_data = read_json_file(f"map\\{map}.json")
        map_filename = map
        # 开始寻路
        print("开始寻路")
        for map_index, map in enumerate(map_data['map']):
            print(f"执行map文件:{map_index + 1}/{len(map_data['map'])}", map)
            key = list(map.keys())[0]
            value = map[key]
            if key in ['w', 's', 'a', 'd', 'f']:
                pyautogui.keyDown(key)
                time.sleep(value)
                pyautogui.keyUp(key)
            elif key == "mouse_move":
                self.Mouse_move(value)
            elif key == "fighting":
                if value == 1:  # 进战斗
                    self.fighting()
                elif value == 2:  # 障碍物
                    self.Click((0, 0))
                else:
                    raise Exception(
                        f"map数据错误, fighting参数异常:{map_filename}", map)
            else:
                raise Exception(f"map数据错误,未匹配对应操作:{map_filename}", map)


# =================state
    def check_state(self):
        if self.wishVerify(95): return '祝福'
        if self.selectVerify(93): return '回响'
        if self.battleVerify(95): return '战斗'
        if self.objVerify(95): return '奇物'
        if self.eventVerify(95): return '事件'
        if self.sceneVerify(95): return '场景'
        return '未知'

    def state_handler(self, state):
        unknown = 0
        max = 60
        if state == 'start':
            max = 1
        while 1:
            print(unknown)
            state = self.check_state()
            print(f'目前状态{state}')
            if state == '祝福':
                self.choose_buff()
                unknown = 0
            elif state == '回响':
                time.sleep(0.5)
                self.click(806, 473)
                time.sleep(1)
                self.click(952, 960)
                self.click(1703, 963)
                unknown = 0
            elif state == '战斗':
                time.sleep(5)
                unknown = 0

            elif state == '奇物':
                # 奇物
                time.sleep(0.5)
                self.click(806, 473)
                time.sleep(1)
                self.click(1703, 963)
                unknown = 0
                time.sleep(2)
                print("clicking")
                self.click(1005, 985)
                self.click(1005, 985)
            elif state == '事件':
                self.handle_event()

            elif state == '场景':
                # 检测到主场景就跳出
                return 

            elif (state == 0) & (unknown > max):
                return
            else:
                unknown += 1
            time.sleep(1.0)

    def handle_event(self):
        # 事件，暂时暴力点几下
        for i in range(10):
            print(f'事件点击循环{i}')
            self.calculated.click_target('temp\\Simulated_Universe\\event_selector.jpg', 0.90, False)
            self.calculated.click_target('temp\\Simulated_Universe\\event_selector2.jpg', 0.90, False)
            self.calculated.click_target('temp\\Simulated_Universe\\event_clicker.jpg', 0.90, False)
            self.calculated.click_target('temp\\Simulated_Universe\\event_confirm.jpg', 0.90, False)     
            if self.sceneVerify(90):
                return 0
            time.sleep(1)
           
    def eventVerify(self, threshold):
        path = 'temp\\Simulated_Universe\\eventVerify.jpg'
        image_s = pyautogui.screenshot(region=(self.event_rect[0], self.event_rect[1], self.event_rect[2], self.event_rect[3])) #
        # image_s = pyautogui.screenshot(region=(0, 0, 300, 300)) #
        image = cv.imread(path)
        similarity = self.pic_similarity(image_s, image, -1)
        if similarity > threshold:
            return 1
        return 0

    def sceneVerify(self, threshold):
        path = 'temp\\Simulated_Universe\\sceneVerify.jpg'
        image_s = pyautogui.screenshot(region=(self.scene_rect[0], self.scene_rect[1], self.scene_rect[2], self.scene_rect[3]))
        image = cv.imread(path)
        similarity = self.pic_similarity(image_s, image, -1)
        if similarity > threshold:
            return 1
        return 0

    def battleVerify(self, threshold):
        path = 'temp\\Simulated_Universe\\battleVerify.jpg'
        image_s = pyautogui.screenshot(region=(self.battle[0], self.battle[1], self.battle[2], self.battle[3]))
        image = cv.imread(path)
        similarity = self.pic_similarity(image_s, image, -1)
        if similarity > threshold:
            return 1
        return 0

    def objVerify(self, threshold):
        path = 'temp\\Simulated_Universe\\objVerify.jpg'
        image_s = pyautogui.screenshot(region=(self.object[0], self.object[1], self.object[2], self.object[3]))
        image = cv.imread(path)
        similarity = self.pic_similarity(image_s, image, -1)
        print(similarity)
        if similarity > threshold:
            return 1
        return 0

    def selectVerify(self, threshold):
        path = 'temp\\Simulated_Universe\\selectVerify.jpg'
        image_s = pyautogui.screenshot(region=(self.select[0], self.select[1], self.select[2], self.select[3]))
        image = cv.imread(path)
        self.saveImage(image_s)
        similarity = self.pic_similarity(image_s, image, -1)
        print(similarity)
        if similarity > threshold:
            return 1
        return 0

    def wishVerify(self, threshold) -> int:
        image_s = pyautogui.screenshot(region=(self.wishV1[0], self.wishV1[1], self.wishV1[2], self.wishV1[3]))
        path_wish = 'temp\\Simulated_Universe\\wishVerify1.jpg'
        image = cv.imread(path_wish)
        similarity = self.pic_similarity(image_s, image, -1)
        if similarity > threshold:
            return 1
        return 0

# =============level
    def is_level(self, level_type, threshold):
        image_s = pyautogui.screenshot(region=(self.level_rect[0], self.level_rect[1], self.level_rect[2], self.level_rect[3]))
        path = f'temp\\Simulated_Universe\\level_{level_type}.jpg'
        image = cv.imread(path)
        similarity = self.pic_similarity(image_s, image, -1)
        if similarity > threshold:
            return 1
        return 0

    def check_level(self, level_index):

        if level_index in self.long_levels:
            return '长战'
        elif level_index in self.relax_levels:
            return '休整'
        elif level_index in self.elite_levels:
            return '精英'

        elif self.is_level('battle', 90):
            return '战斗'        
        elif self.is_level('encounter', 90):
            return '遭遇'
        elif self.is_level('event', 90):
            return '事件'
        return ''

    def handle_level(self,  level_type):
        if level_type == '长战':
            self.handle_long_level()
        elif level_type == '休整':
            pass
        elif level_type == '精英':
            # move_to_atlas('temp\\Simulated_Universe\\atlas_elite.jpg', 'A')
            move(1.5)
            pyautogui.click(600,600)
            self.state_handler('guiding')            
        elif level_type == '事件':
            move_to_atlas('temp\\Simulated_Universe\\atlas_event.jpg')
            self.state_handler('guiding')
        elif level_type == '战斗':
            move_to_atlas('temp\\Simulated_Universe\\atlas_elite.jpg', 'A')
            self.state_handler('guiding')

        time.sleep(3)
        self.state_handler('')


    def click(self, x, y):
        pyautogui.click((x, y))

    def saveImage(self, image):
        image.save(os.path.join(os.path.expanduser('~'), 'Desktop', 'screenshot.jpg'))

    def quit(self):
        cv.destroyAllWindows()
        pyautogui.keyDown("ESC")
        pyautogui.keyUp("ESC")
        time.sleep(1)
        pyautogui.click(1425, 938)
        time.sleep(1)
        pyautogui.click(1164, 670)
        time.sleep(7)
        pyautogui.click(863, 1000)
        print("Round finished")

    def start_simulated(self):
        self.start_init()
        self.start()
        self.state_handler('start')

        cur_map = self.map_select()
        self.pf.guide(cur_map)
        self.state_handler('guiding')
        return 0

    def goto_portal(self):
        move_to_atlas('temp\\Simulated_Universe\\atlas_portal.jpg')
        

        if level_index in self.elite_levels:
            time.sleep(2)
            self.calculated.click_target('temp\\Simulated_Universe\\claim_reward_confirm.jpg', 0.90)


    


    def handle_long_level(self):
        cur_map = self.map_select()
        self.pf.guide(cur_map)
        self.state_handler('guiding')
        





    def choose_buff(self):
        # 判断并选择buff,优先图鉴其次命途
        i = 1
        while i <= 2:
            target = cv.imread('temp\\Simulated_Universe\\new_buff.jpg')
            result = self.calculated.scan_screenshot(target)
            time.sleep(2)
            if result['max_val'] > 0.85:
                self.calculated.click_target(
                    'temp\\Simulated_Universe\\choose_4.jpg', 0.90)  # 如果识别到了图鉴标志则识别并点击目标

            target = cv.imread(f'temp\\Simulated_Universe\\choose_buff_{buff_num}.jpg')
            result = self.calculated.scan_screenshot(target)
            time.sleep(2)
            if result['max_val'] > 0.85:
                self.calculated.click_target(
                    'temp\\Simulated_Universe\\choose_4.jpg', 0.90)  # 如果没识别到图鉴标志则识别命途祝福并点击目标
            elif i <= 2:
                i += 1

            if i == 2:
                self.calculated.click_target(
                    'temp\\Simulated_Universe\\refresh_buff.jpg', 0.90)  # 若以上都没识别到则刷新一次
                time.sleep(2)

            target = cv.imread(f'temp\\Simulated_Universe\\refresh_buff.jpg')  # 大力出奇迹!
            result = self.calculated.scan_screenshot(target)
            if result['max_val'] > 0.85:
                pyautogui.click(960, 580)
                time.sleep(0.5)
                self.calculated.click_target(
                    'temp\\Simulated_Universe\\choose_4.jpg', 0.90)
    def end(self):
        self.calculated.click_target('temp\\Simulated_Universe\\simulation_end.jpg', 0.90)

if __name__ == '__main__':
    switch_window()
    time.sleep(0.5)

    # su = SimulatedUniverse()
    # print(su.choose_buff())
    # sys.exit()
    for simu_time in range(1,10+1):
        print(f'第{simu_time}次模拟开始')
        su = SimulatedUniverse()

        su.start_init()
        su.start()
        su.state_handler('start')

        # 目前容易卡，要是卡了就注释掉start部分，再改range下界吧

        for level_index in range(1,14):
            level_type = ''

            level_type = su.check_level(level_index)
            print(f'第{level_index}关-{level_type}-进行中')
            
            su.handle_level(level_type)
            su.goto_portal()
            time.sleep(0.3)
        su.end()
