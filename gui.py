'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-05-29 16:54:51
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-05-30 23:53:21
Description: 

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
import time
import flet as ft
from flet_core import MainAxisAlignment, CrossAxisAlignment

from utils.log import log,VER,level
from utils.map import Map as map_word
from utils.config import read_json_file,modify_json_file , CONFIG_FILE_NAME
from utils.update_file import update_file
from utils.calculated import calculated
from get_width import get_width

def page_main(page: ft.Page):
    page.client_storage.clear()
    map_dict = map_word("模拟器").map_list_map

    def radiogroup_changed(e):
        """
        说明:
            改变地图选项卡的内容
        参数:
            :param word_select_rg.value 星球选择的编号
            :param map_select_dd.options 所选星球的地图列表
            :param map_select_dd.value 所选星球的地图默认值
        """
        map_select_dd.options=[ft.dropdown.Option(i) for i in list(map_dict[word_select_rg.value].values())]
        map_select_dd.value = list(map_dict[word_select_rg.value].values())[0]
        page.update()

    def add_log(message):
        """
        说明；
            log在gui上输出
        """
        log_text.controls.append(ft.Text(message[:-1]))
        page.update()

    log.add(add_log, level=level, colorize=True,
            format="{module}.{function}"
                    ":{line} - "+f"{VER} - "
                    "{message}"
            )

    def start(e):
        def send_log(e):
            '''
            if log.value:
                log.value += f"\n666"*66
            else:
                log.value = "666"
            '''
            page.update()

        page.clean()
        page.add(
            log_text,
            ft.ElevatedButton("返回", on_click=send_log)
        )

    def map_confirm(e):
        """
        说明:
            选择完地图开始跑图
        参数:
            :param word_select_rg.value 星球选择的编号
            :param map_select_dd.value 所选星球的地图编号
            :param start: 开始地图编号
        """
        keys = list(map_dict[word_select_rg.value].keys())
        values = list(map_dict[word_select_rg.value].values())
        start = word_select_rg.value+"-"+keys[values.index(map_select_dd.value)]
        log.info(start)
        # log显示
        page.clean()
        page.vertical_alignment = "START"
        page.horizontal_alignment = "START"
        page.add(log_text)
        if platform.value == "PC":
            calculated("PC").switch_window()
            time.sleep(0.5)
            get_width()
            import pyautogui # 缩放纠正
        map_word(platform.value).auto_map(start)
        page.add(ft.ElevatedButton("返回", on_click=to_page_main))

    def to_page_main(e):
        """
        说明:
            返回主页
        """
        updata_log = page.client_storage.get("updata_log")
        if updata_log:
            log.remove(updata_log)
        page_main(page)

    def word(e):
        """
        说明:
            地图选择界面
        """
        page.clean()
        page.add(
            ft.Text("星穹铁道小助手", size=50),
            ft.Text("大世界", size=30),
            ft.Text(VER, size=20),
            word_select_rg,
            map_select_dd,
            ft.ElevatedButton("确认", on_click=map_confirm),
            ft.ElevatedButton("返回", on_click=to_page_main),
            platform,
        )

    def updata(e):
        """
        说明:
            更新界面
        """
        pb.width = 100
        ghproxy = read_json_file(CONFIG_FILE_NAME, False).get('github_proxy', "")
        rawghproxy = read_json_file(CONFIG_FILE_NAME, False).get('rawgithub_proxy', "")
        # asyncio.run(check_file(ghproxy, "map"))
        # asyncio.run(check_file(ghproxy, "temp"))
        data = {
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
        def add_updata_log(message):
            message = message[:-1]
            text.value = message
            pb.width = len(message)*13.2
            page.update()
        def up_data(e):
            log.remove()
            updata_log = log.add(add_updata_log, level=level, colorize=True,
                    format="{message}")
            page.client_storage.set("updata_log", updata_log)
            page.clean()
            page.add(
                ft.Text("星穹铁道小助手", size=50),
                ft.Text("检查更新", size=30),
                ft.Text(VER, size=20),
                ft.Column([ text, pb])
            )
            update_file(page,pb).update_file_main(**data[e.control.text])
            page.add(ft.ElevatedButton("返回", on_click=to_page_main))
        Column.controls = [ft.ElevatedButton(i, on_click=up_data) for i in data]
        page.clean()
        page.add(
            ft.Text("星穹铁道小助手", size=50),
            ft.Text("检查更新", size=30),
            ft.Text(VER, size=20),
            Column,
            ft.ElevatedButton("返回", on_click=to_page_main)
        )

    def set_config(e):
        """
        说明:
            硬编码配置编辑，带优化
        """
        config = read_json_file(CONFIG_FILE_NAME)
        print(config)
        simulator = {
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
        github_proxy_list = ['https://ghproxy.com/', 'https://ghproxy.net/', 'hub.fgit.ml', '']
        rawgithub_proxy_list = ['https://ghproxy.com/', 'https://ghproxy.net/', 'raw.fgit.ml', 'raw.iqiq.io', '']
        simulator_keys = list(simulator.keys())
        simulator_values = list(simulator.values())
        adb = simulator_keys[simulator_values.index(config.get("adb", "127.0.0.1:62001"))]
        github_proxy = config.get("github_proxy", "")
        rawgithub_proxy = config.get("rawgithub_proxy", "")
        open_map = config.get("open_map", "m")
        level = config.get("level", "INFO")
        adb_path = config.get("adb_path", "temp\\adb\\adb")
        simulator_dd = ft.Dropdown(
                label="模拟器",
                hint_text="选择你运行的模拟器",
                options=[ft.dropdown.Option(i) for i in list(simulator.keys())],
                value=adb,
                width=200,
            )
        github_proxy_dd = ft.Dropdown(
                label="GITHUB代理",
                hint_text="GITHUB代理地址",
                options=[ft.dropdown.Option(i) for i in github_proxy_list],
                value=github_proxy,
                width=200,
            )
        rawgithub_proxy_dd = ft.Dropdown(
                label="RAWGITHUB代理",
                hint_text="RAWGITHUB代理地址",
                options=[ft.dropdown.Option(i) for i in rawgithub_proxy_list],
                value=rawgithub_proxy,
                width=200,
            )
        level_dd = ft.Dropdown(
                label="日志等级",
                hint_text="日志等级",
                options=[
                    ft.dropdown.Option("INFO"),
                    ft.dropdown.Option("DEBUG"),
                    ft.dropdown.Option("ERROR")
                ],
                value=level,
                width=200,
            )
        adb_path_text = ft.Text(adb_path, size=20)
        def pick_files_result(e: ft.FilePickerResultEvent):
            adb_path_text.value = e.files[0].path
            page.update()
        pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
        open_map_tf = ft.TextField(label="打开地图按钮", value=open_map, width=200)
        def save(e):
            modify_json_file(CONFIG_FILE_NAME, "github_proxy", github_proxy_dd.value)
            modify_json_file(CONFIG_FILE_NAME, "rawgithub_proxy", rawgithub_proxy_dd.value)
            modify_json_file(CONFIG_FILE_NAME, "open_map", open_map_tf.value)
            modify_json_file(CONFIG_FILE_NAME, "level", level_dd.value)
            modify_json_file(CONFIG_FILE_NAME, "adb", simulator[simulator_dd.value])
            modify_json_file(CONFIG_FILE_NAME, "adb_path_text", adb_path_text.value)
            to_page_main(page)
        page.clean()
        page.overlay.append(pick_files_dialog)
        page.add(
            ft.Text("星穹铁道小助手", size=50),
            ft.Text("大世界", size=30),
            ft.Text(VER, size=20),
            simulator_dd,
            github_proxy_dd,
            rawgithub_proxy_dd,
            level_dd,
            open_map_tf,
            ft.Row(
                [
                    adb_path_text,
                    ft.ElevatedButton(
                        "选择文件",
                        icon=ft.icons.UPLOAD_FILE,
                        on_click=lambda _: pick_files_dialog.pick_files(
                            allowed_extensions=["exe"],
                            allow_multiple=True
                        ),
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            ft.ElevatedButton("保存", on_click=save),
        )
        
    # 界面参数区
    text = ft.Text()
    pb = ft.ProgressBar(width=400) #进度条 宽度可更改 pb.width = 400
    ## 更新选项卡
    Column = ft.Column()
    log_text = ft.Column()
    # %% 运行设备选择
    platform = ft.RadioGroup(
        content=ft.Column(
            [
                ft.Radio(value="PC", label="PC"),
                ft.Radio(value="模拟器", label="模拟器")
            ],
            spacing=0
        ),
        value="PC"
    )
    ## 星球选项卡
    word_select_rg = ft.RadioGroup(
        content=ft.Row(
            [
                ft.Radio(value="1", label="空间站「黑塔」"),
                ft.Radio(value="2", label="雅利洛-VI"),
                ft.Radio(value="3", label="仙舟「罗浮」")
            ],
            alignment=MainAxisAlignment.CENTER
        ),
        on_change=radiogroup_changed,
        value="1"
    )
    ## 地图选项卡
    map_select_dd = ft.Dropdown(
        width=100,
        label="地图",
        hint_text="选择地图",
        options=[ft.dropdown.Option(i) for i in list(map_dict['1'].values())],
        value=list(map_dict["1"].values())[0]
    )
    # %%
    img = ft.Image(
        src=f"https://upload-bbs.miyoushe.com/upload/2023/04/04/341589474/5d2239e0352a9b3a561efcf6137b6010_8753232008183647500.jpg",
        fit=ft.ImageFit.FILL,
        repeat=ft.ImageRepeat.NO_REPEAT,
        gapless_playback=False,
    )
    page.title = "星穹铁道小助手"
    page.scroll = "AUTO"
    page.theme = ft.Theme(font_family="Verdana")
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.window_min_width = 600
    page.window_width = 600
    page.window_height = 600
    page.window_min_height = 600
    page.clean()
    page.add(
        ft.Text("星穹铁道小助手", size=50),
        ft.Text(VER, size=20),
        ft.ElevatedButton("大世界", on_click=word),
        ft.ElevatedButton("模拟宇宙", on_click=start),
        ft.ElevatedButton("检查更新", on_click=updata),
        ft.ElevatedButton("编辑配置", on_click=set_config),
        img,
    )

ft.app(target=page_main)
