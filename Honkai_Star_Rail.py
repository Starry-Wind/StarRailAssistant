try:
    from tool.log import log, webhook_and_log
import time
import ctypes
import traceback
from pick import pick

    import traceback
    import time
    import ctypes
    from pick import pick

    from get_width import get_width
    from tool.config import read_json_file, modify_json_file, CONFIG_FILE_NAME
    from tool.update_file import update_file_main
except:
    pass
from get_width import get_width
from tool.log import log, webhook_and_log
from tool.config import read_json_file, modify_json_file, CONFIG_FILE_NAME
from tool.update_file import update_file_main


def main():
    if not read_json_file(CONFIG_FILE_NAME, False).get('start'):
        title = "请选择代理地址："
        options = ['https://github.moeyy.xyz/', 'https://ghproxy.com/', '不使用代理']
        option, index = pick(options, title, indicator='=>', default_index=0)
        if option == "不使用代理":
            option = ""
        modify_json_file(CONFIG_FILE_NAME, "github_proxy", option)
        title = "你游戏里开启了自动战斗吗？："
        options = ['没打开', '打开了', '这是什么']
        option, index = pick(options, title, indicator='=>', default_index=0)
        modify_json_file(CONFIG_FILE_NAME, "auto_battle_persistence", index)
        modify_json_file(CONFIG_FILE_NAME, "start", True)
    if not read_json_file(CONFIG_FILE_NAME, False).get('map_debug'):
        ghproxy = read_json_file(CONFIG_FILE_NAME, False).get('github_proxy')
        # asyncio.run(check_file(ghproxy, "map"))
        # asyncio.run(check_file(ghproxy, "temp"))
        update_file_main(url_proxy=ghproxy)
    if isadmin() == 1:
        start = input('请输入起始地图（如果要从头开始请回車）：')
        if start.isdigit() == True:
            start = (start)+'-1_1'
        elif "-" in start:
            start = (start)+'_1'
        else:
            log.info("错误编号")
            webhook_and_log("脚本已经完成运行")
        log.info("脚本将于5秒后运行,请确保你的游戏置顶")
        time.sleep(5)
        get_width()
        from tool.map import map
        map_instance = map()
        log.info("开始运行，请勿移动鼠标和键盘")
        log.info("若脚本运行无反应,请使用管理员权限运行")
        start = '1-1_1' if start == '' else start
        map_instance.auto_map(start)  # 读取配置
    else:
         log.info("请以管理员权限运行")

def isadmin():
	return ctypes.windll.shell32.IsUserAnAdmin()

if __name__ == '__main__':
    try:
        main()
    except ModuleNotFoundError as e:
        print("请输入: pip install -r requirements.txt")
    except NameError as e:
        print("请输入: pip install -r requirements.txt")
    except:
        log.error(traceback.format_exc())
