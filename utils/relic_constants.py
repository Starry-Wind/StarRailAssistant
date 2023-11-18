"""
遗器模块相关静态数据
"""
import numpy as np
from typing import Any, Dict, List, Literal, Optional, Tuple, Union
from .config import _

StatsEffect = Union[str, Tuple[str, Optional[int], bool]]


EQUIP_SET_NAME = [_("头部"), _("手部"), _("躯干"), _("脚部"), _("位面球"), _("连结绳")]
"""遗器部位名称，已经按游戏界面顺序排序"""

EQUIP_SET_ADDR = [_("头"), _("手"), _("衣"), _("鞋"), _("球"), _("绳")]
"""遗器部位简称"""

RELIC_SET_NAME = np.array([  # 注：因为数据有时要行取有时要列取，故采用数组存储
# 外圈
    [_("过客"), _("过客"), _("治疗"), _("云无留迹的过客")],
    [_("枪手"), _("枪手"), _("快枪手"), _("野穗伴行的快枪手")], 
    [_("圣骑"), _("圣骑"), _("圣骑"), _("净庭教宗的圣骑士")], 
    [_("雪猎"), _("猎人"), _("冰套"), _("密林卧雪的猎人")], 
    [_("拳王"), _("拳王"), _("物理套"), _("街头出身的拳王")], 
    [_("铁卫"), _("铁卫"), _("铁卫"), _("戍卫风雪的铁卫")], 
    [_("火匠"), _("火匠"), _("火套"), _("熔岩锻铸的火匠")], 
    [_("天才"), _("天才"), _("量子套"), _("繁星璀璨的天才")],
    [_("乐队"), _("雷电"), _("雷套"), _("激奏雷电的乐队")], 
    [_("翔"),   _("翔"),   _("风套"), _("晨昏交界的翔鹰")], 
    [_("怪盗"), _("怪盗"), _("怪盗"), _("流星追迹的怪盗")],
    [_("废"),   _("废"),   _("虚数套"), _("盗匪荒漠的废土客")],
    [_("者"),   _("长存"), _("莳者"), _("宝命长存的莳者")], 
    [_("信使"), _("信使"), _("信使"), _("骇域漫游的信使")], 
    [_("大公"), _("大公"), _("追击套"), _("毁烬焚骨的大公")], 
    [_("系囚"), _("系囚"), _("DOT套"), _("幽锁深牢的系囚")], 
# 内圈
    [_("黑塔"), _("太空"), _("空间站"), _("太空封印站")], 
    [_("仙"),   _("仙"),   _("仙舟"), _("不老者的仙舟")], 
    [_("公司"), _("公司"), _("命中"), _("泛银河商业公司")], 
    [_("贝洛"), _("贝洛"), _("防御"), _("筑城者的贝洛伯格")],   # 注：有散件名为'贝洛伯格的铁卫防线'
    [_("丝星"), _("差分"), _("差分"), _("星体差分机")], 
    [_("萨尔"), _("停转"), _("停转"), _("停转的萨尔索图")], 
    [_("利亚"), _("盗贼"), _("击破"), _("盗贼公国塔利亚")], 
    [_("瓦克"), _("瓦克"), _("翁瓦克"), _("生命的翁瓦克")], 
    [_("泰科"), _("繁星"), _("繁星"), _("繁星竞技场")], 
    [_("伊须"), _("龙骨"), _("龙骨"), _("折断的龙骨")],
    [_("格拉"), _("格拉"), _("苍穹"), _("苍穹战线格拉默")],
    [_("匹诺"), _("匹诺"), _("匹诺"), _("梦想之地匹诺康尼")],
], dtype=np.str_)
"""遗器套装名称：0-套装散件名的共有词(ocr-必须)，1-套装名的特异词(ocr-可选，为了增强鲁棒性)，2-玩家惯用简称(print)，3-套装全称(json)，已按[1.4游戏]遗器筛选界面排序 (且前段为外圈，后段为内圈)"""

RELIC_INNER_SET_INDEX = 16
"""RELIC_SET_NAME参数的遗器内圈的起始点索引"""

