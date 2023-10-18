'''
Author: Night-stars-1
Date: 2023-05-17 21:45:43
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-09-08 21:09:08
Description: 一些cv工具

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
import time

import cv2 as cv
import numpy as np
import pywinctl as pwc  # 跨平台支持
from PIL import Image, ImageGrab

from .config import _, sra_config_obj
from .log import log


def show_img(img, scale=1, title='Image', not_close=False):
    # cv.namedWindow('image', cv.WINDOW_NORMAL)
    #h, w = img.shape[:2]
    #img = cv.resize( img ,(int(w*scale), int(h*scale))  )
    cv.imshow(title, img)
    if not_close == False:
        cv.waitKey(0)  # 显示图像并等待1秒
        cv.destroyAllWindows()
    else:
        cv.waitKey(not_close)

def show_imgs(imgs, title='Image'):
    cv.imshow(title, np.hstack(imgs))
    cv.waitKey(0)
    cv.destroyAllWindows()  

class CV_Tools:
    def __init__(self, title=_("崩坏：星穹铁道")):
        self.cmd = pwc.getActiveWindow()
        self.window = pwc.getWindowsWithTitle(title)
        if not self.window:
            raise Exception(_("你游戏没开，我真服了"))
        self.window = self.window[0]
        # self.window.activate() # 将游戏调至前台
        self.hwnd = self.window._hWnd

    def take_screenshot(self,points=(0,0,0,0),sleep = 3):
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
        try:
            game_img = ImageGrab.grab((left, top, right, bottom), all_screens=True)
            # game_img.save(f"logs/image/image_grab_{int(time.time())}.png", "PNG")
            game_width, game_length = game_img.size
            if points != (0,0,0,0):
                #points = (points[0], points[1]+5, points[2], points[3]+5)
                game_img = game_img.crop((game_width/100*points[0], game_length/100*points[1], game_width/100*points[2], game_length/100*points[3]))
            screenshot = np.array(game_img)
            screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2RGB)
            return (screenshot, left, top, right, bottom, game_width, game_length)
        except OSError as e:
            log.error("截图失败，是不是游戏最小化了？")
            time.sleep(sleep)
            return self.take_screenshot(points,sleep = min(sleep*2,600))

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

    def mask_by_saturation(self, image):
        # 将图像转换为灰度图
        gray_image = cv.cvtColor(image, cv.IMREAD_COLOR)
        gray_image = cv.cvtColor(gray_image, cv.COLOR_BGR2GRAY)
        # 使用HoughCircles检测圆形
        circles = cv.HoughCircles(gray_image, cv.HOUGH_GRADIENT, dp=1, minDist=50, param1=50, param2=30, minRadius=90, maxRadius=110)
        # 如果找到了圆形
        if circles is not None and len(circles) == 1:
            circles = np.uint16(np.around(circles))
            circle = circles[0, :][0]
            center = (circle[0], circle[1])
            radius = circle[2] - 5
            # 在原始图像上绘制圆
            height, width = image.shape[:2]
            # 创建一个空白的黑色掩码
            mask2 = np.zeros((height, width), dtype=np.uint8)
            cv.circle(mask2, center, radius, 255, -1)
            image = cv.bitwise_and(image, image, mask=mask2)
        # 将图像转换为HSV色彩空间
        hsv_image = cv.cvtColor(image,cv.COLOR_BGR2HSV)
        #show_img(hsv_image)
        # 获取饱和度通道
        hue_channel = hsv_image[:, :, 0]
        image_hue_channel = image[:, :, 0]
        saturation_channel = hsv_image[:, :, 1]
        value_channel = hsv_image[:, :, 2]
        # 创建一个全透明的遮罩图像
        mask = np.zeros_like(saturation_channel)
        # 根据饱和度进行遮罩
        mask[(saturation_channel < 25) & (image_hue_channel != 0)] = 255
        #mask[(saturation_channel < 200) & (value_channel < 200) & ((hue_channel < 95) | (hue_channel > 105)) & (image_hue_channel != 0)] = 255
        #mask[((hue_channel > 120) | (hue_channel < 100)) & (saturation_channel < 25) & (value_channel < 110) | ((saturation_channel <= 60) & (value_channel < 90)) | ((saturation_channel > 60) & (value_channel > 100) & (value_channel < 125))] = 255
        return mask

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
        global pos
        max_corr = 0
        length = 0
        width = 0
        max_scale_percent = 0
        # range(scale_range[0], scale_range[1],scale_range[2])
        for scale_percent in scale_range:
            resized_template = cv.resize(template, (0,0), fx=scale_percent/100.0, fy=scale_percent/100.0)
            mask = self.mask_by_saturation(resized_template)
            res = cv.matchTemplate(img, resized_template, cv.TM_CCOEFF_NORMED, mask=mask)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
            #log.info(f'正在匹配 {scale_percent}，相似度{max_val}')
            if max_val > max_corr:
                max_scale_percent = scale_percent
                length, width, __ = resized_template.shape
                max_corr = max_val
                #if max_val > 0.95:
                #    break
                
        return max_scale_percent, max_corr, max_loc, length, width

    def get_angle_between_points(self, point1, point2):
        x1, y1 = point1
        x2, y2 = point2

        dx = x2 - x1
        dy = y2 - y1

        angle_radians = np.arctan2(dy, dx)
        angle_degrees = np.degrees(angle_radians)
        angle = np.around(angle_degrees, 2)	

        return angle
    