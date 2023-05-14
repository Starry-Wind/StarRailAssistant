from get_width import get_width
import time
import os
import ctypes
import traceback
from tools.log import log, webhook_and_log

def main():
    if isadmin() == 1:
        log.info("脚本将于5秒后运行,请确保你的游戏置顶")
        time.sleep(5)
        get_width()
        from tools.calculated import calculated
        calculat = calculated()
        calculat.Relative_click((96,9))
        webhook_and_log("脚本已经完成运行")
    else:
        log.info("请以管理员权限运行")

def isadmin():
	return ctypes.windll.shell32.IsUserAnAdmin()

def test():
    pass

if __name__ == '__main__':
    try:
        test()
    except:
        log.error(traceback.format_exc())
