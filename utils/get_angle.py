#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Created by Xe-No at 2023/5/15
# 根据小地图箭头判定人物朝向，若想让摄像头方向与人物朝向一致，先按一次w即可。
# 获取角度可以为后续脚本开发提供帮助，比如自动矫正角度，模拟宇宙寻路等

import cv2 as cv
import numpy as np
import pyautogui
import time
import matplotlib.pyplot as plt

# 计算旋转变换矩阵
def handle_rotate_val(x, y, rotate):
    cos_val = np.cos(np.deg2rad(rotate))
    sin_val = np.sin(np.deg2rad(rotate))
    return np.float32(
        [
            [cos_val, sin_val, x * (1 - cos_val) - y * sin_val],
            [-sin_val, cos_val, x * sin_val + y * (1 - cos_val)],
        ]
    )

# 图像旋转（以任意点为中心旋转）
def image_rotate(src, rotate=0):
    h, w, c = src.shape
    M = handle_rotate_val(w // 2, h // 2, rotate)
    img = cv.warpAffine(src, M, (w, h))
    return img

def get_polar_stats(gray):
    # 将坐标系从图像中心转换到图像左上角
    h, w = gray.shape
    h = np.float64(h)
    w = np.float64(w)
    x, y = np.meshgrid(np.arange(w), np.arange(h))
    x -= w / 2.
    y -= h / 2.

    # 将坐标从笛卡尔坐标系转换为极坐标系
    r, theta = cv.cartToPolar(x, y)

    angle_step = np.pi / 36
    angle_bins = np.arange(-np.pi, np.pi + angle_step, angle_step)
    print(len(theta[gray==255]))

    hist, _ = np.histogram(theta[gray==255], bins=angle_bins)
    # 统计不同角度的像素值 255 的像素数量
    ax = plt.subplot(121,projection='polar')
    ax.plot(angle_bins[1:], hist, linewidth=2.0)
    plt.show()
    return hist
    
def get_orb(img):
    orb = cv.ORB_create()
    # 检测关键点并计算描述子
    keypoints, descriptors = orb.detectAndCompute(img, None)
    img_with_keypoints = cv.drawKeypoints(img, keypoints, None)

    # 显示结果
    # cv.imshow('Original', img)
    cv.imshow('Keypoints', np.hstack((img, img_with_keypoints)))
    cv.waitKey(0)
    cv.destroyAllWindows()

def get_furthest_point(points):
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

def get_mask(img, color_range):
    lower, upper = color_range
    return cv.inRange(img, lower, upper)

def get_img(xy,wh, debug=False, sample_image=False):
    x,y = xy
    w,h = wh
    if sample_image:
        # 任意一张截图即可，最重要的是保留左上部分
        img = cv.imread(sample_image)
    else:
        img = np.array(pyautogui.screenshot())
        img = cv.cvtColor(img, cv.COLOR_RGB2BGR) # pyautogui截取的图为RGB
    return img[y:y+h, x:x+w]

def get_angle(debug=False, sample_image=False):
    
    # x,y = [47,58]
    # w,h = [187,187]
    x,y = [117,128]
    w,h = [47,47]


    img = get_img([x,y], [w,h],debug,sample_image)
    img = img
    img0 = img.copy()
    
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    # 定义青色掩膜，使用较高饱和度下界，过滤掉摄像头圆弧
    cyan_mask = get_mask(hsv, color_range = np.array([
        [90, 200, 200], 
        [100, 255, 255]]))
    # pyautogui.press('w')
    # time.sleep(1)


    # 查找轮廓
    contours, hierarchy = cv.findContours(cyan_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # 暴力断定只有一个青色箭头，获取箭头顶点
    if len(contours) != 1:
        return False
    contour = contours[0]
    peri = cv.arcLength(contour, True)
    approx = cv.approxPolyDP(contour, 0.03 * peri, True)
    fp = get_furthest_point(approx[:,0,:])


    # 获取角度
    fx, fy = fp
    dx = fx - w // 2.0 
    dy = fy - h // 2.0 
    angle = np.degrees(np.arctan2(dy, dx))
    angle = np.around(angle, 2) 

    # print(angle)
    if debug:
        # 画出原图、二值掩膜图以及轮廓图
        cv.polylines(img, [approx], True, (0, 0, 255), thickness=2)
        cv.circle(img, fp, 0, (255,255,255),9)
        cv.imshow("result", np.hstack((img0,hsv,cv.cvtColor(cyan_mask, cv.COLOR_GRAY2RGB),img)))
        cv.waitKey(0)
        cv.destroyAllWindows()

    return angle

def get_angle_2():
    x,y = [117,128]
    w,h = [47,47]
    loc_tp = get_img([x,y], [w,h])
    loc_tp = cv.cvtColor(loc_tp, cv.COLOR_RGB2BGR)

    blue = np.array([234, 191, 4])
    arrow = cv.imread('imgs/loc_arrow.jpg')
    loc_tp[np.sum(np.abs(loc_tp - blue), axis=-1) > 0] = [0, 0, 0]
    mx_acc = 0
    ang = 0
    for i in range(360):
        rt = image_rotate(arrow, i)
        result = cv.matchTemplate(loc_tp, rt, cv.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        if max_val > mx_acc:
            mx_acc = max_val
            mx_loc = (max_loc[0] + 12, max_loc[1] + 12)
            ang = i
    print(max_val)
    return ang

    

def get_camera_angle(debug=False, sample_image=False):
    
    # x,y = [47,58]
    # w,h = [187,187]
    x,y = [107,118]
    w,h = [67,67]

    img = get_img([x,y], [w,h],debug,sample_image)
    img = img

    img0 = img.copy()
    # img = cv.GaussianBlur(img, (5,5), 0)
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    
    
    # 定义青色掩膜，使用较低饱和度上界，过滤掉人物箭头
    cyan_mask = get_mask(hsv, color_range = np.array([
        [78, 30, 30], 
        [99, 150, 150]]))

    # 计算这些像素点的坐标平均值
    rows, cols = np.where(cyan_mask == 255)
    cy, cx = np.mean(rows), np.mean(cols)

    dx = cx - w / 2.0
    dy = cy - h / 2.0 
    angle = np.degrees(np.arctan2(dy, dx))
    angle = np.around(angle, 2)  
    # hist = get_polar_stats(cyan_mask)


    # 输出结果
    # print(hist)

    # print(angle)
    if debug:
        # 画出原图、二值掩膜图以及轮廓图
        # cv.polylines(img, [approx], True, (0, 0, 255), thickness=2)
        cv.circle(img, [int(cx),int(cy)], 0, (255,255,255),9)
        cv.imshow("result", np.hstack((img0,img, hsv,cv.cvtColor(cyan_mask, cv.COLOR_GRAY2RGB),img)))
        cv.waitKey(0)
        cv.destroyAllWindows()

    return angle


def main():
    debug = True
    sample_image = 'sample.png' #False or path
    if not sample_image:
        # switch_window()
        time.sleep(0.5)
    # angle = get_angle(debug,sample_image)

    x,y = [117,128]
    w,h = [47,47]
    img = get_img([x,y], [w,h],debug,sample_image)
    get_orb(img)

    # get_angle(debug,sample_image)
    # print(angle)

# if __name__ == '__main__':
#   main()
