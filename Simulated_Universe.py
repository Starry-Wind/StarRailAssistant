#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Created by Xe-No at 2023/5/16
# 模拟宇宙自动脚本试作，基于群文件demo修改而成，感谢前人贡献

from tools.calculated import *
from tools.switch_window import *
from tools.route_helper import *
from cv_tools import *
import os
import cv2 as cv
import numpy as np
import pyautogui
import time
import win32api
import win32con
import questionary
from universeAuto import Pathfinder

# from pathfinder import PathfinderV1
import keyboard

# World_num = input('请输入数字!!!\n第()世界:')
# buff_num = input('-----选择命途-----\n1:存护 2:记忆 3:虚无 4:丰饶 5:巡猎 6:毁灭 7:欢愉\n请输入数字:')
# print('一定要用拼音输入角色名!!!(绝对不是因为我不会英语)\n' * 3, '举例:布洛妮娅=buluoniya,希儿=xier' * 3,
#       '\n主角是属性+主,如火主即huozhu,物主即wuzhu\n0代表女主,1代表男主')
# print('觉得拼音麻烦可以在 temp\\Simulated_Universe\\role 目录下自行修改对应角色头像文件名')
# 有些buff的图没截取，可以手动截 buff_1.jpg

# 世界序号
World_num = '6'
# 世界难度
difficulty = 1
# 命途序号
buff_num = '5'
# 阵容，填角色对应头像文件名
role_list = ['xier', 'natasha', 'jiepade', 'tingyun']


def match_similar_by_binary(source_img, target_img, threshold, debug=False):
	gray_source = cv.cvtColor(source_img, cv.COLOR_BGR2GRAY)
	gray_target = cv.cvtColor(target_img, cv.COLOR_BGR2GRAY)
	_, binary_source = cv.threshold(gray_source, threshold, 255, cv.THRESH_BINARY)
	_, binary_target = cv.threshold(gray_target, threshold, 255, cv.THRESH_BINARY)

	if debug:
		cv.imshow("result", np.hstack((binary_source,binary_target)))
		cv.waitKey(0)
		cv.destroyAllWindows()

	result = cv.matchTemplate(binary_source, binary_target, cv.TM_CCOEFF_NORMED)
	return cv.minMaxLoc(result)

def wait(t=1.0):
	time.sleep(t)

