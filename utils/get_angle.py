'''
Author: Xe-No
Date: 2023-5-15 19:18:30
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-08-01 20:07:58
Description: 

Copyright (c) 2023 by Xe-No, All Rights Reserved. 
'''
import time

import cv2 as cv
import numpy as np
from PIL import Image, ImageGrab

from .config import _, sra_config_obj
from .cv_tools import CV_Tools, show_img


class Point(CV_Tools):
    def __init__(self, title=_("崩坏：星穹铁道")):
        super().__init__(title)

    def get_furthest_point(self, points):
        # 计算中心点坐标
        center = np.mean(points, axis=0)
        # 初始化最大距离为 0，最远点为第一个点
        max_distance = 0
        furthest_point = points[0]
        # 枚举每个点
        for point in points:
            # 计算该点到中心点的距离
            distance = np.linalg.norm(point - center)
            # 如果该点到中心点的距离大于当前最大距离，则更新最大距离和最远点
            if distance > max_distance:
                max_distance = distance
                furthest_point = point
        return furthest_point

    def get_angle(self):
        
        # x,y = [47,58]
        # w,h = [187,187]
        #time.sleep(0.1)
        x,y = [125,136]
        w,h = [30,30]
        # self.take_screenshot()[0]   [y:y+h, x:x+w]
        img = np.array(self.take_screenshot()[0])[y:y+h, x:x+w]
        #img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        # 定义青色掩膜
        lower_cyan = np.array([78, 180, 180]) # 使用较高饱和度下界，过滤掉摄像头圆弧
        upper_cyan = np.array([99, 255, 255])
        # lower_blue = np.array([100, 50, 50])
        # upper_blue = np.array([130, 255, 255])
        cyan_mask = cv.inRange(hsv, lower_cyan, upper_cyan)
        show_img(cyan_mask, not_close=2000)
        # 查找轮廓
        contours, hierarchy = cv.findContours(cyan_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        # 暴力断定只有一个青色箭头，获取箭头顶点
        print(len(contours))
        if len(contours) != 1:
            return None
        contour = contours[0]
        peri = cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, 0.03 * peri, True)
        fp = self.get_furthest_point(approx[:,0,:])

        # 获取角度
        angle = self.get_angle_between_points((w // 2, h // 2), fp)
		# 画出原图、二值掩膜图以及轮廓图
        return angle
