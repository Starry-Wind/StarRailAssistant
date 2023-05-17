import pyautogui
from tools.switch_window import switch_window
from tools.get_angle import get_angle
import time 
import cv2 
import numpy as np



def get_mask(img, color_range):
    lower, upper = color_range
    return cv2.inRange(img, lower, upper)



[x,y,w,h] = [47,58,187,187]
level_rect = [x,y,w,h]
center = (w//2, h//2)

def get_camera_fan(color = [130, 130, 60],angle=0, w=187, h=187, delta=90):
    center = (w//2, h//2)
    radius = min(h, w)//2
    fan = np.zeros((h, w, 3), np.uint8)
    # 计算圆心位置
    cx, cy = w // 2, h // 2
    axes = (w // 2, h // 2) 
    
    startAngle, endAngle = angle -45, angle +45 # 画90度

    cv2.ellipse(fan, (cx, cy), axes, 0, startAngle, endAngle, color , -1)
    return fan

def get_gradient_mask(w,h):
    center = [w // 2, h // 2]
    radius = 0.8 *w
    # 创建渐变掩码
    gradient_mask = np.zeros((w, h), dtype=np.uint8)
    for r in range(gradient_mask.shape[0]):
        for c in range(gradient_mask.shape[1]):
            dist = np.sqrt((r-center[1])**2 + (c-center[0])**2)
            value =  max(0, min(1 - 2*dist/radius, 1))
            gradient_mask[r,c] = int(value * 255)
    return gradient_mask

debug = True
switch_window()
time.sleep(0.5)
# 获取当前屏幕的截图
im = pyautogui.screenshot(region=level_rect)

img = np.array(im)
img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

angle = get_angle()
fan = get_camera_fan(angle=angle)
gradient_mask = get_gradient_mask(w,h)
gra_fan = cv2.multiply(fan, cv2.cvtColor(gradient_mask, cv2.COLOR_GRAY2BGR), dtype=cv2.CV_8UC3, scale=1/255)
alpha =0.6

comb = cv2.addWeighted(img, alpha, gra_fan, 1-alpha, 0)
comb2 = cv2.addWeighted(img, 1, gra_fan, -alpha, 0)
# 显示结果

# if 1:
#     cv2.imshow("result", np.hstack( [img, fan, gra_fan, comb, comb2] ))
#     time.sleep(0.5)
#     switch_window('result')
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()



gray = cv2.cvtColor(comb2, cv2.COLOR_BGR2GRAY)


mask = get_mask(gray, [30, 60])
cv2.circle(mask, center, 15, 255,-1)
cv2.circle(mask, center, 80+30, 0,60)




def filter_contours_surround_point(gray, point):
    """过滤掉不包围指定点的轮廓"""
    contours, hierarchy = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # 过滤掉所有不包含指定点的轮廓
    filtered_contours = []
    for i in range(len(contours)):
        if cv2.pointPolygonTest(contours[i], point, False) < 0:
            filtered_contours.append(contours[i])
            
    # 过滤掉所有不包围指定点的轮廓
    surrounded_contours = []
    for i in range(len(filtered_contours)):
        rect = cv2.boundingRect(filtered_contours[i])
        if rect[0] <= point[0] <= rect[0] + rect[2] and \
           rect[1] <= point[1] <= rect[1] + rect[3]:
            surrounded_contours.append(filtered_contours[i])
            
    return surrounded_contours

contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
print(len(contours))
filtered_contours = filter_contours_surround_point(mask, center)
cv2.drawContours(mask, filtered_contours, -1, (0, 0, 255), 3)
cv2.drawContours(mask, contours, -1, (0, 255, 255), 3)

cv2.imshow("result", np.hstack( (gray,mask) ) )
time.sleep(0.5)
switch_window('result')
cv2.waitKey(0)
cv2.destroyAllWindows()

