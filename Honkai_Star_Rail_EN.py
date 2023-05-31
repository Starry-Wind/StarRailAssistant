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
    from utils.update_file import update_file
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
        title_ = "Please choose a starting planet: "
        options_map = {"Herta Space Station": "1", "Jarilo-VI": "2", "The Xianzhou Luofu": "3"}
        option_ = questionary.select(title_, list(options_map.keys())).ask()
        main_map = options_map.get(option_)
        title_ = "Please select the starting map："
        options_map = map_instance.map_list_map.get(main_map)
        if not options_map:
            return None, "You haven't downloaded the map, what can you select with?？"
        keys = list(options_map.keys())
        values = list(options_map.values())
        option_ = questionary.select(title_, values).ask()
        side_map = keys[values.index(option_)]
        return f"{main_map}-{side_map}", None
    else:
        title_ = "Please select which universe："
        options_map = ["choose a universe", "Setting presets"]
        option = questionary.select(title_, options_map).ask()
        if option == "choose a universe ":
            title_ = "Please choose which universe:"
            options_map = {"The first world": 1, "The second world": 2, "The third world": 3, "The fourth world": 4, "The fifth world": 5, "The sixth world": 6.}
            option_ = questionary.select(title_, list(options_map.keys())).ask()
            side_map = options_map[option_]
            presets_list = read_json_file(CONFIG_FILE_NAME).get("presets", [])
            presets_list = ['、'.join(i) for i in presets_list]
            choose_role = questionary.select("The preset team to use:", choices=presets_list).ask()
            role_list = choose_role.split("、")
            fate = ['Preservation', 'Remembrance', 'Nihility', 'Abundance', 'Hunt', 'Destruction', 'Elation']
            choose_fate = questionary.select("Preset team to be used:", choices=fate).ask()
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
            log.info( "The script will automatically switch to the game window, please keep the game window active.")
            calculated("PC").switch_window()
            time.sleep(0.5)
            get_width()
            map_instance.calculated.CONFIG = read_json_file(CONFIG_FILE_NAME)
            import pyautogui # Scaling correction
            log.info("Script is running, please do not move the mouse and keyboard")
            log.info("If the script is unresponsive, please run it with administrator privileges")
        elif platform == "Android emulator":
            ADB(order).connect()
        if type == 0:
            map_instance.auto_map(start)  # 读取配置
        elif type == 1:
            simulated_universe.auto_map(start, role_list)  # 读取配置
    else:
        raise Exception(role_list)


def main_start(start = True):
    if not read_json_file(CONFIG_FILE_NAME, False).get('start') or not start:
        title = "Please select a download proxy address: (leave blank if not using a proxy)"
        options = ['https://ghproxy.com/', 'https://ghproxy.net/', 'hub.fgit.ml', '']
        url_ms = []
        pbar = tqdm.tqdm(total=len(options), desc='Testing speed', unit_scale=True, unit_divisor=1024, colour="green")
        for index,url in enumerate(options):
            if url == "":
                url = "https://github.com"
            elif "https://" not in url:
                url =  f"https://"+url
            try:
                response = asyncio.run(get(url))
                ms = response.elapsed.total_seconds()
            except:
                ms = 999
            finally:
                pbar.update(1)
            url_ms.append(options[index]+f" {ms}ms")
        url_ms = [i.replace(" "," "*(len(max(url_ms, key=len))-len(i))) if len(i) < len(max(url_ms, key=len)) else i for i in url_ms]
        option = options[url_ms.index(questionary.select(title, url_ms).ask())]
        modify_json_file(CONFIG_FILE_NAME, "github_proxy", option)
        title = "Please select a download proxy address: (leave blank if not using a proxy)"
        options = ['https://ghproxy.com/', 'https://ghproxy.net/', 'raw.fgit.ml', 'raw.iqiq.io', '']
        url_ms = []
        pbar = tqdm.tqdm(total=len(options), desc='Testing speed', unit_scale=True, unit_divisor=1024, colour="green")
        for index,url in enumerate(options):
            if url == "":
                url = "https://github.com"
            elif "https://" not in url:
                url =  f"https://"+url
            try:
                response = asyncio.run(get(url))
                ms = response.elapsed.total_seconds()
            except:
                ms = 999
            finally:
                pbar.update(1)
            url_ms.append(options[index]+f" {ms}ms")
        url_ms = [i.replace(" "," "*(len(max(url_ms, key=len))-len(i))) if len(i) < len(max(url_ms, key=len)) else i for i in url_ms]
        option = options[url_ms.index(questionary.select(title, url_ms).ask())]
        modify_json_file(CONFIG_FILE_NAME, "rawgithub_proxy", option)
        title = "Did you turn on continuous auto-battle in your game?："
        options = ["Not turned on", "Turned on", "What is this?"]
        option = questionary.select(title, options).ask()
        modify_json_file(CONFIG_FILE_NAME, "auto_battle_persistence", options.index(option))
        title = "Please select the operating platform of the emulator."
        options = {
            "逍遥模拟器": "127.0.0.1:21503",
            "夜神模拟器": "127.0.0.1:62001",
            "海马玩模拟器": "127.0.0.1:26944",
            "天天模拟器": "127.0.0.1:6555",
            "雷电模拟器": "127.0.0.1:5555",
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
        raise Exception("No necessary updates were detected. Please run the script again to force an update.")

    rawghproxy = read_json_file(CONFIG_FILE_NAME, False).get('rawgithub_proxy', "")
    # asyncio.run(check_file(ghproxy, "map"))
    # asyncio.run(check_file(ghproxy, "temp"))
    up_data = {
        "Script":{
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
            'name': "Script"
        },
        "Map":{
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
            'name': "Map"
        },
        "Image":{
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
            'name': "Image"
        },
    }
    title = "Please select the update project."
    options = list(up_data.keys())+["Update all"]
    option = questionary.select(title, options).ask()
    if option != "Update all":
        update_file().update_file_main(**up_data[option])
    else:
        for up_data in list(up_data.values()):
            update_file().update_file_main(**up_data)


if __name__ == "__main__":
    try:
        if not pyuac.isUserAdmin():
            pyuac.runAsAdmin()
        else:
            while True:
                title = "Please select a platform to run on"
                options = ['PC', 'Android emulator', 'Check for updates', 'Configure parameters']
                platform = questionary.select(title, options).ask()
                if platform == "Update":
                    up_data()
                    raise Exception("Please run again")
                if platform == "Configure parameters":
                    main_start(False)
                    raise Exception("Please run again")
                title = "Please select an operation"
                options = ['Overworld', 'Simulated Universe']
                option = questionary.select(title, options).ask()
                try:
                    if option == "Overworld":
                        main(0, platform)
                    elif option == "Simulated Universe":
                        main(1, platform)
                except KeyboardInterrupt:
                    print("\033[1;35m detected an exit\033[0m")
                finally:
                    if questionary.select("User has exited or the script has finished running.", ["Exit", "back"]).ask() == "exit":
                        break
                    else:
                        continue
    except ModuleNotFoundError as e:
        print(traceback.format_exc())
        os.system("pip install -r requirements.txt")
        print("Please run again")
    except NameError as e:
        print(traceback.format_exc())
        os.system("pip install -r requirements.txt")
        print("Please run again")
    except KeyboardInterrupt:
        log.error("Please run again")
    except Exception:
        ...
    except:
        log.error(traceback.format_exc())
    finally:
        ADB().kill()
