from utils.calculated import Calculated as ca
# 差导入ocr的包
"""
计算收益所得
使用calculator.result()即可知道收益
目前不同均衡等级的所得体力对应经验值不确定,所得值不太准确
"""


class Revenue_Calculator:
    def __init__(self):
        self.number = 4      # 携带未满经验的人数
        self.Rank = 1        # 均衡等级
        self.EXP = 288 * self.number      # 经验
        self.MONEY = self.check_value()     # 通过check_value得到的值
        self.EXP_SUM = 0
        self.MONEY_SUM = 0
        self.tili_sum = 0

    def part_ocr(self, points=(0, 450, 405, 990)):
        """
        返回图片文字和坐标参数:
        :param points:图像截取范围返回:
        :return data:文字:坐标u 
        """
        img_fp, left, top, right, bottom = ca.take_screenshot(
            points)
        width = right - left
        length = bottom - top
        x, y = width/100*points[0], length/100*points[1]
        out = self.ocr.ocr(img_fp)  # 使用ocr
        data = {i['text']: (x+(i['position'][2][0]+i['position'][0][0])/2,
                            y+(i['position'][2][1]+i['position '][2][1])/2) for i in out}
        return data

    def check_value(self):
        target_text = None
        # 使用self.part_ocr获取OCR识别结果
        data = self.part_ocr()
        for item in data:
            if isinstance(item, tuple) and '信用点' in item[0]:
                target_text = item[0]
                break

        # 提取"信用点"后的数值部分
        if target_text is not None:
            value = target_text.split(':')[-1].strip()
            return value
        else:
            return -1

    def tili_Calculator(self, Rank, EXP, MONEY):
        if MONEY == -1:
            tili_sum = -1
            return tili_sum
        else:
            tili_ratios = {
                0: (950, 1000),
                1: (1250, 1500),
                2: (1600, 2000),
                3: (2000, 2500),
                4: (2400, 3000)
            }

            tili_MONEY, tili_EXP = tili_ratios.get(Rank, (0, 0))
            tili_sum = (MONEY / tili_MONEY) + (EXP / tili_EXP)

            return tili_sum

    def result(self):
        tili_sum = self.tili_Calculator(self.Rank, self.EXP, self.MONEY)
        if tili_sum == -1:
            # 没有发生战斗
            print(
                f"已获得{self.EXP_SUM}(+{0})经验和{self.MONEY_SUM}信用点(+{0}),已经节省{self.tili_sum}体力(+{0})")
        else:
            self.EXP_SUM += self.EXP
            self.MONEY_SUM += self.MONEY
            self.tili_sum += tili_sum
            print(
                f"已获得{self.EXP_SUM}(+{self.EXP})经验和{self.MONEY_SUM}信用点(+{self.MONEY}),已经节省{self.tili_sum}体力(+{tili_sum})")


# calculator = Revenue_Calculator()
# calculator.result()
# calculator.result()
# calculator.result()
