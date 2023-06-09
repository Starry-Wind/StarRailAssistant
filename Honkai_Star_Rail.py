import os
import traceback
try:
    from utils.log import log
    import time
    import pyuac
    import asyncio
    import questionary
    import importlib
    import tqdm
    from questionary import ValidationError
    from httpx import ReadTimeout, ConnectError, ConnectTimeout
    from pluggy import PluginManager

    from get_width import get_width
    from utils.config import read_json_file, modify_json_file, init_config_file, add_key_value, CONFIG_FILE_NAME, _
    from utils.simulated_universe import Simulated_Universe
    from utils.update_file import update_file
    #from utils.simulated_universe import Simulated_Universe
    from utils.update_file import update_file
    from utils.commission import Commission
    from utils.calculated import calculated
    from utils.exceptions import Exception
    from utils.map import Map as map_word
    from utils.requests import *
    from utils.adb import ADB
except:
    print(traceback.format_exc())
    os.system("pip install -r requirements.txt")
    print("请重新运行")

game_title = _("崩坏：星穹铁道")
plugins_path = "plugins"
plugin_manager = PluginManager("SRA")

class SRA:
    def __init__(self) -> None:
        plugin_manager.register(self)
        self.option_list = [_('PC'), _('模拟器'), _('更新资源'), _('配置参数')]
        self.option_dict = {
            _('PC'): "",
            _('模拟器'): "",
            _('更新资源'): "",
            _('配置参数'): ""
        }

    def run_plugins(self):
        try:
            return plugin_manager.hook.add_option(SRA=self)
        except:
            return [{}]

    def stop(self):
        try:
            plugin_manager.hook.stop(SRA=self)
        except:
            return [{}]

    def end(self):
        try:
            plugin_manager.hook.end(SRA=self)
        except:
            return [{}]


    def add_option(self, option, func, position):
        self.option_dict = add_key_value(self.option_dict, option, func, position)
        return self.option_dict

    def load_plugin(self):
        # 遍历插件文件夹中的文件夹
        if os.path.exists(plugins_path):
            for foldername in os.listdir(plugins_path):
                folder_path = os.path.join(plugins_path, foldername)
                plugins_folder = folder_path.replace("\\",".")
                plugin = importlib.import_module(f"{plugins_folder}")
                main = plugin = importlib.import_module(f"{plugins_folder}.main")
                plugin_name = plugin.plugin_name
                plugin_ver = plugin.plugin_ver
                print(f"\033[0;34;40m正在加载插件 {plugin_name}-{plugin_ver}\033[0m")
                plugin_manager.register(main)
            # 加载通过 setuptools 安装的插件
            plugin_manager.load_setuptools_entrypoints("SRA")

    def choose_map(self, map_instance: map_word, type = 0, platform = "PC"):
        if type == 0:
            title_ = _("请选择起始星球：")
            options_map = {_("空间站「黑塔」"): "1", _("雅利洛-VI"): "2", _("仙舟「罗浮」"): "3"}
            option_ = questionary.select(title_, list(options_map.keys())).ask()
            main_map = options_map.get(option_)
            title_ = _("请选择起始地图：")
            options_map = map_instance.map_list_map.get(main_map)
            if not options_map:
                return None, _("你没下载地图，拿什么选？")
            keys = list(options_map.keys())
            values = list(options_map.values())
            option_ = questionary.select(title_, values).ask()
            side_map = keys[values.index(option_)]
            return f"{main_map}-{side_map}", None
        else:
            title_ = _("请选择第几宇宙：")
            options_map = [_("选择宇宙"), "设置预设"]
            option = questionary.select(title_, options_map).ask()
            if option == _("选择宇宙"):
                title_ = _("请选择第几宇宙：")
                options_map = {_("第一世界"): 1, _("第二世界"): 2, _("第三世界"): 3, _("第四世界"): 4, _("第五世界"): 5, _("第六世界"): 6}
                option_ = questionary.select(title_, list(options_map.keys())).ask()
                side_map = options_map[option_]
                presets_list = read_json_file(CONFIG_FILE_NAME).get("presets", [])
                presets_list = ['、'.join(i) for i in presets_list]
                choose_role = questionary.select(_("要使用的预设队伍:"), choices=presets_list).ask()
                role_list = choose_role.split("、")
                fate = [_('存护'), _('记忆'), _('虚无'), _('丰饶'), _('巡猎'), _('毁灭'), _('欢愉')]
                choose_fate = questionary.select(_("要使用的预设队伍:"), choices=fate).ask()
                choose_list = [role_list, choose_fate]
                return side_map, choose_list
            else:
                Simulated_Universe(platform).choose_presets(option)
                return None, None


    def main(self, type=0,platform="PC",start=None,role_list=None):
        self.main_start()
        order = read_json_file(CONFIG_FILE_NAME, False).get('adb', "")
        adb_path = read_json_file(CONFIG_FILE_NAME, False).get('adb_path', "temp\\adb\\adb")
        map_instance = map_word(game_title, platform, order, adb_path)
        simulated_universe =Simulated_Universe(game_title, platform, order, adb_path)
        start, role_list = self.choose_map(map_instance, type, platform)
        if start:
            if platform == "PC":
                log.info(_("脚本将自动切换至游戏窗口，请保持游戏窗口激活"))
                calculated(game_title, "PC").switch_window()
                time.sleep(0.5)
                get_width(game_title)
                map_instance.calculated.CONFIG = read_json_file(CONFIG_FILE_NAME)
                import pyautogui # 缩放纠正
                log.info(_("开始运行，请勿移动鼠标和键盘"))
                log.info(_("若脚本运行无反应,请使用管理员权限运行"))
            elif platform == _("模拟器"):
                ADB(order).connect()
            if type == 0:
                map_instance.auto_map(start)  # 读取配置
            elif type == 1:
                simulated_universe.auto_map(start, role_list)  # 读取配置
        else:
            raise Exception(role_list)


    def main_start(self, start = True):
        if not read_json_file(CONFIG_FILE_NAME, False).get('start') or not start:
            title = _("请选择下载代理地址：（不使用代理选空白选项）")
            options = ['https://ghproxy.com/', 'https://ghproxy.net/', 'hub.fgit.ml', '']
            url_ms = []
            pbar = tqdm.tqdm(total=len(options), desc=_('测速中'), unit_scale=True, unit_divisor=1024, colour="green")
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
            title = _("请选择代理地址：（不使用代理选空白选项）")
            options = ['https://ghproxy.com/', 'https://ghproxy.net/', 'raw.fgit.ml', 'raw.iqiq.io', '']
            url_ms = []
            pbar = tqdm.tqdm(total=len(options), desc=_('测速中'), unit_scale=True, unit_divisor=1024, colour="green")
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
            title = _("你游戏里开启了连续自动战斗吗？：")
            options = [_('没打开'), _('打开了'), _('这是什么')]
            option = questionary.select(title, options).ask()
            modify_json_file(CONFIG_FILE_NAME, "auto_battle_persistence", options.index(option))
            title = _("请选择模拟器的运行平台(如果你不打算使用模拟器运行请直接回车)")
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
                "手动填写端口号": ""
            }
            option = questionary.select(title, options).ask()
            if option == "手动填写端口号":
                option = questionary.text("请输入端口号:", default="127.0.0.1:62001").ask()
                modify_json_file(CONFIG_FILE_NAME, "adb", option)
            else:
                modify_json_file(CONFIG_FILE_NAME, "adb", options[option])
            modify_json_file(CONFIG_FILE_NAME, "start", True)


    def up_data(self):
        self.main_start()    # 无config直接更新时初始化config文件
        ghproxy = read_json_file(CONFIG_FILE_NAME, False).get('github_proxy', "")
        if "adb" not in read_json_file(CONFIG_FILE_NAME, False):
            init_config_file(1920, 1080)
            raise Exception(_("未检测到必要更新，强制更新脚本，请重新运行脚本"))

        rawghproxy = read_json_file(CONFIG_FILE_NAME, False).get('rawgithub_proxy', "")
        # asyncio.run(check_file(ghproxy, "map"))
        # asyncio.run(check_file(ghproxy, "temp"))
        up_data = {
            _("脚本"):{
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
                'name': _("脚本")
            },
            _("地图"):{
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
                'name': _("地图")
            },
            _("图片"):{
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
                'name': _("图片")
            },
        }
        title = _("请选择更新项目")
        options = list(up_data.keys())+[_("全部更新")]
        option = questionary.select(title, options).ask()
        if option != _("全部更新"):
            update_file().update_file_main(**up_data[option])
        else:
            for up_data in list(up_data.values()):
                update_file().update_file_main(**up_data)

    def commission(self, platform="PC", n=4):
        log.info("脚本将自动切换至游戏窗口，请保持游戏窗口激活，暂时只测试PC")
        cms = Commission(n)
        if platform == "PC":
            cms.calculated.switch_window()
            time.sleep(0.5)
        else:
            return
        cms.open()
        cms.run()
        cms.close()

