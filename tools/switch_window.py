from pyautogui import getWindowsWithTitle
from win32com import client
def switch_window(titles = ['崩坏：星穹铁道', 'Honkai: Star Rail']):
	for title in titles:
		ws = getWindowsWithTitle(title)
		if ws:
			for w in ws:
			# 避免其他窗口也包含崩坏：星穹铁道，比如正好开着github脚本页面
			# print(w.title)
				if w.title == title:
					client.Dispatch("WScript.Shell").SendKeys('%')
					w.activate()
					break
		else:
			print(f'没找到窗口{title}')

if __name__ == '__main__':
	switch_window()
