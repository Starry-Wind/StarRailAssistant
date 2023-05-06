from tool.map import map
import time


# beta-2.5
# 代码进行了重构
# 第一次运行请先运行get_width.py文件
# 在确保你没有在运行过程中不小心碰撞鼠标产生移动问题，若仍存在视角转动出现偏移问题，请先运行一次get_width.py文件


def main():
    map_instance = map()
    print("如果第一次运行脚本,请先运行一次get_width.py文件")
    print("脚本将于5秒后运行,请确保你的游戏置顶")
    time.sleep(5)
    print("开始运行，请勿移动鼠标和键盘\n若脚本运行无反应,请使用管理员权限运行")
    map_instance.auto_map_1()  # 基座舱段
    map_instance.auto_map_2()  # 收容舱段
    map_instance.auto_map_3()  # 支援舱段
    print("脚本已经完成运行")


if __name__ == '__main__':
    main()