class SimulatedUniverse:
	def __init__(self, level_index=0, mode=1):
		self.calculated = calculated()
		self.win32api = win32api
		self.win32con = win32con
		self.mapSize = 12
		self.miniMap = [70, 0, 165, 253]
		self.wishV1 = [1500, 30, 240, 60]
		self.select = [35, 21, 120, 80]
		self.battle = [1700, 1030, 200, 50]
		self.event_rect = [45, 15, 45+140, 15+60]
		# self.level_rect = [56, 17, 56+110, 17+24]
		self.level_rect = [120, 15, 40, 25]
		self.scene_rect = [1758, 1033, 115, 39]
		self.object = [1550, 40, 150, 45]
		# 1长战 2？？ 3？？ 4精英 5休整 
		# 6长战 7？？ 8精英 9休整 10战斗
		# 11？？ 12休整 13首领
		self.relax_levels = [5,9,12]
		self.long_levels = [1,6]
		self.elite_levels = [4,8]
		# self.event_levels= [11]
		self.pf = Pathfinder()
		self.level_index = level_index
		self.mode = mode
		self.prefix = './temp/Simulated_Universe/'


	def start_init(self):
		pyautogui.keyDown("F4")
		pyautogui.keyUp("F4")
		wait(1)

		# self.calculated.click_target(
		#     f'{self.prefix}Interastral_Guide.jpg', 0.98)

		self.calculated.click_target(
			f'{self.prefix}transfer.jpg', 0.98)

		# 初始化模拟宇宙界面
		wait(1)
		# for i in range(6):
		# 	pyautogui.click(x=1180, y=220)
		# 	wait(0.4)

		# 点击至对应世界
		# wait(1.5)
		for _ in range(6 - eval(World_num) ):
			pyautogui.click(x=1180, y=220)
			wait(0.4)



	def start(self):
		self.calculated.click_target(
			f'{self.prefix}World_{World_num}.jpg', 0.98)
		
		wait(0.4)
		# 选择难度
		pyautogui.click(x=130, y=55 + 110* difficulty)
		wait(1)
		self.calculated.click_target(
			f'{self.prefix}start_1.jpg', 0.98)

		wait(2)
		for role in role_list:
			self.calculated.click_target(
				f'{self.prefix}role\\{role}.jpg', 0.95)  # 选择角色
			wait(0.1)

		self.calculated.click_target(
			f'{self.prefix}start_2.jpg', 0.98)

		wait(1)
		target = cv.imread(f'{self.prefix}tips.jpg')  # 解决角色等级\数量不足弹窗
		result = self.calculated.scan_screenshot(target)
		if result['max_val'] > 0.95:
			self.calculated.click_target(
				f'{self.prefix}yes.jpg', 0.98)

		wait(2)
		self.calculated.click_target(
			f'{self.prefix}path\\path_{buff_num}.jpg', 0.90)  # 自选命途回响
		wait(1)
		self.calculated.click_target(
			f'{self.prefix}choose_2.jpg', 0.95)

		wait(2)
		target = cv.imread(f'{self.prefix}choose_3.jpg')
		result = self.calculated.scan_screenshot(target)
		if result['max_val'] > 0.9:
			self.calculated.click_target(
				f'{self.prefix}choose_3.jpg', 0.98)
			wait(1)

			target = cv.imread(f'{self.prefix}choose_4.jpg')
			result = self.calculated.scan_screenshot(target)
			if result['max_val'] > 0.9:
				self.calculated.click_target(
					f'{self.prefix}choose_4.jpg', 0.98)
			print("进入地图")
		wait(5)

	def get_all_map_name(self) -> list:
		map_list = []
		map_name = "universe_21_"
		i = 0
		# 把mapName都加入一个list里
		for i in range(self.mapSize):
			map_list.append(map_name + str(i))
			i += 1
		return map_list

	def map_select(self) -> int:
		# 判断地图
		wait(0.5)
		print("Start searching")
		map_list = self.get_all_map_name()
		cur_map = ''
		similarity_score_buffer = 0
		for map in map_list:
			path = './temp/Simulated_Universe/map/' + map + '.jpg'
			image_b = cv.imread(path)
			image_a = pyautogui.screenshot(region=(self.miniMap[0], self.miniMap[1], self.miniMap[2], self.miniMap[3]))
			similarity_score = self.pic_similarity(image_a, image_b, -1)
			print("The similarity of " + map + " is " + str(similarity_score))
			if similarity_score_buffer < similarity_score:
				screenS = image_a
				cur_map = map
				similarity_score_buffer = similarity_score
		print("The current map is " + cur_map)
		return cur_map

	def pic_similarity(self, image_a, image_b, threshold) -> float:

		result = cv.matchTemplate(np.array(image_a), image_b, cv.TM_CCOEFF_NORMED)
		min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
		similarity_score = max_val * 100
		if (threshold == -1):
			return similarity_score
		return threshold >= similarity_score

	def pathfinder(self, map):
		map_data = read_json_file(f"map\\{map}.json")
		map_filename = map
		# 开始寻路
		print("开始寻路")
		for map_index, map in enumerate(map_data['map']):
			print(f"执行map文件:{map_index + 1}/{len(map_data['map'])}", map)
			key = list(map.keys())[0]
			value = map[key]
			if key in ['w', 's', 'a', 'd', 'f']:
				pyautogui.keyDown(key)
				wait(value)
				pyautogui.keyUp(key)
			elif key == "mouse_move":
				self.Mouse_move(value)
			elif key == "fighting":
				if value == 1:  # 进战斗
					self.fighting()
				elif value == 2:  # 障碍物
					self.Click((0, 0))
				else:
					raise Exception(
						f"map数据错误, fighting参数异常:{map_filename}", map)
			else:
				raise Exception(f"map数据错误,未匹配对应操作:{map_filename}", map)


