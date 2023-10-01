'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-06-08 20:21:02
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-07-03 14:49:58
Description: 

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
import time

from pynput.keyboard import Key

from utils.calculated import calculated
from utils.log import _, log


def get_percentile(rect, shape):
    #获取长方形的相对坐标
    x1,y1,x2,y2 = rect
    w,h = shape
    return [x1/w*100,y1/h*100,x2/w*100,y2/h*100]

class Commission():
    def __init__(self, n:int=4, title = _("崩坏：星穹铁道")):
        self.n = n
        self.calculated = calculated(title)

    def start(self):
        self.open()
        self.run()
        self.close()

    def open(self):
        log.info(_("等待主界面"))
        target = self.calculated.read_img("finish_fighting.jpg")
        while 1:         
            result = self.calculated.scan_screenshot(target,(90,90,100,100))
            if result["max_val"] > 0.95:
                break
            time.sleep(0.3)

        log.info(_("即将进行自动重新委托，当前重新委托次数为{n}").format(n=self.n))
        self.calculated.keyboard.press(Key.esc)
        time.sleep(0.5)
        self.calculated.keyboard.release(Key.esc)
        time.sleep(1)
        self.calculated.ocr_click(_('委托'))

    def run(self):
        for i in range(self.n):
            log.info(_("正在进行第{n}次重新委托").format(n=i+1))
        
            points1 = get_percentile([300,180,300+900,180+100],[1920,1080])
            points2 = get_percentile([350,280,350+480,280+600],[1920,1080])

            self.calculated.take_screenshot()
            result = self.calculated.hsv_click([0,201,212], points=points1, offset=[-20,20], flag=True, tolerance=3)
            if not result:
                log.info("可能没有任务")
                return False
            result = self.calculated.hsv_click([0,201,212], points=points2, offset=[-20,20], flag=True, tolerance=3)
            if not result:
                log.info("可能没有任务")
                return False
            self.calculated.ocr_click(_('领取'), overtime = 100)
            self.calculated.ocr_click(_('再次派遣'), overtime = 100)
            time.sleep(5)
        return True
        
    def close(self):
        self.calculated.ocr_click(_('委托'))
        self.calculated.keyboard.press(Key.esc)
        time.sleep(1.5)
        self.calculated.keyboard.press(Key.esc)
        log.info(_("执行完毕"))
        return True
