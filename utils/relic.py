import math
import pprint
import questionary
import numpy as np
from .calculated import *
from .config import read_json_file, modify_json_file, RELIC_FILE_NAME, LOADOUT_FILE_NAME, TEAM_FILE_NAME, _
from .exceptions import Exception, RelicOCRException
from .log import log
pp = pprint.PrettyPrinter(indent=1, width=40, sort_dicts=False)
IS_PC = True   # paltform flag (同时保存了模拟器与PC的识别位点)

class Relic:
    def __init__(self, title=_("崩坏：星穹铁道")):
        if sra_config_obj.language != "zh_CN":
            raise Exception(_("暂不支持简体中文之外的语言"))
        self.calculated = calculated(title)

        # 部位，已经按页面顺序排序
        self.equip_set_name = [_("头部"), _("手部"), _("躯干"), _("脚部"), _("位面球"), _("连结绳")
                               ] 
        # 套装:np，0-套装散件的共有词(ocr-必须)，1-套装简称(ocr-可选，为了增强鲁棒性)，2-套装全称(json)，已按遗器筛选页面排序
        self.relic_set_name = np.array([        # 注：因为数据有时要行取有时要列取，故采用数组存储
            [_("过客"), _("过客"), _("云无留迹的过客")],
            [_("枪手"), _("枪手"), _("野穗伴行的快枪手")], 
            [_("圣骑"), _("圣骑"), _("净庭教宗的圣骑士")], 
            [_("雪猎"), _("猎人"), _("密林卧雪的猎人")], 
            [_("拳王"), _("拳王"), _("街头出身的拳王")], 
            [_("铁卫"), _("铁卫"), _("戍卫风雪的铁卫")], 
            [_("火匠"), _("火匠"), _("熔岩锻铸的火匠")], 
            [_("天才"), _("天才"), _("繁星璀璨的天才")], 
            [_("乐队"), _("雷电"), _("激奏雷电的乐队")], 
            [_("翔"), _("翔"), _("晨昏交界的翔鹰")], 
            [_("怪盗"), _("怪盗"), _("流星追迹的怪盗")], 
            [_("废"), _("废"), _("盗匪荒漠的废土客")], 
            [_("黑塔"), _("太空"), _("太空封印站")], 
            [_("仙"), _("仙"), _("不老者的仙舟")], 
            [_("公司"), _("公司"), _("泛银河商业公司")], 
            [_("贝洛"), _("贝洛"), _("筑城者的贝洛伯格")], 
            [_("螺丝"), _("差分"), _("星体差分机")], 
            [_("萨尔"), _("停转"), _("停转的萨尔索图")], 
            [_("利亚"), _("盗贼"), _("盗贼公国塔利亚")], 
            [_("瓦克"), _("瓦克"), _("生命的翁瓦克")], 
            [_("泰科"), _("繁星"), _("繁星竞技场")], 
            [_("伊须"), _("龙骨"), _("折断的龙骨")],
            [_("者"), _("长存"), _("宝命长存的莳者")], 
            [_("信使"), _("信使"), _("骇域漫游的信使")]
            ], dtype=np.str_)
        # 属性:np，0-属性简称(ocr-不区分大小词条)，1-属性全称(json-区分大小词条)
        self.stats_name = np.array([
            [_("命值"), _("生命值")], [_("击力"), _("攻击力")], [_("防御"), _("防御力")], 
            [_("命值"), _("生命值%")], [_("击力"), _("攻击力%")], [_("防御"), _("防御力%")],
            [_("度"), _("速度")], [_("击率"), _("暴击率")], [_("击伤"), _("暴击伤害")], [_("命中"), _("效果命中")], [_("治疗"), _("治疗量加成")],
            [_("理"), _("物理属性伤害")], [_("火"), _("火属性伤害")], [_("水"), _("冰属性伤害")], [_("雷"), _("雷属性伤害")], [_("风"), _("风属性伤害")], 
            [_("量"), _("量子属性伤害")], [_("数"), _("虚数属性伤害")], 
            [_("抵抗"), _("效果抵抗")], [_("破"), _("击破特攻")], [_("恢复"), _("能量恢复效率")]
            ], dtype=np.str_)
        # 整数属性
        self.not_pre_stats = [_("生命值"), _("攻击力"), _("防御力"), _("速度")]
        # 主属性
        self.base_stats_name = np.concatenate((self.stats_name[:2],self.stats_name[3:-3],self.stats_name[-2:]), axis=0)
        # 各部位主属性:list[np]
        self.base_stats_name4equip = [self.base_stats_name[0:1],
                                      self.base_stats_name[1:2],
                                      np.vstack((self.base_stats_name[2:5],self.base_stats_name[6:10])),
                                      self.base_stats_name[2:6],
                                      np.vstack((self.base_stats_name[2:5],self.base_stats_name[10:17])),
                                      np.vstack((self.base_stats_name[2:5],self.base_stats_name[-2:]))]
        # 副属性，已按副词条顺序排序
        self.subs_stats_name = np.vstack((self.stats_name[:10],self.stats_name[-3:-1]))
        # 副属性词条挡位: 0-基础值，1-每提升一档的数值
        self.subs_stats_tier = [(33.870, 4.234), (16.935, 2.117), (16.935, 2.117), (3.456, 0.432), (3.456, 0.432), (4.320, 0.540), 
                                (2.0, 0.3), (2.592, 0.324), (5.184, 0.648), (3.456, 0.432), (3.456, 0.432), (5.184, 0.648)]
        # json数据格式规范
        self.relics_schema = {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "equip_set": {
                        "type": "string",
                        "enum": self.equip_set_name
                    },
                    "relic_set": {
                        "type": "string",
                        "enum": self.relic_set_name[:, -1].tolist()
                    },
                    "rarity": {"type": "integer"},
                    "level": {"type": "integer"},
                    "base_stats": {
                        "type": "object",
                        "minProperties": 1,
                        "maxProperties": 1,
                        "properties": {
                            key: {"type": "number"} for key in self.base_stats_name[:, -1]},
                        "additionalProperties": False
                    },
                    "subs_stats": {
                        "type": "object",
                        "minProperties": 2,
                        "maxProperties": 4,
                        "properties": {
                            key: {"type": "number"} for key in self.subs_stats_name[:, -1]},
                        "additionalProperties": False
                    }
                },
                "required": ["relic_set", "equip_set", "level", "base_stats", "subs_stats"],
                "additionalProperties": False
        }}
        self.loadout_schema = {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "additionalProperties": {
                    "type": "array",
                    "minItems": 6,
                    "maxItems": 6,
                    "items": {"type": "string"}
        }}}
        self.team_schema = {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "additionalProperties": {
                    "type": "string"
                },
                "minProperties": 1,
                "maxProperties": 4
        }}
        # 读取json文件，仅初始化时检查格式规范
        self.relics_data = read_json_file(RELIC_FILE_NAME, schema=self.relics_schema)
        self.loadout_data = read_json_file(LOADOUT_FILE_NAME, schema=self.loadout_schema)
        self.team_data = read_json_file(TEAM_FILE_NAME, schema=self.team_schema)
        log.info(_("遗器数据载入完成"))

        self.is_fuzzy_match = True   # 在搜索时开启遗器数据模糊匹配
        self.is_check = True   # 是否对副词条数据进行校验 (关闭后，可临时使程序能够识别五星以下遗器，同时会将数据增强强制关闭)
        self.is_detail = True  # 在打印遗器信息时进行数据增强，显示拓展信息
        self.is_detail = self.is_detail if self.is_check else False

    def relic_entrance(self):
        """
        说明：
            遗器模块入口
            已完成功能：
                1.识别遗器数据 (可打印增强信息，目前仅支持五星遗器)
                2.保存人物配装
                3.读取人物配装并装备 (遗器将强制替换，支持模糊匹配)
            待解决问题：
                1.OCR准确率过低 (对模型进行重训练)
                    (碎碎念：测试结果看PC端比模拟器的OCR准确率还低，但明明PC端的截图分辨率更高...不知道是否为本人的测试环境问题)
            待开发功能：
                1.保存队伍配装
                2.读取队伍配装并装备
                3.遗器管理与配装管理
                4.兼容四星遗器：
                    a. 兼容校验函数 (增加四星遗器副词条挡位数据)
                    b. 对遗器稀有度的识别 (识别指定点位色相[黄,紫])
                5.模糊匹配成功后更新相关数据库
                ...
        """
        title = _("遗器模块：")
        options = [_("保存当前人物的配装"), _("读取当前人物的配装"), _("识别当前遗器的数据"), _("返回主菜单")]
        option = options[0]  # 保存上一次的选择
        while True:
            option = questionary.select(title, options, default=option).ask()
            if option == _("保存当前人物的配装"):
                self.save_loadout_for_char()
            elif option == _("读取当前人物的配装"):
                self.equip_loadout_for_char()
            elif option == _("识别当前遗器的数据"):
                data = self.try_ocr_relic()
                self.print_relic(data)
            elif option == _("返回主菜单"):
                break
    
    def equip_loadout_for_team(self):
        """
        说明：
            装备当前[人物]界面本队伍的遗器配装
        """
        ...

    def equip_loadout_for_char(self):
        """
        说明：
            装备当前[人物]界面本人物的遗器配装
        """
        # 识别当前人物名称
        character_name = self.ocr_character_name() 
        character_data = self.loadout_data[character_name]
        # 选择配装
        if not character_data:  # 字典为空
            log.info(_("当前人物配装记录为空"))
            return
        title = _("请选择将要进行装备的配装：")
        options = list(character_data.keys())
        options.append(_("返回上一级"))
        option = questionary.select(title, options).ask()
        if option == _("返回上一级"):
            return
        relic_hash = character_data[option]
        # 进行配装
        self.calculated.relative_click((12,40) if IS_PC else (16,48))  # 点击遗器，进入[人物]-[遗器]界面
        time.sleep(0.5)
        self.calculated.relative_click((38,26) if IS_PC else (36,21))  # 点击头部遗器，进入[人物]-[遗器]-[遗器详情]界面
        time.sleep(2)
        self.calculated.relative_click((82,12) if IS_PC else (78,12))  # 点击遗器[对比]，将遗器详情的背景由星空变为纯黑
        time.sleep(1)
        self.equip_loadout(relic_hash)
        self.calculated.relative_click((97,6) if IS_PC else (96,5))   # 退出[遗器]界面，返回[人物]界面
        time.sleep(1)

    def equip_loadout(self, relics_hash:list[str]):
        """
        说明：
            装备当前[人物]-[遗器]-[遗器详情]页面内的指定遗器配装。
            遗器将强制替换 (1-替换己方已装备的遗器，2-替换对方已装备的遗器)
        参数：
            :param relics_hash: 遗器配装哈希值列表
        """
        equip_pos_list = [(4,13),(9,13),(13,13),(18,13),(23,13),(27,13)] if IS_PC else [(5,14),(11,14),(17,14),(23,14),(28,14),(34,14)]
        pre_relic_set_index = -1
        for equip_indx, equip_pos in enumerate(equip_pos_list):   # 遗器部位循环
            # 选择部位
            log.info(_(f"选择部位：{self.equip_set_name[equip_indx]}"))
            self.calculated.relative_click(equip_pos)
            time.sleep(0.5)
            # 筛选遗器 (加快遗器搜索)
            tmp_hash = relics_hash[equip_indx]
            tmp_data = self.relics_data[tmp_hash]
            log.debug(tmp_hash)
            relic_set_index = np.where(self.relic_set_name[:, -1] == tmp_data["relic_set"])[0][0]
            if pre_relic_set_index != relic_set_index:  # 判断与先前套装发生变化
                log.info(_("筛选遗器套装"))
                self.calculated.relative_click((3,92) if IS_PC else (4,92))  # 点击筛选图标
                time.sleep(0.5)
                ... # 筛选稀有度
                self.calculated.relative_click((93,20) if IS_PC else (92,23))  # 点击套装选择
                time.sleep(0.5)
                self.calculated.relative_click((40,70) if IS_PC else (37,76))  # 清除之前的筛选项
                # 搜索遗器套装名，并点击
                self.search_relic_set_for_filter(relic_set_index)
                time.sleep(0.2)
                self.calculated.relative_click((62,70) if IS_PC else (64,76))  # 点击确认
                time.sleep(0.5)
                self.calculated.relative_click((3,92) if IS_PC else (4,92))  # 筛选框外任意点击退出筛选
                pre_relic_set_index = relic_set_index
            # 搜索遗器
            pos = self.search_relic(equip_indx, key_hash=tmp_hash) # , key_data=tmp_data)
            if pos is None:
                log.error(_(f"遗器搜索失败: {tmp_hash}"))
                continue
            # 点击装备
            self.calculated.relative_click(pos)
            button = self.calculated.ocr_pos_for_singleLine([_("装备"), _("替换"), _("卸下")], points=(80,90,85,94) if IS_PC else (75,90,82,95))  # 需识别[装备,替换,卸下]
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
        log.info(_("配装装备完毕"))

    def save_loadout_for_team(self):
        """
        说明：
            保存当前[人物]界面本队伍的遗器配装
        """
        ...

    def save_loadout_for_char(self):
        """
        说明：
            保存当前[人物]界面本人物的遗器配装
        """
        character_name = self.ocr_character_name()  # 识别当前人物名称
        self.calculated.relative_click((12,40) if IS_PC else (16,48))  # 点击遗器
        time.sleep(1)
        self.calculated.relative_click((38,26) if IS_PC else (36,21))  # 点击头部遗器，进入[人物]-[遗器]界面
        time.sleep(2)
        self.calculated.relative_click((82,12) if IS_PC else (78,12))  # 点击遗器[对比]，将遗器详情的背景由星空变为纯黑
        time.sleep(1)
        self.save_loadout(character_name)
        self.calculated.relative_click((97,6) if IS_PC else (96,5))   # 退出[遗器]界面，返回[人物]界面
        time.sleep(2)

    def save_loadout(self, character_name:str=None, max_retries=3):
        """
        说明：
            保存当前[人物]-[遗器]-[遗器详情]界面内的遗器配装
        """
        character_name = character_name if character_name else self.ocr_character_name()
        character_data = self.loadout_data[character_name]
        equip_pos = [(4,13),(9,13),(13,13),(18,13),(23,13),(27,13)] if IS_PC else [(5,14), (11,14), (17,14), (23,14), (28,14), (34,14)]
        relics_hash = []
        for equip_indx in range(6):   # 遗器部位循环
            log.info(_(f"选择部位：{self.equip_set_name[equip_indx]}"))
            self.calculated.relative_click(equip_pos[equip_indx])
            time.sleep(1)
            tmp_data = self.try_ocr_relic(equip_indx, max_retries)
            tmp_hash = self.calculated.get_data_hash(tmp_data)
            log.debug("\n"+pp.pformat(tmp_data))
            self.print_relic(tmp_data)
            if tmp_hash in self.relics_data:
                log.info(_("遗器数据已存在"))
            else:
                log.info(_("录入遗器数据"))
                self.add_relic_data(tmp_data, tmp_hash)
            relics_hash.append(tmp_hash)
        log.info(_("配装识别完毕"))
        loadout_name = input(_("自定义配装名称: "))  # 需作为字典key值，确保唯一性 (但不同的人物可以有同一配装名称)
        while loadout_name in character_data:
            loadout_name = input(_("名称冲突，请重定义: "))
        character_data[loadout_name] = relics_hash
        self.loadout_data = modify_json_file(LOADOUT_FILE_NAME, character_name, character_data)
        log.info(_("配装录入成功"))
    
    def search_relic_set_for_filter(self, relic_set_index:int):
        """
        说明：
            在当前滑动[人物]-[遗器]-[遗器详情]-[遗器筛选]界面内，搜索遗器套装名，并点击。
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
                self.calculated.relative_click((35,35) if IS_PC else (35,32))        # 取消选中
        points = ((28,33,42,63) if is_left else (53,33,67,63)) if IS_PC else ((22,29,41,65) if is_left else (53,29,72,65))
        self.calculated.ocr_click(self.relic_set_name[relic_set_index, 1], points=points)

    def search_relic(self, equip_indx:int, key_hash:str=None, key_data:dict=None, overtime=180, max_retries=3) -> tuple[int, int]:
        """
        说明：
            在当前滑动[人物]-[遗器]-[遗器详情]界面内，搜索匹配的遗器。
                key_hash非空: 激活精确匹配 (假设数据保存期间遗器未再次升级); 
                key_data非空: 激活模糊匹配 (假设数据保存期间遗器再次升级);
                key_hash & key_data均空: 遍历当前页面内的遗器
        参数：
            :param equip_indx: 遗器部位索引
            :param key_hash: 所记录的遗器哈希值
            :param key_data: 所记录的遗器数据
            :param overtime: 超时
        返回:
            :return pos: 坐标
        """
        pos_start = (5,24) if IS_PC else (7, 28)
        d_x, d_y, k_x, k_y = (7, 14, 4, 5) if IS_PC else (8, 17, 4, 4)
        pre_pos = [""]
        start_time = time.time()
        while True:
            x, y = pos_start  # 翻页复位
            for i in range(0, k_y):   # 行
                x = pos_start[0]    # 首列复位
                for j in range(0, k_x):  # 列
                    self.calculated.relative_click((x, y))   # 点击遗器，同时将翻页的动态延迟暂停
                    time.sleep(0.2)
                    log.info(f"({i+1},{j+1},{len(pre_pos)})")  # 显示当前所识别遗器的方位与序列号
                    tmp_data = self.try_ocr_relic(equip_indx, max_retries)
                    # log.info("\n"+pp.pformat(tmp_data))
                    tmp_hash = self.calculated.get_data_hash(tmp_data)
                    if key_hash and key_hash == tmp_hash:  # 精确匹配
                        return (x, y)
                    if key_data and self.is_fuzzy_match and self.compare_relics(key_data, tmp_data):  # 模糊匹配
                        log.info(_("模糊匹配成功！"))
                        print(_("旧遗器："))
                        self.print_relic(key_data)
                        print(_("新遗器："))
                        self.print_relic(tmp_data)
                        ...  # 更新数据库 (将旧有遗器数据替换，并更新遗器配装数据的哈希值)
                        return (x, y)
                    # 判断是否遍历完毕
                    if pre_pos[-1] == tmp_hash:
                        log.info(_("遗器数据未发生变化，怀疑点击到空白区域搜索至最后"))
                        return None   # 判断点击到空白，遗器数据未发生变化，结束搜索
                    if j == 0:  # 首列遗器
                        if tmp_hash in pre_pos:
                            if i == k_y-1:
                                log.info(_("已搜索至最后"))
                                return None   # 判断已滑动至末页，结束搜索
                            break     # 本行已搜索过，跳出本行
                    pre_pos.append(tmp_hash)  # 记录
                    x += d_x
                y += d_y
            # 滑动翻页 (从末尾位置滑动至顶部，即刚好滑动一整页)
            log.info(_("滑动翻页"))
            self.calculated.relative_swipe((pos_start[0], pos_start[1]+(k_y-1)*d_y), (pos_start[0], pos_start[1]-d_y))
            if time.time() - start_time > overtime:
                log.info(_("识别超时"))
                break
        return None
    
    def compare_relics(self, old_data:dict, new_data:dict) -> bool:
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
            if old_data["subs_stats"][key] > new_data["subs_stats"][key]:
                return False
        return True
        
    def add_relic_data(self, data:dict, data_hash:str=None) -> bool:
        """
        说明：
            录入仪器数据
        """
        if not data_hash:
            data_hash = self.calculated.get_data_hash(data)
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
        str = self.calculated.ocr_pos_for_singleLine(points=(10,6,18,9) if IS_PC else (13,4,22,9))   # 识别人物名称 (主角名称为玩家自定义，无法适用预选列表)
        character_name = re.sub(r"[.’,，。、·'\"/\\]", '', str)   # 删除由于背景光点造成的误判
        log.info(_(f"识别人物: {character_name}"))
        if character_name not in self.loadout_data:
            self.loadout_data = modify_json_file(LOADOUT_FILE_NAME, character_name, {})
            log.info(_("创建新人物"))
        return character_name
    
    def try_ocr_relic(self, equip_set_index:int = None, max_retries = 3) -> dict:
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
        
    def ocr_relic(self, equip_set_index:int = None) -> dict:
        """
        说明：
            OCR当前静态[人物]-[遗器]-[遗器详情]界面内的遗器数据，用时1-2s。
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
            equip_set_index = self.calculated.ocr_pos_for_singleLine(self.equip_set_name, points=(77,19,83,23) if IS_PC else (71,22,78,26), img_pk=img_pc)
            if equip_set_index < 0:
                raise RelicOCRException(_("遗器套装OCR错误"))
        equip_set_name = self.equip_set_name[equip_set_index]
        # [2]套装识别
        name_list = self.relic_set_name[:, 0].tolist()
        relic_set_index = self.calculated.ocr_pos_for_singleLine(name_list, points=(77,15,92,19) if IS_PC else (71,17,88,21), img_pk=img_pc)
        if relic_set_index < 0: 
            raise RelicOCRException(_("遗器部位OCR错误"))
        relic_set_name = self.relic_set_name[relic_set_index, -1]
        # [3] 稀有度识别
        ...
        rarity = 5   # 目前只支持5星遗器，默认5星
        ...
        # [4]等级识别
        level = self.calculated.ocr_pos_for_singleLine(points=(95,19,98,23) if IS_PC else (94,22,98,26), number=True, img_pk=img_pc)
        level = int(level.split('+')[-1])  # 消除开头可能的'+'号
        if level > 15:
            raise RelicOCRException(_("遗器等级OCR错误"))
        # [5]主属性识别
        name_list = self.base_stats_name4equip[equip_set_index][:, 0].tolist()
        base_stats_index = self.calculated.ocr_pos_for_singleLine(name_list, points=(79,25,92,29) if IS_PC else (74,29,89,34), img_pk=img_pc)
        base_stats_value = self.calculated.ocr_pos_for_singleLine(points=(93,25,98,29) if IS_PC else (91,29,98,34), number=True, img_pk=img_pc)
        if base_stats_index < 0: 
            raise RelicOCRException(_("遗器主词条OCR错误"))
        if base_stats_value is None:
            raise RelicOCRException(_("遗器主词条数值OCR错误"))
        else:
            base_stats_value = str(base_stats_value).replace('.', '')   # 删除所有真假小数点
            if '%' in base_stats_value:
                s = base_stats_value.split('%')[0]   # 修正'48%1'如此的错误识别
                base_stats_value = s[:-1] + '.' + s[-1:]   # 添加未识别的小数点
            base_stats_value = float(base_stats_value)
        base_stats_name = str(self.base_stats_name4equip[equip_set_index][base_stats_index, -1])
        # [6]副属性识别 (词条数量 2-4)
        subs_stats_name_points =  [(79,29,85,33),(79,33,85,36.5),(79,36.5,85,40),(79,40,85,44)] if IS_PC else [(74,35,81,38),(74,39,81,43),(74,44,81,47),(74,48,81,52)]
        subs_stats_value_points = [(93,29,98,33),(93,33,98,36.5),(93,36.5,98,40),(93,40,98,44)] if IS_PC else [(92,35,98,38),(92,39,98,43),(92,44,98,47),(92,48,98,52)]
        name_list = self.subs_stats_name[:, 0].tolist()
        subs_stats_dict = {}
        total_level = 0
        for name_point, value_point in zip(subs_stats_name_points, subs_stats_value_points):
            tmp_index = self.calculated.ocr_pos_for_singleLine(name_list, points=name_point, img_pk=img_pc)
            if tmp_index is None: break   # 所识别data为空，即词条为空，正常退出循环
            if tmp_index < 0:
                raise RelicOCRException(_("遗器副词条OCR错误"))
            tmp_value = self.calculated.ocr_pos_for_singleLine(points=value_point, number=True, img_pk=img_pc)  
            if tmp_value is None:
                raise RelicOCRException(_("遗器副词条数值OCR错误"))
            else:
                tmp_value = str(tmp_value).replace('.', '')   # 删除所有真假小数点
                if '%' in tmp_value:
                    s = tmp_value.split('%')[0]   # 修正'48%1'如此的错误识别
                    tmp_value = s[:-1] + '.' + s[-1:]   # 添加未识别的小数点
                    if tmp_index >= 0 and tmp_index < 3:
                        tmp_index += 3            # 小词条转为大词条
                tmp_value = float(tmp_value)
            tmp_name = str(self.subs_stats_name[tmp_index, -1])
            check = self.get_subs_stats_detail((tmp_name, tmp_value), tmp_index)
            if check is None:   
                raise RelicOCRException(_("遗器副词条数值OCR错误"))
            else:
                total_level += check[0]
            subs_stats_dict[tmp_name] = tmp_value
        if self.is_check and total_level > level // 3 + 4:
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
    
    def print_relic(self, data:dict):
        """
        说明：
            打印遗器信息，
            可通过is_detail设置打印普通信息与增强信息
        """
        print(_("部位: {equip_set}").format(equip_set=data["equip_set"]))
        print(_("套装: {relic_set}").format(relic_set=data["relic_set"]))
        print(_("星级: {rarity}").format(rarity=data["rarity"]))
        print(_("等级: {level}").format(level=data["level"]))
        print(_("主词条:"))
        name, value = list(data["base_stats"].items())[0]
        pre = " " if name in self.not_pre_stats else "%"
        print(_("   {name:<4}\t{value:>5}{pre}").format(name=name, value=value, pre=pre))
        print(_("副词条:"))
        for name, value in data["subs_stats"].items():
            pre = " " if name in self.not_pre_stats else "%"
            if self.is_detail:
                ret = self.get_subs_stats_detail((name, value))  # 增强信息并校验数据
                if ret:
                    level, score, result = ret
                    tag = '>'*(level-1)   # 强化次数的标识
                    print(_("   {name:<4}\t{tag:<7}{value:>6.3f}{pre}   [{score}]").format(name=name, tag=tag, value=result, score=score, pre=pre))
                else:  # 数据校验失败
                    print(_("   {name:<4}\t{value:>5}{pre}   [ERROR ]").format(name=name, value=value, pre=pre))
            else:
                print(_("   {name:<4}\t{value:>5}{pre}").format(name=name, value=value, pre=pre))

    def get_subs_stats_detail(self, data:tuple[str, float], index:int=None) -> tuple[int, int, float]:
        """
        说明：
            计算副词条的详细信息 (强化次数、挡位总积分与修正后的数值)
            对于速度属性只能做保守估计，其他属性可做准确计算。
            可以作为副词条校验函数 (可以检测出大部分的OCR错误)
        返回：
            :return level: 强化次数: 0次强化记为1，最高5次强化为6
            :return score: 挡位总积分: 1挡记0分, 2挡记1分, 3挡记2分
            :return result: 修正后数值 (提高了原数值精度)
        """
        if not self.is_check:
            return (0,0,0)
        name, value = data
        index = np.where(self.subs_stats_name[:, -1] == name)[0][0] if index is None else index
        a, d = self.subs_stats_tier[index]
        if name in self.not_pre_stats:
            a_ = int(a)           # 从个分位截断小数
        else:
            a_ = int(a * 10)/10   # 从十分位截断小数
        level = int(value / a_)                           # 向下取整
        score = (math.ceil((value - a*level) / d - 1.e-6))  # 向上取整 (考虑浮点数运算的数值损失)
        if score < 0:   # 总分小于零打补丁 (由于真实总分过大导致)
            level -= 1
            score = math.ceil((value - a*level) / d - 1.e-6)
        result = round(a*level + d*score, 3)              # 四舍五入 (考虑浮点数运算的数值损失)
        # 校验数据
        check = result - value
        log.debug(f"[{a}, {d}], l={level}, s={score}, r={result}")
        if check < 0 or \
            name in self.not_pre_stats and check > 1 or \
            name not in self.not_pre_stats and check > 0.1 or \
            level > 6 or level < 1 or \
            score > level*2 or score < 0:
            log.error(_(f"校验失败，原数据或计算方法有误: {data}"))
            return None
        return (level, score, result)