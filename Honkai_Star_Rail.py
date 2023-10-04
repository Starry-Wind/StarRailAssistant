"""
Usage:
    Honkai_Star_Rail.py -h | --help
    Honkai_Star_Rail.py [--map=<value>]

Options:
  -h --help                     显示帮助信息
  --map=<value>                 地图编号，可选
"""
import os
import traceback
import time
import pyuac
import asyncio
import questionary
import importlib
import tqdm

from docopt import docopt
from questionary import ValidationError
from pluggy import PluginManager

from get_width import get_width
from utils.log import log, fight_log
from utils.config import read_json_file, modify_json_file, add_key_value, read_maps, CONFIG_FILE_NAME, _
from utils.simulated_universe import Simulated_Universe
from utils.update_file import update_file
from utils.commission import Commission
from utils.calculated import calculated
from utils.exceptions import Exception
from utils.map import Map as map_word
from utils.requests import *

game_title = _("崩坏：星穹铁道")
plugins_path = "plugins"
plugin_manager = PluginManager("SRA")

args = docopt(__doc__) # 命令行快捷参数

class SRA:
    def __init__(self) -> None:
        plugin_manager.register(self)
        self.option_dict = {
            _('大世界'): "",
            _('派遣委托'): "",
            _('更新资源'): "",
            _('编辑配置'): ""
        }
        self.updata_dict = {
            _("脚本"):{
                'skip_verify': False,
                'type': "star",
                'version': "main",
                'url_zip': f"https://github.com/Starry-Wind/StarRailAssistant/archive/refs/heads/main.zip",
                'unzip_path': ".",
                'keep_folder': ['.git', 'logs', 'picture', 'map', 'tmp', 'venv'],
                'keep_file': ['config.json', 'version.json', 'star_list.json', 'README_CHT.md', 'README.md'],
                'zip_path': "StarRailAssistant-main/",
                'name': _("脚本"),
                'delete_file': False
            },
            _("地图"):{
                'skip_verify': False,
                'type': "map",
                'version': "map",
                'url_zip': f"https://raw.githubusercontent.com/Night-stars-1/Auto_Star_Rail_MAP/main/map.zip",
                'unzip_path': "map",
                'keep_folder': [],
                'keep_file': [],
                'zip_path': "map/",
                'name': _("地图"),
                'delete_file': True
            },
            _("图片"):{
                'skip_verify': False,
                'type': "picture",
                'version': "map",
                'url_zip': f"https://raw.githubusercontent.com/Night-stars-1/Auto_Star_Rail_MAP/main/picture.zip",
                'unzip_path': "picture",
                'keep_folder': [],
                'keep_file': [],
                'zip_path': "map/",
                'name': _("图片"),
                'delete_file': True
            },
        }
        self.option_list = list(self.option_dict.keys())

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

    def choose_map(self, option:str=_('大世界')):
        if option == _("大世界"):
            def select_word():
                title_ = _("请选择起始星球：")
                options_map = {_("空间站「黑塔」"): "1", _("雅利洛-VI"): "2", _("仙舟「罗浮」"): "3"}
                option_ = questionary.select(title_, list(options_map.keys())).ask()
                main_map = options_map.get(option_)
                return select_map(main_map)
            def select_map(main_map):
                title_ = _("请选择起始地图：")
                __, map_list_map = read_maps()
                options_map = map_list_map.get(main_map)
                if not options_map:
                    return None, _("你没下载地图，拿什么选？")
                keys = list(options_map.keys())
                values = [_(split_name[0]) + '-' + split_name[1] for split_name in (map_name.split('-') for map_name in options_map.values())]
                values.append(_("返回上一级"))
                option_ = questionary.select(title_, values).ask()
                if option_ == _("返回上一级"):
                    return select_word()
                else:
                    side_map = keys[values.index(option_)]
                    return main_map, side_map
            main_map, side_map = select_word()
            return f"{main_map}-{side_map}", None
        elif option == _("模拟宇宙"):
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
                Simulated_Universe().choose_presets(option)
                return None, None
        return True, None

    def set_config(self, start = True):
        global game_title
        if not sra_config_obj.start or not start:
            import utils.config
            _ = utils.config._
            title = _("请选择你游戏的运行语言:")
            options = {
                "简体中文": "zh_CN",
                "繁體中文": "zh_TC",
                "English": "EN"
            }
            option = questionary.select(title, options).ask()
            sra_config_obj.language = options[option]
            importlib.reload(utils.config)
            title = _("请选择代理地址：（不使用代理选空白选项）")
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
            sra_config_obj.github_proxy = option
            title = _("请选择下载代理地址：（不使用代理选空白选项）")
            options = ['https://ghproxy.com/', 'https://ghproxy.net/', 'raw.fgit.ml', '']
            url_ms = []
            pbar = tqdm.tqdm(total=len(options), desc=_('测速中'), unit_scale=True, unit_divisor=1024, colour="green")
            for index,url in enumerate(options):
                if url == "":
                    url = "https://raw.githubusercontent.com"
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
            sra_config_obj.rawgithub_proxy = option
            title = _("请选择API代理地址：（不使用代理选空白选项）")
            options = ['https://github.srap.link/', '']
            url_ms = []
            pbar = tqdm.tqdm(total=len(options), desc=_('测速中'), unit_scale=True, unit_divisor=1024, colour="green")
            for index,url in enumerate(options):
                if url == "":
                    url = "https://api.github.com"
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
            sra_config_obj.apigithub_proxy = option
            while True:
                if sra_config_obj.picture_version == "0" or sra_config_obj.map_version == "0":
                    sra.up_data()
                else:
                    break
            title = _("你游戏里开启了连续自动战斗吗？：")
            options = [_('没打开'), _('打开了'), _('这是什么')]
            option = questionary.select(title, options).ask()
            sra_config_obj.auto_battle_persistence = options.index(option)
            sra_config_obj.start = True
            raise Exception(_("请重新运行"))

    def up_data(self):
        import utils.config
        importlib.reload(utils.config)
        _ = utils.config._
        # asyncio.run(check_file(ghproxy, "map"))
        # asyncio.run(check_file(ghproxy, "picture"))

        title = _("请选择更新项目")
        options = list(self.updata_dict.keys())+[_("全部更新")]
        option = questionary.select(title, options).ask()
        if option != _("全部更新"):
            update_file().update_file_main(**self.updata_dict[option])
        else:
            for up_data in list(self.updata_dict.values()):
                update_file().update_file_main(**up_data)

    def is_updata(self):
        need_updata = []
        for name, up_data in self.updata_dict.items():
            if not asyncio.run(update_file().is_latest(type=up_data['type'], version=up_data['version'], is_log=False))[0]:
                need_updata.append(name)
        return need_updata

    def main(self, option:str=_('大世界'),start: str=None,role_list: str=None):
        """
        参数:
            :param start: 起始地图编号
            :param role_list: 提示
        """
        if option in self.option_list:
            (start, role_list) = self.choose_map(option) if not start else (start, role_list)
            if start:
                log.info(_("脚本将自动切换至游戏窗口，请保持游戏窗口激活"))
                calculated(game_title, start=False).switch_window()
                time.sleep(0.5)
                get_width(game_title)
                #map_instance.calculated.CONFIG = read_json_file(CONFIG_FILE_NAME)
                import pyautogui # 缩放纠正
                log.info(_("开始运行，请勿移动鼠标和键盘"))
                log.info(_("若脚本运行无反应,请使用管理员权限运行"))
                if option == _("大世界"):
                    map_instance = map_word(game_title)
                    map_instance.auto_map(start)  # 读取配置
                elif option == _("模拟宇宙"):
                    simulated_universe = Simulated_Universe(game_title)
                    simulated_universe.auto_map(start, role_list)  # 读取配置
                elif option == _("派遣委托"):
                    commission = Commission(4, game_title)
                    commission.start()  # 读取配置
            else:
                raise Exception(role_list)
        else:
            log.info(_("脚本将自动切换至游戏窗口，请保持游戏窗口激活"))
            calculated(game_title, start=False).switch_window()
            time.sleep(0.5)
            get_width(game_title)
            #map_instance.calculated.CONFIG = read_json_file(CONFIG_FILE_NAME)
            import pyautogui # 缩放纠正
            log.info(_("开始运行，请勿移动鼠标和键盘"))
            log.info(_("若脚本运行无反应,请使用管理员权限运行"))
            self.option_dict[option]()

