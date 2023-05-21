import time

import cv2 as cv
import pyautogui

from tools.calculated import Calculated
from tools.config import get_file, read_json_file, CONFIG_FILE_NAME
from tools.log import log, webhook_and_log


class Map:
    def __init__(self):
        self.calculated = Calculated()
        self.open_map = read_json_file(CONFIG_FILE_NAME).get("open_map", "m")
        self.map_list = []
        self.map_list_map = {}
        self.read_maps()

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

    def read_maps(self):
        self.map_list = get_file('./map', ['old'])  # 从'./map'目录获取地图文件列表（排除'old'）
        self.map_list_map.clear()
        for map_ in self.map_list:
            map_data = read_json_file(f"map/{map_}")
            key1 = map_[map_.index('_') + 1:map_.index('-')]
            key2 = map_[map_.index('-') + 1:map_.index('.')]
            value = self.map_list_map.get(key1)
            if value is None:
                value = {}
            value[key2] = map_data["name"]
            self.map_list_map[key1] = value
        log.debug(self.map_list)
        log.debug(self.map_list_map)

    def auto_map(self, start):
        if f'map_{start}.json' in self.map_list:
            map_list = self.map_list[self.map_list.index(f'map_{start}.json'):len(self.map_list)]
            for map_ in map_list:
                # 选择地图
                map_ = map_.split('.')[0]
                map_data = read_json_file(f"map/{map_}.json")
                name = map_data['name']
                author = map_data['author']
                start_dict = map_data['start']
                webhook_and_log(f"开始\033[0;34;40m{name}\033[0m锄地")
                log.info(f"该路线导航作者：\033[0;31;40m{author}\033[0m")
                log.info("感谢每一位无私奉献的作者")
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
                        self.calculated.click_target(key, 0.96)
                time.sleep(3)
                count = 0
                while self.calculated.is_blackscreen():
                    count += 1
                    time.sleep(1)
                log.info(f'地图加载完毕，加载时间为 {count} 秒')

                self.calculated.auto_map(map_, False)
        else:
            log.info(f'地图编号 {start} 不存在，请尝试检查更新')
