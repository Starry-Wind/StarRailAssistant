#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Created by Xe-No at 2023/5/17
# 利用cv识别小地图并返回地图索引与坐标
from cv_tools import *
import cv2 as cv
import time
import sys, os, glob
from tools.switch_window import switch_window

def find_best_match(img, template, scale_range=(190, 290)):
    best_match = None
    max_corr = -1
    
    for scale_percent in range(scale_range[0], scale_range[1]):
        
        width = int(template.shape[1] * scale_percent / 100)
        height = int(template.shape[0] * scale_percent / 100)
        dim = (width, height)
        resized_template = cv.resize(template, dim, interpolation=cv.INTER_AREA)


        res = cv.matchTemplate(img, resized_template, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        print(scale_percent, max_val)
        if max_val > max_corr:
            max_corr = max_val
            best_match = scale_percent
                    
    return best_match

class Tracker():
    """docstring for Tracker"""
    def __init__(self):
        self.map_prefix = './temp/Simulated_Universe/map_raw/'
        self.masked_map_prefix = './temp/Simulated_Universe/map_masked/'
        self.template_prefix = './temp/Simulated_Universe/map_template_sample/'
        self.result_prefix = './temp/Simulated_Universe/map_result/'

        # self.minimap_rect = [47,58,187,187] # 全尺度，只有圆形部分匹配度较差
        self.minimap_rect = [77,88,127,127]
        # 节省时间，只有需要时才调用load_all_masked_maps
        self.masked_maps = None


    def load_all_images(self, prefix, gray=False):
        images = {}
        for file in glob.glob(f'{prefix}*.png'):
            index = os.path.basename(file)
            if gray == True :
                images[index] = cv.cvtColor( cv.imread(file), cv.COLOR_BGR2GRAY)
            else:
                images[index] = cv.imread(file)
        return images

    def load_all_gray_images(self, prefix):
        images = {}
        for file in glob.glob(f'{prefix}*.png'):
            index = os.path.basename(file)
            images[index] = cv.imread(file, cv.IMREAD_GRAYSCALE)
        return images

    def load_all_masked_maps(self):
        images = {}
        for file in glob.glob(f'{self.masked_map_prefix}*.png'):
            index = os.path.basename(file)
            images[index] = cv.cvtColor( cv.imread(file), cv.COLOR_BGR2GRAY)
        self.masked_maps = images
        return images

    def save_all_masked_maps(self):
        maps = self.load_all_images(self.map_prefix)
        # # 路面掩膜
        # map_b = get_mask(map_hsv,np.array([[0,0,30],[360,10,90]]))
        # map_b = cv.medianBlur(map_b, 5)
        # 路沿掩膜
        masked_maps = {}
        for index, map_r in maps.items():
            map_hsv = cv.cvtColor(map_r, cv.COLOR_BGR2HSV)
            map_s = get_mask(map_hsv,np.array([[0,0,180],[360,10,255]]))
            map_s = cv.medianBlur(map_s, 3)
            masked_maps[index] = map_s
            cv.imwrite(self.masked_map_prefix + index, map_s)
        # 保存之后也返回
        return masked_maps

    def get_img(self, prefix=None, img_path=False ):
        if img_path:
            img_r = cv.imread(prefix + img_path)
        else:
            img_r = take_screenshot(self.minimap_rect)
        return img_r

    def get_coord_by_map(self, map_b, img_r, scale=2.09):
        # 固定地图，识别坐标 map_index 图片索引 img 彩色图
        img_hsv = cv.cvtColor(img_r, cv.COLOR_BGR2HSV)
        img_s = get_mask(img_hsv,np.array([[0,0,160],[360,10,255]]))
        img_s = cv.resize(img_s, (0,0), fx = scale, fy = scale) # 小地图到大地图的缩放尺度
        w,h = img_s.shape[:2]
        min_val, max_val, min_loc, max_loc = get_loc(map_b, img_s)

        print(max_val)
        cx = max_loc[0] + w//2
        cy = max_loc[1] + h//2
        pos = [cx,cy]
        return [cx, cy, max_val]

    def find_map(self, img_r=False, scale=2.09):
        if self.masked_maps == None:
            self.load_all_masked_maps()
        max_index = -1
        max_corr = -1
        max_ret = None
        for index, map_b in self.masked_maps.items():
            [cx, cy, corr] = self.get_coord_by_map(self.masked_maps[index],img_r)
            print(f'正在找{index}，相似度{corr}')
            # if corr < 0.5:
            #     continue
            if corr > max_corr:
                max_corr = corr
                max_index = index
                max_ret = [cx, cy, corr]


        return [max_index, max_ret]


tracker = Tracker()

map_b = cv.imread(tracker.masked_map_prefix + '38.png', cv.IMREAD_GRAYSCALE)
imgs = tracker.load_all_images(tracker.template_prefix)

img_r = cv.imread(tracker.template_prefix+'screenshot_1684407906_26.png')
ret = tracker.get_coord_by_map(map_b, img_r)
pos = ret[:2]
# pos = ret[1][:2]
cv.rectangle(map_b, pos, np.add(pos,[3,3]), 255, 2)
show_img(map_b,scale=0.5)

ret = tracker.find_map(img_r)
print(ret)



sys.exit()

for name, img_r in imgs.items():
    # img_r = tracker.get_img(tracker.template_prefix, 'screenshot_1684407939_57.png')
    img_hsv = cv.cvtColor(img_r, cv.COLOR_BGR2HSV)
    img_s = get_mask(img_hsv,np.array([[0,0,160],[360,10,255]]))

    img_s = img_s[30:-30,30:-30]
    img_s = cv.resize(img_s, (0,0), fx = 2.09, fy = 2.09)

    w,h = img_s.shape[:2]
    min_val, max_val, min_loc, max_loc = get_loc(map_b, img_s)

    print(max_val)
    cx = max_loc[0] + w//2
    cy = max_loc[1] + h//2
    pos = [cx,cy]

    # cv.rectangle(map_b, max_loc, np.add(max_loc,[w,h]), 128, 2)
    cv.rectangle(map_b, pos, np.add(pos,[3,3]), 255, 2)

    cv.imwrite(tracker.result_prefix+name, map_b)









