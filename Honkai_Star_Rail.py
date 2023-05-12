import time
import ctypes
import traceback
from pick import pick

from get_width import get_width
from tool.log import log, webhook_and_log
from tool.config import read_json_file, modify_json_file, CONFIG_FILE_NAME
from tool.update_file import update_file_main


def main():
    if not read_json_file(CONFIG_FILE_NAME, False).get('start'):
        title = "请选择代理地址："
        options = ['https://github.moeyy.xyz/', 'https://ghproxy.com/', '不使用代理']
        option, index = pick(options, title, indicator='=>', default_index=0)
        modify_json_file(CONFIG_FILE_NAME, "start", True)
        if option == "不使用代理":
            option = ""
        modify_json_file(CONFIG_FILE_NAME, "github_proxy", option)
    if not read_json_file(CONFIG_FILE_NAME, False).get('map_debug'):
        ghproxy = read_json_file(CONFIG_FILE_NAME, False).get('github_proxy')
        # asyncio.run(check_file(ghproxy, "map"))
        # asyncio.run(check_file(ghproxy, "temp"))
        update_file_main(url_proxy=ghproxy)
    if isadmin() == 1:
        start = input('请输入起始地图（如果从头开始请输入0）：')
        if "-" in start and "_" in start or start == '0':
            log.info("脚本将于5秒后运行,请确保你的游戏置顶")
            time.sleep(5)
            get_width()
            from tool.map import map
            map_instance = map()
            log.info("开始运行，请勿移动鼠标和键盘")
            log.info("若脚本运行无反应,请使用管理员权限运行")
            start = '1-1_1' if start == '0' else start
            map_instance.auto_map(start)  # 读取配置
        else:
            log.info("错误编号")
        webhook_and_log("脚本已经完成运行")
    else:
         log.info("请以管理员权限运行")

def isadmin():
	return ctypes.windll.shell32.IsUserAnAdmin()

if __name__ == '__main__':
    try:
        main()
    except:
        log.error(traceback.format_exc())
