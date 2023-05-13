import time

import cv2 as cv
import pyautogui

from .calculated import *
from .config import get_file, read_json_file, CONFIG_FILE_NAME
from .log import log, webhook_and_log

class map:
    def __init__(self):
        self.calculated = calculated()
        self.win32api = win32api
        self.win32con = win32con
        self.open_map = read_json_file(CONFIG_FILE_NAME).get("open_map", "m")

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
        log.debug(map_list)
        if f'map_{start}.json' in map_list:
            map_list = map_list[map_list.index(f'map_{start}.json'):len(map_list)]
            for map in map_list:
                # 选择地图
                map = map.split('.')[0]
                map_data = read_json_file(f"map\\{map}.json")
                name=map_data['name']
                author=map_data['author']
                start_dict=map_data['start']
                webhook_and_log(f"开始\033[0;34;40m{name}\033[0m锄地")
                log.info(f"该路线导航作者：\033[0;31;40m{author}\033[0m")
                log.info(f"感谢每一位无私奉献的作者")
                for start in start_dict:
                    key = list(start.keys())[0]
                    log.debug(key)
                    value = start[key]
                    if key == 'map':
                        pyautogui.keyDown(self.open_map)
                        pyautogui.keyUp(self.open_map)
                        time.sleep(1)
                        self.map_init()
                    else:
                        time.sleep(value)
                        self.calculated.click_target(key, 0.98)
                time.sleep(5)
                self.calculated.auto_map(map, False)
        else:
            log.info('错误编号')
