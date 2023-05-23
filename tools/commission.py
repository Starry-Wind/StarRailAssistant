from tools.calculated import Calculated
from tools.log import log
from tools.switch_window import switch_window as sw
import pyautogui
from time import sleep

class Commission():
    def __init__(self, n=4):
        self.n = n
        self.calculated = Calculated()

    def open(self):
        log.info(f"即将进行自动重新委托，当前重新委托次数为{self.n}")
        pyautogui.press('esc')
        sleep(1)
        self.calculated.click_target('./temp/commission_menu.jpg', 0.98)

    def run(self):
        for i in range(self.n):
            log.info(f"正在进行第{i+1}次重新委托")
            self.calculated.click_target('./temp/red_dot.jpg', 0.98, rect=[300,180,900,100])
            self.calculated.click_target('./temp/red_dot.jpg', 0.98, rect=[350,280,480,600])
            self.calculated.click_target('./temp/commission_reward.jpg', 0.98)
            self.calculated.click_target('./temp/commission_resend.jpg', 0.98)
            time.sleep(5)
    def close(self):
        self.calculated.click_target('./temp/commission_close.jpg', 0.98)
        sleep(1.5)
        pyautogui.press('esc')
        log.info("执行完毕")
