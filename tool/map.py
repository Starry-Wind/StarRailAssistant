import time

import cv2 as cv
import pyautogui

from .calculated import *
from .config import get_file
from .log import log


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
                log.debug(points)
                pyautogui.click(points, clicks=5, interval=0.1)
                break

    def auto_map(self, start):
        map_list = get_file('./map', 'old')  # 从'./map'目录获取地图文件列表（排除'old'）
        if f'map_{start}.json' in map_list:
            map_list = map_list[map_list.index(f'map_{start}.json'):len(map_list)]  # 切片获取指定地图及其之后的地图列表
            for map_file_name in map_list:  # 循环map_list中所有的列表
                # 选择地图
                map_name = map_file_name.split('.')[0]  # 去除文件扩展名，获取地图名称
                map_data = read_json_file(f"map\\{map_name}.json")  # 读取地图文件
                name = map_data['name']  # 获取地图名称
                author = map_data['author']  # 获取地图作者
                start_dict = map_data['start']  # 获取地图起始传送相关数据 （列表）
                log.info(f"开始\033[0;34;40m{name}\033[0m锄地")  # 输出地图名称
                log.info(f"该路线导航作者：\033[0;31;40m{author}\033[0m")  # 输出地图作者
                log.info(f"感谢每一位无私奉献的作者")
                if len(start_dict) > 0:
                    pyautogui.keyDown("m")  # 按下键盘上的"M"键
                    pyautogui.keyUp("m")  # 松开"M"键
                    time.sleep(1)
                    self.map_init()  # 初始化地图
                    for start_data in start_dict:  # start->dict
                        map_start_image_path = list(start_data.keys())[0]  # 获取地图起始传送的图形文件路径
                        log.debug(map_start_image_path)  # 调试输出文件路径
                        value = start_data[map_start_image_path]  # 获取地图起始传送的等待延迟
                        time.sleep(value)  # 等待延迟
                        self.calculated.click_target(map_start_image_path, 0.85)  # 调用点击目标函数
                else:
                    log.info("该地图无需打开地图传送，等待5秒")
                time.sleep(5)  # 等待5秒
                self.calculated.auto_map(map_name, False)  # 调用地图map数据解析函数
        else:
            log.info('错误编号')  # 输出错误信息
