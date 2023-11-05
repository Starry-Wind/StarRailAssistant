'''
Author: AlisaCat
Date: 2023-05-07 21:45:43
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-08-01 21:35:31
Description: wasd移动，x是进战斗，鼠标左键是打障碍物等，不要用鼠标移动视角，用方向键左右来移动视角（脚本运行后方向键左右会映射成鼠标）
            F9停止录制并保存
Copyright (c) 2023 by AlisaCat, All Rights Reserved. 
'''
import builtins
import os
import time
from collections import defaultdict
from datetime import datetime

import cv2 as cv
import numpy as np
import orjson
import pyautogui  # 缩放纠正
import pywinctl as pwc  # 跨平台支持
import win32api
import win32con
from PIL import ImageGrab
from pynput import keyboard, mouse
from pynput.mouse import Controller as mouseController


def timestamped_print(*args, **kwargs):
    currentDT = datetime.now().strftime('%H:%M:%S')
    builtins.print(str(currentDT), *args, **kwargs)


print = timestamped_print

print("3s后开启录制,F9终止保存")
time.sleep(3)
print("start")
# 获取到游戏中心点坐标
cen_mouse_pos = mouseController().position
print("中心点坐标", cen_mouse_pos)
mouse_watch = True

key_list = ['w', 's', 'a', 'd', 'f', 'x']  # 匹配锄大地
# 输出列表
event_list = []
# 不同操作间延迟记录
last_time = time.perf_counter()
# 按键按下的时间字典
# key_down_time = {}
# 创建一个默认值为0的字典
key_down_time = defaultdict(int)

# 控制是否输出调试信息的开关
debug_mode = True

mouse_move_pos_list = []

mouse_val = 200  # 每次视角移动距离

save_name = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

def click(points):
    x, y = points
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)#按下
    time.sleep(0.5)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)#抬起

def normalize_file_path(filename):
    # 尝试在当前目录下读取文件
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, filename)
    if os.path.exists(file_path):
        return file_path
    else:
        # 如果当前目录下没有该文件，则尝试在上一级目录中查找
        parent_dir = os.path.dirname(current_dir)
        file_path = os.path.join(parent_dir, filename)
        if os.path.exists(file_path):
            return file_path
        else:
            # 如果上一级目录中也没有该文件，则返回None
            return None

def read_json_file(filename: str, path=False):
    """
    说明：
        读取文件
    参数：
        :param filename: 文件名称
        :param path: 是否返回路径
    """
    # 找到文件的绝对路径
    file_path = normalize_file_path(filename)
    if file_path:
        with open(file_path, "rb") as f:
            data = orjson.loads(f.read())
            if path:
                return data, file_path
            else:
                return data
    
scaling = read_json_file("config.json")['scaling']

def get_file(path, exclude=[], exclude_file=None, get_path=False) -> list[str]:
    """
    获取文件夹下的文件
    """
    if exclude_file is None:
        exclude_file = []
    file_list = []
    for root, dirs, files in os.walk(path):
        add = True
        for i in exclude:
            if i in root:
                add = False
        if add:
            for file in files:
                add = True
                for ii in exclude_file:
                    if ii in file:
                        add = False
                if add:
                    if get_path:
                        path = root + "/" + file
                        file_list.append(path.replace("//", "/"))
                    else:
                        file_list.append(file)
    return file_list

def show_img(img, scale=1, title='Image'):
    # cv.namedWindow('image', cv.WINDOW_NORMAL)
    h, w = img.shape[:2]
    img = cv.resize( img ,(int(w*scale), int(h*scale))  )
    cv.imshow(title, img)
    cv.waitKey(0)
    cv.destroyAllWindows()  
                
def take_screenshot(points=(0,0,0,0)):
    """
    说明:
        返回RGB图像
    参数:
        :param points: 图像截取范围
    """
    scaling = read_json_file("config.json").get("scaling", 1.0)
    borderless = read_json_file("config.json").get("borderless", False)
    left_border = read_json_file("config.json").get("left_border", 11)
    up_border = read_json_file("config.json").get("up_border", 56)
    window = pwc.getWindowsWithTitle("崩坏：星穹铁道")[0]
    #points = (points[0]*1.5/scaling,points[1]*1.5/scaling,points[2]*1.5/scaling,points[3]*1.5/scaling)
    if borderless:
        left, top, right, bottom = window.left, window.top, window.right, window.bottom
    else:
        left, top, right, bottom = window.left+left_border, window.top+up_border, window.right-left_border, window.bottom-left_border
    picture = ImageGrab.grab((left, top, right, bottom), all_screens=True)
    width, length = picture.size
    if points != (0,0,0,0):
        #points = (points[0], points[1]+5, points[2], points[3]+5) if self.platform == _("PC") else points
        picture = picture.crop((width/100*points[0], length/100*points[1], width/100*points[2], length/100*points[3]))
    screenshot = np.array(picture)
    screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2RGB)
    return (screenshot, left, top, right, bottom, width, length)

def scan_screenshot(prepared:np, screenshot1 = None) -> dict:
    """
    说明：
        比对图片
    参数：
        :param prepared: 比对图片地址
        :param prepared: 被比对图片地址
    """
    if screenshot1:
        screenshot, left, top, right, bottom, width, length = take_screenshot((4,8,10,21))
        screenshot = np.array(screenshot1)
        screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2RGB)
    else:
        screenshot, left, top, right, bottom, width, length = take_screenshot((4,8,10,21))
    result = cv.matchTemplate(screenshot, prepared, cv.TM_CCORR_NORMED)
    length, width, __ = prepared.shape
    length = int(length)
    width = int(width)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    return {
        "screenshot": screenshot,
        "min_val": min_val,
        "max_val": max_val,
        "min_loc": (min_loc[0] + left+(width/2), min_loc[1] + top+(length/2)),
        "max_loc": (max_loc[0] + left+(width/2), max_loc[1] + top+(length/2)),
    }
    
