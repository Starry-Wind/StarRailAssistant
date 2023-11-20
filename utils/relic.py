import re
import time
import math
import pprint
import numpy as np
from itertools import chain
from collections import Counter
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import utils.questionary.questionary as questionary
from utils.questionary.questionary import Choice, Separator, Style
# 改用本地的questionary模块，使之具备show_description功能，基于'tmbo/questionary/pull/330'
# import questionary   # questionary原项目更新并具备当前功能后，可进行替换
from .relic_constants import *
from .calculated import (calculated, Array2dict, StyledText, FloatValidator, ConflictValidator, 
                         get_data_hash, str_just, print_styled_text, combine_styled_text)
from .config import (RELIC_FILE_NAME, LOADOUT_FILE_NAME, TEAM_FILE_NAME, CHAR_PANEL_FILE_NAME, CHAR_WEIGHT_FILE_NAME, USER_DATA_PREFIX,
                     read_json_file, modify_json_file, rewrite_json_file, _, sra_config_obj)
from .exceptions import Exception, RelicOCRException
from .log import log
pp = pprint.PrettyPrinter(indent=1, width=40, sort_dicts=False)
IS_PC = True   # paltform flag (同时保存了模拟器与PC的识别位点)
INDENT = "\n" + " " * 5    # description的一级缩进


class StatsWeight:
    """
    说明：
        属性权重
    """
    def __init__(self, weight: Dict[str, float]={}):
        self.weight = {}
        for key, value in weight.items():
            if key in [_("生命值"), _("攻击力"), _("防御力")]:
                self.weight[key+"%"] = value  # 大词条
                self.weight[key] = value / 2  # 小词条，权重减半
                continue
            elif key == _("速度"):
                self.weight["速度%"] = value  # 大小词条，权值等同
            self.weight[key] = value
    
    def get_color(self, key: str, modify=False) -> str:
        if self.weight == {}:  # 未载入权重数据的情形
            return ""
        # 白值打印修饰
        if key[-2:] == _("白值"):
            value = self.get_weight(key[:-2]+"%")  # 白值视为大词条
            # if value == 0:
            #     value = 0.1  # 标记值，意为所有白值至少为"weight_1"
        else:
            value = self.get_weight(key, modify)
        # 赋色
        if value == 0:
            return "weight_0"  # 灰色 (无效词条)
        elif value <= 0.5:
            return "weight_1"  # 白色
        else:
            return "weight_2"  # 黄色
    
    def get_weight(self, key: str, modify=False) -> float:
        # 权重打印修饰
        if modify and key in [_("生命值"), _("攻击力"), _("防御力")]:
            key += "%"
        return self.weight.get(key, 0)   # 缺损值默认为无效词条
    
    def __repr__(self) -> str:
        return "\n" + pp.pformat(self.weight)
    
    def __bool__(self) -> bool:
        return self.weight != {}

