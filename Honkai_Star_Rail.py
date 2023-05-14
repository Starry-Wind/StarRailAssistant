import traceback
try:
    from tools.log import log, webhook_and_log
    import time
    import ctypes
    from pick import pick

    from get_width import get_width
    from tools.config import read_json_file, modify_json_file, init_config_file, CONFIG_FILE_NAME
    from tools.update_file import update_file_main
    from tools.switch_window import switch_window
    from tools.exceptions import Exception
except:
    pass

def main():
    main_start()
    up_data()
    if isadmin() == 1:
        start = input('请输入起始地图（如果从头开始请输入0）：')
        if "-" in start and "_" in start or start == '0':
            log.info("脚本将自动切换至游戏窗口，请保持游戏窗口激活")
            switch_window()
            time.sleep(0.5)
            get_width()
            from tools.map import map
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

def main_start():
    if not read_json_file(CONFIG_FILE_NAME, False).get('start'):
        title = "请选择下载代理地址：（不使用代理选空白选项）"
        options = ['https://ghproxy.com/', 'https://ghproxy.net/', 'hub.fgit.ml', '']
        option, index = pick(options, title, indicator='=>', default_index=0)
        modify_json_file(CONFIG_FILE_NAME, "github_proxy", option)
        title = "请选择代理地址：（不使用代理选空白选项）"
        options = ['https://ghproxy.com/', 'https://ghproxy.net/', 'raw.fgit.ml', 'raw.iqiq.io', '']
        option, index = pick(options, title, indicator='=>', default_index=0)
        modify_json_file(CONFIG_FILE_NAME, "rawgithub_proxy", option)
        title = "你游戏里开启了连续自动战斗吗？："
        options = ['没打开', '打开了', '这是什么']
        option, index = pick(options, title, indicator='=>', default_index=0)
        modify_json_file(CONFIG_FILE_NAME, "auto_battle_persistence", index)
        modify_json_file(CONFIG_FILE_NAME, "start", True)

def up_data():
    if not read_json_file(CONFIG_FILE_NAME, False).get('map_debug'):
        ghproxy = read_json_file(CONFIG_FILE_NAME, False).get('github_proxy', "")
        if "rawgithub_proxy" not in read_json_file(CONFIG_FILE_NAME, False):
            init_config_file(0,0)
            raise Exception(f"未检测到必要更新，强制更新脚本，请重新运行脚本")
    
        rawghproxy = read_json_file(CONFIG_FILE_NAME, False).get('rawgithub_proxy', "")
        # asyncio.run(check_file(ghproxy, "map"))
        # asyncio.run(check_file(ghproxy, "temp"))
        up_data = [
            {
                'url_proxy': ghproxy,
                'raw_proxy': rawghproxy,
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
            {
                'url_proxy': ghproxy,
                'raw_proxy': rawghproxy,
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
                'raw_proxy': rawghproxy,
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
        ]
        for up in up_data:
            update_file_main(**up)

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
