import os
import traceback
try:
    from utils.log import log, get_message
    import time
    import pyuac
    import asyncio
    import questionary
    import tqdm

    from httpx import ReadTimeout, ConnectError, ConnectTimeout

    from get_width import get_width
    from utils.config import read_json_file, modify_json_file, init_config_file, CONFIG_FILE_NAME
    from utils.simulated_universe import Simulated_Universe
    from utils.update_file import update_file_main
    from utils.calculated import calculated
    from utils.exceptions import Exception
    from utils.requests import webhook_and_log
    from utils.map import Map as map_word
    from utils.requests import *
    from utils.adb import ADB
except:
    print(traceback.format_exc())


def choose_map(map_instance: map_word, type = 0, platform = "PC"):
    if type == 0:
        title_ = "请选择起始星球："
        options_map = {"空间站「黑塔」": "1", "雅利洛-VI": "2", "仙舟「罗浮」": "3"}
        option_ = questionary.select(title_, list(options_map.keys())).ask()
        main_map = options_map.get(option_)
        title_ = "请选择起始地图："
        options_map = map_instance.map_list_map.get(main_map)
        if not options_map:
            return None, "你没下载地图，拿什么选？"
        keys = list(options_map.keys())
        values = list(options_map.values())
        option_ = questionary.select(title_, values).ask()
        side_map = keys[values.index(option_)]
        return f"{main_map}-{side_map}", None
    else:
        title_ = "请选择第几宇宙："
        options_map = ["选择宇宙", "设置预设"]
        option = questionary.select(title_, options_map).ask()
        if option == "选择宇宙":
            title_ = "请选择第几宇宙："
            options_map = {"第一世界": 1, "第二世界": 2, "第三世界": 3, "第四世界": 4, "第五世界": 5, "第六世界": 6}
            option_ = questionary.select(title_, list(options_map.keys())).ask()
            side_map = options_map[option_]
            presets_list = read_json_file(CONFIG_FILE_NAME).get("presets", [])
            presets_list = ['、'.join(i) for i in presets_list]
            choose_role = questionary.select("要使用的预设队伍:", choices=presets_list).ask()
            role_list = choose_role.split("、")
            fate = ['存护', '记忆', '虚无', '丰饶', '巡猎', '毁灭', '欢愉']
            choose_fate = questionary.select("要使用的预设队伍:", choices=fate).ask()
            choose_list = [role_list, choose_fate]
            return side_map, choose_list
        else:
            Simulated_Universe(platform).choose_presets(option)
            return None, None


def main(type=0,platform="PC",start=None,role_list=None):
    main_start()
    order = read_json_file(CONFIG_FILE_NAME, False).get('adb', "")
    adb_path = read_json_file(CONFIG_FILE_NAME, False).get('adb_path', "temp\\adb\\adb")
    map_instance = map_word(platform, order, adb_path)
    simulated_universe =Simulated_Universe(platform, order, adb_path)
    start, role_list = choose_map(map_instance, type, platform)
    if start:
        if platform == "PC":
            log.info("脚本将自动切换至游戏窗口，请保持游戏窗口激活")
            calculated("PC").switch_window()
            time.sleep(0.5)
            get_width()
            import pyautogui # 缩放纠正
            log.info("开始运行，请勿移动鼠标和键盘")
            log.info("若脚本运行无反应,请使用管理员权限运行")
        elif platform == "模拟器":
            ADB(order).connect()
        if type == 0:
            map_instance.auto_map(start)  # 读取配置
        elif type == 1:
            simulated_universe.auto_map(start, role_list)  # 读取配置
    else:
        raise Exception(role_list)


