import pyautogui
import ctypes
if hex(ctypes.windll.kernel32.GetSystemDefaultUILanguage()) == "0x804":
	windowname = "崩坏：星穹铁道"
elif hex(ctypes.windll.kernel32.GetSystemDefaultUILanguage()) == "0x404":
	windowname = "崩壞：星穹鐵道"
def switch_window(title = windowname):

	ws = pyautogui.getWindowsWithTitle(title)
	
	if len(ws) >= 1 :
		for w in ws:
			# 避免其他窗口也包含崩坏：星穹铁道，比如正好开着github脚本页面
			# print(w.title)
			if w.title == title:
				w.activate()
				break
	else:
		print(f'没找到窗口{title}')

if __name__ == '__main__':
	switch_window()