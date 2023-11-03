import re
import time
import math
import pprint
import numpy as np
from collections import Counter
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

from .questionary.questionary import select, Choice
# 改用本地的questionary模块，使之具备show_description功能，基于'tmbo/questionary/pull/330'
# from questionary import select, Choice   # questionary原项目更新并具备当前功能后，可进行替换
from .relic_constants import *
from .calculated import calculated, Array2dict, get_data_hash, str_just
from .config import (read_json_file, modify_json_file, rewrite_json_file, 
                     RELIC_FILE_NAME, LOADOUT_FILE_NAME, TEAM_FILE_NAME, _, sra_config_obj)
from .exceptions import Exception, RelicOCRException
from .log import log
pp = pprint.PrettyPrinter(indent=1, width=40, sort_dicts=False)
IS_PC = True   # paltform flag (同时保存了模拟器与PC的识别位点)

class Relic:
    """
    <<<遗器模块>>>
    已完成功能：
        1.识别遗器数据 (单次用时约0.5s)
            a.录入的遗器数据保存在'relics_set.json'文件
            b.可识别遗器的[部位、套装、稀有度、等级、主词条、副词条]属性
            c.支持所有稀有度遗器 (识别指定点位色相[黄、紫、蓝、绿])
        2.遗器数据匹配
            a.精确匹配：通过计算与匹配遗器哈希值
            b.模糊匹配：判断新旧遗器是否存在升级关系，若匹配成功，则新遗器将自动替换配装中的旧遗器，
                并在遗器数据中建立后继关系，此功能可通过<fuzzy_match_for_relic>设置开关
        3.遗器数据增强
            a.支持计算[四星、五星]遗器的副词条的[强化次数、档位总积分、修正数值(提高原数值的小数精度)]
                1).对于'速度'属性只能做保守估计，其他属性可做准确计算
                2).【新增】可借助其他工具获得'速度'属性的精确值，并手动修改json文件中'速度'属性的小数位，
                    修改后的数据可永久保留，将不影响遗器哈希值计算与模糊匹配，并用于后续的数值计算
            b.【新增】支持计算[四星、五星]遗器的主词条的[修正数值]
            c.【新增】遗器数据打印时的小数精度可通过<ndigits_for_relic>设置选择，范围为[0,1,2,3]
            d.基于遗器数据增强的遗器数据校验功能 (可检测出大部分的遗器识别错误)，可通过<check_stats_for_relic>设置开关
            e.遗器数据增强可通过<detail_for_relic>设置开关
        4.保存角色配装
            a.录入的配装数据保存在'relics_loadout.json'文件
            b.【新增】可检查配装是否已经存在，存在的配装不重复录入
        5.读取角色配装并装备
            a.基于遗器匹配，遗器将强制'替换'，包含[替换己方已装备的遗器、替换对方已装备的遗器]
            b.自动对遗器的[套装、稀有度]属性进行筛选，加快遗器搜索
            c.【新增】配装选择时，将会打印配装信息，包含[内外圈套装、遗器主词条名称、属性数值统计]
        6.【新增】保存队伍配装
            a.录入的队伍配装数据保存在'relics_team.json'文件
            b.录入方式包含[全识别、参考已有的配装数据]
            c.可检查队伍是否存在冲突遗器
        7.【新增】读取队伍配装并装备
            a.队伍选择时，将会打印队伍信息，包含[角色构成、各角色内外圈套装、各角色遗器主词条名称]
            b.对当前队伍的角色顺序不做要求
            b.只支持对已有队伍进行配装，不支持选择相应角色构建队伍

    待解决问题：
        1.【已解决】OCR准确率低：
            对于中文识别更换为项目早期的OCR模型；对于数字识别更换为仅包含英文数字的轻量模型

    待开发功能：
        1.配装管理 [删、改] (需考虑队伍配装)
        2.对忘却之庭双队配装的保存做额外处理，并检查队伍间的遗器冲突
        ...

    开发者说明：
        1.本模块的所有识别位点均采用百分比相对坐标，以兼容不同平台支持不同分辨率
        2.本模块首先会基于安卓模拟器进行测试，再基于PC端测试
        3.【新增】本模块的主体功能已全部完成，现转入日常维护与不定时支线功能开发
        4.【新增】本模块暂不支持简体中文之外的语言
        4.【新增】本模块暂未有开发GUI的计划
    """

    def __init__(self, title=_("崩坏：星穹铁道")):
        """
        说明：
            初始化，载入遗器数据并校验
        """
        if sra_config_obj.language != "zh_CN":
            raise Exception(_("暂不支持简体中文之外的语言"))
        self.calculated = calculated(title, rec_root="model/cnocr_for_relic")

        self.is_fuzzy_match = sra_config_obj.fuzzy_match_for_relic
        """是否在遗器搜索时开启模糊匹配"""
        self.is_check_stats = sra_config_obj.check_stats_for_relic
        """是否在遗器OCR时开启对副词条的数据验证 (关闭后，会将is_detail强制关闭)"""
        self.is_detail = sra_config_obj.detail_for_relic and self.is_check_stats
        """是否在打印遗器信息时显示详细信息 (如各副词条的强化次数、档位积分，以及提高原数据的小数精度)"""
        self.ndigits: Literal[0, 1, 2, 3] = sra_config_obj.ndigits_for_relic
        """在打印遗器信息时的小数精度"""

        # 读取json文件，仅初始化时检查格式规范
        self.relics_data: Dict[str, Dict[str, Any]] = read_json_file(RELIC_FILE_NAME, schema = RELIC_SCHEMA)
        self.loadout_data: Dict[str, Dict[str, List[str]]] = read_json_file(LOADOUT_FILE_NAME, schema = LOADOUT_SCHEMA)
        self.team_data: Dict[str, Dict[str, Any]] = read_json_file(TEAM_FILE_NAME, schema = TEAM_SCHEMA)

        log.info(_("遗器模块初始化完成"))
        log.info(_(f"共载入 {len(list(self.relics_data.keys()))} 件遗器数据"))
        log.info(_(f"共载入 {sum(len(char_loadouts) for char_name, char_loadouts in self.loadout_data.items())} 套配装数据"))
        log.info(_(f"共载入 {sum(len(group_data) for group_name, group_data in self.team_data.items())} 组队伍数据"))

        # 校验遗器哈希值
        if not self.check_relic_data_hash():
            option = select(_("是否依据当前遗器数据更新哈希值："), [_("是"), _("否")]).ask()
            if option == _("是"):
                self.check_relic_data_hash(updata=True)
        # 校验队伍配装规范
        if not self.check_team_data():
            log.error(_("怀疑为手动错误修改json文件导致"))

    def relic_entrance(self):
        """
        说明：
            遗器模块入口
        """
        title = _("遗器模块：")
        tab = "\n" + " " * 5
        options = [
            Choice(_("保存当前角色的配装"), value = 0,
                   description = tab + _("请使游戏保持在[角色]界面")),
            Choice(_("保存当前队伍的配装"), value = 1,
                   description = tab + _("请使游戏保持在[角色]界面") + tab + _("并确保[角色头像列表]移动至开头")),
            Choice(_("读取当前角色的配装记录"), value = 2,
                   description = tab + _("请使游戏保持在[角色]界面")),
            Choice(_("读取队伍的配装记录"), value = 3,
                   description = tab + _("请使游戏保持在[角色]界面") + tab + _("并确保[角色头像列表]移动至开头")),
            Choice(_("识别当前遗器数据"), value = 4,
                   description = tab + _("请使游戏保持在[角色]-[遗器]-[遗器替换]界面") + tab + _("推荐手动点击[对比]提高识别度")),
            _("<返回主菜单>")
        ]  # 注：[角色]界面的前继可为[队伍]-[角色选择]-[详情]界面
        option = None  # 保存上一次的选择
        while True:
            self.calculated.switch_cmd()
            option = select(title, options, default=option, show_description=True).ask()
            if option == 0:
                self.calculated.switch_window()
                self.save_loadout_for_char()
            elif option == 1:
                self.save_loadout_for_team()
            elif option == 2:
                self.equip_loadout_for_char()
            elif option == 3:
                self.equip_loadout_for_team()
            elif option == 4:
                self.calculated.switch_window()
                data = self.try_ocr_relic()
                self.print_relic(data)
            elif option == _("<返回主菜单>"):
                break
    
    def equip_loadout_for_team(self):
        """
        说明：
            装备当前[角色]界面本队伍的遗器配装
        """
        char_pos_list = [(26,6),(31,6),(37,6),(42,6),...,(75,6)] if IS_PC else [(5,16),(5,27),(5,38),(5,49),...,(5,81)]
        # 选择队伍
        option = select(
            _("请选择对当前队伍进行遗器装备的编队："),
            choices = self.get_team_choice_options() + [(_("<返回上一级>"))],
            show_description = True,   # 需questionary具备对show_description的相关支持
        ).ask()
        if option == _("<返回上一级>"):
            return
        team_members = option  # 得到 (char_name: loadout_name) 的键值对
        # 检查人物列表是否移动至开头
        self.calculated.switch_window()
        self.calculated.relative_swipe(char_pos_list[0], char_pos_list[-1])  # 滑动人物列表
        time.sleep(1)
        self.calculated.relative_click((12,40) if IS_PC else (16,48))  # 点击导航栏的遗器，进入[角色]-[遗器]界面
        time.sleep(1)
        # 依次点击人物，进行配装 (编队人物无序)
        for char_index in range(len(team_members)):
            char_pos = char_pos_list[char_index]
            self.calculated.relative_click(char_pos)    # 点击人物
            time.sleep(2)
            character_name = self.ocr_character_name()  # 识别当前人物名称
            if character_name not in team_members:
                log.error(_(f"编队错误：角色'{character_name}'不应在当前队伍中"))
                return
            relic_hash = self.loadout_data[character_name][team_members[character_name]]
            self.equip_loadout(relic_hash)
        log.info(_("队伍配装完毕"))

    def equip_loadout_for_char(self, character_name :Optional[str]=None):
        """
        说明：
            装备当前[角色]界面本人物的遗器配装
        """
        # 识别当前人物名称
        character_name = self.ocr_character_name() if character_name is None else character_name
        character_data = self.loadout_data[character_name]
        # 选择配装
        if not character_data:  # 字典为空
            log.info(_("当前人物配装记录为空"))
            return
        option = select(
            _("请选择将要进行装备的配装："),
            choices = self.get_loadout_choice_options(character_name) + [(_("<返回上一级>"))],
            show_description = True,   # 需questionary具备对show_description的相关支持
        ).ask()
        if option == _("<返回上一级>"):
            return
        loadout_name, relic_hash = option
        self.calculated.switch_window()
        # 进行配装
        self.calculated.relative_click((12,40) if IS_PC else (16,48))  # 点击遗器，进入[角色]-[遗器]界面
        time.sleep(0.5)
        self.equip_loadout(relic_hash)

    def equip_loadout(self, relics_hash:List[str]):
        """
        说明：
            装备当前[角色]-[遗器]页面内的指定遗器配装。
            遗器将强制替换 (1-替换己方已装备的遗器，2-替换对方已装备的遗器)
        参数：
            :param relics_hash: 遗器配装哈希值列表
        """
        equip_pos_list = [(4,13),(9,13),(13,13),(18,13),(23,13),(27,13)] if IS_PC else [(5,14),(11,14),(17,14),(23,14),(28,14),(34,14)]
        relic_filter = self.Relic_filter(self.calculated)   # 遗器筛选器初始化
        relic_set_name_dict = Array2dict(RELIC_SET_NAME)
        self.calculated.relative_click((38,26) if IS_PC else (36,21))  # 点击头部遗器，进入[角色]-[遗器]-[遗器替换]界面
        time.sleep(2)
        self.calculated.relative_click((82,12) if IS_PC else (78,12))  # 点击遗器[对比]，将遗器详情的背景由星空变为纯黑
        time.sleep(1)
        for equip_indx, equip_pos in enumerate(equip_pos_list):   # 遗器部位循环
            # 选择部位
            log.info(_(f"选择部位：{EQUIP_SET_NAME[equip_indx]}"))
            self.calculated.relative_click(equip_pos)
            time.sleep(0.5)
            # 获取遗器数据
            tmp_hash = relics_hash[equip_indx]
            tmp_data = self.relics_data[tmp_hash]
            log.debug(tmp_hash)
            relic_set_index = relic_set_name_dict[tmp_data["relic_set"]]
            rarity = tmp_data["rarity"]
            # 筛选遗器 (加快遗器搜索)
            relic_filter.do(relic_set_index, rarity)
            # 搜索遗器
            pos = self.search_relic(equip_indx, key_hash=tmp_hash, key_data=tmp_data)
            if pos is None:
                log.error(_(f"遗器搜索失败: {tmp_hash}"))
                continue
            # 点击装备
            self.calculated.relative_click(pos)
            button = self.calculated.ocr_pos_for_single_line([_("装备"), _("替换"), _("卸下")], points=(80,90,85,94) if IS_PC else (75,90,82,95))  # 需识别[装备,替换,卸下]
            if button in [0,1]:
                log.info(_("点击装备"))
                self.calculated.relative_click((82,92) if IS_PC else (78,92))
                time.sleep(0.5)
                __, pos_ = self.calculated.ocr_pos(_("提示"), (46,36,54,41) if IS_PC else (46,33,55,38))
                if pos_:
                    log.info(_("确认替换"))
                    self.calculated.relative_click((62,62) if IS_PC else (64,65))
                    time.sleep(0.5)
            elif button == 2:
                log.info(_("已装备"))
        self.calculated.relative_click((97,6) if IS_PC else (96,5))   # 退出[遗器替换]界面，返回[角色]-[遗器]界面
        time.sleep(0.5)
        log.info(_("配装装备完毕"))

    def save_loadout_for_team(self):
        """
        说明：
            保存当前[角色]界面本队伍的遗器配装
        """
        char_pos_list = [(26,6),(31,6),(37,6),(42,6),...,(75,6)] if IS_PC else [(5,16),(5,27),(5,38),(5,49),...,(5,81)]
        char_name_list = []
        relics_hash_list = []
        loadout_name_list = []
        # [1]选择队伍的人数 (能否通过页面识别？)
        char_num = int(select(_("请选择队伍人数："), ['4','3','2','1']).ask())
        # [2]选择是否为互斥队伍组别 
        group_name = "compatible"     # 默认为非互斥队组别
        ...  # 互斥队组别【待扩展】
        if group_name not in self.team_data:
            self.team_data[group_name] = {}
        group_data = self.team_data[group_name]
        # [3]选择组建方式
        options = {
            _("全识别"): 0,
            _("参考已有的配装数据"): 1
        }
        option_ = select(_("请选择组建方式："), options).ask()
        state = options[option_]
        # [4]检查人物列表是否移动至开头
        self.calculated.switch_window()
        self.calculated.relative_swipe(char_pos_list[0], char_pos_list[-1])  # 滑动人物列表
        time.sleep(1)
        self.calculated.relative_click((12,40) if IS_PC else (16,48))  # 点击导航栏的遗器，进入[角色]-[遗器]界面
        time.sleep(1)
        # [5]依次点击人物，识别配装
        char_index = 0
        is_retrying = False
        character_name = None
        loadout_dict = self.HashList2dict()
        while char_index < char_num:
            char_pos = char_pos_list[char_index]
            # [5.1]识别人物名称
            if not is_retrying:    # 如果处于重试，则不再次识别人物名称
                self.calculated.switch_window()
                self.calculated.relative_click(char_pos)    # 点击人物
                time.sleep(2)
                character_name = self.ocr_character_name()  # 识别当前人物名称
            # [5.2]选择识别当前，还是录入已有
            option = None
            if state == 1:
                self.calculated.switch_cmd()
                option = select(
                    _("请选择配装："),
                    choices = self.get_loadout_choice_options(character_name) + [_("<识别当前配装>"), _("<退出>")],
                    show_description = True,   # 需questionary具备对show_description的相关支持
                ).ask()
                if option == _("<退出>"):   # 退出本次编队
                    return
                elif option != _("<识别当前配装>"):
                    loadout_name, relics_hash = option    # 获取已录入的配装数据
            if state == 0 or option == _("<识别当前配装>"):
                self.calculated.switch_window()
                relics_hash = self.save_loadout()
                print(_("配装信息：\n  {}\n{}").format(self.get_loadout_brief(relics_hash), self.get_loadout_detail(relics_hash, 2)))    
                loadout_name = self.find_loadout_name(character_name, relics_hash)
                if loadout_name:
                    log.info(_(f"配装记录已存在，配装名称：{loadout_name}"))
            # [5.3]检查是否存在冲突遗器
            loadout_check = loadout_dict.add(relics_hash, character_name).find_duplicate_hash()
            if loadout_check:  # 列表非空，表示存在遗器冲突
                for equip_index, char_names, element in loadout_check:
                    self.calculated.switch_cmd()
                    log.error(_("队伍遗器冲突：{}间的'{}'遗器冲突，遗器哈希值：{}").format(char_names, EQUIP_SET_NAME[equip_index], element))
                    is_retrying = True  # 将重复本次循环
            if is_retrying:
                log.error(_("请重新选择配装"))
                continue
            log.info(_("配装校验成功"))
            char_name_list.append(character_name)
            relics_hash_list.append(relics_hash)
            loadout_name_list.append(loadout_name)
            is_retrying = False
            char_index += 1
        print(_("队伍配装信息：{}").format("".join("\n  " + str_just(char_name, 10) + " " + self.get_loadout_brief(relics_hash) 
                                                for char_name, relics_hash in zip(char_name_list, relics_hash_list))))
        # [6]自定义名称
        self.calculated.switch_cmd()
        team_name = input(_(">>>>命名编队名称 (将同时作为各人物新建配装的名称): "))
        while team_name in group_data or \
            any([team_name in self.loadout_data[character_name] for character_name, loadout_name in zip(char_name_list, loadout_name_list) if loadout_name is None]):
            team_name = input(_(">>>>命名冲突，请重命名: "))
        # [7]录入数据
        for i, (char_name, relics_hash, loadout_name) in enumerate(zip(char_name_list, relics_hash_list, loadout_name_list)):
            if loadout_name is None:
                loadout_name_list[i] = team_name
                self.loadout_data[char_name][team_name] = relics_hash
                rewrite_json_file(LOADOUT_FILE_NAME, self.loadout_data)
        group_data[team_name] = {"team_members": {key: value for key, value in zip(char_name_list, loadout_name_list)}}
        rewrite_json_file(TEAM_FILE_NAME, self.team_data)
        log.info(_("编队录入成功"))

    def save_loadout_for_char(self):
        """
        说明：
            保存当前[角色]界面本人物的遗器配装
        """
        character_name = self.ocr_character_name()  # 识别当前人物名称
        character_data = self.loadout_data[character_name]
        self.calculated.relative_click((12,40) if IS_PC else (16,48))  # 点击导航栏的遗器，进入[角色]-[遗器]界面
        time.sleep(1)
        relics_hash = self.save_loadout()
        self.calculated.switch_cmd()
        print(_("配装信息：\n  {}\n{}").format(self.get_loadout_brief(relics_hash), self.get_loadout_detail(relics_hash, 2)))
        loadout_name = self.find_loadout_name(character_name, relics_hash)
        if loadout_name:
            log.info(_(f"配装记录已存在，配装名称：{loadout_name}"))
            return
        loadout_name = input(_(">>>>命名配装名称: "))  # 需作为字典key值，确保唯一性 (但不同的人物可以有同一配装名称)
        while loadout_name in character_data:
            loadout_name = input(_(">>>>命名冲突，请重命名: "))
        character_data[loadout_name] = relics_hash
        rewrite_json_file(LOADOUT_FILE_NAME, self.loadout_data)
        log.info(_("配装录入成功"))

    def save_loadout(self, max_retries=3) -> list[str]:
        """
        说明：
            保存当前[角色]-[遗器]界面内的遗器配装
        返回：
            :return relics_hash: 遗器配装哈希值列表
        """
        equip_pos_list = [(4,13),(9,13),(13,13),(18,13),(23,13),(27,13)] if IS_PC else [(5,14),(11,14),(17,14),(23,14),(28,14),(34,14)]
        relics_hash = []
        self.calculated.relative_click((38,26) if IS_PC else (36,21))  # 点击头部遗器，进入[角色]-[遗器]-[遗器替换]界面
        time.sleep(2)
        self.calculated.relative_click((82,12) if IS_PC else (78,12))  # 点击遗器[对比]，将遗器详情的背景由星空变为纯黑
        time.sleep(1)
        for equip_indx, equip_pos in enumerate(equip_pos_list):   # 遗器部位循环
            log.info(_(f"选择部位：{EQUIP_SET_NAME[equip_indx]}"))
            self.calculated.relative_click(equip_pos)
            time.sleep(1)
            tmp_data = self.try_ocr_relic(equip_indx, max_retries)
            tmp_hash = get_data_hash(tmp_data, RELIC_DATA_FILTER)
            log.debug("\n"+pp.pformat(tmp_data))
            self.print_relic(tmp_data)
            if tmp_hash in self.relics_data:
                log.info(_("遗器数据已存在"))
            else:
                log.info(_("录入遗器数据"))
                self.add_relic_data(tmp_data, tmp_hash)
            relics_hash.append(tmp_hash)
        self.calculated.relative_click((97,6) if IS_PC else (96,5))   # 退出[遗器替换]界面，返回[角色]-[遗器]界面
        time.sleep(0.5)
        log.info(_("配装识别完毕"))
        return relics_hash
    
    class Relic_filter:
        """
        说明：
            遗器筛选器。封装了在[角色]-[遗器]-[遗器替换]-[遗器筛选]界面内的遗器筛选方法，
            目前可以对遗器套装与稀有度进行筛选，并记录先前的筛选状态
                (注意在未退出[遗器替换]界面时切换遗器，会保留上一次的筛选状态)
        """
        rarity_pos_list = [(77,38),(89,38),(77,42),(89,42)] if IS_PC else [(71,45),(86,45),(71,52),(86,52)]
        """稀有度筛选项的点击位点 (分别为2,3,4,5星稀有度)"""

        def __init__(self, calculated: calculated):
            self.calculated = calculated
            # 记录上一次的筛选状态
            self.pre_relic_set_index = -1
            """过去遗器套装索引"""
            self.pre_rarity = -1
            """过去稀有度"""
        
        def do(self, relic_set_index: int, rairty: int):
            """
            说明：
                在当前[角色]-[遗器]-[遗器替换]内进行遗器筛选
            参数：
                :param relic_set_index: 遗器套装索引
                :param rairty: 稀有度
            """
            if self.pre_relic_set_index == relic_set_index and self.pre_rarity == rairty:  # 筛选条件未改变
                return
            # 若筛选条件之一发生改变，未改变的不会进行重复动作
            log.debug(_(f"进行遗器筛选，筛选条件: set={relic_set_index}, rairty={rairty}"))
            self.calculated.relative_click((3,92) if IS_PC else (4,92))  # 点击筛选图标进入[遗器筛选]界面
            time.sleep(0.5)
            # 筛选遗器套装
            if self.pre_relic_set_index != relic_set_index:
                self.calculated.relative_click((93,20) if IS_PC else (92,23))  # 点击套装选择进入[遗器套装筛选]界面
                time.sleep(0.5)
                self.calculated.relative_click((40,70) if IS_PC else (37,76))  # 清除之前的筛选项
                time.sleep(0.2)
                self.search_relic_set_for_filter(relic_set_index)  # 搜索遗器套装名，并点击
                time.sleep(0.2)
                self.calculated.relative_click((62,70) if IS_PC else (64,76))  # 点击确认退出[遗器套装筛选]界面
                time.sleep(0.5)
                self.pre_relic_set_index = relic_set_index
            # 筛选遗器稀有度 (注意稀有度筛选要在遗器筛选之后，不然识别位点会改变)
            if self.pre_rarity != rairty:
                if self.pre_rarity != -1:   # 非初始清除之前的筛选项
                    self.calculated.relative_click(self.rarity_pos_list[self.pre_rarity-2])
                    time.sleep(0.5)
                self.calculated.relative_click(self.rarity_pos_list[rairty-2])  # 点击目标稀有度
                time.sleep(0.5)
                self.pre_rarity = rairty
            ...  # 其他筛选条件
            self.calculated.relative_click((3,92) if IS_PC else (4,92))  # 任意点击筛选框外退出[遗器筛选]界面

        def search_relic_set_for_filter(self, relic_set_index: int):
            """
            说明：
                在当前滑动[角色]-[遗器]-[遗器替换]-[遗器筛选]-[遗器套装筛选]界面内，搜索遗器套装名，并点击。
                综合OCR识别与方位计算
            参数：
                :param equip_set_index: 遗器套装索引
            """
            is_left = relic_set_index % 2 == 0  # 计算左右栏
            page_num = 0 if relic_set_index < 8 else (1 if relic_set_index < 16 else 2)  # 计算页数 (将第2页的末尾两件放至第3页来处理)
            last_page = 1
            # 滑动翻页
            for i in range(page_num):
                time.sleep(0.2)
                self.calculated.relative_swipe((30,60) if IS_PC else (30,62), (30,31) if IS_PC else (30,27)) # 整页翻动 (此界面的动态延迟较大)
                if i != last_page:  # 非末页，将翻页的动态延迟暂停 (末页会有个短暂反弹动画后自动停止)
                    self.calculated.relative_click((35,35) if IS_PC else (35,32), 0.5)   # 长按选中
                    time.sleep(0.5)
                    self.calculated.relative_click((35,35) if IS_PC else (35,32))        # 取消选中
            points = ((28,33,42,63) if is_left else (53,33,67,63)) if IS_PC else ((22,29,41,65) if is_left else (53,29,72,65))
            self.calculated.ocr_click(RELIC_SET_NAME[relic_set_index, 1], points=points)


    def search_relic(self, equip_indx: int, key_hash: Optional[str]=None, key_data: Optional[Dict[str, Any]]=None, overtime=180, max_retries=3
                     ) -> Optional[tuple[int, int]]:
        """
        说明：
            在当前滑动[角色]-[遗器]-[遗器替换]界面内，搜索匹配的遗器。
                key_hash非空: 激活精确匹配 (假设数据保存期间遗器未再次升级); 
                key_data非空: 激活模糊匹配 (假设数据保存期间遗器再次升级，匹配成功后自动更新遗器数据);
                key_hash & key_data均空: 遍历当前页面内的遗器
        参数：
            :param equip_indx: 遗器部位索引
            :param key_hash: 所记录的遗器哈希值
            :param key_data: 所记录的遗器数据
            :param overtime: 超时
        返回:
            :return pos: 坐标
        """
        pos_start = (5,24) if IS_PC else (7,28)
        d_x, d_y, k_x, k_y = (7, 14, 4, 5) if IS_PC else (8, 17, 4, 4)
        r_x = range(pos_start[0], pos_start[0]+d_x*k_x, d_x)
        r_y = range(pos_start[1], pos_start[1]+d_y*k_y, d_y)
        pre_pos = [""]
        start_time = time.time()
        while True:
            for index in range(0, k_y*k_x):
                i = index // k_x   # 行
                j = index % k_x    # 列
                x, y = r_x[j], r_y[i]   # 坐标查表
                self.calculated.relative_click((x, y))   # 点击遗器，同时将翻页的动态延迟暂停
                time.sleep(0.2)
                log.info(f"({i+1},{j+1},{len(pre_pos)})")  # 显示当前所识别遗器的方位与序列号
                tmp_data = self.try_ocr_relic(equip_indx, max_retries)
                # log.info("\n"+pp.pformat(tmp_data))
                tmp_hash = get_data_hash(tmp_data)
                if key_hash and key_hash == tmp_hash:  # 精确匹配
                    return (x, y)
                if key_data and self.is_fuzzy_match and self.compare_relics(key_data, tmp_data):  # 模糊匹配
                    print(_("<<<<旧遗器>>>>"))
                    self.print_relic(key_data)
                    print(_("<<<<新遗器>>>>"))
                    self.print_relic(tmp_data)
                    log.info(_("模糊匹配成功！自动更新遗器数据"))
                    # 更新数据库 (录入新遗器数据，并将配装数据中的旧有哈希值替换)
                    tmp_data["pre_ver_hash"] = key_hash   # 建立后继关系
                    self.updata_relic_data(key_hash, tmp_hash, equip_indx, tmp_data)
                    return (x, y)
                # 判断是否遍历完毕
                if pre_pos[-1] == tmp_hash:
                    log.info(_("遗器数据未发生变化，怀疑点击到空白区域搜索至最后"))
                    return None   # 判断点击到空白，遗器数据未发生变化，结束搜索
                if j == 0 and tmp_hash in pre_pos: # 判断当前行的首列遗器是否已被搜索
                    if i == k_y-1:
                        log.info(_("已搜索至最后"))
                        return None   # 判断已滑动至末页，结束搜索
                    break     # 本行已搜索过，跳出本行
                pre_pos.append(tmp_hash)  # 记录
            # 滑动翻页 (从末尾位置滑动至顶部，即刚好滑动一整页)
            log.info(_("滑动翻页"))
            self.calculated.relative_swipe((pos_start[0], pos_start[1]+(k_y-1)*d_y), (pos_start[0], pos_start[1]-d_y))
            if time.time() - start_time > overtime:
                log.info(_("识别超时"))
                break
        return None
    
    def compare_relics(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> bool:
        """
        说明：
            比对两者遗器数据，判断新遗器是否为旧遗器升级后
        """
        # 大条件判断
        if old_data["equip_set"] != new_data["equip_set"] or old_data["relic_set"] != new_data["relic_set"] or \
            old_data["rarity"] != new_data["rarity"] or old_data["base_stats"].keys() != new_data["base_stats"].keys() or \
            old_data["level"] >= new_data["level"]:
            return False
        # 副词条判断，判断data_old的副词条key是否全包含在data_new中，且value均小于等于它
        for key in old_data["subs_stats"].keys():
            if key not in new_data["subs_stats"]:
                return False
            if key == _("速度") and int(old_data["subs_stats"][key]) > int(new_data["subs_stats"][key]) or \
                key != _("速度") and old_data["subs_stats"][key] > new_data["subs_stats"][key]:
                return False        # 考虑手动提高速度数据精度的情况
        return True
    
    def find_loadout_name(self, char_name: str, relics_hash: List[str]) -> Optional[str]:
        """
        说明：
            通过配装数据在记录中寻找配装名称
        """
        for loadout_name, hash_list in self.loadout_data[char_name].items():
            if hash_list == relics_hash:
                return loadout_name
        return None

    def check_team_data(self) -> bool:
        """
        说明：
            检查队伍配装数据是否满足规范
        """
        ret = True
        for group_name, team_group in self.team_data.items():
            for team_name, team_data in team_group.items():
                loadout_dict = self.HashList2dict()
                [loadout_dict.add(self.loadout_data[char_name][loadout_name], char_name) for char_name, loadout_name in team_data["team_members"].items()]
                for equip_index, char_names, element in loadout_dict.find_duplicate_hash():
                    log.error(_("队伍遗器冲突：'{}'队伍的{}间的'{}'遗器冲突，遗器哈希值：{}").format(team_name, char_names, EQUIP_SET_NAME[equip_index], element))
                    ret = False
            if group_name != "compatible": ...   # 互斥队伍组别【待扩展】
        if ret:
            log.info(_("队伍配装校验成功"))
        return ret

    class HashList2dict:
        """
        说明：
            将队伍或队伍组别的配装按遗器部位进行字典统计，以查找可能存在的重复遗器
        """

        def __init__(self):
            self.hash_dict_for_equip: List[Dict[str, List[str]]] = [{},{},{},{},{},{}]
            """按遗器部位分别的配装统计，key-遗器哈希值，value-装备者的名称"""

        def add(self, relics_hash: List[str], char_name: str) -> 'Relic.HashList2dict':
            """
            说明：
                添加一组数据
            参数：
                :param relics_hash: 配装遗器哈希值列表
                :param char_name: 配装装备者的名称
            """
            for equip_index, element in enumerate(relics_hash):
                if element in self.hash_dict_for_equip[equip_index]:
                    self.hash_dict_for_equip[equip_index][element].append(char_name)
                else:
                    self.hash_dict_for_equip[equip_index][element] = [char_name]
            return self

        def find_duplicate_hash(self) -> List[Tuple[int, List[str], str]]:
            """
            说明：
                按遗器部位遍历字典，查找可能存在的重复遗器
            返回：
                :return ret[list(tuple)]:
                    0-遗器部位索引，1-装备者的名称序列，2-遗器哈希值
            """
            ret = []
            for equip_index in range(len(self.hash_dict_for_equip)):
                for element, char_names in self.hash_dict_for_equip[equip_index].items():
                    if len(char_names) > 1:
                        ret.append((equip_index, char_names, element))
            return ret

    def check_relic_data_hash(self, updata=False) -> bool:
        """
        说明：
            检查遗器数据是否发生手动修改 (应对json数据格式变动或手动矫正仪器数值)，
            若发生修改，可选择更新仪器哈希值，并替换配装数据中相应的数值
        """
        equip_set_dict = {key: value for value, key in enumerate(EQUIP_SET_NAME)}
        relics_data_copy = self.relics_data.copy()  # 字典迭代过程中不允许修改key
        cnt = 0
        for old_hash, data in relics_data_copy.items():
            new_hash = get_data_hash(data, RELIC_DATA_FILTER, speed_modified=True)
            if old_hash != new_hash:
                equip_indx = equip_set_dict[data["equip_set"]]
                log.debug(f"(old={old_hash}, new={new_hash})")
                if updata: 
                    self.updata_relic_data(old_hash, new_hash, equip_indx)
                cnt += 1
        if not cnt:
            log.info(_("遗器哈希值校验成功"))
            return True
        if updata:
            log.info(_(f"已更新 {cnt} 件遗器的哈希值"))
            return True
        else:
            log.error(_(f"发现 {cnt} 件遗器的哈希值校验失败"))
            return False

    def updata_relic_data(self, old_hash: str, new_hash: str, equip_indx: int, new_data: Optional[Dict[str, Any]]=None, delete_old_data=False):
        """
        说明：
            更改仪器数据，先后修改遗器与配装文件
        参数：
            :param old_hash: 遗器旧哈希值
            :param new_hash: 遗器新哈希值
            :parma equip_indx: 遗器部位索引 (减轻一点遍历压力)
            :parma new_data: 新的遗器数据
            :parma delete_old_data: 是否删除旧的数据
        """
        # 修改遗器文件
        if new_data is None:
            self.relics_data[new_hash] = self.relics_data.pop(old_hash)
        else:
            if delete_old_data:
                self.relics_data.pop(old_hash)
            self.relics_data[new_hash] = new_data
        rewrite_json_file(RELIC_FILE_NAME, self.relics_data)
        # 修改配装文件
        for char_name, loadouts in self.loadout_data.items():
            for loadout_name, hash_list in loadouts.items():
                if hash_list[equip_indx] == old_hash:
                    self.loadout_data[char_name][loadout_name][equip_indx] = new_hash
        rewrite_json_file(LOADOUT_FILE_NAME, self.loadout_data)
        # 队伍配装文件无需修改
        
    def add_relic_data(self, data: Dict[str, Any], data_hash: Optional[str]=None) -> bool:
        """
        说明：
            录入仪器数据
        """
        if not data_hash:
            data_hash = get_data_hash(data, RELIC_DATA_FILTER)
        if data_hash not in self.relics_data:
            self.relics_data = modify_json_file(RELIC_FILE_NAME, data_hash, data) # 返回更新后的字典
            return True
        else:
            log.error(_(f"哈希值重复: {data_hash}"))
            return False
        
    def ocr_character_name(self) -> str:
        """
        说明：
            OCR当前人物界面的人物名称，并写入loadout_data
        返回：
            :return character_name: 人物名称
        """
        str = self.calculated.ocr_pos_for_single_line(points=(10.4,6,18,9) if IS_PC else (13,4,22,9))   # 识别人物名称 (主角名称为玩家自定义，无法适用预选列表)
        character_name = re.sub(r"[.’,，。、·'-_——「」/|\[\]\"\\]", '', str)   # 删除由于背景光点造成的误判
        log.info(_(f"识别人物: {character_name}"))
        if character_name not in self.loadout_data:
            self.loadout_data = modify_json_file(LOADOUT_FILE_NAME, character_name, {})
            log.info(_("创建新人物"))
        return character_name
    
    def try_ocr_relic(self, equip_set_index:Optional[int]=None, max_retries=3) -> Dict[str, Any]:
        """
        说明：
            在规定次数内尝试OCR遗器数据
        参数：
            :param equip_set_index: 遗器部位索引
            :param max_retries: 重试次数
        返回：
            :return result_data: 遗器数据包
        """
        retry = 0
        while True:  # 视作偶发错误进行重试
            try:  
                data = self.ocr_relic(equip_set_index)
                return data
            except: 
                if retry >= max_retries:
                    raise Exception(_("重试次数达到上限"))
                retry += 1
                log.info(_(f"第 {retry} 次尝试重新OCR"))
        
    def ocr_relic(self, equip_set_index: Optional[int]=None) -> Dict[str, Any]:
        """
        说明：
            OCR当前静态[角色]-[遗器]-[遗器替换]界面内的遗器数据，单次用时约0.5s。
            更改为ocr_for_single_line()后，相较ocr()已缩短一半用时，且提高了部分识别的准确性，
            若更改为ocr_for_single_lines()后的性能变化【待测】(代码重构较大)
        参数：
            :param equip_set_index: 遗器部位索引
        返回：
            :return result_data: 遗器数据包
        """
        start_time = time.time()
        img_pc = self.calculated.take_screenshot()  # 仅截取一次图片
        # [1]部位识别
        if equip_set_index is None:
            equip_set_index = self.calculated.ocr_pos_for_single_line(EQUIP_SET_NAME, points=(77,19,83,23) if IS_PC else (71,22,78,26), img_pk=img_pc)
            if equip_set_index < 0:
                raise RelicOCRException(_("遗器套装OCR错误"))
        equip_set_name = EQUIP_SET_NAME[equip_set_index]
        # [2]套装识别
        name_list = RELIC_SET_NAME[:, 0].tolist()
        name_list = name_list[:RELIC_INNER_SET_INDEX] if equip_set_index < 4 else name_list[RELIC_INNER_SET_INDEX:]   # 取外圈/内圈的切片
        relic_set_index = self.calculated.ocr_pos_for_single_line(name_list, points=(77,15,92,19) if IS_PC else (71,17,88,21), img_pk=img_pc)
        if relic_set_index < 0: 
            raise RelicOCRException(_("遗器部位OCR错误"))
        if equip_set_index in [4, 5]:
            relic_set_index += RELIC_INNER_SET_INDEX    # 还原内圈遗器的真实索引
        relic_set_name = RELIC_SET_NAME[relic_set_index, -1]
        # [3]稀有度识别
        hue, __, __ = self.calculated.get_relative_pix_hsv((43,55) if IS_PC else (41,55))   # 识别指定位点色相
        log.debug(f"hue = {hue}")
        if hue < 40:     # [黄]模拟器测试结果的均值为 25
            rarity = 5
        elif hue < 80:   # [绿]未有测试样本
            rarity = 2
        elif hue < 120:  # [蓝]模拟器测试结果的均值为 105
            rarity = 3
        elif hue < 160:  # [紫]模拟器测试结果的均值为 140
            rarity = 4
        else:
            raise RelicOCRException(_("遗器稀有度识别错误"))
        # [4]等级识别
        level = self.calculated.ocr_pos_for_single_line(points=(95,19,98,23) if IS_PC else (94,22,98,26), number=True, img_pk=img_pc)
        level = int(level.split('+')[-1])  # 消除开头可能的'+'号
        if level > 15:
            raise RelicOCRException(_("遗器等级OCR错误"))
        # [5]主属性识别
        name_list = BASE_STATS_NAME_FOR_EQUIP[equip_set_index][:, 0].tolist()
        base_stats_index = self.calculated.ocr_pos_for_single_line(name_list, points=(79.5,25,92,29) if IS_PC else (74,29,89,34), img_pk=img_pc)
        base_stats_value = self.calculated.ocr_pos_for_single_line(points=(93,25,98,29) if IS_PC else (91,29,98,34), number=True, img_pk=img_pc)
        if base_stats_index < 0: 
            raise RelicOCRException(_("遗器主词条OCR错误"))
        if base_stats_value is None:
            raise RelicOCRException(_("遗器主词条数值OCR错误"))
        base_stats_value = str(base_stats_value).replace('.', '')   # 删除所有真假小数点
        if '%' in base_stats_value:
            s = base_stats_value.split('%')[0]   # 修正'48%1'如此的错误识别
            base_stats_value = s[:-1] + '.' + s[-1:]   # 添加未识别的小数点
        base_stats_value = float(base_stats_value)
        base_stats_name = str(BASE_STATS_NAME_FOR_EQUIP[equip_set_index][base_stats_index, -1])
        # [6]副属性识别 (词条数量 2-4)
        subs_stats_name_points =  [(79.5,29,85,33),(79.5,33,85,36.5),(79.5,36.5,85,40),(79.5,40,85,44)] if IS_PC else [(74,35,81,38),(74,39,81,43),(74,44,81,47),(74,48,81,52)]
        subs_stats_value_points = [(93,29,98,33),(93,33,98,36.5),(93,36.5,98,40),(93,40,98,44)] if IS_PC else [(92,35,98,38),(92,39,98,43),(92,44,98,47),(92,48,98,52)]
        name_list = SUBS_STATS_NAME[:, 0].tolist()
        subs_stats_dict = {}
        total_level = 0
        for name_point, value_point in zip(subs_stats_name_points, subs_stats_value_points):
            tmp_index = self.calculated.ocr_pos_for_single_line(name_list, points=name_point, img_pk=img_pc)
            if tmp_index is None: break   # 所识别data为空，即词条为空，正常退出循环
            if tmp_index < 0:
                raise RelicOCRException(_("遗器副词条OCR错误"))
            tmp_value = self.calculated.ocr_pos_for_single_line(points=value_point, number=True, img_pk=img_pc)  
            if tmp_value is None:
                raise RelicOCRException(_("遗器副词条数值OCR错误"))
            tmp_value = str(tmp_value).replace('.', '')   # 删除所有真假小数点
            if '%' in tmp_value:
                s = tmp_value.split('%')[0]   # 修正'48%1'如此的错误识别
                tmp_value = s[:-1] + '.' + s[-1:]   # 添加未识别的小数点
                if tmp_index >= 0 and tmp_index < 3:
                    tmp_index += 3            # 小词条转为大词条
            tmp_value = float(tmp_value)
            tmp_name = str(SUBS_STATS_NAME[tmp_index, -1])
            check = self.get_subs_stats_detail((tmp_name, tmp_value), rarity, tmp_index)
            if check is None:   
                raise RelicOCRException(_("遗器副词条数值OCR错误"))
            total_level += check[0]
            subs_stats_dict[tmp_name] = tmp_value
        if self.is_check_stats and rarity in [4,5] and total_level > level // 3 + 4:
            log.error(f"total_level: {total_level}")
            raise RelicOCRException(_("遗器副词条某一数值OCR错误"))
        # [7]生成结果数据包
        result_data = {
            "equip_set": equip_set_name,
            "relic_set": relic_set_name,
            "rarity": rarity,
            "level": level,
            "base_stats": {
                base_stats_name: base_stats_value
            },
            "subs_stats": subs_stats_dict
        } # 注：需手动把'np.str_'类型转化为'str'类型，以确保key值有效
        end_time = time.time()
        seconds = end_time - start_time
        log.info(f"用时\033[1;92m『{seconds:.1f}秒』\033[0m")
        return result_data
    
    def print_relic(self, data: Dict[str, Any]):
        """
        说明：
            打印遗器信息，
            可通过is_detail设置打印普通信息与拓展信息
        """
        token = []
        token.append(_("部位: {equip_set}").format(equip_set=data["equip_set"]))
        token.append(_("套装: {relic_set}").format(relic_set=data["relic_set"]))
        token.append(_("星级: {star}").format(star='★'*data["rarity"]))
        token.append(_("等级: +{level}").format(level=data["level"]))
        token.append(_("主词条:"))
        name, value = list(data["base_stats"].items())[0]
        pre = " " if name in NOT_PRE_STATS else "%"
        result = self.get_base_stats_detail((name, value), data["rarity"], data["level"])
        if result:
            token.append(_("   {name:<4}\t{value:>7.{ndigits}f}{pre}").format(name=name, value=result, pre=pre, ndigits=self.ndigits))
        else:
            token.append(_("   {name:<4}\t{value:>5}{pre}   [ERROR]").format(name=name, value=value, pre=pre))
        token.append(_("副词条:"))
        subs_stats_dict = Array2dict(SUBS_STATS_NAME)
        for name, value in data["subs_stats"].items():
            pre = " " if name in NOT_PRE_STATS else "%"
            if not self.is_detail or data["rarity"] not in [4,5]:    # 不满足校验条件
                token.append(_("   {name:<4}\t{value:>5}{pre}").format(name=name, value=value, pre=pre))
                continue
            stats_index = subs_stats_dict[name]
            # 增强信息并校验数据
            ret = self.get_subs_stats_detail((name, value), data["rarity"], stats_index)
            if ret:  # 数据校验成功
                level, score, result = ret
                tag = '>'*(level-1)   # 强化次数的标识
                token.append(_("   {name:<4}\t{tag:<7}{value:>7.{ndigits}f}{pre}   [{score}]").
                      format(name=name, tag=tag, value=result, score=score, pre=pre, ndigits=self.ndigits))
            else:    # 数据校验失败
                token.append(_("   {name:<4}\t{value:>5}{pre}   [ERROR]").format(name=name, value=value, pre=pre))           
        token.append('-'*50)
        print("\n".join(token))

    def get_team_choice_options(self) -> List[Choice]:
        """
        说明：
            获取所有队伍配装记录的选项表
        返回：
            :return choice_options: 队伍配装记录的选项列表，Choice构造参数如下：
                :return title: 队伍名称,
                :return value: 队员信息字典(key-人物名称，value-配装名称),
                :return description: 队员配装的简要信息
        """
        group_data = self.team_data["compatible"]    # 获取非互斥队组别信息
        ...  # 获取互斥队伍组别信息【待扩展】
        prefix = "\n" + " " * 5
        choice_options = [Choice(
                title = str_just(team_name, 12), 
                value = team_data["team_members"],
                description = "".join(
                        prefix + str_just(char_name, 10) + " " + self.get_loadout_brief(self.loadout_data[char_name][loadout_name]) 
                    for char_name, loadout_name in team_data["team_members"].items())
            ) for team_name, team_data in group_data.items()]
        return choice_options

    def get_loadout_choice_options(self, character_name:str) -> List[Choice]:
        """
        说明：
            获取该人物配装记录的选项表
        参数：
            :param character_name: 人物名称
        返回：
            :return choice_options: 人物配装记录的选项表，Choice构造参数如下：
                :return title: 配装名称+配装简要信息,
                :return value: 元组(配装名称, 遗器哈希值列表),
                :return description: 配装各属性数值统计
        """
        character_data = self.loadout_data[character_name]
        choice_options = [Choice(
                title = str_just(loadout_name, 14) + " " + self.get_loadout_brief(relics_hash), 
                value = (loadout_name, relics_hash),
                description = '\n' + self.get_loadout_detail(relics_hash, 5, True)
            ) for loadout_name, relics_hash in character_data.items()]
        return choice_options
    
    def get_loadout_detail(self, relics_hash: List[str], tab_num: int=0, flag=False) -> str:
        """
        说明：
            获取配装的详细信息 (各属性数值统计)
        """
        stats_total_value = [0 for _ in range(len(STATS_NAME))]
        stats_name_dict = Array2dict(STATS_NAME)
        base_stats_dict = Array2dict(BASE_STATS_NAME)
        subs_stats_dict = Array2dict(SUBS_STATS_NAME)
        for equip_indx in range(len((relics_hash))):
            tmp_data = self.relics_data[relics_hash[equip_indx]]
            rarity = tmp_data["rarity"]
            level = tmp_data["level"]
            stats_list = [(key, self.get_base_stats_detail((key, value), rarity, level, base_stats_dict[key]))
                          for key, value in tmp_data["base_stats"].items()]           # 获取数值精度提高后的主词条
            stats_list.extend([(key, self.get_subs_stats_detail((key, value), rarity, subs_stats_dict[key])[-1]) 
                               for key, value in tmp_data["subs_stats"].items()])     # 获取数值精度提高后的副词条
            for key, value in stats_list:
                stats_total_value[stats_name_dict[key]] += value  # 数值统计
        token_list = []
        has_ = False  # 标记有无属性伤害
        for index, value in enumerate(stats_total_value):
            name = STATS_NAME[index, -1]
            if index in range(11, 18):
                if index == 17 and not has_ and value == 0 :  # 无属性伤害的情形
                    name = _("属性伤害")
                elif value == 0:  continue
                else:  has_ = True
            pre = " " if name in NOT_PRE_STATS else "%"
            token_list.append(_("{name}{value:>7.{ndigits}f}{pre}").format(name=str_just(name, 15), value=value, pre=pre, ndigits=self.ndigits))
        msg = ""
        column = 2    # 栏数 (可调节)
        tab = " " * tab_num
        for index in range(len(token_list)):   # 分栏输出 (纵向顺序，横向逆序，保证余数项在左栏)
            i = index // column
            j = index % column
            n = (column-j-1) * len(token_list) // column + i
            msg += token_list[n] if j != 0 else tab+token_list[n]
            msg += "\n" if j == column-1 else "   "
        if msg[-1] != "\n": msg += "\n"
        if flag: msg += "\n" + tab + _("(未计算遗器套装的属性加成)")    # 【待扩展】
        return msg

    def get_loadout_brief(self, relics_hash: List[str]) -> str:
        """
        说明：
            获取配装的简要信息 (包含内外圈套装信息与主词条信息)
        """
        set_abbr_dict = Array2dict(RELIC_SET_NAME, -1, 2)
        stats_abbr_dict = Array2dict(BASE_STATS_NAME, -1, 1)
        outer_set_list, inner_set_list, base_stats_list = [], [], []
        # 获取遗器数据
        for equip_indx in range(len((relics_hash))):
            tmp_data = self.relics_data[relics_hash[equip_indx]]
            tmp_set = set_abbr_dict[tmp_data["relic_set"]]
            tmp_base_stats = stats_abbr_dict[list(tmp_data["base_stats"].keys())[0]]
            base_stats_list.append(tmp_base_stats)
            if equip_indx < 4:
                outer_set_list.append(tmp_set)  # 外圈
            else:
                inner_set_list.append(tmp_set)  # 内圈
        outer_set_cnt = Counter(outer_set_list)
        inner_set_cnt = Counter(inner_set_list)
        # 生成信息
        outer = _("外:") + '+'.join([str(cnt) + name for name, cnt in outer_set_cnt.items()]) + "  "
        inner = _("内:") + '+'.join([str(cnt) + name for name, cnt in inner_set_cnt.items()]) + "  "
        # stats = " ".join([EQUIP_SET_ADDR[idx]+":"+name for idx, name in enumerate(base_stats_list) if idx > 1])
        stats = ".".join([name for idx, name in enumerate(base_stats_list) if idx > 1])   # 排除头部与手部
        msg = str_just(stats, 17) + " " + str_just(inner, 10) + " " + outer   # 将长度最不定的外圈信息放至最后
        return msg

    def get_base_stats_detail(self, data: Tuple[str, float], rarity: int, level: int, stats_index: Optional[int]=None) -> Optional[float]:
        """
        说明：
            计算主词条的详细信息 (提高原数据的小数精度)
            可以作为主词条校验函数 (可以检测出大部分的OCR错误)
            支持五星遗器与四星遗器
        参数：
            :param data: 遗器副词条键值对
            :param stats_index: 遗器副词条索引
            :param rarity: 遗器稀有度
            :param level: 遗器等级
        返回：
            :return result: 修正后数值 (提高了原数值精度)
        """
        name, value = data
        if not self.is_check_stats or rarity not in [4,5]:   # 仅支持五星遗器与四星遗器
            return value
        stats_index = np.where(BASE_STATS_NAME[:, -1] == name)[0][0] if stats_index is None else stats_index
        rarity_index = rarity - 4   # 0-四星，1-五星
        a, d = BASE_STATS_TIER[rarity_index][stats_index]
        result = round(a + d*level, 4)    # 四舍五入 (考虑浮点数运算的数值损失)
        # 校验数据
        check = result - value
        if check < 0 or \
            name in NOT_PRE_STATS and check >= 1 or \
            name not in NOT_PRE_STATS and check >= 0.1:
            log.error(_(f"校验失败，原数据或计算方法有误: {data}"))
            log.debug(f"[{a}, {d}], l={level} r={result}")
            return None
        return result

    def get_subs_stats_detail(self, data: Tuple[str, float], rarity: int, stats_index: Optional[int]=None) -> Optional[Tuple[int, int, float]]:
        """
        说明：
            计算副词条的详细信息 (如强化次数、档位积分，以及提高原数据的小数精度)
            对于速度属性只能做保守估计，其他属性可做准确计算。
            可以作为副词条校验函数 (可以检测出大部分的OCR错误)
            支持五星遗器与四星遗器
        参数：
            :param data: 遗器副词条键值对
            :param stats_index: 遗器副词条索引
            :param rarity: 遗器稀有度
        返回：
            :return level: 强化次数: 0次强化记为1，最高5次强化为6
            :return score: 档位总积分: 1档记0分, 2档记1分, 3档记2分
            :return result: 修正后数值 (提高了原数值精度)
        """
        name, value = data
        if not self.is_check_stats or rarity not in [4,5]:   # 仅支持五星遗器与四星遗器
            return (-1, -1, value)
        stats_index = np.where(SUBS_STATS_NAME[:, -1] == name)[0][0] if stats_index is None else stats_index
        rarity_index = rarity - 4  # 0-四星，1-五星
        a, d = SUBS_STATS_TIER[rarity_index][stats_index]
        if name in NOT_PRE_STATS:
            a_ = int(a)           # 从个分位截断小数
        else:
            a_ = int(a * 10)/10   # 从十分位截断小数
        level = int(value / a_)   # 向下取整
        a_ = a_ if name == _("速度") else a    # 给四星速度打补丁
        score = (math.ceil((value - a_*level) / d - 1.e-6))  # 向上取整 (考虑浮点数运算的数值损失)
        if score < 0:   # 总分小于零打补丁 (由于真实总分过大导致)
            level -= 1
            score = math.ceil((value - a_*level) / d - 1.e-6)
        result = round(a*level + d*score, 4)                 # 四舍五入 (考虑浮点数运算的数值损失)
        # 校验数据
        check = result - value
        if check < 0 or \
            name in NOT_PRE_STATS and check >= 1 or \
            name not in NOT_PRE_STATS and check >= 0.1 or \
            level > 6 or level < 1 or \
            score > level*2 or score < 0:
            log.error(_(f"校验失败，原数据或计算方法有误: {data}"))
            log.debug(f"[{a}, {d}], l={level}, s={score}, r={result}")
            return None
        return (level, score, result)