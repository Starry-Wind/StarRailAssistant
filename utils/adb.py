'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-05-25 12:54:10
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-05-25 13:10:02
Description: 

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
from subprocess import run, DEVNULL
from PIL import ImageGrab, Image
from typing import Dict, Optional, Any, Union

class ADB:
    def __init__(self, order="127.0.0.1:62001"):
        """
        参数: 
            :param order: ADB端口
        """
        self.order = order

    def connect(self):
        """
        说明:
            连接ADB
        参数:
            :param order: ADB端口
        """
        shell = ["temp\\adb\\adb", "connect", self.order]
        run(shell, shell=True) 
    def input_swipe(self, pos1=(919,617), pos2=(919,908), time: int=100):
        """
        说明:
            滑动屏幕
        参数:
            :param pos1: 坐标1
            :param pos2: 坐标2
            :param time: 操作时间
        """
        shell = ["temp\\adb\\adb", "-s", self.order, "shell", "input", "swipe", str(pos1[0]), str(pos1[1]), str(pos2[0]), str(pos2[1]), str(time)]
        run(shell, shell=True) 

    def input_tap(self, pos=(880,362)):
        """
        说明:
            点击坐标
        参数:
            :param pos: 坐标
        """
        shell = ["temp\\adb\\adb", "-s", self.order, "shell", "input", "tap", str(pos[0]), str(pos[1])]
        run(shell, shell=True) 

    def screencast(self, path = "/sdcard/Pictures/screencast.png") -> Image:
        """
        说明:
            截图
        参数:
            :param path: 手机中截图保存位置
        """
        img_name = path.split("/")[-1]
        shell = ["temp\\adb\\adb", "-s", self.order, "shell", "screencap", "-p", path]
        run(shell, shell=True)
        shell = ["temp\\adb\\adb", "-s", self.order, "pull", path]
        run(shell, shell=True, stdout=DEVNULL) 
        img = Image.open(f"./{img_name}")
        return img