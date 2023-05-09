from tool.calculated import *
import cv2 as cv
import pyautogui
import time
import win32api
import win32con

World_num = input('请输入数字!!!\n第()世界:')
buff_num = input('-----选择命途-----\n1:存护 2:记忆 3:虚无 4:丰饶 5:巡猎 6:毁灭 7:欢愉\n请输入数字:')
Num_for_role = input('要使用几名角色(1~4):')
print('一定要用拼音输入角色名!!!(绝对不是因为我不会英语)\n' * 3, '举例:布洛妮娅=buluoniya,希儿=xier' * 3,
      '\n主角是属性+主,如火主即huozhu,物主即wuzhu')
print('觉得拼音麻烦可以在 temp\\Simulated_Universe\\role 目录下自行修改对应角色头像文件名')
role_list = []
for role_num in range(1, eval(Num_for_role) + 1):
    choose_role = input(f'第{role_num}名角色:')
    role_list.append(choose_role)


class SimulatedUniverse:
    def __init__(self):
        self.calculated = calculated()
        self.win32api = win32api
        self.win32con = win32con

    def start_init(self):
        pyautogui.keyDown("ESC")
        pyautogui.keyUp("ESC")
        time.sleep(1)

        self.calculated.click_target(
            'temp\\Simulated_Universe\\Interastral_Guide.jpg', 0.98)

        self.calculated.click_target(
            'temp\\Simulated_Universe\\transfer.jpg', 0.98)

        # 初始化模拟宇宙界面
        time.sleep(1)
        for i in range(6):
            pyautogui.click(x=1180, y=220)
            time.sleep(0.4)

        # 点击至对应世界
        time.sleep(0.5)
        for i in range(eval(World_num) - 1):
            pyautogui.click(x=1180, y=940)
            time.sleep(0.4)

    def start(self):
        self.calculated.click_target(
            f'temp\\Simulated_Universe\\World_{World_num}.jpg', 0.98)

        self.calculated.click_target(
            'temp\\Simulated_Universe\\start_1.jpg', 0.98)

        time.sleep(2)
        self.calculated.click_target(
            'temp\\Simulated_Universe\\choose_role.jpg', 0.98)

        for role in role_list:
            self.calculated.click_target(
                f'temp\\Simulated_Universe\\role\\{role}.jpg', 0.95)  # 选择角色
            time.sleep(1)

        self.calculated.click_target(
            'temp\\Simulated_Universe\\start_2.jpg', 0.98)

        time.sleep(1)
        target = cv.imread('temp\\Simulated_Universe\\tips.jpg')  # 解决角色等级\数量不足弹窗
        result = self.calculated.scan_screenshot(target)
        if result['max_val'] > 0.95:
            self.calculated.click_target(
                'temp\\Simulated_Universe\\yes.jpg', 0.98)
        else:
            pass

        time.sleep(2)
        self.calculated.click_target(
            f'temp\\Simulated_Universe\\buff_{buff_num}.jpg', 0.95)  # 自选命途回响
        time.sleep(1)
        self.calculated.click_target(
            'temp\\Simulated_Universe\\choose_2.jpg', 0.95)

        time.sleep(5)
        target = cv.imread('temp\\Simulated_Universe\\choose_3.jpg')
        result = self.calculated.scan_screenshot(target)
        if result['max_val'] > 0.9:
            self.calculated.click_target(
                'temp\\Simulated_Universe\\choose_3.jpg', 0.98)
            time.sleep(1)

            target = cv.imread('temp\\Simulated_Universe\\choose_4.jpg')
            result = self.calculated.scan_screenshot(target)
            if result['max_val'] > 0.9:
                self.calculated.click_target(
                    'temp\\Simulated_Universe\\choose_4.jpg', 0.98)
            print("进入地图")

        target = cv.imread('temp\\Simulated_Universe\\choose_buff.jpg')
        while True:
            result = self.calculated.scan_screenshot(target)
            if result['max_val'] > 0.95:
                points = self.calculated.calculated(result, target.shape)
                print(points)
                print("完成自动战斗")
                time.sleep(3)
                break

    def choose_buff(self):
        points = self.calculated.click_target(
            'temp\\Simulated_Universe\\refreshbuff.jpg', 0.98)
        if points:
            start_time = time.time()
            while time.time() - start_time < 40:
                points = self.calculated.click_target(
                    'temp\\Simulated_Universe\\refreshbuff.jpg', 0.98)
                time.sleep(1)
                x, y = points
                y = y + 500
                points = x, y
                self.calculated.Click(points)

                self.calculated.click_target(
                    'temp\\Simulated_Universe\\choose_4.jpg', 0.98)
                time.sleep(1)

    def start_simulated(self):
        self.start_init()
        self.start()
