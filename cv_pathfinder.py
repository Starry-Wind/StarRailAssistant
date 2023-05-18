import pyautogui
from tools.switch_window import switch_window
from tools.get_angle import get_angle
import time 
import cv2 as cv
import numpy as np
from cv_tools import *

# 本脚本生成渐变圆弧遮罩，反向抹除圆弧遮罩

[x,y,w,h] = [47,58,187,187]

level_rect = [x,y,w,h]
center = (w//2, h//2)


debug = True
# switch_window()
# time.sleep(0.5)
# 获取当前屏幕的截图
# im = pyautogui.screenshot(region=level_rect)
# img = np.array(im)
# img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
img = cv.imread('img_r.jpg')

# angle = get_angle()
angle =-12


fan = get_camera_fan(angle=angle)
gradient_mask = get_gradient_mask(w,h)
gra_fan = cv.multiply(fan, cv.cvtColor(gradient_mask, cv.COLOR_GRAY2BGR), dtype=cv.CV_8UC3, scale=1/255)
alpha =0.6

comb = cv.addWeighted(img, alpha, gra_fan, 1-alpha, 0)
comb2 = cv.addWeighted(img, 1, gra_fan, -alpha, 0)

show_imgs([img,comb2])
# sys.exit()
# 显示结果

# if 1:
#     cv.imshow("result", np.hstack( [img, fan, gra_fan, comb, comb2] ))
#     time.sleep(0.5)
#     switch_window('result')
#     cv.waitKey(0)
#     cv.destroyAllWindows()
gray = cv.cvtColor(comb2, cv.COLOR_BGR2GRAY)


mask = get_mask(gray, [30, 60])
cv.circle(mask, center, 15, 255,-1)
cv.circle(mask, center, 80+30, 0,60)

img_hsv = cv.cvtColor(comb2, cv.COLOR_BGR2HSV)
img_b = get_mask(img_hsv,np.array([[0,0,00],[360,1,80]]))

show_imgs([img_b])

# contours, hierarchy = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
# print(len(contours))
# filtered_contours = filter_contours_surround_point(mask, center)
# cv.drawContours(mask, filtered_contours, -1, (0, 0, 255), 3)
# cv.drawContours(mask, contours, -1, (0, 255, 255), 3)
# show_img(np.hstack( (gray,mask) ) )