# =================state
	def check_state(self):
		# 频率高的尽量放前面
		if self.wishVerify(90): return '祝福'
		if self.selectVerify(90): return '回响'
		if self.battleVerify(90): return '战斗'
		if self.objVerify(90): return '奇物'
		if self.eventVerify(90): return '事件'
		if self.sceneVerify(90): return '场景'
		# if self.sceneVerify(90): return '祝福确认'
		
		return '未知'

	def state_handler(self, init_state=''):
		print(f'状态处理器已经启动，初始状态为：【{init_state}】')
		unknown = 0
		max = 60
		if init_state == '':
			state = self.check_state
		else:
			state = init_state

		if state == 'start':
			max = 1
		while 1:
			print(f'目前状态{state}')
			if state == '祝福':
				# 丢弃祝福
				if self.verify(f'{self.prefix}wish_drop.jpg', [830,98,262,34], 0.9):
					print('需要丢弃祝福')
					self.click(806, 473) #选中间
					self.calculated.click_target(f'{self.prefix}drop.jpg', 0.9)
					wait()
					self.calculated.click_target(f'{self.prefix}claim_reward_confirm.jpg', 0.9)
					return


				while self.wishVerify(90):
					self.choose_buff()
					wait(1)
			elif state == '回响':
				wait(0.5)
				self.click(806, 473)
				wait(1)
				self.click(952, 960)
				self.click(1703, 963)
				unknown = 0
			elif state == '战斗':
				print('等待战斗结束')
				while self.check_state() in ['战斗','未知']:
					wait(1)
				print('战斗结束')

			elif state == '奇物':
				self.choose_object()
				
				

				# self.calculated.click_target(f'{self.prefix}object_confirm.jpg', 0.70, True)
			elif state == '事件':
				self.handle_event()
				return '事件完成'

			elif state == '场景':
				# 前面的状态都已经完成
				if self.level_index ==0:
					return 

				print('完成本关任务，回到场景，寻找传送门')
				for _ in range(3):
					if move_to_atlas(f'{self.prefix}atlas_portal.jpg'):
						print('正在传送')
						if self.level_type in  ['精英', '首领']:
							wait(3)
							self.calculated.click_target(f'{self.prefix}claim_reward_confirm.jpg', 0.90)
						return
					else:
						pyautogui.keyDown('s')
						wait(1)
						pyautogui.keyUp('s')
						wait(3)

				
				print('没找到传送门，暂时挂起，F8继续')
				self.hang()
				return

			elif (state == '未知') :
				unknown += 1
				if unknown > 10:
					print('尝试一些少见的情况')
					self.find_and_click(f'{self.prefix}object_confirm.jpg', 0.70)
					self.find_and_click(f'{self.prefix}confirm2.jpg', 0.70)
					self.find_and_click(f'{self.prefix}confirm3.jpg', 0.70)
				if unknown > 20:
					state = '失败'

			elif (state == '失败') :
				print('尝试失败，暂时挂起，稍微远离传送门并且按F8以继续')
				while 1:
					if keyboard.is_pressed("F8"):
						return

			
			wait(1.0)
			state = self.check_state()

	def handle_level(self):
		self.level_type = self.check_level()
		print(f'开始执行关卡{self.level_index}-{self.level_type}')
		if self.level_index == 0:
			self.start_init()
			self.start()
			self.state_handler('start')
		elif self.level_type in ['长战','战斗','精英','首领']:
			# move_to_atlas(f'{self.prefix}atlas_elite.jpg', 'A')
			if self.level_type == '长战':
				if self.mode == 1:
					print('长战，直接挂起，进入与看门敌人的战斗后按F8')
					self.hang()
				if self.mode == 2:
					self.handle_long_level()

			else:
				move(2) 
				pyautogui.click(600,600)   
			wait(2)
			if self.sceneVerify(90):
				print('尝试攻击后还在主场景中，进入战斗后按F8')
				self.hang()
				
			print('已经发动攻击，10秒后将控制权移交给状态处理器')
			wait(8)
			self.state_handler('战斗')

		elif self.level_type in ['事件', '遭遇', '交易']:
			move_to_atlas(f'{self.prefix}atlas_event.jpg')
			self.state_handler()

		elif self.level_type == '休整':
			self.run_f(15)
		
		else:
			print('未知关，过到下一个关之后输入F8以同步状态')
			while 1:
				if keyboard.is_pressed("F8"):
					break

		self.level_index += 1
		wait(3)

	def hang(self):
		while 1:
			if keyboard.is_pressed("F8"):
				break


	def handle_event(self):
		# 事件，暂时暴力点几下
		for i in range(30):
			print(f'事件点击循环{i}')
			self.find_and_click(f'{self.prefix}event_selector.jpg', 0.90)
			self.find_and_click(f'{self.prefix}event_selector2.jpg', 0.90)
			self.find_and_click(f'{self.prefix}event_clicker.jpg', 0.90)
			self.find_and_click(f'{self.prefix}event_confirm.jpg', 0.90)     
			if not self.eventVerify(90):
				print('完成事件')
				return 0
			wait(1)

	def verify(self, img_path, rect, threshold):
		im = pyautogui.screenshot(region=rect) #
		image_s = cv2.cvtColor(np.array(im),cv2.COLOR_RGB2BGR)
		# image_s = pyautogui.screenshot(region=(0, 0, 300, 300)) #
		image = cv.imread(img_path)
		min_val, max_val, min_loc, max_loc = match_similar_by_binary(image_s, image, 40)


		print(f'{img_path} : {max_val}')
		if max_val > threshold:
			return 1
		return 0
		   
	def eventVerify(self, threshold):
		path = f'{self.prefix}eventVerify.jpg'
		image_s = pyautogui.screenshot(region=(self.event_rect[0], self.event_rect[1], self.event_rect[2], self.event_rect[3])) #
		# image_s = pyautogui.screenshot(region=(0, 0, 300, 300)) #
		image = cv.imread(path)
		similarity = self.pic_similarity(image_s, image, -1)
		if similarity > threshold:
			return 1
		return 0

	def sceneVerify(self, threshold):
		path = f'{self.prefix}sceneVerify.jpg'
		image_s = pyautogui.screenshot(region=(self.scene_rect[0], self.scene_rect[1], self.scene_rect[2], self.scene_rect[3]))
		image = cv.imread(path)
		similarity = self.pic_similarity(image_s, image, -1)
		print(similarity)
		if similarity > threshold:
			return 1
		return 0

	def battleVerify(self, threshold):
		path = f'{self.prefix}battleVerify.jpg'
		image_s = pyautogui.screenshot(region=(self.battle[0], self.battle[1], self.battle[2], self.battle[3]))
		image = cv.imread(path)
		similarity = self.pic_similarity(image_s, image, -1)
		if similarity > threshold:
			return 1
		return 0

	def objVerify(self, threshold):
		path = f'{self.prefix}objVerify.jpg'
		image_s = pyautogui.screenshot(region=(self.object[0], self.object[1], self.object[2], self.object[3]))
		image = cv.imread(path)
		similarity = self.pic_similarity(image_s, image, -1)
		# print(similarity)
		if similarity > threshold:
			return 1
		return 0

	def selectVerify(self, threshold):
		path = f'{self.prefix}selectVerify.jpg'
		image_s = pyautogui.screenshot(region=(self.select[0], self.select[1], self.select[2], self.select[3]))
		image = cv.imread(path)
		similarity = self.pic_similarity(image_s, image, -1)
		# print(similarity)
		if similarity > threshold:
			return 1
		return 0

	def wishVerify(self, threshold) -> int:
		image_s = pyautogui.screenshot(region=(self.wishV1[0], self.wishV1[1], self.wishV1[2], self.wishV1[3]))
		path_wish = f'{self.prefix}wishVerify1.jpg'
		image = cv.imread(path_wish)
		similarity = self.pic_similarity(image_s, image, -1)
		if similarity > threshold:
			return 1
		return 0

