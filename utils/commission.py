'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-06-08 20:21:02
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-06-16 21:00:23
Description: 

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
from utils.calculated import calculated
from utils.log import log, _
from pynput.keyboard import Key
import time

def get_percentile(rect, shape):
    #获取长方形的相对坐标
    x1,y1,x2,y2 = rect
    w,h = shape
    return [x1/w*100,y1/h*100,x2/w*100,y2/h*100]

class Commission():
    def __init__(self, n:int=4, title = _("崩坏：星穹铁道"), platform=_("PC"),order="127.0.0.1:62001",adb_path="temp\\adb\\adb"):
        self.n = n
        self.calculated = calculated(title, platform,order,adb_path)

    def start(self):
        self.open()
        self.run()
        self.close()

    def open(self):
        log.info(_("即将进行自动重新委托，当前重新委托次数为{n}").format(n=self.n))
        self.calculated.keyboard.press(Key.esc)
        time.sleep(0.5)
        self.calculated.keyboard.release(Key.esc)
        time.sleep(1)
        # self.calculated.click_target('./temp/commission_menu.jpg', 0.98)
        self.calculated.ocr_click(_('委托'))

    def run(self):
        for i in range(self.n):
            log.info(_("正在进行第{n}次重新委托").format(n=i+1))
        
            points1 = get_percentile([300,180,300+900,180+100],[1920,1080])
            points2 = get_percentile([350,280,350+480,280+600],[1920,1080])

            self.calculated.take_screenshot()
            self.calculated.click_hsv([0,201,212], points=points1, offset=[-20,20], flag=True, tolerance=3)
            self.calculated.click_hsv([0,201,212], points=points2, offset=[-20,20], flag=True, tolerance=3)

            self.calculated.ocr_click(_('领取'))
            self.calculated.ocr_click(_('再次派遣'))
            time.sleep(5)
    def close(self):
        self.calculated.ocr_click(_('委托'))
        self.calculated.keyboard.press(Key.esc)
        time.sleep(1.5)
        self.calculated.keyboard.press(Key.esc)
        log.info(_("执行完毕"))