if __name__ == "__main__":
    join_time = read_json_file(CONFIG_FILE_NAME).get("join_time", {})
    if type(join_time) == dict:
        sra_config_obj.join_time = 9
    sra = SRA()
    try:
        sra.set_config()    # 无config直接更新时初始化config文件
        print(_("\033[0;31;40m星穹铁道小助手为开源项目，完全免费\n如果你是购买的那么你被骗了\n开源仓库地址: https://github.com/Starry-Wind/StarRailAssistant\033[0m"))
        sra.load_plugin()
        sra.run_plugins()
        if not pyuac.isUserAdmin():
            pyuac.runAsAdmin()
        else:
            def select():
                title = _("请选择运行项目")
                options = list(sra.option_dict.keys())
                need_updata = sra.is_updata()
                if need_updata:
                    options[options.index(_('更新资源'))] = _("更新资源")+f"({','.join(need_updata)})"
                option = questionary.select(title, options).ask()
                option = list(sra.option_dict.keys())[options.index(option)]
                if option == _("更新资源"):
                    sra.up_data()
                    raise Exception(_("请重新运行"))
                elif option == _("编辑配置"):
                    sra.set_config(False)
                elif option == None:
                    ...
                else:
                    if option:
                        sra.main(option)
                    else:
                        if questionary.select(_("请问要退出脚本吗？"), [_("退出"), _("返回主菜单")]).ask() == _("返回主菜单"):
                            select()
            serial_map = args.get("--map") if args.get("--map") != "default" else "1-1_1" # 地图编号
            select() if not serial_map else sra.main(start=serial_map)
            sra.end()
    except KeyboardInterrupt:
        log.error(_("监控到退出"))
    except Exception:
        ...
    except:
        log.error(traceback.format_exc())
    finally:
        sra.stop()
