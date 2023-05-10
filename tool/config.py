import os

import orjson

from tool.constants import CONFIG_FILE_NAME


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


def read_json_file(filename, path=False):
    # 找到文件的绝对路径
    file_path = normalize_file_path(filename)
    with open(file_path, "rb") as f:
        data = orjson.loads(f.read())
        if path == True:
            return data, file_path
        else:
            return data


def modify_json_file(filename, key, value):
    # 先读，再写
    data, file_path = read_json_file(filename, path=True)
    data[key] = value
    current_dir = os.getcwd()
    with open(file_path, "wb") as f:
        f.write(orjson.dumps(data))
        return


def init_config_file(real_width, real_height):
    with open(CONFIG_FILE_NAME, "wb+") as f:
        f.write(
            orjson.dumps(
                {
                    "real_width": real_width,
                    "auto_battle_persistence": 0,
                    "real_height": real_height,
                }
            )
        )


def get_file(path, exclude):
    """
    获取文件夹下的文件
    """
    file_list = []
    for root, dirs, files in os.walk(path):
        if exclude not in root:
            for file in files:
                file_list.append(file)
    return file_list
