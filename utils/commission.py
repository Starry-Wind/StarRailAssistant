from utils.calculated import calculated
from utils.log import log
import pyautogui
import time

def get_percentile(rect, shape):
    #获取长方形的相对坐标
    x1,y1,x2,y2 = rect
    w,h = shape
    return [x1/w,y1/h,x2/w,y2/h]

class Commission():
    def __init__(self, n=4):
        self.n = n
        self.calculated = calculated("PC")


    def open(self):
        log.info(f"即将进行自动重新委托，当前重新委托次数为{self.n}")
        pyautogui.press('esc')
        time.sleep(1)
        self.calculated.click_target('./temp/commission_menu.jpg', 0.98)

    def run(self):
        for i in range(self.n):
            log.info(f"正在进行第{i+1}次重新委托")
        
            points1 = get_percentile([300,180,300+900,180+100],[1920,1080])
            points2 = get_percentile([350,280,350+480,280+600],[1920,1080])

            self.calculated.click_target('./temp/red_dot.jpg', 0.98, points=points1 )
            self.calculated.click_target('./temp/red_dot.jpg', 0.98, points=points2 )
            self.calculated.click_target('./temp/commission_reward.jpg', 0.98)
            self.calculated.click_target('./temp/commission_resend.jpg', 0.98)
            time.sleep(5)
    def close(self):
        self.calculated.click_target('./temp/commission_close.jpg', 0.98)
        time.sleep(1.5)
        pyautogui.press('esc')
        log.info("执行完毕")
