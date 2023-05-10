from get_width import get_width
import time
import os
import ctypes
import asyncio
import traceback
from tool.log import log
from tool.config import check_file

def main():
    asyncio.run(check_file("https://ghproxy.com/", "map"))
    asyncio.run(check_file("https://ghproxy.com/", "temp"))
    if isadmin() == 1:
        start = input('请输入起始地图（如果从头开始请输入0）：')
        if "-" in start and "_" in start or start == '0':
            log.info("脚本将于5秒后运行,请确保你的游戏置顶")
            time.sleep(5)
            get_width()
            from tool.map import map
            map_instance = map()
            log.info("开始运行，请勿移动鼠标和键盘")
            log.info("若脚本运行无反应,请使用管理员权限运行")
            start = '1-1_1' if start == '0' else start
            map_instance.auto_map(start)  # 读取配置
        else:
            log.info("错误编号")
        log.info("脚本已经完成运行")
    else:
         log.info("请以管理员权限运行")

def isadmin():
	return ctypes.windll.shell32.IsUserAnAdmin()

if __name__ == '__main__':
    try:
        main()
    except:
        log.error(traceback.format_exc())