def main_start(start = True):
    if not read_json_file(CONFIG_FILE_NAME, False).get('start') or not start:
        title = "请选择下载代理地址：（不使用代理选空白选项）"
        options = ['https://ghproxy.com/', 'https://ghproxy.net/', 'hub.fgit.ml', '']
        url_ms = []
        pbar = tqdm.tqdm(total=len(options), desc='测速中', unit_scale=True, unit_divisor=1024, colour="green")
        for index,url in enumerate(options):
            if url == "":
                url = "https://github.com"
            elif "https://" not in url:
                url =  f"https://"+url
            try:
                response = asyncio.run(get(url))
                ms = response.elapsed.total_seconds()
            except (ReadTimeout, ConnectError, ConnectTimeout):
                ms = 999
            finally:
                pbar.update(1)
            url_ms.append(options[index]+f" {ms}ms")
        url_ms = [i.replace(" "," "*(len(max(url_ms, key=len))-len(i))) if len(i) < len(max(url_ms, key=len)) else i for i in url_ms]
        option = options[url_ms.index(questionary.select(title, url_ms).ask())]
        modify_json_file(CONFIG_FILE_NAME, "github_proxy", option)
        title = "请选择代理地址：（不使用代理选空白选项）"
        options = ['https://ghproxy.com/', 'https://ghproxy.net/', 'raw.fgit.ml', 'raw.iqiq.io', '']
        url_ms = []
        pbar = tqdm.tqdm(total=len(options), desc='测速中', unit_scale=True, unit_divisor=1024, colour="green")
        for index,url in enumerate(options):
            if url == "":
                url = "https://github.com"
            elif "https://" not in url:
                url =  f"https://"+url
            try:
                response = asyncio.run(get(url))
                ms = response.elapsed.total_seconds()
            except (ReadTimeout, ConnectError, ConnectTimeout):
                ms = 999
            finally:
                pbar.update(1)
            url_ms.append(options[index]+f" {ms}ms")
        url_ms = [i.replace(" "," "*(len(max(url_ms, key=len))-len(i))) if len(i) < len(max(url_ms, key=len)) else i for i in url_ms]
        option = options[url_ms.index(questionary.select(title, url_ms).ask())]
        modify_json_file(CONFIG_FILE_NAME, "rawgithub_proxy", option)
        title = "你游戏里开启了连续自动战斗吗？："
        options = ['没打开', '打开了', '这是什么']
        option = questionary.select(title, options).ask()
        modify_json_file(CONFIG_FILE_NAME, "auto_battle_persistence", options.index(option))
        title = "请选择模拟器的运行平台"
        options = {
            "逍遥游": "127.0.0.1:21503",
            "夜神模拟器": "127.0.0.1:62001",
            "海马玩模拟器": "127.0.0.1:26944",
            "天天模拟器": "127.0.0.1:6555",
            "雷电安卓模拟器": "127.0.0.1:5555",
            "安卓模拟器大师": "127.0.0.1:54001",
            "网易mumu模拟器": "127.0.0.1:7555",
            "BlueStacks": "127.0.0.1:5555",
            "天天安卓模拟器": "127.0.0.1:5037",
        }
        option = questionary.select(title, options).ask()
        modify_json_file(CONFIG_FILE_NAME, "adb", options[option])
        modify_json_file(CONFIG_FILE_NAME, "start", True)


def up_data():
    main_start()    # 无config直接更新时初始化config文件
    ghproxy = read_json_file(CONFIG_FILE_NAME, False).get('github_proxy', "")
    if "adb" not in read_json_file(CONFIG_FILE_NAME, False):
        init_config_file(1920, 1080)
        raise Exception("未检测到必要更新，强制更新脚本，请重新运行脚本")

    rawghproxy = read_json_file(CONFIG_FILE_NAME, False).get('rawgithub_proxy', "")
    # asyncio.run(check_file(ghproxy, "map"))
    # asyncio.run(check_file(ghproxy, "temp"))
    up_data = {
        "脚本":{
            'url_proxy': ghproxy,
            'raw_proxy': rawghproxy,
            'skip_verify': False,
            'type': "star",
            'version': "main",
            'url_zip': "https://github.com/Starry-Wind/StarRailAssistant/archive/refs/heads/main.zip",
            'unzip_path': ".",
            'keep_folder': ['.git', 'logs', 'temp', 'map', 'tmp', 'venv'],
            'keep_file': ['config.json', 'version.json', 'star_list.json', 'README_CHT.md', 'README.md'],
            'zip_path': "StarRailAssistant-main/",
            'name': "脚本"
        },
        "地图":{
            'url_proxy': ghproxy,
            'raw_proxy': rawghproxy,
            'skip_verify': False,
            'type': "map",
            'version': "map",
            'url_zip': "https://raw.githubusercontent.com/Starry-Wind/StarRailAssistant/map/map.zip",
            'unzip_path': "map",
            'keep_folder': [],
            'keep_file': [],
            'zip_path': "map/",
            'name': "地图"
        },
        "图片":{
            'url_proxy': ghproxy,
            'raw_proxy': rawghproxy,
            'skip_verify': False,
            'type': "temp",
            'version': "map",
            'url_zip': "https://raw.githubusercontent.com/Starry-Wind/StarRailAssistant/map/temp.zip",
            'unzip_path': "temp",
            'keep_folder': [],
            'keep_file': [],
            'zip_path': "map/",
            'name': "图片"
        },
    }
    title = "请选择更新项目"
    options = list(up_data.keys())+["全部更新"]
    option = questionary.select(title, options).ask()
    if option != "全部更新":
        update_file_main(**up_data[option])
    else:
        for up_data in list(up_data.values()):
            update_file_main(**up_data)


if __name__ == "__main__":
    try:
        if not pyuac.isUserAdmin():
            pyuac.runAsAdmin()
        else:
            title = "请选择运行平台"
            options = ['PC', '模拟器','检查更新','配置参数']
            platform = questionary.select(title, options).ask()
            if platform == "检查更新":
                up_data()
                raise Exception("请重新运行")
            if platform == "配置参数":
                main_start(False)
                raise Exception("请重新运行")
            title = "请选择操作"
            options = ['大世界', '模拟宇宙']
            option = questionary.select(title, options).ask()
            if option == "大世界":
                main(0,platform)
            elif option == "模拟宇宙":
                main(1,platform)
    except ModuleNotFoundError as e:
        print(traceback.format_exc())
        os.system("pip install -r requirements.txt")
        print("请重新运行")
    except NameError as e:
        print(traceback.format_exc())
        os.system("pip install -r requirements.txt")
        print("请重新运行")
    except KeyboardInterrupt:
        log.error("监控到退出")
    except Exception:
        ...
    except:
        log.error(traceback.format_exc())
    finally:
        ADB().kill()
