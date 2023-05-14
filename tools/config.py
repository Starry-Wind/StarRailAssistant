import os
import orjson
import hashlib
import asyncio

try:
    from .requests import *
    from .log import log
except:
    from requests import *
    from log import log

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
            if path == True:
                return data, file_path
            else:
                return data
    else:
        init_config_file(0,0)
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
                    "map_debug": False,
                    "github_proxy": "",
                    "rawgithub_proxy": "",
                    "webhook_url": "",
                    "start": False,
                    "temp_version": "0",
                    "star_version": "0",
                    "open_map": "m"
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

async def check_file(github_proxy, filename = 'map'):
    """
    说明：
        检测文件是否完整
    参数：
        :param github_proxy: github代理
        :param filename: 文件名称
    """
    try:
        map_list = await get(
            f'{github_proxy}https://raw.githubusercontent.com/Starry-Wind/Honkai-Star-Rail/map/{filename}_list.json',
            follow_redirects=True)
        map_list = map_list.json()
    except Exception:
        log.warning('读取资源列表失败，请尝试更换github资源地址')
        return
    flag = False
    for map in map_list:
        file_path = Path() / map['path']
        if os.path.exists(file_path):
            if hashlib.md5(file_path.read_bytes()).hexdigest() == map['hash']:
                continue
        try:
            await download(
                url=f'{github_proxy}https://raw.githubusercontent.com/Starry-Wind/Honkai-Star-Rail/map/{map["path"]}',
                save_path=file_path)
            await asyncio.sleep(0.2)
            flag = True
        except Exception:
            log.warning(f'下载{map["path"]}时出错，请尝试更换github资源地址')
    log.info('资源下载完成' if flag else '资源完好，无需下载')