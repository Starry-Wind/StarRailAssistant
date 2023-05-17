import pyautogui
from switch_window import switch_window
import time 
import cv2
import numpy as np
# [292,865,292+138,865+38]
# [x,y,w,h] = [160,860,120,120]

region = [70, 0, 165, 253]
level_rect = [60, 15, 100, 25]
wish_drop_rect = [830,98,262,34]

switch_window()
time.sleep(0.5)
# 获取当前屏幕的截图
im = pyautogui.screenshot(region=wish_drop_rect)
# im.save('./temp/Simulated_Universe/level_relax.jpg')

img = cv2.cvtColor(np.array(im),cv2.COLOR_RGB2BGR)
img2 = cv2.imread('..\\temp\\Simulated_Universe\\wish_drop.jpg')
# source_img = cv2.imread('source.jpg')
# target_img = cv2.imread('target.jpg')
def match_similar_by_binary(source_img, target_img, threshold, debug=False):
	gray_source = cv2.cvtColor(source_img, cv2.COLOR_BGR2GRAY)
	gray_target = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)
	_, binary_source = cv2.threshold(gray_source, threshold, 255, cv2.THRESH_BINARY)
	_, binary_target = cv2.threshold(gray_target, threshold, 255, cv2.THRESH_BINARY)

	if debug:
		cv2.imshow("result", np.hstack((binary_source,binary_target)))
		cv2.waitKey(0)
		cv2.destroyAllWindows()

	result = cv2.matchTemplate(binary_source, binary_target, cv2.TM_CCOEFF_NORMED)
	return cv2.minMaxLoc(result)

def match_similar_by_color(source_img, target_img, color_lower, color_upper, debug= False):
	"""
	通过指定颜色范围获取两张图片的mask并比较相似度
	Args:
		source_img: 源图片路径
		target_img: 目标图片路径
		color_lower: 颜色下限，类型为元组，例如(0, 100, 100)
		color_upper: 颜色上限，类型为元组，例如(20, 255, 255)
	Returns:
		同minMaxLoc
	"""
	# 在HSV颜色空间中定义颜色范围并提取mask
	hsv_source = cv2.cvtColor(source_img, cv2.COLOR_BGR2HSV)
	hsv_target = cv2.cvtColor(target_img, cv2.COLOR_BGR2HSV)
	mask_source = cv2.inRange(hsv_source, color_lower, color_upper)
	mask_target = cv2.inRange(hsv_target, color_lower, color_upper)
	if debug:
		cv2.imshow("result", np.hstack((mask_source,mask_target)))
		cv2.waitKey(0)
		cv2.destroyAllWindows()
	result = cv2.matchTemplate(mask_source, mask_target, cv2.TM_CCOEFF_NORMED)
	return cv2.minMaxLoc(result)

cv2.imshow("result", np.hstack((img,img2)))
cv2.waitKey(0)
cv2.destroyAllWindows()

ret = match_similar_by_color(img, img2, (0, 0, 50), (360, 80, 100),debug=1)
print(ret)
ret = match_similar_by_binary(img, img2, 40,debug=1)
print(ret)
# cv2.imshow("result", np.hstack((img,img2)))