STATS_NAME = np.array([
    [_("命值"), _("生"), _("生命值")], 
    [_("击力"), _("攻"), _("攻击力")], 
    [_("防"), _("防"), _("防御力")], 
    [_("命值"), _("生"), _("生命值%")], 
    [_("击力"), _("攻"), _("攻击力%")], 
    [_("防"), _("防"), _("防御力%")],
    [_("度"), _("速"), _("速度")], 
    [_("度"), _("速"), _("速度%")],        # 注：非遗器主副属性 (不用于OCR，因为属性相关性放置在此)
    [_("击率"), _("暴击"), _("暴击率")], 
    [_("击伤"), _("爆伤"), _("暴击伤害")], 
    [_("治疗"), _("治疗"), _("治疗量加成")],
    [_("命中"), _("命中"), _("效果命中")], 
    [_("抵抗"), _("效果抵抗"), _("效果抵抗")], 
    [_("破"), _("击破"), _("击破特攻")], 
    [_("恢复"), _("能"), _("能量恢复效率")],
    [_("理"), _("伤害"), _("物理属性伤害")], 
    [_("火"), _("火伤"), _("火属性伤害")], 
    [_("冰"), _("冰伤"), _("冰属性伤害")], 
    [_("雷"), _("雷伤"), _("雷属性伤害")], 
    [_("风"), _("风伤"), _("风属性伤害")], 
    [_("量"), _("量子"), _("量子属性伤害")], 
    [_("数"), _("虚数"), _("虚数属性伤害")], 
], dtype=np.str_)
"""遗器属性名称：0-属性名的特异词(ocr-不区分大小词条)，1-玩家惯用简称(print)，2-属性全称(json-区分大小词条)"""

BASE_VALUE_NAME = [_("生命值白值"), _("攻击力白值"), _("防御力白值"), _("速度白值")]
"""角色白值属性名称"""

NOT_PRE_STATS = [_("生命值"), _("攻击力"), _("防御力"), _("速度")] + BASE_VALUE_NAME
"""遗器的整数属性名称"""

BASE_STATS_NAME = np.concatenate((STATS_NAME[:2],STATS_NAME[3:7],STATS_NAME[8:12],STATS_NAME[13:]), axis=0)
"""遗器主属性名称"""

BASE_STATS_NAME_FOR_EQUIP = [
    BASE_STATS_NAME[0:1],
    BASE_STATS_NAME[1:2],
    np.vstack((BASE_STATS_NAME[2:5],BASE_STATS_NAME[6:10])),
    BASE_STATS_NAME[2:6],
    np.vstack((BASE_STATS_NAME[2:5],BASE_STATS_NAME[-7:])),
    np.vstack((BASE_STATS_NAME[2:5],BASE_STATS_NAME[10:12]))
]
"""遗器各部位主属性名称"""

SUBS_STATS_NAME = np.vstack((STATS_NAME[:7],STATS_NAME[8:10],STATS_NAME[11:14]))
"""遗器副属性名称，已按副词条顺序排序"""

EXTRA_STATS_NAME = [
    _("属性抗性"), _("受到伤害降低"), _("护盾量"), _("抵抗控制"), _("无视防御力"), _("属性抗性穿透"),    # 均为己方的buff
    _("造成伤害"), _("普攻伤害"), _("战技伤害"), _("终结技伤害"), _("追加攻击伤害"), _("持续伤害")]
"""额外属性名称 (遗器套装效果涉及的部分属性)"""

ALL_STATS_NAME: List[str] = STATS_NAME[:, -1].tolist() + EXTRA_STATS_NAME
"""全属性名称 (包含遗器属性、遗器套装效果涉及的属性)"""

WEIGHT_STATS_NAME: List[str] = np.vstack((STATS_NAME[:3],STATS_NAME[6:7],STATS_NAME[8:]))[:, -1].tolist()
"""供设定权重的属性名称"""

SUBS_STATS_TIER_WEIGHT = [
    None,
    (0.9, 0.1, "[0.9, 1.0, 1.1]"),    # 主流赋值
    (0.8, 0.1, "[0.8, 0.9, 1.0]"),    # 真实比例赋值，除五星遗器'速度'属性的真实比例为 [0.7692, 0.8846, 1.0]
    (1-1/9, 1/9, "[0.888~, 1.0, 1.111~]"),   # 主流赋值比例矫正
]
"""副词条档位权重：0-空，1-主流赋值，2-真实比例赋值，3-主流赋值比例矫正 (五星遗器*1，四星遗器*0.8)"""

SUBS_STATS_TIER = [
    [(27.096, 3.3870  ), (13.548 , 1.6935  ), (13.548 , 1.6935  ), (2.7648, 0.3456), (2.7648, 0.3456), (3.456, 0.4320),  # 四星遗器数值
        (1.60, 0.20), (2.0736, 0.2592), (4.1472, 0.5184), (2.7648, 0.3456), (2.7648, 0.3456), (4.1472, 0.5184)],
    [(33.870, 4.233755), (16.935 , 2.116877), (16.935 , 2.116877), (3.4560, 0.4320), (3.4560, 0.4320), (4.320, 0.5400),  # 五星遗器数值
        (2.00, 0.30), (2.5920, 0.3240), (5.1840, 0.6480), (3.4560, 0.4320), (3.4560, 0.4320), (5.1840, 0.6480)]]
