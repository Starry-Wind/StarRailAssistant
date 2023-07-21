'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-05-15 21:45:43
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-07-17 23:26:54
Description: 

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
import os
import re
import sys
import orjson
import gettext

from pathlib import Path
from copy import copy
from loguru import logger

message = ""

class FileFilter:
    def __init__(self, file):
        self.file = file

    def __call__(self, record):
        return record["extra"].get("file") == self.file
    
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
        return {}
    
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

def get_message(*arg):
    """
    说明:
        收集消息并返回
    返回:
        收集到的消息
    """
    global message
    if arg:
        content = arg[0][:-1].replace("\x1b[0;34;40m","").replace("-1\x1b[0m","")
        if re.match(_(r'开始(.*)锄地'),content):
            message += f"\n{content}"
    return message

dir_log = "logs"
data = read_json_file("config.json")
VER = str(data.get("star_version",0))+"/"+str(data.get("picture_version",0))+"/"+str(data.get("map_version",0))
path_log = os.path.join(dir_log, _('日志文件.log'))
fight_path_log = os.path.join(dir_log, _('战斗日志.log'))
level = data.get("level","INFO")
log = logger.bind(file=path_log)
fight_log = logger.bind(file=fight_path_log)
log.remove()

stdout_log = log.add(sys.stdout, level=level, colorize=True,
            format="<cyan>{module}</cyan>.<cyan>{function}</cyan>"
                    ":<cyan>{line}</cyan> - "+f"<cyan>{VER}</cyan> - "
                    "<level>{message}</level>",filter=FileFilter(path_log))

#logger.add(get_message, level=level,format="{message}")

log.add(path_log,
            format="{time:HH:mm:ss} - "
                    "{level}\t| "
                    "{module}.{function}:{line} - "+f"<cyan>{VER}</cyan> - "+" {message}",
            rotation="1 days", enqueue=True, serialize=False, encoding="utf-8", retention="10 days",filter=FileFilter(path_log))

fight_log.add(fight_path_log,
            format="{time:HH:mm:ss} - "
                    "{level}\t| "
                    "{module}.{function}:{line} - "+f"<cyan>{VER}</cyan> - "+" {message}",
            rotation="1 days", enqueue=True, serialize=False, encoding="utf-8", retention="10 days",filter=FileFilter(fight_path_log))

def set_log(header:str):
    global stdout_log
    global level
    log.remove(stdout_log)
    stdout_log = log.add(sys.stdout, level=level, colorize=True,
                format=f"<cyan>{header}</cyan> - "+f"<cyan>{VER}</cyan> - "
                        "<level>{message}</level>",filter=FileFilter(path_log))
