import win32gui
import win32print
import win32con
import time
import json


print("3秒后开始获取,请确保你的游戏置顶")
time.sleep(3)
hwnd = win32gui.GetForegroundWindow()  # 根据当前活动窗口获取句柄
print(hwnd)
Text = win32gui.GetWindowText(hwnd)
print(Text)

# 获取活动窗口的大小
window_rect = win32gui.GetWindowRect(hwnd)
width = window_rect[2] - window_rect[0]
height = window_rect[3] - window_rect[1]

# 获取当前显示器的缩放比例
dc = win32gui.GetWindowDC(hwnd)
dpi_x = win32print.GetDeviceCaps(dc, win32con.LOGPIXELSX)
dpi_y = win32print.GetDeviceCaps(dc, win32con.LOGPIXELSY)
win32gui.ReleaseDC(hwnd, dc)
scale_x = dpi_x / 96
scale_y = dpi_y / 96

# 计算出真实分辨率
real_width = int(width * scale_x)
real_height = int(height * scale_y)

print("Real resolution: {} x {}".format(
    real_width, real_height))

print("real_width的值为:{}如有需要请将此值更改到calculated.py 中Mouse_move函数里".format(real_width))

with open('./real_width.json', 'w+', encoding='utf8') as f:
    json.dump({'real_width': real_width}, f, indent=4, ensure_ascii=False)
