'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-05-15 21:45:43
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-05-20 19:10:53
Description: 

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
import os
import sys
from loguru import logger

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
