'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-05-29 16:54:51
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-07-30 18:39:41
Description: 

Copyright (c) 2023 by Night-stars-1, All Rights Reserved. 
'''
import sys
import pyuac
import traceback
import tkinter as tk
from tkinter import messagebox
root = tk.Tk()
root.withdraw()
try:
    import time
    import flet as ft
    from re import sub
    from cryptography.fernet import Fernet
    from flet_core import MainAxisAlignment

    from utils.log import log,level
    from utils.map import Map as map_word
    from utils.config import sra_config_obj, read_maps, _
    import utils.config
    from utils.update_file import update_file
    from utils.calculated import calculated
    from get_width import get_width
    from Honkai_Star_Rail import SRA
except:
    messagebox.showerror("运行错误", traceback.format_exc())

sra = SRA()

if getattr(sys, 'frozen', None):
    check_console = False
else:
    check_console = True

def page_main(page: ft.Page):
    '''
    if page.session.contains_key("updata_log"):
        page.session.remove("updata_log")
    '''
    __, map_dict = read_maps()
    VER = sra_config_obj.star_version+"/"+sra_config_obj.picture_version+"/"+sra_config_obj.map_version
    img_url = [
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4//8/AAX+Av4N70a4AAAAAElFTkSuQmCC",
        "https://upload-bbs.miyoushe.com/upload/2023/04/04/341589474/5d2239e0352a9b3a561efcf6137b6010_8753232008183647500.jpg",
        "https://upload-bbs.miyoushe.com/upload/2023/05/31/272930625/2c884f70bcd35555b5ad59163df6a952_2976928227773983219.jpg"
    ]
    def add(*args,**kargs):
        """
        说明:
            页面提交元素的重写
        """
        if type(args[0]) != list:
            args = [i for i in args]
        else:
            args = args[0]
        if not kargs.get("left_page", None):
            kargs["left_page"] = []
        bg_img.width = page.window_width
        bg_img.height = page.window_height-58
        about_ib.width = page.window_width
        about_ib.height = page.window_height-58
        first_page = [
                bg_img,
                ft.Row(
                    [
                        ft.Column(
                            args,
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ]+kargs['left_page']
        return page.add(
            ft.Stack(first_page)
        )

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
        page.title = _("Auto_Star_Rail-{VER}").format(VER=VER)
        log_text.controls.append(ft.Text(message[:-1]))
        page.update()

    if not page.session.get("updata_log"):
        log.add(add_log, level=level, colorize=True,
                format="{module}.{function}"
                        ":{line} - {message}"
                )

    def get_mess(num:int):
        data = [b"gAAAAABkd00kmO4Lkj6jdx88m9HqzU1RQC85SfB_h19TI1WP5pkLZHlA1nauTYBU6ga5hRFlKas9i-rFaC-Q0PPkLd_NLSR9sh8TbGBRE952hIHecP9uwyufZrWwhmdFg4EzlJR4Us64ojJZBm6DkfXSRS2syqbhlg==", b"gAAAAABkd05QbDIzYa9ebhDd6oL1ScrWhuQv8Vay1zj3c3NenzXIpGvWcmiNsNz7nYGJg2G9KJ9edRahlVASebG6zm0YTP-XeJQlgQzChoRnr606FZg0feQSzQVz_Rzri1j_HAmHQR20",b"gAAAAABkd0SIKuiC3bqUwWmhWFr_uqlWUMmv1rclIJNhvr-GteOiT_ahz3Z6GKXoCL-IG0G8_AReT9ISb2PUI_TMXGxWGEW3YrmRy5F5kiQCLORXn8mA7GE="]
        cp = Fernet(b"VKcGP_EkdRbXTe8aAVcjKoI2fULVuyrSX8Le-QZsDOA=")
        return cp.decrypt(data[num]).decode('utf-8')

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
            ft.ElevatedButton(_("返回"), on_click=send_log),
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
        add(log_text)
        #calculated(_("崩坏：星穹铁道"), start=False).switch_window()
        time.sleep(0.5)
        get_width(_("崩坏：星穹铁道"))
        map_word().auto_map(start)
        add(ft.ElevatedButton(_("返回"), on_click=to_page_main))

    def to_page_main(e):
        """
        说明:
            返回主页
        """
        updata_log = page.session.get("updata_log")
        if updata_log:
            log.remove(updata_log)
            page.session.set("updata_log", False)
        page_main(page)

    def word(e):
        """
        说明:
            地图选择界面
        """
        page.clean()
        add(
            ft.Text(_("Auto_Star_Rail"), size=50),
            ft.Text(_("大世界"), size=30),
            ft.Text(VER, size=20),
            word_select_rg,
            map_select_dd,
            ft.ElevatedButton(_("确认"), on_click=map_confirm),
            ft.ElevatedButton(_("返回"), on_click=to_page_main),
        )

    def updata(e):
        """
        说明:
            更新界面
        """
        pb.width = 100
        ghproxy = sra_config_obj.github_proxy
        rawghproxy = sra_config_obj.rawgithub_proxy
        # asyncio.run(check_file(ghproxy, "map"))
        # asyncio.run(check_file(ghproxy, "picture"))
        data = sra.updata_dict
        if not check_console:
            del data[_("脚本")]
        def add_updata_log(message):
            message = message[:-1]
            text.value = sub(r"(.{67})", "\\1\r\n", message)
            pb.width = len(message)*13.2 if len(message) <= 50 else 50*13.2
            page.update()
        def up_data(e):
            log.remove()
            updata_log = log.add(add_updata_log, level=level, colorize=True,
                    format="{message}")
            page.session.set("updata_log", updata_log)
            page.clean()
            up_close = ft.ElevatedButton(_("返回"), disabled=True, on_click=to_page_main)
            add(
                ft.Text(_("Auto_Star_Rail"), size=50),
                ft.Text(_("检查更新"), size=30),
                ft.Text(VER, size=20),
                ft.Column([ text, pb]),
                up_close
            )
            update_file(page,pb).update_file_main(**data[e.control.text])
            up_close.disabled = False
            page.update()
        Column.controls = [ft.ElevatedButton(i, on_click=up_data) for i in data]
        page.clean()
        add(
            ft.Text(_("Auto_Star_Rail"), size=50),
            ft.Text(_("检查更新"), size=30),
            ft.Text(VER, size=20),
            Column,
            ft.ElevatedButton(_("返回"), on_click=to_page_main)
        )

    def set_config(e):
        """
        说明:
            硬编码配置编辑，带优化
        """

        language_dict = {
            "简体中文": "zh_CN",
            "繁體中文": "zh_TC",
            "English": "EN"
        }
        language = sra_config_obj.language
        language = list(filter(lambda key: language_dict[key] == language, language_dict))[0]

        fighting_list = [_('没打开'), _('打开了'), _('这是什么')]
        fighting = fighting_list[sra_config_obj.auto_battle_persistence]

        github_proxy_list = ['https://ghproxy.com/', 'https://ghproxy.net/', "不设置代理"]
        github_proxy = sra_config_obj.github_proxy
        rawgithub_proxy_list = ['https://ghproxy.com/', 'https://ghproxy.net/', 'raw.iqiq.io', "不设置代理"]
        rawgithub_proxy = sra_config_obj.rawgithub_proxy
        apigithub_proxy_list = ['https://github.srap.link/', "不设置代理"]
        apigithub_proxy = sra_config_obj.apigithub_proxy
        open_map = sra_config_obj.open_map
        level = sra_config_obj.level

        github_proxy_dd = ft.Dropdown(
                label=_("GITHUB代理"),
                hint_text=_("如果你无法下载资源，请设置此代理"),
                options=[ft.dropdown.Option(i) for i in github_proxy_list],
                value=github_proxy,
                width=200,
            )
        rawgithub_proxy_dd = ft.Dropdown(
                label=_("RAWGITHUB代理"),
                hint_text=_("如果你无法下载资源，请设置此代理"),
                options=[ft.dropdown.Option(i) for i in rawgithub_proxy_list],
                value=rawgithub_proxy,
                width=200,
            )
        apigithub_proxy_dd = ft.Dropdown(
                label=_("RAWGITHUB代理"),
                hint_text=_("如果你无法下载资源，请设置此代理"),
                options=[ft.dropdown.Option(i) for i in apigithub_proxy_list],
                value=apigithub_proxy,
                width=200,
            )
        level_dd = ft.Dropdown(
                label=_("日志等级"),
                hint_text=_("日志等级"),
                options=[
                    ft.dropdown.Option("INFO"),
                    ft.dropdown.Option("DEBUG"),
                    ft.dropdown.Option("ERROR")
                ],
                value=level,
                width=200,
            )
        language_dd = ft.Dropdown(
                label=_("游戏语言"),
                hint_text=_("设置Auto_Star_Rail的语言"),
                options=[ft.dropdown.Option(i) for i in list(language_dict.keys())],
                value=language,
                width=200,
            )
        fighting_dd = ft.Dropdown(
                label= _("你游戏打开自动战斗了吗？"),
                hint_text= _("你游戏打开自动战斗了吗？"),
                options=[ft.dropdown.Option(i) for i in fighting_list],
                value=fighting,
                width=200,
            )

        open_map_tf = ft.TextField(label=_("打开地图按钮"), value=open_map, width=200)
        def save(e):
            sra_config_obj.github_proxy = "" if github_proxy_dd.value == "不设置代理" else github_proxy_dd.value
            sra_config_obj.rawgithub_proxy = "" if rawgithub_proxy_dd.value == "不设置代理" else rawgithub_proxy_dd.value
            sra_config_obj.apigithub_proxy = "" if apigithub_proxy_dd.value == "不设置代理" else apigithub_proxy_dd.value
            sra_config_obj.open_map = open_map_tf.value
            sra_config_obj.level = level_dd.value
            sra_config_obj.language = language_dict[language_dd.value]
            sra_config_obj.auto_battle_persistence = fighting_list.index(fighting_dd.value)
            sra_config_obj.start = True
            to_page_main(page)
        page.clean()
        add(
            ft.Text(_("Auto_Star_Rail"), size=50),
            ft.Text(_("大世界"), size=30),
            ft.Text(VER, size=20),
            github_proxy_dd,
            rawgithub_proxy_dd,
            apigithub_proxy_dd,
            level_dd,
            open_map_tf,
            language_dd,
            fighting_dd,
            ft.ElevatedButton(_("保存"), on_click=save),
        )

    def change__img(e):
        """
        说明:
            切换背景
        """
        img_v = img_url.index(bg_img.src)
        img_v = 0 if img_v+1 >= len(img_url) else img_v+1
        page.session.set("img_v", img_v)
        bg_img.src = img_url[img_v]
        sra_config_obj.img = img_v
        page.update()

    def about(e):
        """
        说明:
            关于界面
        """
        page.clean()
        add(
            ft.Text(_("Auto_Star_Rail"), size=50),
            ft.Text(_("关于"), size=30),
            ft.Text(VER, size=20),
            ft.Text(get_mess(0), size=40, color=ft.colors.RED),
            ft.Text(get_mess(1), size=40, color=ft.colors.RED),
            ft.Text(
                disabled=False,
                size=25,
                spans=[
                    ft.TextSpan(get_mess(2)),
                    ft.TextSpan(
                        "https://github.com/Night-stars-1/Auto_Star_Rail",
                        ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE,color = ft.colors.BLUE),
                        url="https://github.com/Night-stars-1/Auto_Star_Rail",
                    ),
                ],
            ),
            ft.ElevatedButton(_("返回"), on_click=to_page_main),
        )

    def on_window_event(e):
        """
        说明:
            当应用程序的本机操作系统窗口更改其状态时触发：位置、大小、最大化、最小化等。
        """
        if e.data in ["maximize","unmaximize"]:
            bg_img.width = page.window_width
            bg_img.height = page.window_height-58
            about_ib.width = page.window_width
            about_ib.height = page.window_height-58
            page.update()

    # 界面参数区
    text = ft.Text()
    pb = ft.ProgressBar(width=400) #进度条 宽度可更改 pb.width = 400
    ## 更新选项卡
    Column = ft.Column()
    log_text = ft.Column(
        width=page.window_width,
        spacing=0
    )
    # 背景图片
    if not page.session.get("start"):
        img_url2 = img_url[sra_config_obj.img]
    elif page.session.get("img_v"):
        img_url2 = img_url[page.session.get("img_v")]
    else:
        img_url2 = img_url[0]
    bg_img = ft.Image(
        src=img_url2,
        width=page.window_width,
        height=page.window_height-58,
        fit=ft.ImageFit.FIT_HEIGHT,
        repeat=ft.ImageRepeat.NO_REPEAT,
        gapless_playback=False,
    )
    # 关于按钮
    about_ib = ft.Column(
                [
                    ft.IconButton(
                        icon=ft.icons.CHANGE_CIRCLE_OUTLINED,
                        icon_color="blue200",
                        icon_size=35,
                        tooltip=_("切换背景"),
                        on_click=change__img
                    ),
                    ft.IconButton(
                        icon=ft.icons.INFO_OUTLINED,
                        icon_color="blue200",
                        icon_size=35,
                        tooltip=_("关于"),
                        on_click=about
                    )
                ],
                width=page.window_width,
                height=page.window_height-60,
                alignment=ft.MainAxisAlignment.END,
                horizontal_alignment=ft.CrossAxisAlignment.END,
                spacing=0
            )
    ## 星球选项卡
    word_select_rg = ft.RadioGroup(
        content=ft.Row(
            [
                ft.Radio(value="1", label=_("空间站「黑塔」")),
                ft.Radio(value="2", label=_("雅利洛-VI")),
                ft.Radio(value="3", label=_("仙舟「罗浮」"))
            ],
            alignment=MainAxisAlignment.CENTER
        ),
        on_change=radiogroup_changed,
        value="1"
    )
    ## 地图选项卡
    map_select_dd = ft.Dropdown(
        width=100,
        label=_("地图"),
        hint_text=_("选择地图"),
        options=[ft.dropdown.Option(i) for i in list(map_dict.get('1', {}).values())],
        value=list(map_dict.get('1', {"no":""}).values())[0]
    )
    # %%
    page.clean()
    page.title = _("Auto_Star_Rail")
    page.scroll = "AUTO"
    page.theme = ft.Theme(font_family="Verdana")
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    if not page.session.get("start"):
        page.window_min_width = 800
        page.window_width = 800
        page.window_height = 600
        page.window_min_height = 600
    page.session.set("start", True)
    page.on_window_event = on_window_event
    page.fonts = {
        "Kanit": "picture/fonts/Kanit-Bold.ttf",
    }

    page.theme = ft.Theme(font_family="Kanit")
    sra.option_dict = {
    }
    button_dict = sra.run_plugins()[-1]
    page_list = [
        ft.Text(_("Auto_Star_Rail"), size=50),
        ft.Text(VER, size=20),
        ft.ElevatedButton(_("大世界"), on_click=word),
        #ft.ElevatedButton(_("模拟宇宙")),
    ]+[ft.ElevatedButton(i, on_click=lambda x:button_dict[i](page)) for i in list(button_dict.keys())]+[
        ft.ElevatedButton(_("更新资源"), on_click=updata),
        ft.ElevatedButton(_("编辑配置"), on_click=set_config),
    ]
    if sra_config_obj.picture_version == "0" or sra_config_obj.map_version == "0":
        page_list = [
            ft.Text(_("Auto_Star_Rail"), size=50),
            ft.Text(VER, size=20),
            ft.ElevatedButton(_("更新资源"), on_click=updata),
            ft.ElevatedButton(_("编辑配置"), on_click=set_config),
        ]
        if not sra_config_obj.start:
            page_list.pop(2)
    add(
        page_list,
        left_page=[about_ib]
    )

if __name__ == "__main__":
    try:
        if not pyuac.isUserAdmin():
            messagebox.showerror("运行错误", "请以管理员权限运行")
        else:
            sra.load_plugin()
            ft.app(target=page_main)
    except KeyboardInterrupt:
        ...
    except:
        log.error(traceback.format_exc())
        messagebox.showerror("运行错误", traceback.format_exc())
    finally:
        sra.stop()