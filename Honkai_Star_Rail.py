try:
    from tool.log import log, webhook_and_log
    import traceback
    import time
    import ctypes
    from pick import pick

    from get_width import get_width
    from tool.config import read_json_file, modify_json_file, CONFIG_FILE_NAME
    from tool.update_file import update_file_main
except:
    pass

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
        up_data = [
            {
                'url_proxy': ghproxy,
                'skip_verify': False,
                'type': "map",
                'version': "map",
                'url_zip': "https://github.com/Starry-Wind/Honkai-Star-Rail/archive/refs/heads/map.zip",
                'unzip_path': "map",
                'keep_folder': [],
                'keep_file': [],
                'zip_path': "Honkai-Star-Rail-map/map",
                'name': "地图"
            },
            {
                'url_proxy': ghproxy,
                'skip_verify': False,
                'type': "temp",
                'version': "map",
                'url_zip': "https://github.com/Starry-Wind/Honkai-Star-Rail/archive/refs/heads/map.zip",
                'unzip_path': "temp",
                'keep_folder': [],
                'keep_file': [],
                'zip_path': "Honkai-Star-Rail-map/temp",
                'name': "图片"
            },
            {
                'url_proxy': ghproxy,
                'skip_verify': False,
                'type': "star",
                'version': "beta-2.7_test",
                'url_zip': "https://github.com/Starry-Wind/Honkai-Star-Rail/archive/refs/heads/beta-2.7_test.zip",
                'unzip_path': ".",
                'keep_folder': ['.git','logs','temp','map','tmp'],
                'keep_file': ['config.json','version.json','Honkai_Star_Rail.py','star_list.json'],
                'zip_path': "Honkai-Star-Rail-beta-2.7_test/",
                'name': "脚本"
            },
        ]
        for up in up_data:
            update_file_main(**up)
    if isadmin() == 1:
        start = input('请输入起始地图（如果要从头开始请回車）：')
        if start.isdigit() == True:
            start = (start)+'-1_1'
        elif "-" in start and "_" not in start:
            start = (start)+'_1'
        elif "-" in start and "_" in start:
            start = start
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
        print(traceback.format_exc())
        print("请输入: pip install -r requirements.txt")
    except NameError as e:
        print(traceback.format_exc())
        print("请输入: pip install -r requirements.txt")
    except:
        log.error(traceback.format_exc())
