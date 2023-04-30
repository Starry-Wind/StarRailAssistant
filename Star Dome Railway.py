import pyautogui
import cv2 as cv
import numpy as np
import time
import win32api,win32con,win32gui

def Click(points):
    x,y = points
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x,y, 0, 0)
    time.sleep(0.5)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x,y, 0, 0)
    
def scan_screenshot(prepared):
    temp = pyautogui.screenshot()
    screenshot = np.array(temp)
    screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2RGB)
    result = cv.matchTemplate(screenshot, prepared, cv.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    return {'screenshot': screenshot, 'min_val': min_val, 'max_val': max_val, 'min_loc': min_loc, 'max_loc': max_loc}


def calculated(result, shape):
    mat_top, mat_left = result['max_loc']
    prepared_height, prepared_width, prepared_channels = shape

    x = int((mat_top + mat_top + prepared_width) / 2)

    y = int((mat_left + mat_left + prepared_height) / 2)

    return x,y
    

def fighting():
    start_time = time.time()
    target = cv.imread('./temp/attack.jpg')
    while True:
        print("识别中")
        result = scan_screenshot(target)
        if result['max_val'] > 0.95:
            points = calculated(result, target.shape)
            print(points)
            Click(points)
            break
        elif time.time() - start_time > 30: # 如果已经识别了30秒还未找到目标图片，则退出循环
            print("识别超时,此处可能无敌人")
            break
    
    time.sleep(3)
    target = cv.imread('./temp/auto.jpg')
    start_time = time.time()
    while True:
        result = scan_screenshot(target)
        if result['max_val'] > 0.95:
            points = calculated(result, target.shape)
            print(points)
            Click(points)
            print("开启自动战斗")
            break
        elif time.time() - start_time > 30:break
    
    start_time = time.time()  #开始计算战斗时间
    target = cv.imread('./temp/finish_fighting.jpg')
    while True:
        result = scan_screenshot(target)
        if result['max_val'] > 0.95:
            points = calculated(result, target.shape)
            print(points)
            print("完成自动战斗")
            break
        elif time.time() - start_time > 180: # 如果已经识别了180秒还未找到目标图片，则退出循环
            print("超时")
            Click(points)
            break

def auto_map_1():

    #选择地图
    pyautogui.keyDown("m")
    pyautogui.keyUp("m")
    time.sleep(1)
    target = cv.imread('./temp/orientation_1.jpg')
    while True:
        result = scan_screenshot(target)
        if result['max_val'] > 0.98:
            points = calculated(result, target.shape)
            print(points)
            Click(points)
            break
    #time.sleep(1)
    target = cv.imread('./temp/orientation_2.jpg')
    while True:
        result = scan_screenshot(target)
        if result['max_val'] > 0.98:
            points = calculated(result, target.shape)
            print(points)
            Click(points)
            time.sleep(1)
            Click(points)
            break
    
    target = cv.imread('./temp/map_1.jpg')
    while True:
        result = scan_screenshot(target)
        if result['max_val'] > 0.98:
            points = calculated(result, target.shape)
            print(points)
            Click(points)
            break

    target = cv.imread('./temp/map_1_point.jpg')
    while True:
        result = scan_screenshot(target)
        if result['max_val'] > 0.98:
            points = calculated(result, target.shape)
            print(points)
            Click(points)
            break
    
    target = cv.imread('./temp/transfer.jpg')
    while True:
        result = scan_screenshot(target)
        if result['max_val'] > 0.98:
            points = calculated(result, target.shape)
            print(points)
            Click(points)
            break
    
    #选择完地图，开始寻路
    print("选择完地图，开始寻路")
    time.sleep(3)
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 4650, 0)
    pyautogui.keyDown("w")
    time.sleep(2)
    pyautogui.keyUp("w")

    #进入路径点一
    fighting()
    print("完成基座舱段刷怪")