"""副属性词条档位：t0-基础值，t1-每提升一档的数值；l1-四星遗器数值，l2-五星遗器数值 <<数据来源：米游社@666bj>>"""

BASE_STATS_TIER = [
    [( 90.3168, 31.61088), (45.1584, 15.80544), (5.5296, 1.9354), (5.5296, 1.9354), (6.9120, 2.4192), (3.2256, 1.1),    # 四星遗器数值
    (4.1472, 1.4515), ( 8.2944, 2.9030), (4.4237, 1.5483), (5.5296, 1.9354), ( 8.2944, 2.9030), (2.4883, 0.8709), (4.9766, 1.7418)],
    [(112.896,  39.5136 ), (56.448,  19.7568 ), (6.9120, 2.4192), (6.9120, 2.4192), (8.6400, 3.0240), (4.032,  1.4),    # 五星遗器数值
    (5.1840, 1.8144), (10.3680, 3.6288), (5.5296, 1.9354), (6.9120, 2.4192), (10.3680, 3.6288), (3.1104, 1.0886), (6.2208, 2.1773)]]
"""主属性词条级别：t0-基础值，t1-每提升一级的数值；l1-四星遗器数值，l2-五星遗器数值 <<数据来源：米游社@666bj>>"""

for i in range(len(BASE_STATS_TIER)):
    BASE_STATS_TIER[i].extend([BASE_STATS_TIER[i][-1]] * 6)   # 复制属性伤害

SET_EFFECT_OF_TWO_PC: List[List[StatsEffect]] = [
# 外圈
    [(_("治疗量加成"), 10, True)],
    [(_("攻击力%"), 12, True)],
    [(_("防御力%"), 15, True)],
    [(_("冰属性伤害"), 10, True)],
    [(_("物理伤害"), 10, True)],
    [(_("受到伤害降低"), 8, True)],
    [(_("火属性伤害"), 10, True)],
    [(_("量子属性伤害"), 10, True)],
    [(_("雷属性伤害"), 10, True)],
    [(_("风属性伤害"), 10, True)],
    [(_("击破特攻"), 16, True)],
    [(_("虚数属性伤害"), 10, True)],
    [(_("生命值%"), 12, True)],
    [(_("速度%"), 6, True)],
    [(_("追加攻击伤害"), 20, True)],
    [(_("攻击力%"), 12, True)],
# 内圈
    [(_("攻击力%"), 12, True), (_("攻击力%"), 12, False), _("当装备者的速度大于等于120时，攻击力额外提高12%")],
    [(_("生命值%"), 12, True), (_("攻击力%"), 8, False), _("当装备者的速度大于等于120时，我方全体攻击力提高8%")],
    [(_("效果命中"), 10, True), (_("攻击力"), None, False), _("同时提高装备者等同于当前效果命中25%的攻击力，最多提高25%")],
    [(_("防御力%"), 15, True), (_("防御力%"), 15, False), _("当装备者的效果命中大于等于50%时，防御力额外提高15%")],
    [(_("暴击伤害"), 16, True), (_("暴击率"), 60, False), _("当装备者的暴击伤害大于等于120%时，进入战斗后装备者的暴击率提高60%，持续到施放首次攻击后结束")],
    [(_("暴击率"), 8, True), (_("终结技伤害"), 15, False), (_("追加攻击伤害"), 15, False), _("当装备者当前暴击率大于等于50%时，终结技和追加攻击造成的伤害提高15%")],
    [(_("击破特攻"), 16, True), (_("击破特攻"), 20, False), _("当装备者的速度大于等于145时，击破特攻额外提高20%")],
    [(_("能量恢复效率"), 5, True), _("当装备者的速度大于等于120时，进入战斗时立刻使行动提前40%")],
    [(_("暴击率"), 8, True), (_("普攻伤害"), 20, False), (_("战技伤害"), 20, False), _("当装备者的当前暴击率大于等于70%时，普攻和战技造成的伤害提高20%")],
    [(_("效果抵抗"), 10, True), (_("暴击伤害"), 10, False), _("当装备者的效果抵抗大于等于30%时，我方全体暴击伤害提高10%")],
    [(_("攻击力%"), 12, True), (_("造成伤害"), 12, False), (_("造成伤害"), 6, False), _("当装备者的速度大于等于135/160时，使装备者造成的伤害提高12%/18%")],
    [(_("能量恢复效率"), 5, True), (_("造成伤害"), 10, False), _("使队伍中与装备者属性相同的我方其他角色造成的伤害提高10%")],
]
"""遗器二件套效果，True-非条件效果，False-条件效果"""

