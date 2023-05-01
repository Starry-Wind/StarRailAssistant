from tool.map import map
import time

def main():
    map_instance = map()
    time.sleep(5)
    print("开始运行，请勿移动鼠标和键盘\n若脚本运行无反应，请使用管理员权限运行")
    map_instance.auto_map_1()  #基座舱段
    map_instance.auto_map_3()  #支援舱段
    print("脚本已经完成运行")

if __name__ == '__main__':
    main()