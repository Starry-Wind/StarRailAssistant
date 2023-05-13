#!/usr/bin/env python3
# Author AlisaCat
# -*- encoding:utf-8 -*-
# Created by AlisaCat at 2023/5/7

# 说明：wasd移动，x是进战斗，鼠标左键是打障碍物等，不要用鼠标移动视角，用方向键左右来移动视角（脚本运行后方向键左右会映射成鼠标）
# F9停止录制并保存

import builtins
import time
from collections import defaultdict
from datetime import datetime

import orjson
import win32api
import win32con
from pynput import keyboard
from pynput import mouse
from pynput.mouse import Controller as mouseController

from config import read_json_file


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
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    time.sleep(0.5)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)


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
    except AttributeError:
        pass
    if key == keyboard.Key.left:
        x = mouse_val * -1
        dx = int(x * 1295 / real_width)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, 0)  # 进行视角移动
        mouse_move_pos_list.append(
            {"mouse_move_dxy": (x, 0), "time_sleep": current_time - last_time})
        last_time = current_time
        if debug_mode:
            print("捕捉M:", "mouse_move_dxy", (x, 0), "MExec:", dx)
    elif key == keyboard.Key.right:
        x = mouse_val  # 200
        dx = int(x * 1295 / real_width)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, 0)  # 进行视角移动
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
