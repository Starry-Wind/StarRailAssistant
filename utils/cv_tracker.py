#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Created by Xe-No at 2023/5/17
# 利用cv识别小地图并返回地图索引与坐标
from .cv_tools import *
from .calculated import calculated
from .log import log
import cv2 as cv
import time
import os, glob


class Tracker():
    """docstring for Tracker"""
    def __init__(self):
        self.map_prefix = './temp/Simulated_Universe/map_raw/'
        self.masked_map_prefix = './temp/Simulated_Universe/map_masked/'
        #self.template_prefix = './temp/Simulated_Universe/map_template_sample/'
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

    def get_minimap_mask(self, img_r, color_range = np.array([[0,0,180],[360,10,255]]) ):
        img_hsv = cv.cvtColor(img_r, cv.COLOR_BGR2HSV)
        img_s = get_mask(img_hsv, color_range)
        return img_s

    def get_coord_by_map(self, map_b, img_r, scale=2.09):
        # 固定地图，识别坐标 map_index 图片索引 img 彩色图
        img_s =self.get_minimap_mask(img_r)
        img_s = cv.resize(img_s, (0,0), fx = scale, fy = scale) # 小地图到大地图的缩放尺度
        w,h = img_s.shape[:2]
        min_val, max_val, min_loc, max_loc = get_loc(map_b, img_s)

        log.debug(max_val)
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
            img_hsv = cv.cvtColor(img_r, cv.COLOR_BGR2HSV)
            img_s = get_mask(img_hsv,np.array([[0,0,160],[360,10,255]]))
            log.debug(f'正在匹配{index}的缩放尺度')
            [scale, corr, loc] = find_best_match(map_b, img_s, (100,200,5))
            # [cx, cy, corr] = self.get_coord_by_map(self.masked_maps[index],img_r)
            log.debug(f'正在找{index}，相似度{corr}')
            # if corr < 0.5:
            #     continue
            if corr > max_corr:
                max_corr = corr
                max_ret = [index, scale, corr, loc]


        return max_ret

    def get_scale_percent(self, map_b, mini_b ):

        # 获取小地图比例尺，一次获取，终生受益

        [scale_percent, max_val, max_loc] = find_best_match(map_b, mini_b)
        # show_img(ret)
        [h, w] = mini_b.shape[:2]
        hf = int(h * scale_percent/100)
        wf = int(w * scale_percent/100)

        cv.rectangle(map_b, max_loc, np.add(max_loc, [wf,hf]), 255, 5   )
        show_img(map_b, 0.25)
        
        return scale_percent, max_loc


def get_rolepos(index, platform="PC", order="127.0.0.1:62001", adb_path="temp\\adb\\adb"):
    """
    说明：
        获取玩家坐标
    参数：
        :param index: 玩家所在地图编号
    返回:
        :return 坐标
    """
    time.sleep(0.5)
    if platform == "PC":
        calculated().switch_window()
        time.sleep(0.5)
    tr = Tracker()
    
    map_bgra = cv.imread(tr.map_prefix + index, cv.IMREAD_UNCHANGED) 
    b, g, r, a = cv.split(map_bgra)
    mask = a>200
    b = b * mask
    # show_img(b, 0.25)
    map_b = cv.threshold(b, 20, 150, cv.THRESH_BINARY)[1]
    mini = take_fine_screenshot([30,50,200,200],platform,order,adb_path)
    pos = calculated().hsv2pos(mini, [97, 255,255])
    #show_img(mini)
    mini = cv.cvtColor(mini, cv.COLOR_BGR2GRAY)
    mini_b = cv.threshold(mini, 20, 150, cv.THRESH_BINARY)[1]
    kernel = np.ones((5, 5), np.uint8)
    mini_b = cv.dilate(mini_b, kernel, iterations=1)


    scale_percent,max_loc = tr.get_scale_percent( map_b, mini_b)

    log.debug(f'地图{index}最佳匹配缩放百分比为{scale_percent}')
    return (max_loc[0]+pos[0], max_loc[1]+pos[1])

'''
index = '57.png'
test_2(index)
'''