for set_index, set_effect in enumerate(SET_EFFECT_OF_TWO_PC):
    if isinstance(set_effect[-1], str):
        set_effect[-1] = RELIC_SET_NAME[set_index, 2] + _("2件套：") + set_effect[-1]

SET_EFFECT_OF_FOUR_PC: List[List[StatsEffect]] = [
# 外圈
    [_("在战斗开始时，立即为我方恢复1个战技点")],
    [(_("速度%"), 6, True), (_("普攻伤害"), 10, True)],
    [(_("护盾量加成"), 20, True)],
    [(_("暴击伤害"), 25, False), _("当装备者施放终结技时，暴击伤害提高25%，持续2回合")],
    [(_("攻击力%"), 25, False), _("当装备者施放攻击或受到攻击后，其在本场战斗中攻击力提高5%，最多叠加5层")],
    [_("回合开始时，如果装备者当前生命值百分比小于等于50%，则回复等同于自身生命上限8%的生命值，并恢复5点能量")],
    [(_("战技伤害"), 12, True), (_("火属性伤害"), 12, False), _("使施放终结技后的下一次攻击造成的火属性伤害提高12%")],
    [(_("无视防御力"), 10, True), (_("无视防御力"), 10, False), _("若目标拥有量子属性弱点，额外无视其10%的防御力")],
    [(_("攻击力%"), 20, False), _("当装备者施放战技时，使装备者的攻击力提高20%，持续1回合")],
    [_("当装备者施放终结技后，使其行动提前25%")],
    [(_("击破特攻"), 16, True), _("当装备者击破敌方目标弱点后，恢复3点能量")],
    [(_("暴击率"), 10, False), (_("暴击伤害"), 20, False), _("装备者对陷入负面效果的敌方目标造成伤害时暴击率提高10%"), _("装备者对陷入禁锢状态的敌方目标造成伤害时暴击伤害提高20%")],
    [(_("暴击率"), 12, False), _("当装备者受到攻击或被我方目标消耗生命值后，暴击率提高8%，持续2回合，该效果最多叠加2层")],
    [(_("速度%"), 12, False), _("当装备者对我方目标施放终结技时，我方全体速度提高12%，持续1回合，该效果无法叠加")],
    [(_("攻击力%"), 48, False), _("装备者施放追加攻击时，根据追加攻击造成伤害的次数，每次造成伤害时使装备者的攻击力提高6%，最多叠加8次，持续3回合。该效果在装备者下一次施放追加攻击时移除")],
    [(_("无视防御力"), 18, False), _("敌方目标每承受1个持续伤害效果，装备者对其造成伤害时就无视其6%的防御力，最多计入3个持续伤害效果")],
]
"""遗器四件套效果，True-非条件效果，False-条件效果"""

for set_index, set_effect in enumerate(SET_EFFECT_OF_FOUR_PC):
    for i, effect in enumerate(set_effect):
        if isinstance(effect, str):
            set_effect[i] = RELIC_SET_NAME[set_index, 2] + _("4件套：") + effect


RELIC_SCHEMA = {
    "type": "object",
    "additionalProperties": {    # [主键]遗器哈希值 (由其键值遗器数据自动生成)
        "type": "object",
        "properties": {
            "equip_set": {       # 遗器部位
                "type": "string",
                "enum": EQUIP_SET_NAME
            },
            "relic_set": {       # 遗器套装
                "type": "string",
                "enum": RELIC_SET_NAME[:, -1].tolist()
            },
            "rarity": {          # 遗器稀有度 (2-5星)
                "type": "integer",
                "minimum": 2,
                "maximum": 5
            },
            "level": {           # 遗器等级 (0-15级)
                "type": "integer",
                "minimum": 0,
                "maximum": 15
            },
            "base_stats": {      # 遗器主属性 (词条数为 1)
                "type": "object",
                "minProperties": 1,
                "maxProperties": 1,
                "properties": {
                    key: {"type": "number"} for key in BASE_STATS_NAME[:, -1]
                },
                "additionalProperties": False
            },
            "subs_stats": {      # 遗器副属性 (词条数为 1-4)
                "type": "object",
                "minProperties": 1,
                "maxProperties": 4,
                "properties": {
                    key: {"type": "number"} for key in SUBS_STATS_NAME[:, -1]
                },
                "additionalProperties": False
            },
            "pre_ver_hash": {"type": "string"}     # [外键]本次升级前的版本
        },
        "required": ["relic_set", "equip_set", "rarity", "level", "base_stats", "subs_stats"],  # 需包含遗器的全部固有属性
        "additionalProperties": False
}}
"""遗器数据json格式规范"""