# =============level
	def is_level(self, level_type, threshold=90):
		[x,y,w,h] = [160,860,120,120]
		# rect = [x,y,x+w,y+h]
		rect = [x,y,w,h]
		image_s = pyautogui.screenshot(region=(rect[0], rect[1], rect[2], rect[3]))
		path = f'{self.prefix}level\\level_{level_type}.jpg'
		image = cv.imread(path)
		similarity = self.pic_similarity(image_s, image, -1)
		print(f'{level_type} : {similarity}')
		if similarity > threshold:
			return 1
		return 0

	def is_level2(self, level_type, threshold=90):
		[x,y,w,h] = [120, 15,40,25]
		# rect = [x,y,x+w,y+h]
		img = take_screenshot(rect=[x,y,w,h] )

		img_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
		img_s = get_mask(img_hsv,np.array([[0,0,100],[255,60,255]]))

		path = f'{self.prefix}level\\{level_type}.jpg'
		img2 = cv.imread(path)
		img2_hsv = cv.cvtColor(img2, cv.COLOR_BGR2HSV)
		img2_s = get_mask(img2_hsv,np.array([[0,0,100],[255,60,255]]))


		similarity = self.pic_similarity(img2_s, img_s, -1)
		print(f'{level_type} : {similarity}')
		if similarity > threshold:
			return 1
		return 0


	def check_level(self):
		if self.level_index == 0: return '初始'
		elif self.level_index in self.long_levels: return '长战'
		elif self.level_index in self.relax_levels: return '休整'
		elif self.level_index in self.elite_levels: return '精英'
		elif self.level_index == 13: return '首领'
		else:
			
			if self.is_level2('battle', 80):  return '战斗'  
			elif self.is_level2('event', 80):  return '事件'
			elif self.is_level2('elite', 80):  return '精英'
			elif self.is_level2('encounter', 80):  return '遭遇'
			elif self.is_level2('relax', 80):  return '休整'   
			elif self.is_level2('trade', 80): return '交易'
			# elif self.is_level2('boss', 90):  return '首领'
			
			print('左上ui未识别，按m仔细识别')
			pyautogui.press('m')
			wait(3)
			if self.is_level('battle', 80):  ret = '战斗'  
			elif self.is_level('event', 80):  ret = '事件'
			elif self.is_level('elite', 80):  ret = '精英'
			elif self.is_level('encounter', 80):  ret = '遭遇'
			elif self.is_level('relax', 80):  ret = '休整'   
			elif self.is_level('trade', 80): ret = '交易'
			elif self.is_level('boss', 80):  ret = '首领'			
			else: ret = '未识别'
			pyautogui.press('esc')
			wait(3)


		return ret



	def handle_battle(self):
		print('进入战斗，等待祝福出现')
		while 1:
			if self.wishVerify(95):
				break
		print('进入祝福，等待结束祝福')

		self.choose_buff()

		print('等待场景')
		while 1:
			if self.sceneVerify(90):
				break
		
	def run_f(self, times):
		pyautogui.keyDown('w')
		pyautogui.keyDown('shift')
		for _ in range(times):
			pyautogui.press('f')
			wait(0.2)
		pyautogui.keyUp('w')
		pyautogui.keyUp('shift')

	def click(self, x, y):
		pyautogui.click((x, y))

	def saveImage(self, image):
		image.save(os.path.join(os.path.expanduser('~'), 'Desktop', 'screenshot.jpg'))

	def quit(self):
		cv.destroyAllWindows()
		pyautogui.keyDown("ESC")
		pyautogui.keyUp("ESC")
		wait(1)
		pyautogui.click(1425, 938)
		wait(1)
		pyautogui.click(1164, 670)
		wait(7)
		pyautogui.click(863, 1000)
		print("Round finished")

	def start_simulated(self):
		self.start_init()
		self.start()
		self.state_handler('start')

		cur_map = self.map_select()
		self.pf.guide(cur_map)
		self.state_handler('guiding')
		return 0

	def goto_portal(self):
		ret = move_to_atlas(f'{self.prefix}atlas_portal.jpg')
		if level_index in self.elite_levels:
			wait(2)
			self.calculated.click_target(f'{self.prefix}claim_reward_confirm.jpg', 0.90)    

		print(ret)
		if not ret:
			print('自动过图失败，程序将会等待您手动过图，过图之后按F8重新同步状态')
			self.hang()
				# wait(1)

	


	def handle_long_level(self):
		cur_map = self.map_select()
		self.pf.guide(cur_map)
		# self.state_handler('guiding')
		


	def find_and_click(self, path, threshold):
		# threshold 阈值为0~1
		target = cv.imread(path)
		result = self.calculated.scan_screenshot(target)
		sim = result['max_val']
		x, y = result['max_loc']
		print(f'找图最大相似为{sim},坐标为{[x,y]}')
		if sim > threshold:
			# self.click(x,y)
			print('?')
			win32api.SetCursorPos((x, y))
			win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
			win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
			return True
		return False

	def choose_buff(self):
		# 判断并选择buff,优先图鉴其次命途
		re_num = 1 #刷新次数
		
		while 1:
			wait(2)
			# 选择最好的祝福，
			
			if self.find_and_click(f'{self.prefix}new_buff.jpg', 0.96): 
				print('选择新祝福')
				break
			elif self.find_and_click(f'{self.prefix}buff_{buff_num}.jpg', 0.96): 
				print(f'选择命途{buff_num}祝福')
				break
			elif self.find_and_click(f'{self.prefix}refresh_buff.jpg', 0.96):
				print('刷新一次')
			else:
				print('不能刷新了，选个中间的')
				self.click(900,400) 
				break
		wait(0.3)
		# 确认
		self.calculated.click_target(f'{self.prefix}choose_4.jpg', 0.90)

	def choose_object(self):
		# 奇物
		wait(1)
		self.click(806, 473)
		wait(1.5)
		self.click(1703, 963)
		wait(2.5)
		self.click(1703, 963)
	

	def end(self):
		print('结算完成，确认模拟完成')
		self.calculated.click_target(f'{self.prefix}simulation_end.jpg', 0.90)
		wait(5)