def on_press(key):
    global last_time, key_down_time
    try:
        if key.char in key_list and key.char in key_down_time:
            pass
        elif key.char in key_list:
            save_mouse_move_by_key()
            key_down_time[key.char] = time.perf_counter()
            if debug_mode:
                print("捕捉按键按下:", key.char, time.perf_counter())
    except AttributeError:
        pass


def on_release(key):
    current_time = time.perf_counter()
    global last_time, key_down_time, mouse_move_pos_list, cen_mouse_pos, mouse_watch, save_name
    try:
        if key.char in key_list and key.char in key_down_time:
            event_list.append(
                {'key': key.char, 'time_sleep': key_down_time[key.char] - last_time,
                 'duration': current_time - key_down_time[key.char]})
            last_time = time.perf_counter()
            del key_down_time[key.char]
            if debug_mode:
                print("捕捉:", event_list[-1])
            if key.char == "x":
                if debug_mode:
                    print("捕捉X进入战斗")
                mouse_watch = False
                click(cen_mouse_pos)
                mouse_watch = True
        if key.char == "v":
            if debug_mode:
                print("捕捉v截图")
            win32api.mouse_event(1, 0, 2000)  # 进行视角移动
            screenshot, left, top, right, bottom, width, length = take_screenshot((4,8,10,21))
            cv.imwrite(f"H://Download//Zip//StarRailAssistant//utils//map//{save_name}.png", screenshot)
            win32api.mouse_event(1, 0, -2000)  # 进行视角移动
            print("截图成功")
    except AttributeError:
        pass
    if key == keyboard.Key.left:
        x = mouse_val * -1
        dx = int(x * scaling)
        win32api.mouse_event(1, dx, 0)  # 进行视角移动
        mouse_move_pos_list.append(
            {"mouse_move_dxy": (x, 0), "time_sleep": current_time - last_time})
        last_time = current_time
        if debug_mode:
            print("捕捉M:", "mouse_move_dxy", (x, 0), "MExec:", dx)
    elif key == keyboard.Key.right:
        x = mouse_val  # 200
        dx = int(x * scaling)
        win32api.mouse_event(1, dx, 0)  # 进行视角移动
        mouse_move_pos_list.append(
            {"mouse_move_dxy": (x, 0), "time_sleep": current_time - last_time})
        last_time = current_time
        if debug_mode:
            print("捕捉M:", "mouse_move_dxy", (x, 0), "MExec:", dx)
    if key == keyboard.Key.f9:
        save_mouse_move_by_key()
        save_json()
        if debug_mode:
            print("保存")
        return False
    if  key == keyboard.Key.f8:
        save_mouse_move_by_key()
        save_json()
        if debug_mode:
            print("保存")
        save_name = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    if  key == keyboard.Key.f10:
        fils = get_file("H://Download//Zip//StarRailAssistant//utils//map//",exclude_file=[".json"])
        win32api.mouse_event(1, 0, 2000)  # 进行视角移动
        if debug_mode:
            for file in fils:
                target = cv.imread(f"H://Download//Zip//StarRailAssistant//utils//map//{file}")
                max_val = scan_screenshot(target)['max_val']
                print(max_val)
        win32api.mouse_event(1, 0, -2000)  # 进行视角移动
    if  key == keyboard.Key.f7:
        return False


def on_click(x, y, button, pressed):
    if mouse_watch:
        save_mouse_move_by_key()
        global last_time
        if pressed:
            event_list.append(
                {'key': 'click', 'time_sleep': time.perf_counter() - last_time})
            print("捕捉:", event_list[-1])
    else:
        pass


def save_mouse_move_by_key():
    global mouse_move_pos_list
    if mouse_move_pos_list:
        element = None
        mouse_dx = 0
        mouse_dy = 0
        for element in mouse_move_pos_list:
            mouse_dx += element["mouse_move_dxy"][0]
            mouse_dy += element["mouse_move_dxy"][1]
        event_list.append(
            {"mouse_move_dxy": (mouse_dx, mouse_dy), "time_sleep": element["time_sleep"]})
        print("视角相对距离计算完成:", mouse_dx, mouse_dy, element["time_sleep"])
    mouse_move_pos_list.clear()


def save_json():
    # with open('output.json', 'w') as f:
    #     json.dump(event_list, f, indent=4)
    global save_name
    normal_save_dict = {
        "name": "地图-编号",
        "author": "作者",
        "start": [],
        "map": []
    }
    for element_save in event_list:
        if 'key' in element_save:
            if element_save['key'] == "click":
                normal_save_dict["map"].append({"fighting": 2})
            elif element_save['key'] == "x":
                normal_save_dict["map"].append({"fighting": 1})  # 进战斗
            else:
                normal_save_dict["map"].append(
                    {element_save['key']: element_save['duration']})
        elif 'mouse_move_dxy' in element_save:
            normal_save_dict["map"].append(
                {"mouse_move": element_save['mouse_move_dxy'][0]})
    if not os.path.exists("maps"):
        os.makedirs("maps")
    with open(f'maps//{save_name}.json', 'wb') as f:
        f.write(orjson.dumps(normal_save_dict, option=orjson.OPT_INDENT_2))


#mouse_listener = mouse.Listener(on_click=on_click)  # , on_move=on_move
#mouse_listener.start()

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:  # 创建按键监听线程
    listener.join()  # 等待按键监听线程结束

#mouse_listener.stop()
