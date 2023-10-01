'''
Author: Night-stars-1
Date: 2023-05-17 21:45:43
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-07-31 01:38:24
Description: 一些cv工具

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
import time

import cv2 as cv
import numpy as np
import pygetwindow as gw
from PIL import Image, ImageGrab

from .config import _, sra_config_obj
from .log import log


def show_img(img, scale=1, title='Image'):
    # cv.namedWindow('image', cv.WINDOW_NORMAL)
    h, w = img.shape[:2]
    img = cv.resize( img ,(int(w*scale), int(h*scale))  )
    cv.imshow(title, img)
    cv.waitKey(0)  # 显示图像并等待1秒
    cv.destroyAllWindows()  

def show_imgs(imgs, title='Image'):
    cv.imshow(title, np.hstack(imgs))
    cv.waitKey(0)
    cv.destroyAllWindows()  

class CV_Tools:

    def __init__(self, title=_("崩坏：星穹铁道")):
        self.window = gw.getWindowsWithTitle(title)
        if not self.window:
            raise Exception(_("你游戏没开，我真服了"))
        self.window = self.window[0]
        self.hwnd = self.window._hWnd

    def take_screenshot(self,points=(0,0,0,0)):
        """
        说明:
            返回RGB图像
        参数:
            :param points: 图像截取范围
        """
        borderless = sra_config_obj.borderless
        left_border = sra_config_obj.left_border
        up_border = sra_config_obj.up_border
        #points = (points[0]*1.5/scaling,points[1]*1.5/scaling,points[2]*1.5/scaling,points[3]*1.5/scaling)
        if borderless:
            left, top, right, bottom = self.window.left, self.window.top, self.window.right, self.window.bottom
        else:
            left, top, right, bottom = self.window.left+left_border, self.window.top+up_border, self.window.right-left_border, self.window.bottom-left_border
        # log.info(f"{left}, {top}, {right}, {bottom}")
        game_img = ImageGrab.grab((left, top, right, bottom), all_screens=True)
        # game_img.save(f"logs/image/image_grab_{int(time.time())}.png", "PNG")
        game_width, game_length = game_img.size
        if points != (0,0,0,0):
            #points = (points[0], points[1]+5, points[2], points[3]+5)
            game_img = game_img.crop((game_width/100*points[0], game_length/100*points[1], game_width/100*points[2], game_length/100*points[3]))
        screenshot = np.array(game_img)
        screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2RGB)
        return (screenshot, left, top, right, bottom, game_width, game_length)
    
    def match_scaled(self, img, template, scale, mask=False):
        # 返回最大相似度，中心点x、y
        t0 = time.time()
        # finish = cv.imread(".imgs/finish_fighting.jpg")
        # while True:
        #     result = calculated.scan_screenshot(finish,pos=(0,95,100,100))
        #     if result["max_val"] > 0.98:
        #         print("未进入战斗")                       
        #         break

        resized_template = cv.resize(template, (0,0), fx=scale, fy=scale)
        if mask ==False:
            res = cv.matchTemplate(img, resized_template, cv.TM_CCORR_NORMED)
        else:
            res = cv.matchTemplate(img, resized_template, cv.TM_CCORR_NORMED, mask=resized_template)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        h, w = resized_template.shape[:2]
        x, y = max_loc[0] + w/2, max_loc[1] + h/2
        return max_val, (int(x), int(y))

    def find_best_match(self, img, template, scale_range=(140, 170, 1)):
        """
        说明:
            缩放图片并与进行模板匹配
        参数:
            :param img: 图片
            :param img: 匹配的模板
            :param img: 缩放区间以及步长
        返回:
            最佳缩放大小, 最大匹配度, 最近位置, 模板缩放后的长度, 模板缩放后的宽度
        """
        best_match = None
        max_corr = 0
        length = 0
        width = 0
        
        for scale_percent in range(scale_range[0], scale_range[1],scale_range[2]):
            
            # width = int(template.shape[1] * scale_percent / 100)
            # height = int(template.shape[0] * scale_percent / 100)
            # dim = (width, height)
            # resized_template = cv.resize(template, dim, interpolation=cv.INTER_AREA)
            resized_template = cv.resize(template, (0,0), fx=scale_percent/100.0, fy=scale_percent/100.0)

            res = cv.matchTemplate(img, resized_template, cv.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
            log.debug(f'正在匹配 {scale_percent}，相似度{max_loc}')
            if max_val > max_corr:
                length, width, __ = resized_template.shape
                length = int(length)
                width = int(width)
                max_corr = max_val

        return scale_percent, max_corr, max_loc, length, width
