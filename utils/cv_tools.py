'''
Author: Night-stars-1
Date: 2023-05-17 21:45:43
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-07-21 19:31:43
Description: 一些cv工具

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
import time
import cv2 as cv
import numpy as np

from .log import log

def show_img(img, scale=1, title='Image'):
    # cv.namedWindow('image', cv.WINDOW_NORMAL)
    h, w = img.shape[:2]
    img = cv.resize( img ,(int(w*scale), int(h*scale))  )
    cv.imshow(title, img)
    cv.waitKey(5000)  # 显示图像并等待1秒
    cv.destroyAllWindows()  

def show_imgs(imgs, title='Image'):
    cv.imshow(title, np.hstack(imgs))
    cv.waitKey(0)
    cv.destroyAllWindows()  

def match_scaled(img, template, scale, mask=False):
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

def find_best_match(img, template, scale_range=(140, 170, 1)):
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
