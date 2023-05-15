#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Created by Xe-No at 2023/5/15
# 根据小地图箭头判定人物朝向，若想让摄像头方向与人物朝向一致，先按一次w即可。
# 获取角度可以为后续脚本开发提供帮助，比如自动矫正角度，模拟宇宙寻路等

import cv2
import numpy as np
import pyautogui
# import win32api, win32con
from switch_window import switch_window
import time



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

def get_angle(debug=False, use_sample_image=False):
	
	# x,y = [47,58]
	# w,h = [187,187]
	x,y = [117,128]
	w,h = [47,47]

	if use_sample_image:
		# 任意一张截图即可，最重要的是保留左上部分
		img = cv2.imread('temp/sample.png')[y:y+h, x:x+w]
	else:
		img = np.array(pyautogui.screenshot())[y:y+h, x:x+w] 
		img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) # pyautogui截取的图为RGB
	img0 = img.copy()
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	
	# 定义青色掩膜
	lower_cyan = np.array([78, 200, 200]) # 使用较高饱和度下界，过滤掉摄像头圆弧
	upper_cyan = np.array([99, 255, 255])
	# lower_blue = np.array([100, 50, 50])
	# upper_blue = np.array([130, 255, 255])
	cyan_mask = cv2.inRange(hsv, lower_cyan, upper_cyan)

	# 查找轮廓
	contours, hierarchy = cv2.findContours(cyan_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	# 暴力断定只有一个青色箭头，获取箭头顶点
	if len(contours) != 1:
		return False
	contour = contours[0]
	peri = cv2.arcLength(contour, True)
	approx = cv2.approxPolyDP(contour, 0.03 * peri, True)
	fp = get_furthest_point(approx[:,0,:])


	# 获取角度
	fx, fy = fp
	dx = fx - w // 2
	dy = fy - h // 2
	angle = np.degrees(np.arctan2(dy, dx))
	angle = np.around(angle, 2)	

	print(angle)
	if debug:
		# 画出原图、二值掩膜图以及轮廓图
		cv2.polylines(img, [approx], True, (0, 0, 255), thickness=2)
		cv2.circle(img, fp, 0, (255,255,255),9)
		cv2.imshow("result", np.hstack((img0,hsv,img)))
		cv2.waitKey(0)
		cv2.destroyAllWindows()

	return angle

def main():
	debug = False
	use_sample_image = False
	if not use_sample_image:
		switch_window()
		time.sleep(0.5)
	get_angle(debug,use_sample_image)

if __name__ == '__main__':
	main() 
