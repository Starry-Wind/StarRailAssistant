from get_width import get_width
import time
import os
from tool.log import log

def main():
    start = input('请输入起始地图（如果从头开始请输入0）：')
    if "-" in start and "_" in start:
        log.info("脚本将于5秒后运行,请确保你的游戏置顶")
        time.sleep(5)
        get_width()
        from tool.map import map
        map_instance = map()
        log.info("开始运行，请勿移动鼠标和键盘")
        log.info("若脚本运行无反应,请使用管理员权限运行")
        start = '1-1_1' if start == 0 else start
        map_instance.auto_map(start)  # 读取配置
    else:
        log.info("错误编号")
    log.info("脚本已经完成运行")

if __name__ == '__main__':
    main()