class Relic:

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
        self.subs_stats_iter_weight: Literal[0, 1, 2, 3] = sra_config_obj.stats_weight_for_relic
        """副词条档位权重选择：0-空，1-主流赋值，2-真实比例赋值，3-主流赋值的比例矫正"""
        self.activate_conditional = False
        """在打印面板信息时开启条件效果"""
        self.loadout_detail_type: Literal[0, 1] = 0
        """配装详情的类别：0-面板详情，1-遗器详情"""
        self.msg_style = Style([
            ("highlighted", "fg:#FF9D00 bold"),    # 在select中对选中的项进行高亮
            ("bold", "bold"),
            ("green", "fg:#45bd45"),
            ("grey", "fg:#5f819d"),
            ("orange", "fg:#FF9D00"),
            ("red", "red"),
            ("reverse", "reverse"),
            ("grey_reverse", "fg:#5f819d reverse"),
            ("rarity_5", "orange"),
            ("rarity_4", "magenta"),
            ("rarity_3", "blue"),
            ("rarity_2", "green"),
            ("weight_0", "fg:#5f819d"),
            ("weight_1", "bold"),
            ("weight_2", "fg:#FF9D00 bold")
        ])

        # 读取json文件，仅初始化时检查格式规范
        self.relics_data: Dict[str, Dict[str, Any]] = read_json_file(RELIC_FILE_NAME, schema=RELIC_SCHEMA)
        self.char_panel_data: Dict[str, Dict[str, Dict[str, Any]]] = read_json_file(CHAR_PANEL_FILE_NAME, schema=CHAR_STATS_PANEL_SCHEMA)
        self.char_weight_data: Dict[str, Dict[str, Dict[str, Any]]] = read_json_file(CHAR_WEIGHT_FILE_NAME, schema=CHAR_STATS_WEIGHT_SCHEMA)
        try:
            self.loadout_data: Dict[str, Dict[str, Dict[str, Any]]] = read_json_file(LOADOUT_FILE_NAME, schema=LOADOUT_SCHEMA)
        except:
            # 尝试使用旧版本 (<=1.8.7) 格式读取数据
            log.error(_(f"'{LOADOUT_FILE_NAME}'读取失败，尝试使用旧版本格式读取"))
            self.loadout_data: Dict[str, Dict[str, List[str]]] = read_json_file(LOADOUT_FILE_NAME, schema=LOADOUT_SCHEMA_OLD)
            for loadouts in self.loadout_data.values():
                for loadout_name, relic_hash in loadouts.items():
                    loadouts[loadout_name] = {"relic_hash": relic_hash}
            # pp.pprint(self.loadout_data)
            rewrite_json_file(LOADOUT_FILE_NAME, self.loadout_data)
            log.info(_(f"'{LOADOUT_FILE_NAME}'再读成功，已将其更新至当前版本格式"))
        self.team_data: Dict[str, Dict[str, Dict[str, Any]]] = read_json_file(TEAM_FILE_NAME, schema=TEAM_SCHEMA)

        log.info(_("共载入 {} 件遗器数据").format(len(self.relics_data)))
        log.info(_("共载入 {} 套配装数据").format(sum(len(char_loadouts) for char_loadouts in self.loadout_data.values())))
        log.info(_("共载入 {} 组队伍数据").format(sum(len(group_data) for group_data in self.team_data.values())))
        log.info(_("共载入 {} 位角色的裸装面板").format(len(self.char_panel_data)))
        log.info(_("共载入 {} 位角色的属性权重").format(len(self.char_weight_data)))

        # 校验遗器哈希值
        if not self.check_relic_data_hash():
            if questionary.confirm(_("是否依据当前遗器数据更新哈希值"), default=False).ask():
                self.check_relic_data_hash(updata=True)
        # 校验队伍配装规范
        if not self.check_team_data():
            log.error(_("怀疑为手动错误修改json文件导致"))
        # 首次启动权值进行选择
        if self.subs_stats_iter_weight == 0:
            msg = INDENT+_("仅首次启动进行选择")+INDENT+_("后续可在'config.json'中的'stats_weight_for_relic'选择设置[1,2,3]")
            self.subs_stats_iter_weight = questionary.select(
                _("请选择副词条三个档位的权值"),
                choices = [
                    Choice(SUBS_STATS_TIER_WEIGHT[1][-1], value = 1, 
                        description = INDENT+_("主流赋值")+msg),
                    Choice(SUBS_STATS_TIER_WEIGHT[2][-1], value = 2, 
                        description = INDENT+_("真实比例，除了五星遗器'速度'属性的真实比例为 [0.7692, 0.8846, 1.0]")+msg),
                    Choice(SUBS_STATS_TIER_WEIGHT[3][-1], value = 3, 
                        description = INDENT+_("主流赋值比例矫正后的结果")+msg),
                    Separator(" ")
                ],
                instruction = _("(将影响词条计算与遗器评分)"),
                use_shortcuts = True,
            ).ask()
            sra_config_obj.stats_weight_for_relic = self.subs_stats_iter_weight  # 修改配置文件
        # 用户提示
        questionary.print(_("推荐使用 Windows Termianl 并将窗口调整至合适宽度，以达到更佳的显示效果"), "green")

    def relic_entrance(self):
        """
        说明：
            遗器模块入口
        """
        title = _("遗器模块:")
        option = None  # 保存上一次的选择
        msg = "\n"+INDENT+_("注：[角色]界面的前继可为[队伍]-[角色选择]-[详情]等界面")
        while True:
            options = [
                Choice(_("识别遗器数据"), value = 4,
                    description = INDENT+_("支持批量识别、载入[属性权重]进行评估、导出数据\n")+INDENT+_("注：对于[速度]副属性只能做保守评估，其他属性可做准确计算")
                    +INDENT+_("  可以借助第三方工具获得[速度]副属性的精确值，")+INDENT+_("  并手动修改'relics_set.json'文件中相应的小数位，")+INDENT+_("  修改后的数据会永久保存，不影响遗器哈希值，可用于后续评估")),
                Choice(_("保存当前角色的配装"), value = 0,
                    description = INDENT+_("请使游戏保持在[角色]界面")+msg),
                Choice(_("保存当前队伍的配装"), value = 1,
                    description = INDENT+_("请使游戏保持在[角色]界面")+INDENT+_("并确保目标队伍[1号位]-[角色头像]移动至列表[起始位置]")+INDENT+_("对于[混沌回忆]的队伍可以分上下半分别保存")+msg),
                Choice(_("读取当前角色的配装并装备"), value = 2,
                    description = INDENT+_("请使游戏保持在[角色]界面")+msg),
                Choice(_("读取队伍的配装并装备"), value = 3,
                    description = INDENT+_("请使游戏保持在[角色]界面")+INDENT+_("并确保目标队伍[1号位]-[角色头像]移动至列表[起始位置]")+INDENT+_("对于[混沌回忆]的队伍可以分上下半分别读取")+msg),
                Choice(_("编辑角色配装"), value = 5,
                    description = INDENT+_("支持查看配装、配装重命名、替换遗器等功能")),
                Choice(_("编辑角色裸装面板"), value = 6,
                    description = INDENT+_("此处的[角色裸装面板]是指角色卸下[遗器]、佩戴[光锥]时的角色面板")+INDENT+_("若不满足于交互界面，可在明晰构造方法的前提下直接编辑'char_panel.json'文件")),
                Choice(_("编辑角色属性权重"), value = 7, 
                    description = INDENT+_("权重范围为0~1，缺损值为0")+INDENT+_("评分系统开发中...当前权重只会影响[属性着色]与[有效词条]计算")),
                Choice(_("<清空控制台>"), shortcut_key='c'),
                Choice(_("<返回主菜单>"), shortcut_key='z'),
                Separator(" "),
            ]
            self.calculated.switch_cmd()
            option = questionary.select(title, options, default=option, use_shortcuts=True, style=self.msg_style).ask()
            if option == 0:
                self.save_loadout_for_char()
            elif option == 1:
                self.save_loadout_for_team()
            elif option == 2:
                self.equip_loadout_for_char()
            elif option == 3:
                self.equip_loadout_for_team()
            elif option == 4:
                self.batch_ocr_relics()
            elif option == 5:
                self.edit_loadout_for_char()
            elif option == 6:
                self.edit_character_panel()
            elif option == 7:
                self.edit_character_weight()
            elif option == _("<清空控制台>"):
                import os
                os.system("cls")
            elif option == _("<返回主菜单>"):
                break

    def batch_ocr_relics(self, stats_weight: StatsWeight=StatsWeight(), weight_name: Optional[str]=None):
        """
        说明：
            批量识别遗器
        """
        # [1]选择识别范围与权重
        options_0 = [
            Choice(_("仅当前遗器"), value=0,
                   description = INDENT+_("请使游戏保持在[角色]-[遗器]-[遗器替换]界面")+INDENT+_("建议识别前手动点击[对比]提高识别度")),
            Choice(_("当前筛选条件下的当前所选部位的所有遗器"), value=1, 
                   description = INDENT+_("识别途中不可中断")+INDENT+_("请使游戏保持在[角色]-[遗器]-[遗器替换]界面")+INDENT+_("建议识别前手动点击[对比]提高识别度")),
            Choice(_("<<载入属性权重>>"), shortcut_key='x',
                   description=combine_styled_text(self.print_stats_weight(stats_weight), prefix="\n  启用权重:\n", indent=5) if stats_weight else None),
            Choice(_("<返回上一级>"), shortcut_key='z'),
            Separator(" "),
        ]
        option_0 = questionary.select(_("请选择识别的范围"), options_0, use_shortcuts=True, style=self.msg_style).ask()
        if option_0 == _("<返回上一级>"):
            return
        if option_0 == _("<<载入属性权重>>"):
            charcacter_names = sorted(self.char_weight_data.keys())      # 对权重数据中角色名称排序
            options_1 = []
            for char_name in charcacter_names:
                has_ = char_name in self.char_weight_data
                __, weight = self.find_char_weight(char_name)
                weight_text = combine_styled_text(self.print_stats_weight(weight), prefix="\n", indent=5)
                choice_text = str_just(char_name, 15) + _("■ {}").format("1" if has_ else "0")
                options_1.append(
                    Choice(choice_text, value=char_name, description=weight_text) 
                )
            options_1.extend([
                Choice(_("<<创建临时权重>>"), shortcut_key='x'),
                Choice(_("<取消>"), shortcut_key='z'),
                Separator(" ")
            ])
            option_1 = questionary.select(_("请选择属性权重:"), options_1, use_shortcuts=True, style=self.msg_style).ask()
            if option_1 == _("<取消>"):
                return self.batch_ocr_relics()
            elif option_1 == _("<<创建临时权重>>"):
                stats_weight = self.edit_character_weight(True)
                if stats_weight is None:   # 取消创建
                    return self.batch_ocr_relics()
                weight_name = _("临时权重")
            else:
                weight_name, stats_weight = self.find_char_weight(option_1)
            return self.batch_ocr_relics(stats_weight, weight_name)
        # [2]进行识别
        relics_data = {}
        self.calculated.switch_window()
        if option_0 == 0:
            tmp_data = self.try_ocr_relic()
            tmp_hash = get_data_hash(tmp_data)
            self.print_relic(tmp_data, tmp_hash, stats_weight)
            relics_data[tmp_hash] = tmp_data
        elif option_0 == 1:
            relics_data = self.search_relic(stats_weight=stats_weight, overtime=None)
            log.info(_("共识别到 {} 件遗器").format(len(relics_data)))
        # [3]选择数据保存方式
        self.calculated.switch_cmd()
        options_3 = [
            Choice(_("不保存"), value=0),
            Choice(_("录入遗器数据库"), value=1),
            Choice(_("保存至单独文件"), value=2),
        ]
        option_3 = questionary.select(_("请选择保存方式:"), options_3).ask()
        if option_3 == 0:
            return self.batch_ocr_relics(stats_weight, weight_name)
        elif option_3 == 1:
            cnt = 0
            for tmp_hash, tmp_data in relics_data.items():
                if tmp_hash not in self.relics_data:
                    self.add_relic_data(tmp_data, tmp_hash)
                    cnt += 1
            rewrite_json_file(RELIC_FILE_NAME, self.relics_data)
            log.info(_("共写入 {} 件新遗器至'{}'文件").format(cnt, RELIC_FILE_NAME))
        elif option_3 == 2:
            from datetime import datetime
            file_name = "{}relics_set_{}.json".format(USER_DATA_PREFIX, str(int(datetime.timestamp(datetime.now()))))
            rewrite_json_file(file_name, relics_data)
            log.info(_("共写入 {} 件遗器至'{}'文件").format(len(relics_data), file_name))
        return self.batch_ocr_relics(stats_weight, weight_name)

    def edit_loadout_for_char(self):
        """
        说明：
            编辑角色配装 (查看配装、更改名称、替换遗器(更改/新建))
        """
        charcacter_names = sorted(self.loadout_data.keys())      # 对配装数据中角色名称排序
        option_0 = None
        def interface_3(key_hash: str, equip_index: int) -> Optional[str]:
            """
            说明：
                第[3]层级，替换遗器
            """
            option_3 = None
            options_3 = [
                Choice(_("识别当前遗器"), value = 0,
                       description = INDENT+_("请使游戏保持在[角色]-[遗器]-[遗器替换]界面")+INDENT+_("建议识别前手动点击[对比]提高识别度")),
                # 【待扩展】查询遗器数据库、推荐系统
                Choice(_("<返回上一级>"), shortcut_key='z'),
                Separator(" "),
            ]
            # [0]进行选择
            option_3 = questionary.select(_("请选择替换方式:"), options_3, use_shortcuts=True, style=self.msg_style).ask()
            if option_3 == _("<返回上一级>"):
                return
            elif option_3 != 0:
                ...  # 【待扩展】
            # [1]识别当前遗器
            self.calculated.switch_window()
            tmp_data = self.try_ocr_relic()
            tmp_hash = get_data_hash(tmp_data)
            log.debug("\n"+pp.pformat(tmp_data))
            if tmp_hash in self.relics_data:
                tmp_data = self.relics_data[tmp_hash]  # 载入可能的速度修正
            self.calculated.switch_cmd()
            # [2]有效性检测
            key_data = self.relics_data[key_hash]
            if tmp_data["equip_set"] != key_data["equip_set"]:
                log.error(_("遗器替换失败：识别到错误部位"))
                return None
            if tmp_hash == key_hash:
                log.error(_("遗器替换失败：识别到相同遗器"))
                return None
            # [3]打印对比信息
            tmp_text = self.print_relic(tmp_data, tmp_hash, char_weight, False)
            key_text = self.print_relic(key_data, key_hash, char_weight, False)
            print("\n  {:>28}    {:<28}".format("<<<<<<< NEW", "OLD >>>>>>>"))
            print_styled_text(combine_styled_text(tmp_text, key_text, sep=" "*4, indent=2), style=self.msg_style)
            # [4]模糊匹配
            if self.is_fuzzy_match and self.compare_relics(key_data, tmp_data):
                log.info(_("模糊匹配成功！识别到新遗器为旧遗器升级后，自动更新数据库"))
                # 更新数据库 (录入新遗器数据，并将配装数据中的旧有哈希值替换)
                tmp_data["pre_ver_hash"] = key_hash   # 建立后继关系
                self.updata_relic_data(key_hash, tmp_hash, equip_index, tmp_data)
                return tmp_hash
            # [5]是否进行替换
            if questionary.confirm(_("是否进行替换:")).ask():
                # 录入遗器数据
                if tmp_hash in self.relics_data:
                    log.info(_("遗器数据已存在"))
                else:
                    log.info(_("录入遗器数据"))
                    self.add_relic_data(tmp_data, tmp_hash)
                return tmp_hash
            else:
                return None
        def interface_2(old_relics_hash: List[str]):
            """
            说明：
                第[2]层级，配装内部选项
            """
            option_2 = None
            new_relics_hash = old_relics_hash.copy()
            while True:
                options_2 = []
                # 生成选项
                for equip_index, (equip_set_name, new_hash, old_hash) in enumerate(zip(EQUIP_SET_NAME, new_relics_hash, old_relics_hash)):
                    msg = StyledText()
                    msg.append("\n\n")
                    relic_text = self.print_relic(self.relics_data[new_hash], new_hash, char_weight, False)
                    relic_text = combine_styled_text(relic_text, indent=2)
                    msg.extend(relic_text)
                    tag = _("[已更改]") if new_hash != old_hash else " "
                    # 使用本配装的队伍
                    teams_in_loadout = self.find_teams_in_loadout(character_name, loadout_name)
                    teams_msg = INDENT.join(
                        "   {}) {} ■ {}".format(i+1, str_just(team_name, 17), ", ".join(list(self.team_data[group_name][team_name]["team_members"].keys()))) 
                        for i, (group_name, team_name) in enumerate(teams_in_loadout)
                    ) if teams_in_loadout else _("  --空--")
                    options_2.append(Choice(_("替换{} {}").format(equip_set_name, tag), value=(equip_index, new_hash), description=msg))
                options_2.extend([
                    # 【待扩展】删除配装、更改权重、更改面板
                    Choice(_("<完成并更新配装 (可进行重命名)>"), shortcut_key='y', description=INDENT+_("使用本配装的队伍:")+INDENT+teams_msg),
                    Choice(_("<完成并新建配装>"), shortcut_key='x'),
                    Choice(_("<取消>"), shortcut_key='z'),
                    Separator(" "),
                ])
                # 进行选择
                option_2 = questionary.select(_("请选择要编辑的内容:"), options_2, use_shortcuts=True, style=self.msg_style).ask()
                character_data = self.loadout_data[character_name]
                # 处理特殊选择
                if option_2 == _("<取消>"):
                    return
                elif option_2 == _("<完成并新建配装>"):
                    new_loadout_name = questionary.text(_("命名配装名称:"), validate=ConflictValidator(character_data.keys())).ask()
                    self.loadout_data[character_name][new_loadout_name] = {"relic_hash": new_relics_hash}
                    rewrite_json_file(LOADOUT_FILE_NAME, self.loadout_data)
                    return
                elif option_2 == _("<完成并更新配装 (可进行重命名)>"):
                    new_loadout_name = loadout_name
                    if questionary.confirm(_("是否更改配装名称"), default=False).ask():
                        new_loadout_name = questionary.text(_("命名配装名称:"), validate=ConflictValidator(character_data.keys())).ask()
                    # 判断是否是否修改了遗器数据
                    new_loadout_data = {"relic_hash": new_relics_hash} if new_relics_hash != old_relics_hash else None
                    # 尝试进行配装修改
                    ret = self.updata_loadout_data(character_name, loadout_name, new_loadout_name, new_loadout_data)
                    if ret:
                        return    # 配装修改成功
                    else:
                        continue  # 配装修改失败，给予机会重新修改
                # 替换遗器
                equip_index, key_hash = option_2
                new_hash = interface_3(key_hash, equip_index)
                if new_hash:
                    new_relics_hash[equip_index] = new_hash
        # 第[0]层级，选择角色
        while True:
            options_0 = [
                Choice(str_just(char_name, 15) + _("■ {}").format(len(self.loadout_data[char_name])), value = char_name) 
                for char_name in charcacter_names
            ]
            if not options_0:
                options_0.append(Choice(_(" --空--"), disabled=_("请先保存角色配装")))
            options_0.append(Choice(_("<返回上一级>"), shortcut_key='z'))
            option_0 = questionary.select(_("请选择角色:"), options_0, default=option_0, use_shortcuts=True, style=self.msg_style).ask()
            if option_0 == "<返回上一级>":
                return
            character_name = option_0
            # 查询角色裸装面板
            char_weight_name, char_weight = self.find_char_weight(character_name)
            # 第[1]层级，选择配装
            option_1 = None
            while True:
                option_1 = self.ask_loadout_options(character_name, title=_("请选择要编辑的配装:"))
                if option_1 == _("<返回上一级>"):
                    break
                loadout_name, relics_hash = option_1
                interface_2(relics_hash)

    def edit_character_weight(self, tmp=False) -> Optional[StatsWeight]:
        """
        说明：
            编辑角色属性权重
        参数：
            :parma tmp: 是否为创建临时权重
        """
        option_0 = None
        def interface_1(char_weight: Dict[str, Union[Dict[str, float], Any]]) -> Optional[Dict[str, Union[Dict[str, float], Any]]]:
            """
            说明：
                第[1]层级，编辑权重
            """
            option_1 = None
            weight: Dict[str, float] = char_weight["weight"].copy()
            def get_choices(st: Optional[int]=None, ed: Optional[int]=None) -> List[Choice]:
                choices = []
                for name in WEIGHT_STATS_NAME[st:ed]:  # 按需切片
                    # 按需显示已有数值
                    value_str = "{value:.2f}".format(value=weight[name]) if name in weight else " "
                    choices.append(Choice(str_just(name, 15) + f"{value_str:>7}", value=name))
                return choices
            while True:
                options_1 = get_choices(0,-7) + [Separator()] + get_choices(-7) + [Separator()]
                options_1.extend([
                    Choice(_("<取消>"), shortcut_key='q'),
                    Choice(_("<完成>"), shortcut_key='z'),
                    Separator(" "),
                ])
                # 进行选择
                option_1 = questionary.select(_("编辑权重"), options_1, default=option_1, use_shortcuts=True, style=self.msg_style).ask()
                if option_1 == _("<取消>"):
                    return None
                elif option_1 == _("<完成>"):
                    log.debug("\n"+pp.pformat(weight))
                    return {"weight": weight}
                # 进行编辑
                name = option_1
                value = questionary.text("请输入数值:", validate=FloatValidator(0, 1)).ask()  # input float
                weight[name] = float(value[:4])  # 更新数据 (截取数据到百分位)
        # 第[0]层级
        if tmp:    # 创建临时权重
            tmp_weight = interface_1({"weight": {}})
            return StatsWeight(tmp_weight["weight"]) if tmp_weight else None
        while True:
            # 选择人物
            charcacter_names = sorted(self.loadout_data.keys())      # 对配装数据中角色名称排序
            options_0 = []
            for char_name in charcacter_names:
                has_ = char_name in self.char_weight_data
                if has_:
                    __, weight = self.find_char_weight(char_name)
                    weight_text = combine_styled_text(self.print_stats_weight(weight), prefix="\n", indent=5)
                else:
                    weight_text = None
                choice_text = str_just(char_name, 15) + _("■ {}").format("1" if has_ else "0")
                options_0.append(
                    Choice(choice_text, value=char_name, description=weight_text) 
                )
            if not options_0:
                options_0.append(Choice(_(" --空--"), disabled=_("请先保存角色配装")))
            options_0.extend([
                Choice(_("<返回上一级>"), shortcut_key='z'),
                Separator(" ")
            ])
            option_0 = questionary.select(_("请选择角色:"), options_0, default=option_0, use_shortcuts=True, style=self.msg_style).ask()
            if option_0 == _("<返回上一级>"):
                return
            # 获取记录
            charcacter_name = option_0
            weight_name, charcacter_weight = list(self.char_weight_data.get(charcacter_name, {"None":{"weight": {}}}).items())[0]
            ... # 【待扩展】同一角色支持保存多组权重
            # 交互编辑
            charcacter_weight = interface_1(charcacter_weight)
            if charcacter_weight is None:   # 取消编辑
                continue
            # 保存记录
            if weight_name == "None": weight_name = ""
            if not weight_name or weight_name and questionary.confirm(_("是否对权重重命名"), default=False).ask():
                weight_name = questionary.text(_("命名权重名称:"), default=weight_name).ask()
            self.char_weight_data[charcacter_name] = {weight_name: charcacter_weight}
            rewrite_json_file(CHAR_WEIGHT_FILE_NAME, self.char_weight_data)
            log.info(_("角色权重编辑成功"))

    def edit_character_panel(self):
        """
        说明：
            编辑角色裸装面板
        """
        option_0 = None
        def interface_2(title: str, stats: Dict[str, float], stats_names: List[str]):
            """
            说明：
                第[2]层级，选择编辑的属性，结果通过stats字典引用返回
            """
            option_2 = None
            def get_choices(st: Optional[int]=None, ed: Optional[int]=None) -> List[Choice]:
                choices = []
                for name in stats_names[st:ed]:  # 按需切片，并显示已有数值
                    value_str = "{value:.2f}{pre}".format(value=stats[name], pre=" " if name in NOT_PRE_STATS else "%") if name in stats else " "
                    choices.append(Choice(str_just(name, 15) + f"{value_str:>7}", value=name))
                return choices
            while True:
                # 生成选择
                if stats_names[0] == BASE_VALUE_NAME[0]:  # 白值面板
                    options_2 = get_choices()
                else:                                     # 属性面板，使属性按组别呈现
                    options_2 = get_choices(0,8) + [Separator()] + get_choices(8,15) + [Separator()] + get_choices(15,22) + [Separator()] + get_choices(22,28) + [Separator()] + get_choices(28)
                options_2.append(Choice(_("<返回上一级>"), shortcut_key='z'))
                # 进行选择
                option_2 = questionary.select(title, options_2, default=option_2, use_shortcuts=True, style=self.msg_style).ask()
                if option_2 == _("<返回上一级>"):
                    return
                # 处理选择
                name = option_2
                value = questionary.text("请输入数值:", validate=FloatValidator(0)).ask()  # input float
                stats[name] = float(value)  # 更新数据
        def interface_1(char_panel: Dict[str, Union[Dict[str, float], List[str]]]) -> Optional[Dict[str, Union[Dict[str, float], List[str]]]]:
            """
            说明：
                第[1]层级，选择编辑的类别
            """
            option_1 = None
            base_values = char_panel.get("base", {}).copy()   # 白值属性
            additonal_stats = char_panel.get("additonal", {"暴击率":5, "暴击伤害":50, "能量恢复效率":100}).copy()  # 附加属性 (设置角色默认值)
            conditional_stats = char_panel.get("conditional", {}).copy()  # 条件属性
            extra_effect_list:list = char_panel.get("extra_effect", []).copy() # 额外效果
            while True:
                extra_effect_msg = "".join(INDENT+f"{i+1}.{text}" for i, text in enumerate(extra_effect_list))
                options_1 = [
                    Choice(_("白值属性"), value = 0,
                           description = INDENT+_("游戏内的[白值]只显示到整数位，推荐通过第三方获取精确数值")),
                    Choice(_("附加属性 (可选)"), value=1, 
                           description = INDENT+_("涵盖[基础面板]、[形迹]、[光锥]、[命座]等提供的固定属性加成")+INDENT+_("注意区分大小词条，不推荐直接无脑录入角色面板内的[绿值]作为小词条")),
                    Choice(_("条件属性 (可选)"), value=2,
                           description = INDENT+_("涵盖[形迹]、[光锥]、[命座]等提供的条件属性加成")+INDENT+_("在[角色配装]中打印[面板信息]时可通过开关控制条件效果的开启")+INDENT+_("推荐每一个条件效果对应一条[额外效果说明]记录在下方")),
                    Choice(_("额外效果说明 (可选)"), value=3,
                           description = extra_effect_msg if extra_effect_msg else INDENT+_("涵盖条件属性的文本说明、其他额外效果说明，例如：")+INDENT+_("  光锥5叠：当装备者生命百分比小于50%造成伤害提高50%")+INDENT+_("  光锥5叠：当装备者消灭敌方目标后，恢复50%能量")),
                    Choice(_("<取消>"), shortcut_key='q'),
                    Choice(_("<完成>"), shortcut_key='z', disabled = None if len(base_values)==len(BASE_VALUE_NAME) else _("白值属性缺失")),
                    Separator(" "),
                ]  # 注：必须白值属性非空才可选择完成
                option_1 = questionary.select(_("编辑人物裸装面板："), choices=options_1, default=option_1, use_shortcuts=True, style=self.msg_style).ask()
                if option_1 == 0:
                    interface_2(_("编辑白值属性"), base_values, BASE_VALUE_NAME)
                elif option_1 == 1:
                    interface_2(_("编辑附加属性"), additonal_stats, ALL_STATS_NAME)
                elif option_1 == 2:
                    interface_2(_("编辑条件属性"), conditional_stats, ALL_STATS_NAME)
                elif option_1 == 3:
                    text_lines = questionary.text("添加额外效果 (一行为一条)", multiline=True).ask()
                    text_lines = filter(lambda x: not re.match(r"\s*$", x), text_lines.split("\n"))  # 过滤无效行
                    extra_effect_list.extend(text_lines)
                elif option_1 == _("<取消>"):
                    return None
                elif option_1 == _("<完成>"):
                    char_panel = {
                        "base": base_values,
                        "additonal": additonal_stats,
                        "conditional": conditional_stats,
                        "extra_effect": extra_effect_list,
                    }
                    log.debug("\n"+pp.pformat(char_panel))
                    return char_panel
        # 第[0]层级
        while True:
            # 选择人物
            charcacter_names = sorted(self.loadout_data.keys())      # 对配装数据中角色名称排序
            options_0 = [
                Choice(str_just(char_name, 15) + _("■ {}").format("1" if char_name in self.char_panel_data else "0"), value = char_name) 
                for char_name in charcacter_names
            ]
            if not options_0:
                options_0.append(Choice(_(" --空--"), disabled=_("请先保存角色配装")))
            options_0.append(Choice(_("<返回上一级>"), shortcut_key='z'))
            option_0 = questionary.select(_("请选择角色:"), options_0, default=option_0, use_shortcuts=True, style=self.msg_style).ask()
            if option_0 == _("<返回上一级>"):
                return
            # 获取记录
            charcacter_name = option_0
            panel_name, charcacter_panel = list(self.char_panel_data.get(charcacter_name, {"None":{}}).items())[0]
            ... # 【待扩展】同一角色支持保存多个面板
            # 交互编辑
            charcacter_panel = interface_1(charcacter_panel)
            if charcacter_panel is None:   # 取消编辑
                continue
            # 保存记录
            if panel_name == "None": panel_name = ""
            if not panel_name or panel_name and questionary.confirm(_("是否对面板重命名"), default=False).ask():
                panel_name = questionary.text(_("命名面板名称:"), default=panel_name).ask()
            self.char_panel_data[charcacter_name] = {panel_name: charcacter_panel}
            rewrite_json_file(CHAR_PANEL_FILE_NAME, self.char_panel_data)
            log.info(_("角色面板编辑成功"))

    def equip_loadout_for_team(self):
        """
        说明：
            装备当前[角色]界面本队伍的遗器配装
        """
        char_pos_list = [(26,6),(31,6),(37,6),(42,6),...,(75,6)] if IS_PC else [(5,16),(5,27),(5,38),(5,49),...,(5,81)]
        # 选择队伍
        option = questionary.select(
            _("请选择对当前队伍进行遗器装备的编队："),
            choices = self.get_team_options() + [Choice(_("<返回上一级>"), shortcut_key='z'), Separator(" ")],
            use_shortcuts=True, style=self.msg_style,
        ).ask()
        if option == _("<返回上一级>"):
            return
        team_members = option  # 得到 (char_name: loadout_name) 的键值对
        # 检查人物列表是否移动至开头 (取消自动，改为用户手动)
        self.calculated.switch_window()
        # self.calculated.relative_swipe(char_pos_list[0], char_pos_list[-1])  # 滑动人物列表
        # time.sleep(1)
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
            relic_hash = self.loadout_data[character_name][team_members[character_name]]["relic_hash"]
            self.equip_loadout(relic_hash)
        log.info(_("队伍配装完毕"))

    def equip_loadout_for_char(self, character_name :Optional[str]=None):
        """
        说明：
            装备当前[角色]界面本人物的遗器配装
        """
        # 识别当前人物名称
        self.calculated.switch_window()
        character_name = self.ocr_character_name() if character_name is None else character_name
        character_data = self.loadout_data[character_name]
        # 选择配装
        if not character_data:  # 字典为空
            log.info(_("当前人物配装记录为空"))
            return
        self.calculated.switch_cmd()
        option = self.ask_loadout_options(character_name, title=_("请选择要装备的配装:"))
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
            # 在筛选遗器前尝试匹配当前遗器表格中的首个遗器 (加快配装)
            pos = self.search_relic(equip_indx, key_hash=tmp_hash, key_data=tmp_data, max_num=1)
            if pos is None:
                # 筛选遗器 (加快遗器搜索)
                relic_filter.do(relic_set_index, rarity)
                # 搜索遗器
                pos = self.search_relic(equip_indx, key_hash=tmp_hash, key_data=tmp_data)
            if pos is None:
                log.error(_(f"遗器搜索失败: {tmp_hash}"))
                continue
            # 点击装备
            # self.calculated.relative_click(pos)   # 重复性点击
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
        char_num = int(questionary.select(_("请选择队伍人数："), ['4','3','2','1']).ask())
        # [2]选择是否为互斥队伍组别 
        group_name = "compatible"     # 默认为非互斥队组别
        ...  # 互斥队组别【待扩展】
        if group_name not in self.team_data:
            self.team_data[group_name] = {}
        group_data = self.team_data[group_name]
        # [3]选择组建方式
        options = {
            _("参考已有的配装记录"): 0,
            _("全识别"): 1,
        }
        option_ = questionary.select(_("请选择组建方式："), options).ask()
        state = options[option_]
        # [4]检查人物列表是否移动至开头 (取消自动，改为用户手动)
        self.calculated.switch_window()
        # self.calculated.relative_swipe(char_pos_list[0], char_pos_list[-1])  # 滑动人物列表
        # time.sleep(1)
        self.calculated.relative_click((12,40) if IS_PC else (16,48))  # 点击导航栏的遗器，进入[角色]-[遗器]界面
        time.sleep(1)
        # [5]依次点击人物，识别配装
        char_index = 0
        is_retrying = False
        character_name = None
        char_weight = StatsWeight()
        loadout_dict = self.HashList2dict()
        while char_index < char_num:
            char_pos = char_pos_list[char_index]
            # [5.1]识别人物名称
            if not is_retrying:    # 如果处于重试，则不再次识别人物名称
                self.calculated.switch_window()
                self.calculated.relative_click(char_pos)    # 点击人物
                time.sleep(2)
                character_name = self.ocr_character_name()  # 识别当前人物名称
                __, char_weight = self.find_char_weight(character_name)
            # [5.2]选择识别当前，还是录入已有
            option = None
            if state == 0:
                self.calculated.switch_cmd()
                option = self.ask_loadout_options(
                    character_name,
                    add_options=[
                        Choice(_("<识别当前配装>"), shortcut_key='y', description=INDENT+_("请使游戏保持在当前[角色]界面")), 
                        Choice(_("<退出>"), shortcut_key='z')]
                )
                if option == _("<退出>"):   # 退出本次编队
                    return
                elif option != _("<识别当前配装>"):
                    loadout_name, relics_hash = option    # 获取已录入的配装数据
                else:
                    self.calculated.switch_window()
                    self.calculated.relative_click((12,40) if IS_PC else (16,48))  # 再次点击导航栏的遗器，防止用户离开此界面
                    time.sleep(1)
            if state == 1 or option == _("<识别当前配装>"):
                self.calculated.switch_window()
                relics_hash = self.save_loadout(char_weight)
                print(_("'{}'配装信息：").format(character_name))
                print_styled_text(self.get_loadout_detail_0(relics_hash, character_name, 2), style=self.msg_style)
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
        print(_("队伍配装信息：{}\n").format("".join("\n  " + str_just(char_name, 10) + " " + self.get_loadout_brief(relics_hash) 
                                                for char_name, relics_hash in zip(char_name_list, relics_hash_list))))
        # [6]自定义名称
        self.calculated.switch_cmd()
        # 统计互斥名称
        names = chain(group_data.keys())    # 队伍互斥名称
        for character_name, loadout_name in zip(char_name_list, loadout_name_list):
            if loadout_name is None:        # 配装互斥名称
                names = chain(names, self.loadout_data[character_name].keys())
        team_name = questionary.text(
            _("命名编队名称:"),
            instruction = _("(将同时作为角色的新建配装名称)"),
            validate = ConflictValidator(names),
        ).ask()
        # team_name = input(_(">>>>命名编队名称 (将同时作为各人物新建配装的名称): "))
        # while team_name in group_data or \
        #     any([team_name in self.loadout_data[character_name] for character_name, loadout_name in zip(char_name_list, loadout_name_list) if loadout_name is None]):
        #     team_name = input(_(">>>>命名冲突，请重命名: "))
        # [7]录入数据
        for i, (char_name, relics_hash, loadout_name) in enumerate(zip(char_name_list, relics_hash_list, loadout_name_list)):
            if loadout_name is None:
                loadout_name_list[i] = team_name
                self.loadout_data[char_name][team_name] = {"relic_hash": relics_hash}
                rewrite_json_file(LOADOUT_FILE_NAME, self.loadout_data)
        group_data[team_name] = {"team_members": {key: value for key, value in zip(char_name_list, loadout_name_list)}}
        rewrite_json_file(TEAM_FILE_NAME, self.team_data)
        log.info(_("编队录入成功"))

    def save_loadout_for_char(self):
        """
        说明：
            保存当前[角色]界面本人物的遗器配装
        """
        self.calculated.switch_window()
        character_name = self.ocr_character_name()  # 识别当前人物名称
        character_data = self.loadout_data[character_name]
        __, char_weight = self.find_char_weight(character_name)
        self.calculated.relative_click((12,40) if IS_PC else (16,48))  # 点击导航栏的遗器，进入[角色]-[遗器]界面
        time.sleep(1)
        relics_hash = self.save_loadout(char_weight)
        self.calculated.switch_cmd()
        print(_("'{}'配装信息：").format(character_name))
        print_styled_text(self.get_loadout_detail_0(relics_hash, character_name, 2), style=self.msg_style)
        loadout_name = self.find_loadout_name(character_name, relics_hash)
        if loadout_name:
            log.info(_(f"配装记录已存在，配装名称：{loadout_name}"))
            return
        # 需作为字典key值，确保唯一性 (但不同的人物可以有同一配装名称)
        loadout_name = questionary.text(_("命名配装名称:"), validate=ConflictValidator(character_data.keys())).ask()
        character_data[loadout_name] = {"relic_hash": relics_hash}
        rewrite_json_file(LOADOUT_FILE_NAME, self.loadout_data)
        log.info(_("配装录入成功"))

    def save_loadout(self, char_weight: StatsWeight=StatsWeight(), max_retries=3) -> list[str]:
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
            if tmp_hash in self.relics_data:
                log.info(_("遗器数据已存在"))
                tmp_data = self.relics_data[tmp_hash]  # 载入可能的速度修正
            else:
                log.info(_("录入遗器数据"))
                self.add_relic_data(tmp_data, tmp_hash)
            log.debug("\n"+pp.pformat(tmp_data))
            self.print_relic(tmp_data, tmp_hash, char_weight)
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
                综合OCR识别与方位计算 (游戏1.5版本共28套遗器)
            参数：
                :param equip_set_index: 遗器套装索引
            """
            is_left = relic_set_index % 2 == 0  # 计算左右栏
            # 计算页数 (页间有重叠，每页滑动4行)
            if relic_set_index < 8:
                page_num = 0
            elif relic_set_index < 16:
                page_num = 1
            elif relic_set_index < 24:
                page_num = 2
            else:
                page_num = 3
            last_page = 3
            # 滑动翻页
            for i in range(page_num):
                time.sleep(0.2)
                self.calculated.relative_swipe((30,60) if IS_PC else (30,62), (30,36) if IS_PC else (30,32)) # 页面翻动4行 (此动作的动态延迟较大)
                if page_num != last_page:  # 非末页，将翻页的动态延迟暂停
                    self.calculated.relative_click((35,35) if IS_PC else (35,32), 0.5)   # 长按选中
                    time.sleep(0.5)
                    self.calculated.relative_click((35,35) if IS_PC else (35,32))        # 取消选中
                elif i == last_page-1:
                    time.sleep(0.5)  # 等待末页的短暂反弹动画停止
            points = ((28,33,42,63) if is_left else (53,33,67,63)) if IS_PC else ((22,29,41,65) if is_left else (53,29,72,65))
            self.calculated.ocr_click(RELIC_SET_NAME[relic_set_index, 1], points=points)


    def search_relic(
        self, equip_indx: Optional[int]=None, 
        key_hash: Optional[str]=None, 
        key_data: Optional[Dict[str, Any]]=None,
        stats_weight: StatsWeight=StatsWeight(),
        max_num :Optional[int]=None, overtime :Optional[int]=180, max_retries=3
    ) -> Union[Optional[tuple[int, int]], Dict[str, Dict[str, Any]]]:
        """
        说明：
            在当前滑动[角色]-[遗器]-[遗器替换]界面内，搜索匹配的遗器。
                key_hash非空: 激活精确匹配 (假设数据保存期间遗器未再次升级); 
                key_data非空: 激活模糊匹配 (假设数据保存期间遗器再次升级，匹配成功后自动更新遗器数据);
                key_hash & key_data均空: 遍历当前页面内的遗器
        参数：
            :param equip_indx: 遗器部位索引 (激活匹配状态时需非空)
            :param key_hash: 所记录的遗器哈希值
            :param key_data: 所记录的遗器数据
            :param stats_weight: 属性权重 (用于修饰遗器打印)
            :param max_num: 搜索的遗器数量上限
            :param overtime: 超时
            :param max_retries: 单个遗器OCR重试次数
        返回:
            :return: 匹配状态返回遗器的坐标，非匹配状态返回遗器记录
        """
        pos_start = (5,24) if IS_PC else (7,28)
        d_x, d_y, k_x, k_y = (7, 14, 4, 5) if IS_PC else (8, 17, 4, 4)
        r_x = range(pos_start[0], pos_start[0]+d_x*k_x, d_x)
        r_y = range(pos_start[1], pos_start[1]+d_y*k_y, d_y)
        relics_data = {"": None}  # 记录识别的遗器，初始化为标记值
        matching = not (key_hash is None and key_data is None)
        skiped_line = False  # 是否执行过跳行功能
        def format_return() -> Optional[Dict[str, Dict[str, Any]]]:
            """
            说明： 格式化返回值
            """
            if matching:  # 激活匹配状态
                return None
            # 非匹配状态
            relics_data.pop("")   # 删除标记值
            return relics_data
        start_time = time.time()
        while True:
            index = 0
            while index < k_y*k_x:
                i = index // k_x   # 行
                j = index % k_x    # 列
                x, y = r_x[j], r_y[i]   # 坐标查表
                self.calculated.relative_click((x, y))   # 点击遗器，同时将翻页的动态延迟暂停
                time.sleep(0.2)
                log.info(f"({i+1},{j+1},{len(relics_data)})")  # 显示当前所识别遗器的方位与序列号
                tmp_data = self.try_ocr_relic(equip_indx, max_retries)
                if tmp_data is None:   # 识别到 "未装备"，即此时遗器表格为空
                    return format_return()
                # log.info("\n"+pp.pformat(tmp_data))
                tmp_hash = get_data_hash(tmp_data)
                # 精确匹配
                if key_hash and key_hash == tmp_hash:
                    return (x, y)
                # 模糊匹配
                if key_data and self.is_fuzzy_match and self.compare_relics(key_data, tmp_data):
                    # 打印对比信息
                    tmp_text = self.print_relic(tmp_data, tmp_hash, stats_weight, False)
                    key_text = self.print_relic(key_data, key_hash, stats_weight, False)
                    print("\n  {:>28}    {:<28}".format("<<<<<<< NEW", "OLD >>>>>>>"))
                    print_styled_text(combine_styled_text(tmp_text, key_text, sep=" "*4, indent=2), style=self.msg_style)
                    log.info(_("模糊匹配成功！识别到新遗器为旧遗器升级后，自动更新数据库"))
                    # 更新数据库 (录入新遗器数据，并将配装数据中的旧有哈希值替换)
                    tmp_data["pre_ver_hash"] = key_hash   # 建立后继关系
                    self.updata_relic_data(key_hash, tmp_hash, equip_indx, tmp_data)
                    return (x, y)
                # 判断是否遍历完毕
                if tmp_hash in relics_data and list(relics_data.keys())[-1] == tmp_hash:
                    log.info(_("点击到空白区域，判定为搜索至最后"))
                    return format_return()   # 判断点击到空白，遗器数据未发生变化，结束搜索
                if j == 0 and tmp_hash in relics_data: # 判断当前行的首列遗器是否已被搜索
                    if i == k_y-1:
                        log.info(_("已搜索至最后"))
                        return format_return()   # 判断已滑动至末页，结束搜索
                    log.info(_("本行已搜索过，跳过本行"))
                    index += k_x     # 本行已搜索过，跳过本行
                    skiped_line = True
                    continue
                if j == k_x-1 and i == k_y-1 and skiped_line:
                    log.info(_("出现过跳行，判定为搜索至最后"))
                    return format_return()   # 出现过跳行操作，且搜索至表尾，判断为搜索结束
                # 判断是否达到搜索上限
                if max_num and len(relics_data) >= max_num:
                    if not matching:
                        self.print_relic(tmp_data, tmp_hash, stats_weight)
                    relics_data[tmp_hash] = tmp_data  # 记录
                    return format_return()
                # 判断是否超时
                if overtime and time.time() - start_time > overtime:
                    log.info(_("识别超时"))
                    return format_return()
                # 非匹配状态，打印每一次的识别结果
                if not matching:
                    self.print_relic(tmp_data, tmp_hash, stats_weight)
                # 本次循环结束
                relics_data[tmp_hash] = tmp_data  # 记录
                index += 1
            # 滑动翻页 (从末尾位置滑动至顶部，即刚好滑动一整页)
            log.info(_("滑动翻页"))
            self.calculated.relative_swipe((pos_start[0], pos_start[1]+(k_y-1)*d_y), (pos_start[0], pos_start[1]-d_y))
    
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
    
    def find_char_weight(self, char_name:str) -> Tuple[Optional[str], StatsWeight]:
        """
            通过角色名查询属性权重
        """
        char_weight = StatsWeight()
        char_weight_name = None
        if char_name in self.char_weight_data:
            char_weights = self.char_weight_data[char_name]
            if len(char_weights) > 0:
                # 默认载入首个
                char_weight = StatsWeight(list(char_weights.values())[0]["weight"])
                char_weight_name =  "{}_{}".format(char_name, list(char_weights.keys())[0])
                ... # 【待扩展】处理多组权重
        return char_weight_name, char_weight

    def find_char_panel(self, char_name:str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
            通过角色名查询裸装面板
        """
        char_panel, char_panel_name = None, None
        if char_name in self.char_panel_data:
            char_panels = self.char_panel_data[char_name]
            if len(char_panels) > 0:
                # 默认载入首个
                char_panel = list(char_panels.values())[0]
                char_panel_name =  "{}_{}".format(char_name, list(char_panels.keys())[0])
                ... # 【待扩展】处理多个面板
        return char_panel_name, char_panel

    def find_loadout_name(self, char_name: str, relics_hash: List[str]) -> Optional[str]:
        """
        说明：
            通过配装数据查询配装名称
        """
        for loadout_name, loadout_data in self.loadout_data[char_name].items():
            if loadout_data["relic_hash"] == relics_hash:
                return loadout_name
        return None

    def find_teams_in_loadout(self, char_name: str, loadout_name: str) -> List[Tuple[str, str]]:
        """
        说明：
            通过角色名与配装名查询所在的队伍
        """
        ret = []
        for group_name, team_group in self.team_data.items():
            for team_name, team_data in team_group.items():
                if (char_name, loadout_name) in team_data["team_members"].items():
                    ret.append((group_name, team_name))
        return ret

    def updata_loadout_data(self, char_name: str, old_name: str, new_name: str, new_data: Optional[Dict[str, Any]]=None) -> bool:
        """
        说明：
            更改配装数据，先后修改配装与队伍文件，
            若修改了遗器配装，需检查队伍配装规范性
        """
        # 尝试修改配装文件
        if new_data is None:
            self.loadout_data[char_name][new_name] = self.loadout_data[char_name].pop(old_name)
        else:
            self.loadout_data[char_name].pop(old_name)
            self.loadout_data[char_name][new_name] = new_data
        # 尝试修改队伍文件
        check = True
        teams_in_loadout = self.find_teams_in_loadout(char_name, old_name)
        for group_name, team_name in teams_in_loadout:
            team_data = self.team_data[group_name][team_name]
            team_data["team_members"][char_name] = new_name
            if new_data is not None:   # 若修改了遗器配装，需检查队伍配装规范性
                check = self.check_team_loadout(team_name, team_data)
        if check:  # 校验成功，保存修改
            rewrite_json_file(LOADOUT_FILE_NAME, self.loadout_data)
            rewrite_json_file(TEAM_FILE_NAME, self.team_data)
            log.info(_("配装修改成功"))
            return True
        else:      # 校验失败，任务回滚
            self.loadout_data = read_json_file(LOADOUT_FILE_NAME)
            self.team_data = read_json_file(TEAM_FILE_NAME)
            log.error(_("配装修改失败"))
            return False

    def check_team_data(self) -> bool:
        """
        说明：
            检查队伍配装数据的数据完整性与配装规范性
        """
        ret = True
        for group_name, team_group in self.team_data.items():
            for team_name, team_data in team_group.items():
                ret = self.check_team_loadout(team_name, team_data)
            if group_name != "compatible": ...   # 互斥队伍组别【待扩展】
        if ret:
            log.info(_("队伍配装校验成功"))
        return ret
    
    def check_team_loadout(self, team_name: str, team_data: Dict[str, Any]) -> bool:
        """
        说明：
            检查当前队伍配装的数据完整性与配装规范性
        """
        ret = True
        loadout_dict = self.HashList2dict()
        # 数据完整性
        for char_name, loadout_name in team_data["team_members"].items():
            char_data = self.loadout_data.get(char_name)
            if char_data is None:
                log.error(_("角色记录缺失：'{}'队伍的'{}'角色记录缺失").format(team_name, char_name))
                ret = False
                continue
            loadout_data = char_data.get(loadout_name)
            if loadout_data is None:
                log.error(_("配装记录缺失：'{}'队伍的'{}'角色的'{}'配装记录缺失").format(team_name, char_name, loadout_name))
                ret = False
                continue
            loadout_dict.add(loadout_data["relic_hash"], char_name)
        # 配装规范性
        for equip_index, char_names, element in loadout_dict.find_duplicate_hash():
            log.error(_("队伍遗器冲突：'{}'队伍的{}间的'{}'遗器冲突，遗器哈希值：{}").format(team_name, char_names, EQUIP_SET_NAME[equip_index], element))
            ret = False
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
        equip_set_dict = Array2dict(EQUIP_SET_NAME)
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
                if hash_list["relic_hash"][equip_indx] == old_hash:
                    self.loadout_data[char_name][loadout_name]["relic_hash"][equip_indx] = new_hash
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
        character_name = re.sub(r"[.’,，。、·'-_——「」/|\[\]\"\\\s]", '', str)   # 删除由于背景光点造成的误判
        log.info(_(f"识别人物: {character_name}"))
        if character_name not in self.loadout_data:
            self.loadout_data = modify_json_file(LOADOUT_FILE_NAME, character_name, {})
            log.info(_("创建新人物"))
        return character_name
    
    def try_ocr_relic(self, equip_set_index:Optional[int]=None, max_retries=3) -> Optional[Dict[str, Any]]:
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
        debug = False
        while True:  # 视作偶发错误进行重试
            try:  
                data = self.ocr_relic(equip_set_index, debug)
                return data
            except: 
                if retry >= max_retries:
                    self.calculated.switch_cmd()
                    questionary.print(_("请检查是否按要求与建议进行操作。\n若仍然发生此错误，请同时上传相应的日志文件与'logs/image'目录下的相应截图至交流群或gihub"), "orange")
                    raise Exception(_("重试次数达到上限"))
                retry += 1
                debug = True  # 开启对识别区域的截图保存
                log.info(_(f"第 {retry} 次尝试重新OCR"))

    def ocr_relic(self, equip_set_index: Optional[int]=None, debug=False) -> Optional[Dict[str, Any]]:
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
            equip_set_index = self.calculated.ocr_pos_for_single_line(EQUIP_SET_NAME, points=(77,19,83,23) if IS_PC else (71,22,78,26), img_pk=img_pc, debug=debug)
            if equip_set_index < 0:
                raise RelicOCRException(_("遗器套装OCR错误"))
        equip_set_name = EQUIP_SET_NAME[equip_set_index]
        # [2]套装识别
        name_list = RELIC_SET_NAME[:, 0].tolist()
        name_list = name_list[:RELIC_INNER_SET_INDEX] if equip_set_index < 4 else name_list[RELIC_INNER_SET_INDEX:]   # 取外圈/内圈的切片
        name_list += [_("未装备")]
        relic_set_index = self.calculated.ocr_pos_for_single_line(name_list, points=(77,15,92,19) if IS_PC else (71,17,88,21), img_pk=img_pc, debug=debug)
        if relic_set_index < 0: 
            raise RelicOCRException(_("遗器部位OCR错误"))
        if relic_set_index == len(name_list)-1:   # 识别到"未装备"，即遗器为空
            return None
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
        level = self.calculated.ocr_pos_for_single_line(points=(95,19,98,23) if IS_PC else (94,22,98,26), number=True, img_pk=img_pc, debug=debug)
        level = int(level.split('+')[-1])  # 消除开头可能的'+'号
        if level > 15:
            raise RelicOCRException(_("遗器等级OCR错误"))
        # [5]主属性识别
        name_list = BASE_STATS_NAME_FOR_EQUIP[equip_set_index][:, 0].tolist()
        base_stats_index = self.calculated.ocr_pos_for_single_line(name_list, points=(79.5,25,92,29) if IS_PC else (74,29,89,34), img_pk=img_pc, debug=debug)
        base_stats_value = self.calculated.ocr_pos_for_single_line(points=(93,25,98,29) if IS_PC else (91,29,98,34), number=True, img_pk=img_pc, debug=debug)
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
            # 必须先识别属性数值，后识别属性名称 
            # (当副词条不足4个时，需判定识别结果为空，而此时属性名称的识别区域会可能与下方的"套装效果"文字重合使结果非空)
            tmp_value = self.calculated.ocr_pos_for_single_line(points=value_point, number=True, img_pk=img_pc, debug=debug)
            if tmp_value:
                tmp_value = str(tmp_value).replace('.', '')   # 删除所有真假小数点
            if tmp_value is None or tmp_value == '':
                break    # 所识别data为空，判断词条为空，正常退出循环
            tmp_index = self.calculated.ocr_pos_for_single_line(name_list, points=name_point, img_pk=img_pc, debug=debug)
            if tmp_index is None or tmp_index < 0:
                raise RelicOCRException(_("遗器副词条OCR错误"))
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
    
    def print_relic(
        self, data: Dict[str, Any], relic_hash: Optional[str]=None, 
        char_weight: StatsWeight=StatsWeight(), flag=True
    ) -> Optional[StyledText]:
        """
        说明：
            打印遗器信息 (占用窗口列数28)，
            可通过`detail_for_relic`设置打印普通信息与详细信息，
        参数：
            :param data: 遗器数据
            :param relic_hash: 遗器哈希值 (填入即打印)
            :param char_weight: 角色属性权重
            :param flag: 是-打印，否-返回文本
        """
        token = StyledText()
        rarity = data["rarity"]
        token.append("{:<3}".format("+"+str(data["level"])), "bold")
        token.append(" {}".format(str_just(data["equip_set"], 7)))
        token.append(" {star:>5}".format(star='★'*rarity), f"rarity_{rarity}")
        # 副词条
        sub_token = StyledText()
        subs_stats_dict = Array2dict(SUBS_STATS_NAME)
        total_num = 0   # 总词条数或有效词条数
        bad_num = 0     # 强化歪了的次数
        good_num = 0    # 强化中了的次数
        for name, value in data["subs_stats"].items():
            pre = " " if name in NOT_PRE_STATS else "%"
            if not self.is_detail or rarity not in [4,5]:    # 不满足校验条件
                sub_token.append(_("   ■ {name}      {value:>6.{nd}f}{pre}\n").format(name=str_just(name, 10), value=value, pre=pre, nd=self.ndigits))
                continue
            stats_index = subs_stats_dict[name]
            # 增强信息并校验数据
            ret = self.get_subs_stats_detail((name, value), rarity, stats_index)
            if ret:  # 数据校验成功
                level, score, result = ret
                num = self.get_num_of_stats(ret, rarity)  # 计算词条数
                if char_weight and char_weight.get_weight(name) > 0 or not char_weight:
                    total_num += num
                    good_num += level-1
                if char_weight and char_weight.get_weight(name) == 0:
                    bad_num += level-1
                tag = '>'*(level-1)   # 强化次数的标识
                sub_token.append(
                    _(" {num:.1f} {name}{tag:<6}{value:>6.{nd}f}{pre}\n"). \
                        format(name=str_just(name, 10), tag=tag, value=result, num=num, pre=pre, nd=self.ndigits),
                    char_weight.get_color(name))
            else:    # 数据校验失败
                sub_token.append(" ERR", "red")  
                sub_token.append(_(" {name}      {value:>6.{nd}f}{pre}\n").format(name=str_just(name, 10), value=value, pre=pre, nd=self.ndigits))           
        # 填充空缺的副词条 (防止遗器联合打印时出现错位)
        for __ in range(4-len(data["subs_stats"])):
            sub_token.append(_("{:>5}{}\n").format(" ", str_just(_("---空---"), 23)), "grey")
        # 遗器得分
        ...   # 计算方法【待扩展】
        if rarity in [6]:   # 此处为示例
            token.append(_(" 36.9分"), "highlighted")
            token.append(_(" SSS\n"), "orange")
        else:
            token.append(" "*11+"\n")
        # 套装
        token.append(str_just("="+data["relic_set"]+"=", 18))
        # 副词条统计
        if not self.is_detail or rarity not in [4,5]:
            token.append(" "*10+"\n")
        elif char_weight:
            if good_num == 0:  # 未有副词条的强化次数
                token.append(_("  有效 "), "green")
            elif bad_num == 0:
                token.append(_("  全中 "), "green")
            else:
                token.append(_(" 歪{}次 ").format(bad_num), "green")
            token.append("{:>3.1f}\n".format(total_num), "green")
        else:
            token.append("  总计 ", "green")
            token.append("{:>3.1f}\n".format(total_num), "green")
        # 主词条
        name, value = list(data["base_stats"].items())[0]
        pre = " " if name in NOT_PRE_STATS else "%"
        result = self.get_base_stats_detail((name, value), rarity, data["level"])
        if result:
            token.append(_("■ {name}{value:>6.{nd}f}{pre}\n").format(name=str_just(name, 19), value=result, pre=pre, nd=self.ndigits))
        else:
            token.append(_("■ {name} ").format(name=str_just(name, 13)))
            token.append("ERR", "red")
            token.append(_("  {value:>6.{nd}f}{pre}\n").format(value=value, pre=pre, nd=self.ndigits))
        token.extend(sub_token)
        if relic_hash:
            token.append("{:>28}\n".format("hash:"+relic_hash[:10]), "grey")
        if flag:
            print_styled_text(token, style=self.msg_style)
        else:
            return token

    def print_stats_weight(self, stats_weight: Union[StatsWeight, Dict[str, float]]) -> Optional[StyledText]:
        """
        说明：
            打印属性权重信息
        """
        if isinstance(stats_weight, dict):
            stats_weight = StatsWeight(stats_weight)
        token = StyledText()
        has_ = False  # 标记有无属性伤害
        for index, name in enumerate(WEIGHT_STATS_NAME):
            value = stats_weight.get_weight(name, True)
            value_str = "{:.2f}".format(value)
            if index >= 11:   # 过滤属性伤害
                if index == 17 and not has_ and value == 0 :  # 无属性伤害的情形
                    token.append(str_just(_("属性伤害"), 15) + f"{value_str:>7}\n", "weight_0")
                    continue
                elif value == 0:
                    continue
                else:  has_ = True
            token.append(str_just(name, 15) + f"{value_str:>7}\n", stats_weight.get_color(name, True))
        return token

    def ask_loadout_options(
        self, character_name: str,
        add_options: Optional[List[Choice]] = [Choice(_("<返回上一级>"), shortcut_key='z')],
        title: str = _("请选择配装:"),
    ) -> Union[Tuple[str, List[str]], str]:
        """
        说明：
            询问并获得该角色配装的选择
        参数：
            :param character_name: 人物名称
            :param add_options: 附加选项 (注意已占用快捷键'x','v'，需要至少有一个退出选项)
            :param title: 标题
        返回：
            :return option: (配装名称，遗器哈希值列表)元组 或 附加选项名称
        """
        options = self.get_loadout_options(character_name)
        if options:
            if self.loadout_detail_type == 0:
                options.append(Choice(_("<<切换为遗器详情>>"), shortcut_key='v'))
                options.append(
                    Choice(
                        _("<<关闭条件效果>>") if self.activate_conditional else _("<<开启条件效果>>"), shortcut_key='x',
                        description = INDENT+_("涵盖[遗器套装效果]与自定义的[角色裸装面板]中的条件效果")+INDENT+_("开启时，默认激活全部条件效果的最大效果")
                    )
                )  # 【待扩展】自动激活达到可计算触发条件的条件效果
            else:
                options.append(Choice(_("<<切换为面板详情>>"), shortcut_key='v'))
        else:
            options.append(Separator(_("--配装记录为空--")))
        if add_options:
            options.extend(add_options)
        options.append(Separator(" "))
        option = questionary.select(title, choices=options, use_shortcuts=True, style=self.msg_style).ask()
        if option in [_("<<切换为遗器详情>>"), _("<<切换为面板详情>>")]:
            self.loadout_detail_type = (self.loadout_detail_type + 1) & 1
            return self.ask_loadout_options(character_name, add_options)
        if option in [_("<<关闭条件效果>>"), _("<<开启条件效果>>")]:
            self.activate_conditional = not self.activate_conditional
            return self.ask_loadout_options(character_name, add_options)
        return option

    def get_team_options(self) -> List[Choice]:
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
        group_data = sorted(group_data.items())      # 按键名即队伍名称排序
        ...  # 获取互斥队伍组别信息【待扩展】
        prefix = "\n" + " " * 5
        choice_options = [Choice(
                title = str_just(team_name, 12), 
                value = team_data["team_members"],
                description = "".join(
                        prefix + str_just(char_name, 10) + " " + self.get_loadout_brief(self.loadout_data[char_name][loadout_name]["relic_hash"]) 
                    for char_name, loadout_name in team_data["team_members"].items())
            ) for team_name, team_data in group_data]
        return choice_options

    def get_loadout_options(self, character_name: str) -> List[Choice]:
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
        character_data = sorted(character_data.items())      # 按键名即配装名排序
        choice_options = [Choice(
                title = str_just(loadout_name, 16) + " " + self.get_loadout_brief(loadout_data["relic_hash"]), 
                value = (loadout_name, loadout_data["relic_hash"]),
                description = self.get_loadout_detail(loadout_data["relic_hash"], character_name, 5)
            ) for loadout_name, loadout_data in character_data]
        return choice_options

    def get_loadout_detail(self, relics_hash: List[str], character_name: Optional[str]=None, indent_num: int=0) -> StyledText:
        """
        说明：
            获取配装的详细信息 (0-面板详情，1-遗器详情)
        参数：
            :param relics_hash: 遗器哈希值列表
            :param indent_num: 缩进长度
            :param character_name: 人物名称 (非空时激活人物裸装面板统计)
        """
        if self.loadout_detail_type == 0:
            return self.get_loadout_detail_0(relics_hash, character_name, indent_num)
        if self.loadout_detail_type == 1:
            return self.get_loadout_detail_1(relics_hash, character_name, indent_num-3)

    def get_loadout_detail_1(self, relics_hash: List[str], character_name: Optional[str]=None, indent_num: int=0) -> StyledText:
        """
        说明：
            获取配装的遗器详情
        参数：
            :param relics_hash: 遗器哈希值列表
            :param character_name: 人物名称 (非空时激活人物属性权重)
            :param indent_num: 缩进长度
        """
        msg = StyledText()
        text_list = []
        # 查询角色裸装面板
        char_weight_name, char_weight = self.find_char_weight(character_name)
        # 处理遗器数据
        # for equip_index in [0,2,4,1,3,5]:  # 优化部位显示顺序
        for equip_index in range(len(relics_hash)):   # 主流显示顺序
            tmp_hash = relics_hash[equip_index]
            tmp_data = self.relics_data[tmp_hash]
            text_list.append(self.print_relic(tmp_data, tmp_hash, char_weight, False))
        msg.append(_("词条挡位权值{}\n").format(SUBS_STATS_TIER_WEIGHT[self.subs_stats_iter_weight][-1]))
        msg.append("\n")
        msg.extend(combine_styled_text(*text_list[:3], sep="  ", indent=indent_num))
        msg.append("\n")
        msg.extend(combine_styled_text(*text_list[3:], sep="  ", indent=indent_num))
        indent = "\n" + " "*indent_num
        msg.append(indent)
        msg.append(_("属性权重'{}'").format(char_weight_name) if char_weight else _("未启用权重"))
        msg.append(_("  评分系统开发中...\n"), "grey")
        return msg

    def get_loadout_detail_0(self, relics_hash: List[str], character_name: Optional[str]=None, indent_num: int=0) -> StyledText:
        """
        说明：
            获取配装的面板详情
        参数：
            :param relics_hash: 遗器哈希值列表
            :param character_name: 人物名称 (非空时激活人物裸装面板与属性权重)
            :param indent_num: 缩进长度
        """
        stats_panel_S = np.zeros(len(ALL_STATS_NAME))   # 固定属性面板
        stats_panel_C = np.zeros(len(ALL_STATS_NAME))   # 条件属性面板
        extra_effect_list = []   # 额外效果说明
        stats_name_dict = Array2dict(ALL_STATS_NAME)
        base_stats_dict = Array2dict(BASE_STATS_NAME)
        subs_stats_dict = Array2dict(SUBS_STATS_NAME)
        # [0.1]查询角色裸装面板
        char_panel_name, char_panel = self.find_char_panel(character_name)
        # [0.2]查询角色属性权重
        char_weight_name, char_weight = self.find_char_weight(character_name)
        # [1]统计遗器主副属性
        relic_subs_nums = [.0]*6    # 各部位遗器的副词条词条总数
        for equip_index, relic_hash in enumerate(relics_hash):
            tmp_data: Dict[str, Dict[str, float]] = self.relics_data[relic_hash]
            rarity = tmp_data["rarity"]
            level = tmp_data["level"]
            stats_list = [(key, self.get_base_stats_detail((key, value), rarity, level, base_stats_dict[key]))
                          for key, value in tmp_data["base_stats"].items()]           # 获取数值精度提高后的主词条
            for key, value in tmp_data["subs_stats"].items():
                ret = self.get_subs_stats_detail((key, value), rarity, subs_stats_dict[key])
                stats_list.append((key, ret[-1]))        # 获取数值精度提高后的副词条
                num = self.get_num_of_stats(ret, rarity)   # 计算词条数
                if char_weight and char_weight.get_weight(key) > 0 or not char_weight:
                    relic_subs_nums[equip_index] += num    # 当有权重时统计有效词条，无权重时统计总词条
            for key, value in stats_list:
                stats_panel_S[stats_name_dict[key]] += value  # 数值统计
        # [2]统计遗器套装效果
        set_cnt: Counter = self.get_loadout_brief(relics_hash, False)
        def parse_set_effect(set_effect_list: List[StatsEffect]):
            """
            说明： 解析遗器套装效果，进行数值统计
            """
            for effect in set_effect_list:
                if isinstance(effect, str):
                    extra_effect_list.append(effect)
                elif isinstance(effect, tuple):
                    key, value, unconditional = effect
                    if unconditional:   # 非条件效果
                        stats_panel_S[stats_name_dict[key]] += value
                    elif not unconditional and self.activate_conditional: # 已开启的条件效果
                        stats_panel_C[stats_name_dict[key]] += value
        for set_idx, cnt in set_cnt.items():
            if cnt >= 2:    # 激活二件套效果
                parse_set_effect(SET_EFFECT_OF_TWO_PC[set_idx])
            if cnt >= 4:    # 激活四件套效果
                parse_set_effect(SET_EFFECT_OF_FOUR_PC[set_idx])
        # [3]统计人物裸装面板
        def parse_char_stats_panel() -> List[Tuple[float, float]]:
            """
            说明：解析人物裸装面板，引用传递返回参数stats_panel
            """
            # 统计附加属性
            additonal_stats = char_panel.get("additonal", {})
            for key, value in additonal_stats.items():
                stats_panel_S[stats_name_dict[key]] += value
            # 统计条件属性
            conditional_stats = char_panel.get("conditional", {})
            if self.activate_conditional:
                for key, value in conditional_stats.items():
                    stats_panel_C[stats_name_dict[key]] += value
            # 统计额外效果
            extra_effect_list.extend(char_panel.get("extra_effect", []))
            # 通过白值计算绿值
            b_value: Dict[str, float] = char_panel["base"]
            bs_value = [b_value[_("生命值白值")], b_value[_("攻击力白值")], b_value[_("防御力白值")], b_value[_("速度白值")]]
            en_value = []
            for i, j, base in zip([3,4,5,7], [0,1,2,6], bs_value):  # 大小词条的索引
                large = stats_panel_S[i] + stats_panel_C[i]
                small = stats_panel_S[j] + stats_panel_C[j]
                en_value.append(base * large / 100 + small)
            return list(zip(bs_value, en_value))
        if char_panel:
            bs_and_en_value = parse_char_stats_panel()
        else:
            bs_and_en_value = [(0, 0)] * len(BASE_VALUE_NAME)
        # [4]合成属性分词 
        token_list: List[StyledText] = []
        total_stats_num = .0
        has_ = False  # 标记有无属性伤害
        normal_stats_len = len(STATS_NAME)   # 额外属性的起始索引 (预防被激活多个属性伤害的情形)
        for index, (std, cnd) in enumerate(zip(stats_panel_S, stats_panel_C)):
            name = ALL_STATS_NAME[index]
            value = std + cnd
            color = char_weight.get_color(name) if index < len(STATS_NAME) else ""
            if index in range(15, 22):   # 过滤属性伤害
                if index == 21 and not has_ and value == 0 :  # 无属性伤害的情形
                    name = _("属性伤害")
                elif value == 0:
                    normal_stats_len -= 1
                    continue
                else:  has_ = True
            elif index >= len(STATS_NAME) and value == 0: 
                continue                                 # 跳过无效的额外属性
            token = StyledText()
            pre = " " if name in NOT_PRE_STATS else "%"
            # 词条数量
            subs_idx = subs_stats_dict[name]
            if subs_idx is not None or name == _("速度%") and value != 0 and char_panel:
                tmp_name, tmp_value = name, value  # 修饰
                if name == _("速度%"):  # 将速度大词条转化为小词条来计算
                    tmp_name = _("速度")
                    tmp_value = bs_and_en_value[3][0] * value / 100
                elif char_panel and name == _("暴击率"):    # 减去面板默认提供的
                    tmp_value = value - 5
                elif char_panel and  name == _("暴击伤害"): # 减去面板默认提供的
                    tmp_value = value - 50
                num = self.get_num_of_stats(self.get_subs_stats_detail((tmp_name, tmp_value), 5, subs_idx, check=False))
                if char_weight and char_weight.get_weight(name) > 0 or not char_weight:
                    total_stats_num += num
                token.append("{:>4.1f} ".format(num), color)
            else:
                token.append(" " * 5)
            # 名称数值
            token.append(
                "{name}{value:>7.{ndigits}f}{pre}".format(name=str_just(name, 13), value=value, pre=pre, ndigits=self.ndigits), color
            )
            # 条件效果
            if self.activate_conditional and cnd != 0:
                # token.append("{std:>4.{ndigits}f}".format(std=std, ndigits=self.ndigits), "")
                token.append("{cnd:>7.{ndigits}f}".format(cnd=cnd, ndigits=self.ndigits), "green")
            elif self.activate_conditional:
                token.append(" " * 7)
            token_list.append(token)
        # # 更改属性的打印顺序
        # token_list = token_list[0:1]+token_list[3:4]+token_list[1:2]+token_list[4:5]+token_list[2:3]+token_list[5:6]+token_list[6:]
        # [5]打印信息
        msg = StyledText()
        indent = " " * indent_num
        indent_ = "\n" + indent
        msg.append(_("词条挡位权值{}\n").format(SUBS_STATS_TIER_WEIGHT[self.subs_stats_iter_weight][-1]))
        def format_table(sequence: List[StyledText], column=2, reverse=True) -> StyledText:
            """
            说明： 打印单个表单
            """
            msg = StyledText()
            sep = "   "
            for index in range(len(sequence)):   # 分栏输出 (纵向顺序，横向逆序，保证余数项在左栏)
                i = index // column
                j = index % column
                n = ((column-j-1) * len(sequence) // column + i) if reverse else (j * len(sequence) // column + i)
                msg.append(sep if j != 0 else indent_)
                msg.extend(sequence[n])
            if msg: msg.append("\n")
            return msg
        # [5.1]打印遗器简要信息
        relic_list: List[StyledText] = []
        # for equip_index in range(len(relics_hash)):   # 优化部位显示顺序
        for equip_index in [0,3,1,4,2,5]:  # 主流显示顺序
            token = StyledText()
            relic_hash = relics_hash[equip_index]
            num = relic_subs_nums[equip_index]   # 词条数
            tmp_data = self.relics_data[relic_hash]
            rarity = tmp_data["rarity"]
            token.append("{:.1f}".format(num), "green")
            token.append("{}".format(EQUIP_SET_ADDR[equip_index]))
            token.append(":{}".format(relic_hash[:10]))
            relic_list.append(token)
        msg.extend(format_table(relic_list, 3, False))
        # [5.2]打印白值绿值
        msg.append("\n")
        for idx, (bs, en) in enumerate(bs_and_en_value):
            name = BASE_VALUE_NAME[idx]
            msg.append(indent)
            msg.append("{name}".format(name=str_just(name[:int(_("-2"))], 8)), char_weight.get_color(name))  # 截除某尾的‘白值’字样
            msg.append("{total:>9.{ndigits}f}".format(total=bs+en, ndigits=self.ndigits), char_weight.get_color(name))
            msg.append("{bs:>9.{ndigits}f}".format(bs=bs, ndigits=self.ndigits), "")
            msg.append("{en:>9.{ndigits}f}".format(en=en, ndigits=self.ndigits), "green")
            msg.append("  | ")  # 分隔符
            # [5.3]利用右侧空间打印其他信息
            if idx == 0:
                msg.append(_("遗器副词条"))
                msg.append("{:.1f}".format(sum(relic_subs_nums)), "green")
                msg.append(_(" 总计词条"))
                msg.append("{:.1f}".format(total_stats_num), "green")
            elif idx == 1:
                msg.append(_("裸装面板'{}'").format(char_panel_name) if char_panel else _("未启用裸装面板"))
            elif idx == 2:
                msg.append(_("属性权重'{}'").format(char_weight_name) if char_weight else _("未启用权重"))
            elif idx == 3:
                msg.append(_("评分系统开发中..."), "grey")
            msg.append("\n")
        # [5.4]打印属性数值统计
        msg.extend(format_table(token_list[:normal_stats_len]))  # 遗器主副属性
        msg.extend(format_table(token_list[normal_stats_len:]))  # 额外属性
        # [5.5]打印额外效果
        if extra_effect_list:
            msg.append("\n" + " " * (indent_num-3) + _("额外效果："))
            msg.append("".join(indent_ + f"{i+1}) {text}"  for i, text in enumerate(extra_effect_list)))
        msg.append("\n")
        return msg

    def get_loadout_brief(self, relics_hash: List[str], flag = True) -> Union[str, Counter]:
        """
        说明：
            获取配装的简要信息 (包含内外圈套装信息与主词条信息)
        参数：
            :param relics_hash: 遗器哈希值列表
            :param flag: 如果`True`返回消息，如果`False`返回遗器套装计数器
        """
        set_name_dict = Array2dict(RELIC_SET_NAME)
        stats_abbr_dict = Array2dict(BASE_STATS_NAME, -1, 1)
        outer_set_list, inner_set_list, base_stats_list = [], [], []
        # 获取遗器数据
        for equip_indx in range(len((relics_hash))):
            tmp_data = self.relics_data[relics_hash[equip_indx]]
            tmp_set = set_name_dict[tmp_data["relic_set"]]
            tmp_base_stats = stats_abbr_dict[list(tmp_data["base_stats"].keys())[0]]
            base_stats_list.append(tmp_base_stats)
            if equip_indx < 4:
                outer_set_list.append(tmp_set)  # 外圈
            else:
                inner_set_list.append(tmp_set)  # 内圈
        outer_set_cnt = Counter(outer_set_list)
        inner_set_cnt = Counter(inner_set_list)
        if not flag:
            return outer_set_cnt + inner_set_cnt
        # 生成信息
        outer = _("外:") + '+'.join([str(cnt) + RELIC_SET_NAME[set_idx, 2] for set_idx, cnt in outer_set_cnt.items()])
        inner = _("内:") + '+'.join([str(cnt) + RELIC_SET_NAME[set_idx, 2] for set_idx, cnt in inner_set_cnt.items()])
        stats = ".".join([name for idx, name in enumerate(base_stats_list) if idx > 1])   # 排除头部与手部
        msg = str_just(stats, 17) + "  " + str_just(inner, 10) + "  " + outer   # 将长度最不定的外圈信息放至最后
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

    def get_subs_stats_detail(self, data: Tuple[str, float], rarity: int, stats_index: Optional[int]=None, check=True) -> Optional[Tuple[int, int, float]]:
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
            :param check: 开启校验
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
        # 不启用校验，用于统计词条使用
        if not check:
            log.debug(f"({name}, {value}): [{a}, {d}], l={level}, s={score}, r={result}")
            return (level, score, result)
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
    
    def get_num_of_stats(self, stats_detail: Tuple[int, int, Any], rarity: int=5) -> Optional[float]:
        """
        说明：
            计算词条数量
        """
        if rarity not in [4,5]:
            return None
        level, score, __ = stats_detail
        level_w, score_w, __ = SUBS_STATS_TIER_WEIGHT[self.subs_stats_iter_weight]
        num = level*level_w + score*score_w
        if rarity == 4:  # 四星与五星遗器比值为 0.8
            num *= 0.8
        return num
