#!/usr/bin/env python3
# Author AlisaCat
# -*- encoding:utf-8 -*-
# Created by AlisaCat at 2023/5/7

# 说明：wasd移动，z是进战斗，鼠标左键是打障碍物等，不要用鼠标移动视角，用方向键左右来移动视角（脚本运行后方向键左右会映射成鼠标）
# F9停止录制并保存

# 优化 输出
import builtins
from datetime import datetime

import win32api
import win32con
from pynput.mouse import Controller as mouseController


def timestamped_print(*args, **kwargs):
    currentDT = datetime.now().strftime('%H:%M:%S')
    builtins.print(str(currentDT), *args, **kwargs)


print = timestamped_print
# 优化 输出 END

import json
import time
from pynput import mouse


from pynput import keyboard

print("3s后开启录制，F9终止保存")
time.sleep(3)
print("start")
# 获取到游戏中心点坐标
cen_mouse_pos = mouseController().position
print("中心点坐标", cen_mouse_pos)
mouse_watch = True
# mouse_move_hold_pos = ()
# mouse_move_hold = False
# 记录的列表
# key_list = ['w', 's', 'a', 'd', 'f', 'm']
key_list = ['w', 's', 'a', 'd', 'f', 'z']  # 匹配锄大地
# 输出列表
event_list = []
# 不同操作间延迟记录
last_time = time.time()
# 按键按下的时间字典
key_down_time = {}

mouse_move_pos_list = []

mouse_val = 200  # 每次视角移动距离
# real_width = None


import os
import json

def read_json_file(filename):
    # 尝试在当前目录下读取文件
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, filename)
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data
    else:
        # 如果当前目录下没有该文件，则尝试在上一级目录中查找
        parent_dir = os.path.dirname(current_dir)
        file_path = os.path.join(parent_dir, filename)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data
        else:
            # 如果上一级目录中也没有该文件，则返回None
            return None

def Click(points):
    x, y = points
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    time.sleep(0.5)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

data = read_json_file('real_width.json')
if data is not None:
    print(data)
else:
    print('未找到文件')

real_width = read_json_file("real_width.json")['real_width']



def on_press(key):
    global last_time, key_down_time, real_width
    try:
        if key.char in key_list and key.char in key_down_time:
            pass
        elif key.char in key_list:
            # save_mouse_move()  # 计算上一次鼠标移动的相对距离
            save_mouse_move_by_key()
            key_down_time[key.char] = time.time()
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
            print("捕捉:", event_list[-1])
            if key.char == "z":
                print("捕捉Z进入战斗")
                mouse_watch = False
                Click(cen_mouse_pos)
                mouse_watch = True
    except AttributeError:
        pass
    if key == keyboard.Key.left:
        x = mouse_val * -1
        dx = int(x * 1295 / real_width)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, 0)  # 进行视角移动
        mouse_move_pos_list.append({"mouse_move_dxy": (x, 0), "time_sleep": current_time - last_time})
        last_time = current_time
        print("捕捉M:", mouse_move_pos_list[-1])
    elif key == keyboard.Key.right:
        x = mouse_val   # 200
        dx = int(x * 1295 / real_width)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, 0)  # 进行视角移动
        mouse_move_pos_list.append({"mouse_move_dxy": (x, 0), "time_sleep": current_time - last_time})
        last_time = current_time
        print("捕捉M:", mouse_move_pos_list[-1])
        print("MExec:", dx)
    if key == keyboard.Key.f9:
        save_mouse_move_by_key()
        save_json()
        print("保存")
        return False


def on_click(x, y, button, pressed):
    if mouse_watch:
        # save_mouse_move()  # 计算上一次鼠标移动的相对距离
        save_mouse_move_by_key()
        global last_time
        if pressed:
            event_list.append({'key': 'click', 'time_sleep': time.time() - last_time})
            print("捕捉:", event_list[-1])
    else:
        pass


# def on_scroll(x, y, dx, dy):
#     global last_time
#     event_list.append({'scroll': [dx, dy], 'time': time.time() - last_time})
#     last_time = time.time()


# def on_move(x, y):
#     global last_time, cen_mouse_pos, mouse_move_hold_pos, mouse_move_hold, mouse_move_pos_list
#     current_time = time.time()
#
#     # # 每0.1秒记录一次鼠标移动的相对距离
#     # if current_time - last_time >= 0.01:
#     #     if x != cen_mouse_pos[0] or y != cen_mouse_pos[1]:
#     #         # 记录鼠标移动的相对距离
#     #         dx = cen_mouse_pos[0] - x
#     #         dy = cen_mouse_pos[1] - y
#     #         mouse_move_pos_list.append({"mouse_move_dxy": (dx, dy), "time_sleep": current_time - last_time})
#     #         # print("捕捉:", event_list[-1])
#     #
#     #     last_time = current_time
#
#     if x != cen_mouse_pos[0] or y != cen_mouse_pos[1]:
#         # 记录鼠标移动的相对距离
#         if not (mouse_move_hold and (x, y) == mouse_move_hold_pos):
#             dx = cen_mouse_pos[0] - x
#             dy = cen_mouse_pos[1] - y
#             mouse_move_hold_pos = (x, y)
#             mouse_move_hold = True
#             mouse_move_pos_list.append({"mouse_move_dxy": (dx, dy), "time_sleep": current_time - last_time})
#             # print("相对距离捕捉:", event_list[-1])
#     elif x == cen_mouse_pos[0] and y == cen_mouse_pos[1]:
#         mouse_move_hold = False
#
#     last_time = current_time


# def save_mouse_move():
#     global mouse_move_pos_list
#     if mouse_move_pos_list:
#         element = None
#         mouse_dx = 0
#         mouse_dy = 0
#         for element in mouse_move_pos_list:
#             mouse_dx += element["mouse_move_dxy"][0]
#             mouse_dy += element["mouse_move_dxy"][1]
#         event_list.append({"mouse_move_dxy": (mouse_dx, mouse_dy), "time_sleep": element["time_sleep"]})
#         print("相对距离计算:", mouse_dx, mouse_dy, element["time_sleep"])
#     mouse_move_pos_list.clear()

def save_mouse_move_by_key():
    global mouse_move_pos_list
    if mouse_move_pos_list:
        element = None
        mouse_dx = 0
        mouse_dy = 0
        for element in mouse_move_pos_list:
            mouse_dx += element["mouse_move_dxy"][0]
            mouse_dy += element["mouse_move_dxy"][1]
        event_list.append({"mouse_move_dxy": (mouse_dx, mouse_dy), "time_sleep": element["time_sleep"]})
        print("视角相对距离计算完成:", mouse_dx, mouse_dy, element["time_sleep"])
    mouse_move_pos_list.clear()


def save_json():
    # with open('output.json', 'w') as f:
    #     json.dump(event_list, f, indent=4)

    normal_save_dict = {"map": []}
    for element_save in event_list:
        if 'key' in element_save:
            if element_save['key'] == "click":
                normal_save_dict["map"].append({"fighting": 2})
            elif element_save['key'] == "z":
                normal_save_dict["map"].append({"fighting": 1})     # 进战斗
            else:
                normal_save_dict["map"].append({element_save['key']: element_save['duration']})
        elif 'mouse_move_dxy' in element_save:
            normal_save_dict["map"].append({"mouse_move": element_save['mouse_move_dxy'][0]})


    with open('output.json', 'w') as f:
        json.dump(normal_save_dict, f, indent=4)


mouse_listener = mouse.Listener(on_click=on_click)  # , on_move=on_move
mouse_listener.start()

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

mouse_listener.stop()
