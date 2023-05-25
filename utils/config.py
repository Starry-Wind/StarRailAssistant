import os
import orjson

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


def read_json_file(filename: str, path=False):
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
        init_config_file(0, 0)
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
        f.write(orjson.dumps(data))


def init_config_file(real_width, real_height):
    with open(CONFIG_FILE_NAME, "wb+") as f:
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
                    "adb": "127.0.0.1:62001"
                }
            )
        )


def get_file(path, exclude=[], exclude_file=None, get_path=False):
    """
    获取文件夹下的文件
    """
    if exclude_file is None:
        exclude_file = []
    file_list = []
    for root, dirs, files in os.walk(path):
        add = True
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
