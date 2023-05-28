'''
Author: AlisaCat
Date: 2023-05-07 21:45:43
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-05-28 17:03:10
Description: wasd移动，x是进战斗，鼠标左键是打障碍物等，不要用鼠标移动视角，用方向键左右来移动视角（脚本运行后方向键左右会映射成鼠标）
            F9停止录制并保存
Copyright (c) 2023 by AlisaCat, All Rights Reserved. 
'''
import os
import builtins
import time
from collections import defaultdict
from datetime import datetime
import win32gui
import orjson
from PIL import ImageGrab
from pynput import keyboard
from pynput import mouse
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
last_time = time.time()
# 按键按下的时间字典
# key_down_time = {}
# 创建一个默认值为0的字典
key_down_time = defaultdict(int)

# 控制是否输出调试信息的开关
debug_mode = True

mouse_move_pos_list = []

mouse_val = 200  # 每次视角移动距离


def Click(points):
    x, y = points
    mouse.position = (x, y)
    mouse.press(mouse.Button.left)
    time.sleep(0.5)
    mouse.release(mouse.Button.left)

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
    
real_width = read_json_file("config.json")['real_width']


def on_press(key):
    global last_time, key_down_time, real_width
    try:
        if key.char in key_list and key.char in key_down_time:
            pass
        elif key.char in key_list:
            save_mouse_move_by_key()
            key_down_time[key.char] = time.time()
            if debug_mode:
                print("捕捉按键按下:", key.char, time.time())
    except AttributeError:
        pass


def on_release(key):
    global last_time, key_down_time, mouse_move_pos_list, cen_mouse_pos, mouse_watch
    current_time = time.time()
    try:
        if key.char in key_list and key.char in key_down_time:
            event_list.append(
                {'key': key.char, 'time_sleep': key_down_time[key.char] - last_time,
                 'duration': time.time() - key_down_time[key.char]})
            last_time = time.time()
            del key_down_time[key.char]
            if debug_mode:
                print("捕捉:", event_list[-1])
            if key.char == "x":
                if debug_mode:
                    print("捕捉X进入战斗")
                mouse_watch = False
                Click(cen_mouse_pos)
                mouse_watch = True
        if key.char == "v":
            if debug_mode:
                print("捕捉v截图")
            hwnd = win32gui.FindWindow("UnityWndClass", "崩坏：星穹铁道")
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            temp = ImageGrab.grab((left*1.5, top*1.5, right*1.5, bottom*1.5))
            temp.save(f"temp//maps//{int(time.time())}.png")
            print("截图成功")
    except AttributeError:
        pass
    if key == keyboard.Key.left:
        x = mouse_val * -1
        dx = int(x * 1295 / real_width)
        mouseController().move(dx, 0)
        mouse_move_pos_list.append(
            {"mouse_move_dxy": (x, 0), "time_sleep": current_time - last_time})
        last_time = current_time
        if debug_mode:
            print("捕捉M:", "mouse_move_dxy", (x, 0), "MExec:", dx)
    elif key == keyboard.Key.right:
        x = mouse_val  # 200
        dx = int(x * 1295 / real_width)
        mouseController().move(dx, 0)
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


def on_click(x, y, button, pressed):
    if mouse_watch:
        save_mouse_move_by_key()
        global last_time
        if pressed:
            event_list.append(
                {'key': 'click', 'time_sleep': time.time() - last_time})
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

    with open(f'output{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.json', 'wb') as f:
        f.write(orjson.dumps(normal_save_dict, option=orjson.OPT_INDENT_2))


mouse_listener = mouse.Listener(on_click=on_click)  # , on_move=on_move
mouse_listener.start()

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:  # 创建按键监听线程
    listener.join()  # 等待按键监听线程结束

mouse_listener.stop()
