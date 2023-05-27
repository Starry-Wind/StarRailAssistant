from .calculated import *
from .config import get_file, read_json_file, CONFIG_FILE_NAME
from .log import log
from .requests import webhook_and_log


class Map:
    def __init__(self, platform="PC",order="127.0.0.1:62001"):
        """
        参数: 
            :param platform: 运行设备
        """
        self.platform = platform # 运行设备
        platform2name = {
            "PC": "pc",
            "模拟器": "mnq"
        }
        self.platform_name = platform2name[platform]
        self.adb = ADB(order)

        self.calculated = calculated(platform,order)
        self.keyboard = self.calculated.keyboard
        self.open_map = read_json_file(CONFIG_FILE_NAME).get("open_map", "m")
        self.map_list = []
        self.map_list_map = {}
        self.read_maps()

    def map_init(self):

        # 进行地图初始化，把地图缩小,需要缩小5次
        if self.platform == "PC":
            target = cv.imread(f'./temp/{self.platform_name}/contraction.jpg')
            while True:
                result = self.calculated.scan_screenshot(target)
                if result['max_val'] > 0.98:
                    #points = self.calculated.calculated(result, target.shape)
                    points = result["max_loc"]
                    log.debug(points)
                    for i in range(5):
                        self.calculated.Click(points)
                    break
        elif self.platform == "模拟器":
            for i in range(5):
                self.calculated.img_click((366, 660))

    def start_map(self, map, old=True):
        map_data = (
            read_json_file(f"map\\old\\{map}.json")
            if old
            else read_json_file(f"map\\{map}.json")
        )
        map_filename = map
        # 开始寻路
        log.info("开始寻路")
        for map_index, map in enumerate(map_data["map"]):
            log.info(f"执行{map_filename}文件:{map_index+1}/{len(map_data['map'])} {map}")
            key = list(map.keys())[0]
            value = map[key]
            if key in ["w", "s", "a", "d"]:
                self.calculated.move(key, value)
            elif key == "f":
                self.calculated.teleport(key, value)
            elif key == "mouse_move":
                self.calculated.Mouse_move(value)
            elif key == "fighting":
                if value == 1:  # 进战斗
                    if self.platform == '模拟器':
                        self.adb.input_tap((1040, 550))
                    self.calculated.fighting()
                elif value == 2:  # 障碍物
                    if self.platform == "PC":
                        self.calculated.Click()
                        time.sleep(1)
                    else:
                        self.adb.input_tap((1040, 550))
                else:
                    raise Exception(f"map数据错误, fighting参数异常:{map_filename}", map)
            elif key == "scroll":
                self.calculated.scroll(value)
            else:
                raise Exception(f"map数据错误,未匹配对应操作:{map_filename}", map)

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
            for map in map_list:
                # 选择地图
                map = map.split('.')[0]
                map_data = read_json_file(f"map/{map}.json")
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
                        self.calculated.open_map(self.open_map)
                        self.map_init()
                    else:
                        time.sleep(value)
                        self.calculated.click_target(key, 0.98)
                time.sleep(3)
                count = self.calculated.wait_join()
                log.info(f'地图加载完毕，加载时间为 {count} 秒')
                time.sleep(2) # 加2s防止人物未加载

                self.start_map(map, False)
        else:
            log.info(f'地图编号 {start} 不存在，请尝试检查更新')