def auto_map_3():
    #选择地图
    pyautogui.keyDown("m")
    pyautogui.keyUp("m")
    time.sleep(1)
    target = cv.imread('./temp/orientation_1.jpg')
    while True:
        result = scan_screenshot(target)
        if result['max_val'] > 0.98:
            points = calculated(result, target.shape)
            print(points)
            Click(points)
            break
    #time.sleep(1)
    target = cv.imread('./temp/orientation_2.jpg')
    while True:
        result = scan_screenshot(target)
        if result['max_val'] > 0.98:
            points = calculated(result, target.shape)
            print(points)
            Click(points)
            time.sleep(1)
            Click(points)
            break
    
    target = cv.imread('./temp/map_3.jpg')
    while True:
        result = scan_screenshot(target)
        if result['max_val'] > 0.98:
            points = calculated(result, target.shape)
            print(points)
            Click(points)
            break
    target = cv.imread('./temp/map_3_point_1.jpg')
    while True:
        result = scan_screenshot(target)
        if result['max_val'] > 0.98:
            points = calculated(result, target.shape)
            print(points)
            Click(points)
            break
    target = cv.imread('./temp/map_3_point_2.jpg')
    while True:
        result = scan_screenshot(target)
        if result['max_val'] > 0.98:
            points = calculated(result, target.shape)
            print(points)
            Click(points)
            break

    target = cv.imread('./temp/transfer.jpg')
    while True:
        result = scan_screenshot(target)
        if result['max_val'] > 0.98:
            points = calculated(result, target.shape)
            print(points)
            Click(points)
            break
    
    #开始寻路
    time.sleep(3)
    pyautogui.keyDown("w")
    time.sleep(3.8)
    pyautogui.keyUp("w")

    #已到达第一个检查点
    fighting()

    #继续寻路
    pyautogui.keyDown("w")
    time.sleep(4)
    pyautogui.keyUp("w")
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, -2300, 0)
    pyautogui.keyDown("w")
    time.sleep(3.5)
    pyautogui.keyUp("w")
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 2300, 0)
    pyautogui.keyDown("w")
    time.sleep(1.5)
    pyautogui.keyUp("w")
    
    #已到达第二个检查点
    fighting()

    #继续寻路
    pyautogui.keyDown("m")
    pyautogui.keyUp("m")
    target = cv.imread('./temp/map_3_point_3.jpg')
    while True:
        result = scan_screenshot(target)
        if result['max_val'] > 0.98:
            points = calculated(result, target.shape)
            print(points)
            Click(points)
            break

    target = cv.imread('./temp/transfer.jpg')
    while True:
        result = scan_screenshot(target)
        if result['max_val'] > 0.98:
            points = calculated(result, target.shape)
            print(points)
            Click(points)
            break

    time.sleep(3)

    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, -3800, 0)
    pyautogui.keyDown("w")
    time.sleep(3)
    pyautogui.keyUp("w")
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, -2000, 0)
    pyautogui.keyDown("w")
    time.sleep(0.8)
    pyautogui.keyUp("w")
    pyautogui.keyDown("f")
    pyautogui.keyUp("f")
    time.sleep(1)   #等待传送

    #继续寻路
    pyautogui.keyDown("w")
    time.sleep(0.6)
    pyautogui.keyUp("w")
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 2300, 0)
    pyautogui.keyDown("w")
    time.sleep(5)
    pyautogui.keyUp("w")

    #已到达第三个检查点
    fighting()

    #继续寻路
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 4650, 0)
    pyautogui.keyDown("w")
    time.sleep(11)
    pyautogui.keyUp("w")
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 2300, 0)
    pyautogui.keyDown("w")
    time.sleep(3.5)
    pyautogui.keyUp("w")

    #已到达第四个检查点
    fighting()

    #继续寻路
    pyautogui.keyDown("m")
    pyautogui.keyUp("m")
    target = cv.imread('./temp/map_3_point_4.jpg')
    while True:
        result = scan_screenshot(target)
        if result['max_val'] > 0.98:
            points = calculated(result, target.shape)
            print(points)
            Click(points)
            break

    target = cv.imread('./temp/transfer.jpg')
    while True:
        result = scan_screenshot(target)
        if result['max_val'] > 0.98:
            points = calculated(result, target.shape)
            print(points)
            Click(points)
            break
    
    time.sleep(3)
    pyautogui.keyDown("w")
    time.sleep(5.9)
    pyautogui.keyUp("w")

    #已到达第五个检查点
    fighting()


time.sleep(5)
print("开始运行，请勿移动鼠标和键盘")
auto_map_1()  #基座舱段
auto_map_3()   #支援舱段
print("完成")











#win32api.SetCursorPos((200, 200))


#pyautogui.keyDown("w")
#time.sleep(2)
#pyautogui.keyUp("w")

#win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 4650, 0)
#pyautogui.screenshot().save("./screenshot.png")