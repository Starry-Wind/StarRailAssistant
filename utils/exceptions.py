'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-05-13 13:05:56
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-05-13 13:08:28
FilePath: \Honkai-Star-Rail-beta-2.4h:\Download\Zip\Honkai-Star-Rail-beta-2.7\tool\exceptions.py
Description: 

Copyright (c) 2023 by ${git_name_email}, All Rights Reserved. 
'''
from .log import log
import traceback

class Exception(Exception):


    def __init__(self, message):
        super().__init__(message)
        log.error(message)
        log.debug(traceback.format_exc())
