import pyautogui

def switch_window(title = '崩坏：星穹铁道'):

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