LOADOUT_SCHEMA = {
    "type": "object",
    "additionalProperties": {       # [主键]人物名称 (以OCR结果为准)
        "type": "object",
        "additionalProperties": {   # [次主键]配装名称 (自定义)
            "type": "object",
            "properties": {
                "relic_hash": {         # 配装组成 (6件遗器，按部位排序)
                    "type": "array",
                    "minItems": 6,
                    "maxItems": 6,
                    "items": {"type": "string"}  # [外键]遗器哈希值                
                },
                # 【待扩展】如裸装面板、遗器属性权重
            },
            "required": ["relic_hash"],
            "additionalProperties": False
}}}
"""人物配装数据json格式规范"""

LOADOUT_SCHEMA_OLD = {
    "type": "object",
    "additionalProperties": {       # [主键]人物名称 (以OCR结果为准)
        "type": "object",
        "additionalProperties": {   # [次主键]配装名称 (自定义)
            "type": "array",        # 配装组成 (6件遗器，按部位排序)
            "minItems": 6,
            "maxItems": 6,
            "items": {"type": "string"}  # [外键]遗器哈希值
}}}
"""人物配装数据json格式规范 (兼容旧版)"""

TEAM_SCHEMA_PART = {
    "additionalProperties": {       # [主键]队伍名称 (自定义)
        "type": "object",
        "properties": {
            "team_members": {       # 队伍成员 (无序，1-4人)
                "type": "object",
                "additionalProperties": {   # [外键]队伍成员名称 (以OCR结果为准)
                    "type": "string"        # [外键]各队伍成员的配装名称
                },
                "minProperties": 1,
                "maxProperties": 4
            },
            # 【可扩展】如"visible","ordered"等其他队伍属性
        },
        "required": ["team_members"],  # 需包含遗器的全部固有属性
        "additionalProperties": False
}}
TEAM_SCHEMA = {
    "type": "object",
    "properties": {
        "compatible":          # [主键]非互斥队伍组别 (默认，不可更改)
            TEAM_SCHEMA_PART,
    },
    "additionalProperties":    # [主键]互斥队伍组别名称 (自定义，例如用于忘却之庭上下半配队)【待扩展】 
        TEAM_SCHEMA_PART,
}
"""队伍配装数据json格式规范"""

CHAR_STATS_PANEL_SCHEMA = {
    "type": "object",
    "additionalProperties": {       # [主键]人物名称 (以OCR结果为准)
        "type": "object",
        "additionalProperties": {   # [次主键]面板名称 (自定义)
            "type": "object",
            "properties": {
                "base": {           # 白值属性面板
                    "properties": {
                        key: {"type": "number"} for key in BASE_VALUE_NAME
                    },
                    "required": BASE_VALUE_NAME,     # 白值属性为必需
                    "additionalProperties": False
                },
                "additonal": {      # 附加属性面板
                    "properties": {
                        key: {"type": "number"} for key in ALL_STATS_NAME
                    },
                    "additionalProperties": False
                },
                "conditional": {    # 条件属性面板
                    "properties": {
                        key: {"type": "number"} for key in ALL_STATS_NAME
                    },
                    "additionalProperties": False
                },
                "extra_effect": {   # 额外效果说明
                    "type": "array", 
                    "items": {"type": "string"}
                },
                # 【待扩展】 如"global"
            },
            "required": ["base"],   # 白值属性面板为必需
            "additionalProperties": False
}}}
"""角色属性面板"""

WEIGHT_SCHEMA_PART = {
    "type": "object",
    "properties": {
        "weight": {
            "type": "object",
            "properties": {
                key: {"type": "number"} for key in WEIGHT_STATS_NAME
            },
            "additionalProperties": False
        },
        # 【待扩展】 如"global"
    },
    "required": ["weight"],
    "additionalProperties": False
}
CHAR_STATS_WEIGHT_SCHEMA = {
    "type": "object",
    "additionalProperties": { # [主键]人物名称 (以OCR结果为准)
        "type": "object",
        "properties": {
            "default":             # [次主键]默认权重 (默认，名称不可更改)
                WEIGHT_SCHEMA_PART,
        },
        "additionalProperties":    # [次主键]自定义权重 (自定义)【待扩展】 
            WEIGHT_SCHEMA_PART,
    }
}
"""角色属性权重"""

RELIC_DATA_FILTER = ["pre_ver_hash"]
"""遗器数据过滤器"""