'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-05-12 23:22:54
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-05-14 01:22:36
FilePath: \Honkai-Star-Rail-beta-2.4h:\Download\Zip\Honkai-Star-Rail-beta-2.7\tools\log.py
Description: 

Copyright (c) 2023 by ${git_name_email}, All Rights Reserved. 
'''
import os
import sys
from loguru import logger

try:
    from .requests import post
except:
    from requests import post

VER = "3.1"
log = logger
dir_log = "logs"
path_log = os.path.join(dir_log, '日志文件.log')
logger.remove()
logger.add(sys.stdout, level='INFO', colorize=True,
            format="<cyan>{module}</cyan>.<cyan>{function}</cyan>"
                    ":<cyan>{line}</cyan> - "+f"<cyan>{VER}</cyan> - "
                    "<level>{message}</level>"
            )
logger.add(path_log,
            format="{time:HH:mm:ss} - "
                    "{level}\t| "
                    "{module}.{function}:{line} - "+f"<cyan>{VER}</cyan> - "+" {message}",
            rotation='0:00', enqueue=True, serialize=False, encoding="utf-8", retention="10 days")

def webhook_and_log(message):
    log.info(message)
    from tools.config import read_json_file # Circular import
    url = read_json_file("config.json", False).get("webhook_url")
    if url == "" or url == None:
        return
    try:
        post(url, json={"content": message})
    except Exception as e:
        log.error(f"Webhook发送失败: {e}")
