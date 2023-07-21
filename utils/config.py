import os
import sys
from typing import Any, get_type_hints, Union
import orjson
import gettext
import inspect

from pathlib import Path
from orjson import JSONDecodeError

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
        if path:
            return {}, filename
        else:
            return {}


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


def get_file(path, exclude=[], exclude_file=None, get_path=False, only_place=False) -> list[str]:
    """
    获取文件夹下的文件
    """
    if exclude_file is None:
        exclude_file = []
    file_list = []
    for index,(root, dirs, files) in enumerate(os.walk(path)):
        add = True
        if (index==0 and only_place) or not only_place:
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
if getattr(sys, 'frozen', None):
    dir = sys._MEIPASS
else:
    dir = Path()
locale_path = os.path.join(dir, "locale")
t = gettext.translation('sra', locale_path, [language])
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

def read_maps():
    """
    说明:
        读取地图
    """
    map_list = get_file('./map',only_place=True)
    map_list_map = {}
    for map_ in map_list:
        map_data = read_json_file(f"map/{map_}")
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


def get_class_methods(cls):
    """
    说明:
        获取类属性
    """
    methods = []
    for name, member in inspect.getmembers(cls): # 获取类属性
        if not inspect.isfunction(member) and not name.startswith("__"):
            methods.append(name)
    return methods

def load_config_data(cls, __name):
    """
    加载配置文件
    """
    #methods = get_class_methods(cls)
    sradata = read_json_file(CONFIG_FILE_NAME)
    if __name in sradata:
        setattr(cls, __name, sradata[__name])
    '''
    lack_methods = set(methods) - set(sradata.keys()) # 获取缺少的配置
    # 如果缺少配置则添加
    if lack_methods:
        for lack_method in lack_methods:
            sradata[lack_method] = getattr(cls, lack_method)
            modify_json_file(CONFIG_FILE_NAME, lack_method, getattr(cls, lack_method))
    # 读取配置
    for key, value in sradata.items():
        setattr(cls, key, value)
    '''

class SRADataMeta(type):
    def __setattr__(cls, __name, __value):
        type_hints = get_type_hints(cls) # 获取所有类属性的类型信息
        __name_type = type_hints.get(__name)
        if  __name_type is not None and not isinstance(__value, __name_type):
            raise TypeError(f"{__name}类型错误, 期望类型为{__name_type.__name__}, 实际类型为{type(__value).__name__}")
        modify_json_file(CONFIG_FILE_NAME, __name, __value)
        super().__setattr__(__name, __value)

class SRAData(metaclass=SRADataMeta):
    test: bool = False
    real_width: int = 0
    """实际宽度"""
    real_height: int = 0
    """实际高度"""
    scaling: float = 1.5
    """缩放比例"""
    borderless:bool = False
    """是否无边框"""
    left_border:float = 11.25
    """左边框距离"""
    up_border:float = 44.25
    """上边框距离"""
    auto_battle_persistence: int = 0
    """是否开启自动战斗"""
    github_proxy: str = ""
    """github代理"""
    rawgithub_proxy: str = ""
    """rawgithub代理"""
    webhook_url: str = ""
    """webhook地址"""
    start: bool = False
    """是否第一次运行"""
    picture_version: str = "0"
    """图片版本"""
    map_version: str = "0"
    """地图版本"""
    star_version: str = "0"
    """小助手版本"""
    open_map: str = "m"
    """打开地图的按钮"""
    level: str = "INFO"
    """日志等级"""
    debug: bool = False
    """是否开启debug"""
    proxies: str = ""
    """代理"""
    language: str = "zh_CN"
    """游戏语言"""
    move_excursion: int = 0
    """移动偏移"""
    move_division_excursion: float = 1.0
    """移动偏移除数"""
    sprint: bool = False
    """是否开启冲刺"""
    join_time: int = 8
    """进入地图时间"""
    deficiency: bool = True
    """是否开启捡漏"""
    img: int = 0
    """图片编号"""
    fight_time:int = 300
    """战斗时间"""
    fight_data: dict = {}
    """战斗数据"""
    team_number: int = 1
    """切换队伍的队伍编号"""
    stop: bool = False
    """是否停止"""
    github_source: str = "Night-stars-1"
    """github仓库源"""

    def __init__(self) -> None:
        ...
    
    def __setattr__(self, __name: str, __value: Any) -> None:
        type_hints = get_type_hints(self) # 获取所有类属性的类型信息
        __name_type = type_hints.get(__name)
        if not isinstance(__value, __name_type):
            raise TypeError(f"{__name}类型错误, 期望类型为{__name_type.__name__}, 实际类型为{type(__value).__name__}")
        modify_json_file(CONFIG_FILE_NAME, __name, __value)
        super().__setattr__(__name, __value)

    def __getattribute__(self, __name: str) -> Any:
        if "__" in __name:
            return super().__getattribute__(__name)
        if __name in self.__dict__:
            type_hints = get_type_hints(self) # 获取所有类属性的类型信息
            __name_type = type_hints.get(__name)
            __value = super().__getattribute__(__name)
            if not isinstance(__value, __name_type):
                raise TypeError(f"{__name}类型错误, 期望类型为{__name_type.__name__}, 实际类型为{type(__value).__name__}")
        load_config_data(SRAData, __name)
        return super().__getattribute__(__name)
    
    def set_config(self, key, value):
        """
        说明:
            设置配置
        """
        setattr(self, key, value)

    def get_config(self, key):
        """
        说明:
            获取配置
        """
        return getattr(self, key)

sra_config_obj = SRAData()
