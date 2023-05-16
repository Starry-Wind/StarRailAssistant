from .get_angle import get_camera_angle, get_angle
from .switch_window import switch_window
from .calculated import *
import time
import pyautogui
import win32con, win32api
import numpy as np
import sys
import cv2 
# 分辨率1920x1080
# 角度，顺时针为正，东方为0
# 速度，正常情况下，跑动速度为25小地图像素/秒（停稳后），？大地图像素/秒

# ================基础操作
def turn_by(angle):
	print(f'转{angle}度')

	x = (angle / 90.0) * 1500.0
	win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(x), 0, 0, 0)
	time.sleep(0.5)
	

def move(t, run=True):
	print(f'前进{t}秒')
	pyautogui.keyDown("w")
	if run:
		pyautogui.keyDown("shift")
	time.sleep(t)
	pyautogui.keyUp("w")
	if run:
		pyautogui.keyUp("shift")
		time.sleep(0.5)



def get_image_pos(target_path, threshold, flag=True):
    target = cv2.imread(target_path)
    result = calculated.scan_screenshot(target)
    if result["max_val"] > threshold:
        points = calculated.calculated(result, target.shape)
        return points
    return False



# ================组合操作

def turn_to(target_angle, n=1):
	print(f'目标{target_angle}度')
	time.sleep(0.5)
	# n为校准次数，至少为1 
	for _ in range(n):
		current_angle = get_camera_angle() 
		turn_angle = target_angle - current_angle
		turn_angle -= round(turn_angle/360)*360
		turn_by(turn_angle)
		time.sleep(1.0)

def turn_to_precise(target_angle, tolerance=4.0):
	print(f'目标{target_angle}度')
	time.sleep(0.5)
	# n为校准次数，至少为1 
	while 1:
		pyautogui.press('w')
		time.sleep(0.5)
		current_angle = get_angle() 
		turn_angle = target_angle - current_angle
		turn_angle -= round(turn_angle/360)*360
		print(f'{turn_angle} {current_angle}')
		if abs(turn_angle) < tolerance:
			break

		turn_by(turn_angle)
		time.sleep(1.0)



def move_by(dr, v = 25.0):
	# 相对移动
	dx, dy = dr 
	theta = np.arctan2(dy,dx)
	angle = np.rad2deg(theta) 
	r = np.linalg.norm([dx,dy])
	turn_to(angle)
	time.sleep(0.1)
	move(r / v)
	time.sleep(0.1)


def hunt():
	# 巡猎模式，干掉小地图上所有敌人
	pass

def move_to_atlas(atlas_path,  post_action = 'F'):
	# 根据小地图找图获取当前目标的相对位置，并移动到目标附近
	pos = get_image_pos(atlas_path, 0.9)
	if not pos:
		return False
	tx,ty = pos
	print(f'目标坐标{tx} {ty}')
	cx,cy = [141,152]
	rx,ry = [tx-cx, (ty-cy)] # 图像坐标系

	speed = 30.0 # runningFron 在小地图上的移动速度
	distance = np.linalg.norm([rx,ry])

	theta = np.arctan2(ry,rx)
	angle = np.rad2deg(theta) 

	turn_to_precise(angle)
	move( distance/speed)        

	if post_action == 'F':
		pyautogui.press('F')
	if post_action == 'A':
		pyautogui.click(600, 600)

def solve_route(route):
	# 依照路线行动，路线为[x,y, point_type ]的数组
	cx, cy, point_type = route[0]
	for x, y, action in route[1:]:
		dx, dy = [x-cx, y-cy]
		move_by([dx,dy])
		cx, cy = x, y

		if action == 'X':
			hunt()

# class RouteHelper():
# 	"""docstring for RouteHelper"""
# 	def __init__(self, route):
# 		self.route = route
#
# 	def solve_route(self):
# 		



def main():
	# move_to_atlas('..\\temp\\Simulated_Universe\\atlas_portal.jpg')
	# move_to_atlas('..\\temp\\Simulated_Universe\\atlas_elite.jpg', 'A')
	# move_to_atlas('..\\temp\\Simulated_Universe\\atlas_event.jpg')
	# turn_by(90)
	print(get_angle())
	turn_to_precise(135)

	sys.exit()
	turn_to(180,2)
	turn_to(360,2)
	route = [
		[0,0,'S'],
		[-20,0,'N'],
		[-20,-20,'N'],
		[0,-20,'N'],
		[0,0,'N']

	]
	solve_route(route)


# if __name__ == '__main__':
# 	switch_window()
# 	time.sleep(0.5)
# 	main()