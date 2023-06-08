from utils.calculated import calculated
from utils.log import log
import pyautogui
import time

def get_percentile(rect, shape):
    #获取长方形的相对坐标
    x1,y1,x2,y2 = rect
    w,h = shape
    return [x1/w*100,y1/h*100,x2/w*100,y2/h*100]

class Commission():
    def __init__(self, n=4):
        self.n = n
        self.calculated = calculated(title="崩坏：星穹铁道", platform="PC")


    def open(self):
        log.info(f"即将进行自动重新委托，当前重新委托次数为{self.n}")
        pyautogui.press('esc')
        time.sleep(1)
        # self.calculated.click_target('./temp/commission_menu.jpg', 0.98)
        self.calculated.ocr_click('委托')

    def run(self):
        for i in range(self.n):
            log.info(f"正在进行第{i+1}次重新委托")
        
            points1 = get_percentile([300,180,300+900,180+100],[1920,1080])
            points2 = get_percentile([350,280,350+480,280+600],[1920,1080])

            self.calculated.take_screenshot()
            self.calculated.click_hsv([0,201,212], points=points1, offset=[-20,20], flag=True, tolerance=3)
            self.calculated.click_hsv([0,201,212], points=points2, offset=[-20,20], flag=True, tolerance=3)

            self.calculated.ocr_click('领取')
            self.calculated.ocr_click('再次派遣')
            time.sleep(5)
    def close(self):
        self.calculated.ocr_click('委托')
        pyautogui.press('esc')
        time.sleep(1.5)
        pyautogui.press('esc')
        log.info("执行完毕")
