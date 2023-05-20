import keyboard
import win32gui
from tools.log import log


def switch_window(class_name='UnityWndClass', title='崩坏：星穹铁道'):
    hwnd = win32gui.FindWindow(class_name, title)
    if not hwnd:
        log.warning("未发现游戏,请完全启动游戏后输入：1")
        keyboard.wait("1")
        switch_window()
    win32gui.SetForegroundWindow(hwnd)


if __name__ == '__main__':
    switch_window()
