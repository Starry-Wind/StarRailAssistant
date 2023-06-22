import os
import orjson
import gettext

from orjson import JSONDecodeError
from pydantic import BaseModel, ValidationError, BaseSettings, validator

from .log import log

CONFIG_FILE_NAME = "config.json"

def normalize_file_path(filename):
    # 尝试在当前目录下读取文件
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, filename)
    if os.path.exists(file_path):
        return file_path
    else:
        # 如果当前目录下没有该文件，则尝试在上一级目录中查找
        parent_dir = os.path.dirname(current_dir)
        file_path = os.path.join(parent_dir, filename)
        if os.path.exists(file_path):
            return file_path
        else:
            # 如果上一级目录中也没有该文件，则返回None
            return None


def read_json_file(filename: str, path=False) -> dict:
    """
    说明：
        读取文件
    参数：
        :param filename: 文件名称
        :param path: 是否返回路径
    """
    # 找到文件的绝对路径
    file_path = normalize_file_path(filename)
    if file_path:
        with open(file_path, "rb") as f:
            data = orjson.loads(f.read())
            if path:
                return data, file_path
            else:
                return data
    else:
        init_config_file(1920, 1080, filename)
        return read_json_file(filename, path)


def modify_json_file(filename: str, key, value):
    """
    说明：
        写入文件
    参数：
        :param filename: 文件名称
        :param key: key
        :param value: value
    """
    # 先读，再写
    data, file_path = read_json_file(filename, path=True)
    data[key] = value
    with open(file_path, "wb") as f:
        f.write(orjson.dumps(data, option=orjson.OPT_PASSTHROUGH_DATETIME | orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_INDENT_2))


def init_config_file(real_width, real_height, file_name = CONFIG_FILE_NAME):
    if file_name == CONFIG_FILE_NAME:
        with open(CONFIG_FILE_NAME, "wb+") as f:
            log.info("配置初始化")
            f.write(
                orjson.dumps(
                    {
                        "real_width": real_width,
                        "auto_battle_persistence": 0,
                        "real_height": real_height,
                        "github_proxy": "",
                        "rawgithub_proxy": "",
                        "webhook_url": "",
                        "start": False,
                        "temp_version": "0",
                        "star_version": "0",
                        "open_map": "m",
                        "level": "INFO",
                        "debug": False,
                        "adb": "127.0.0.1:62001",
                        "adb_path": "temp\\adb\\adb",
                        "proxies": "",
                        "language": "zh_CN",
                        "move_excursion": 0,
                        "move_division_excursion": 1,
                        "sprint": False,
                        "join_time": {
                            "pc": 8,
                            "mnq": 15
                        },
                        "deficiency": True
                    },option = orjson.OPT_PASSTHROUGH_DATETIME | orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_INDENT_2
                )
            )
    else:
        with open(file_name, "wb+") as f:
            log.info("配置初始化")
            f.write(
                orjson.dumps(
                    {},option = orjson.OPT_PASSTHROUGH_DATETIME | orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_INDENT_2
                )
            )


def get_file(path, exclude=[], exclude_file=None, get_path=False, only_place=False) -> list[str]:
    """
    获取文件夹下的文件
    """
    if exclude_file is None:
        exclude_file = []
    file_list = []
    for root, dirs, files in os.walk(path):
        add = True
        if (dirs==[] and only_place) or not only_place:
            for i in exclude:
                if i in root:
                    add = False
            if add:
                for file in files:
                    add = True
                    for ii in exclude_file:
                        if ii in file:
                            add = False
                    if add:
                        if get_path:
                            path = root + "/" + file
                            file_list.append(path.replace("//", "/"))
                        else:
                            file_list.append(file)
    return file_list

def get_folder(path) -> list[str]:
    """
    获取文件夹下的文件夹列表
    """
    for root, dirs, files in os.walk(path):
        return dirs
    
language = read_json_file("config.json").get("language", "zh_CN")
t = gettext.translation('sra', 'locale', [language])
_ = t.gettext

