import pyautogui
import win32api
import time
import win32con
# from switch_window import switch_window

class Pathfinder:
    def guide(self, mapName):
        if mapName == "universe_21_0":
            self.universe_21_0()
        elif mapName == "universe_21_1":
            self.universe_21_1()
        elif mapName == "universe_21_2":
            self.universe_21_2()
        elif mapName == "universe_21_3":
            self.universe_21_3()
        elif mapName == "universe_21_4":
            self.universe_21_4()
        elif mapName == "universe_21_5":
            self.universe_21_5()
        elif mapName == "universe_21_6":
            self.universe_21_6()
        elif mapName == "universe_21_7":
            self.universe_21_7()
        elif mapName == "universe_21_8":
            self.universe_21_8()
        elif mapName == "universe_21_9":
            self.universe_21_9()
        elif mapName == "universe_21_11":
            self.universe_21_11()
        return 1

    def universe_21_0(self):
        self.runningFron(3.5)
        self.click()

    def universe_21_1(self):
        self.runningFron(3.2)
        self.turing(85)
        self.runningFron(1)
        self.turing(75)
        self.runningFron(1.0)
        self.click()

    def universe_21_2(self):
        self.turing(5)
        self.runningFron(1)
        self.turing(-6)
        self.runningFron(1)
        self.runningFron(3.6)
        self.turing(90)
        self.runningFron(2.5)
        self.click()

    def universe_21_3(self):
        self.turing(30)
        self.runningFron(1)
        self.turing(-55)
        self.runningFron(1.2)
        self.turing(25)
        self.runningFron(2.4)
        self.turing(-90)
        self.runningFron(1.0)
        self.click()

    def universe_21_4(self):
        self.runningFron(2.8)
        self.click()

    def universe_21_5(self):
        self.runningFron(2.2)
        self.turing(90)
        self.runningFron(4.5)
        self.turing(98)
        self.runningFron(1)
        self.turing(-40)
        self.runningFron(1.2)
        self.click()

    def universe_21_6(self):
        self.runningFron(1.5)
        self.turing(30)
        self.runningFron(1.5)
        self.turing(-30)
        self.runningFron(1.5)
        self.turing(-55)
        self.runningFron(1.2)
        self.turing(10)
        self.runningFron(1.1)
        self.click()

    def universe_21_7(self):
        self.runningFron(3.5)
        self.turing(45)
        self.runningFron(3)
        self.turing(-45)
        self.runningFron(0.3)
        self.click()

    def universe_21_8(self):
        self.turing(30)
        self.runningFron(2.1)
        self.turing(-110)
        self.runningFron(3.5)
        self.turing(-45)
        self.runningFron(2.5)
        self.turing(100)
        self.runningFron(2.0)
        self.turing(-50)
        self.runningFron(2.3)
        self.click()

    def universe_21_9(self):
        self.turing(10)
        self.runningFron(5)
        self.turing(45)
        self.runningFron(1.5)
        self.click()

    def universe_21_11(self):
        self.runningFron(2)
        self.turing(-90)
        self.runningFron(2.8)
        self.turing(-90)
        self.runningFron(5.4)
        self.turing(90)
        self.runningFron(2.4)
        self.click()

    def universe_F1(self):
        self.runningFron(2)
        self.click()




    def runningFron(self, t):
        pyautogui.keyDown("w")
        pyautogui.keyDown("shift")
        time.sleep(t)
        pyautogui.keyUp("w")
        pyautogui.keyUp("shift")

    def turing(self, degree):
        x, y = win32api.GetCursorPos()
        x += 150
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int((degree / 90) * 1500), 0, 0, 0)

    def click(self):
        x, y = win32api.GetCursorPos()
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

# if __name__ == '__main__':
#     switch_window()
#     pf= Pathfinder()
#     time.sleep(0.5)    
#     pf.universe_F1(self)