def single_run():
	wait(0.5)
	switch_window()
	wait(0.5)
	while 1:
		su = SimulatedUniverse()
		su.start_init()
		su.start()
		su.state_handler('start')
		su.handle_long_level()
		wait(4)
		su.state_handler('战斗')
		su.quit()
		wait(1)

def semi_run():
	# start_index = 3
	print('阵容难度需要在 Simulated_Universe.py 中手动调整，目前有些判定只对第六宇宙生效')
	start_index = int(input('请输入当前关，不在模拟宇宙里填0：'))
	
	wait(0.5)
	switch_window()
	wait(0.5)

	su = SimulatedUniverse(start_index)
	for i in range(start_index,14):

		su.handle_level()
		wait(0.3)
	su.end()	

def auto_run():
	# start_index = 3
	print('阵容难度需要在 Simulated_Universe.py 中手动调整，目前有些判定只对第六宇宙生效')
	start_index = int(input('请输入当前关，不在模拟宇宙里填0：'))
	
	wait(0.5)
	switch_window()
	wait(0.5)

	su = SimulatedUniverse(start_index)
	for i in range(start_index,14):
		su.handle_level()
		wait(0.3)
	su.end()

if __name__ == '__main__':
	# 9 选项设定todo
	if 0:

		su = SimulatedUniverse(-1)
		wait(0.5)
		switch_window()
		wait(0.5)		
		move_to_atlas(f'{su.prefix}atlas_portal.jpg')
		# su.verify(f'{self.prefix}wish_drop.jpg', [830,98,262,34], 0.9)
		# print(su.battleVerify(70))
		# sys.exit()
		# su.handle_level()
		print(su.check_level())
		# print(su.check_state())
		# su.handle_battle()
		# su.state_handler('')
		
		# print(su.is_level2('relax'))
		# su.choose_object()
		# su.choose_buff()
		# su.handle_long_level()

		# target = cv.imread(f'{self.prefix}buff_5.jpg')
		# result = su.calculated.scan_screenshot(target)
		# print(result)
		# point = result['min_loc']
		# su.click(point[0],point[1])
		sys.exit()

	title = '请选择模式 : '
	options = [ 
		'半自动模式（推荐使用，接管除了第一关和第六关跑图和传送之外的一切，根据提示按F8继续）',
		'自动模式（暂时禁用，软体不稳定，根据提示按F8继续）',
		'单图模式（暂时禁用，打完第一图退出，然后循环）'
	]
	option = questionary.select(title, options).ask()
	index = options.index(option)


	if index == 0:
		semi_run()
	if index == 1:
		auto_run()
	if index == 2:
		single_run()

