from get_width import get_width
import time
import os
import ctypes
import traceback
import pygetwindow as gw
from utils.log import log

def main():

    # 通过窗口标题查找窗口句柄
    window = gw.getWindowsWithTitle('崩坏：星穹铁道')[0]
    print(gw.getWindowsWithTitle('崩坏：星穹铁道'))
    # 获取窗口句柄
    handle = window._hWnd

    print("窗口句柄：", handle)

def isadmin():
	return ctypes.windll.shell32.IsUserAnAdmin()

def test():
    pass

if __name__ == '__main__':
    try:
        main()
    except:
        log.error(traceback.format_exc())