if __name__ == "__main__":
    print(_("\033[0;31;40m星穹铁道小助手为开源项目，完全免费\n如果你是购买的那么你被骗了\n开源仓库地址: https://github.com/Starry-Wind/StarRailAssistant\033[0m"))
    sra = SRA()
    sra.load_plugin()
    sra.run_plugins()
    try:
        if not pyuac.isUserAdmin():
            pyuac.runAsAdmin()
        else:
            def select():
                title = _("请选择运行平台")
                options = sra.option_dict
                options_list = sra.option_list
                platform = questionary.select(title, list(options.keys())).ask()
                if platform == _("更新资源"):
                    sra.up_data()
                    raise Exception(_("请重新运行"))
                elif platform == _("配置参数"):
                    sra.main_start(False)
                    raise Exception(_("请重新运行"))
                elif platform == None:
                    ...
                elif platform not in options_list:
                    options[platform]()
                else:
                    title = _("请选择操作")
                    options = [_('大世界'), _('模拟宇宙'), _('派遣委托')]
                    option = questionary.select(title, options).ask()
                    if option:
                        if option == _("大世界"):
                            sra.main(0, platform)
                        elif option == _("模拟宇宙"):
                            ''''''
                            #main(1, platform)
                        elif option == _("派遣委托"):
                            sra.commission()
                    else:
                        if questionary.select(_("请问要退出脚本吗？"), [_("退出"), _("返回主菜单")]).ask() == _("返回主菜单"):
                            select()
            select()
            #sra.end()
    except ModuleNotFoundError as e:
        print(traceback.format_exc())
        #os.system("pip install -r requirements.txt")
        print("请重新运行")
    except NameError as e:
        print(traceback.format_exc())
        #os.system("pip install -r requirements.txt")
        print("请重新运行")
    except KeyboardInterrupt:
        log.error(_("监控到退出"))
    except Exception:
        ...
    except:
        log.error(traceback.format_exc())
    finally:
        sra.stop()
        ADB().kill()