def add_key_value(dictionary, key, value, position):
    """
    说明:
        在指定位置添加键值对
    参数:
        :param dictionary 需要添加的字典
        :param key: 键
        :param value: 值
        :param position: 需要添加的位置
    返回:
        new_dictionary: 添加后的字典
    """
    keys = list(dictionary.keys())
    values = list(dictionary.values())
    keys.insert(position, key)
    values.insert(position, value)
    new_dictionary = dict(zip(keys, values))
    return new_dictionary

def read_maps(platform):
    """
    说明:
        读取地图
    """
    map_list = get_file('./map',only_place=True) if platform == _("PC") else get_file('./map/mnq',only_place=True)
    map_list_map = {}
    for map_ in map_list:
        map_data = read_json_file(f"map/{map_}") if platform == _("PC") else read_json_file(f"map/mnq/{map_}")
        key1 = map_[map_.index('_') + 1:map_.index('-')]
        key2 = map_[map_.index('-') + 1:map_.index('.')]
        value = map_list_map.get(key1)
        if value is None:
            value = {}
        value[key2] = map_data["name"]
        map_list_map[key1] = value
    map_list.sort()
    log.debug(map_list)
    log.debug(map_list_map)
    return map_list, map_list_map

def insert_key(my_dict:dict, new_key, new_value, insert_after_key):
    """
    说明:
        将指定键值对插入指定key后面
    参数:
        :param my_dict: 被操作的字典
        :param new_key: 需要插入的key
        :param new_value: 需要插入的value
        :param insert_after_key: 插入到那个key后面
    """
    # 创建一个空的 OrderedDict
    new_dict = {}

    # 遍历原始字典的键值对
    for key, value in my_dict.items():
        # 将键值对添加到新的字典中
        new_dict[key] = value
        
        # 在指定键后面插入新的键值对
        if key == insert_after_key:
            new_dict[new_key] = new_value
            
    return new_dict

class FightConfig(BaseSettings):
    """
    检漏信息
    """
    data: list[str]= []
    '''遗漏的地图'''
    day_time: str = "0"
    '''地图写入时间'''

class SRAConfig:
    """
    配置文件
    """
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    real_width: int = 0
    '''游戏宽度'''
    real_height: int = 0
    '''游戏高度'''
    scaling: int = 0
    '''缩放大小'''
    borderless: bool = False
    '''是否全屏'''
    left_border: float = 11.25
    '''左边框大小'''
    up_border: float = 44.25
    '''上边框大小'''
    auto_battle_persistence: int = 0
    '''是否要程序开启自动战斗（1为否）'''
    github_proxy: str = ""
    '''github代理'''
    rawgithub_proxy: str = ""
    '''rawgithub代理代理'''
    webhook_url: str = ""
    '''未知'''
    start: bool = True
    '''是否第一次运行'''
    open_map: str = "m"
    '''打开地图的按钮'''
    language: str =  "zh_CN"
    '''语言'''
    proxies: str = ""
    '''网络代理'''
    img: int = 0
    '''GUI背景图片序号'''
    move_excursion:int = 0
    '''角色移动偏移（加减）'''
    move_division_excursion:int = 1.0
    '''角色移动偏移（乘除）'''
    sprint: bool = False
    '''是否疾跑'''
    deficiency: bool = True
    '''是否检漏'''

    map_version: str = "0"
    '''地图版本'''
    temp_version: str = "0"
    '''图片版本'''
    star_version: str = "0"
    '''程序版本'''

    level: str = "INFO"
    '''LOG等级'''
    adb: str = "127.0.0.1:62001"
    '''ADB地址'''
    adb_path: str = "temp\\adb\\adb"
    '''ADB程序路径地址'''

    fight_data: FightConfig = FightConfig()

settings_data = read_json_file(CONFIG_FILE_NAME)
plugin_data_obj = SRAConfig(**settings_data)