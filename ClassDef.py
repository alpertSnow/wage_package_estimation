import numpy as np
import FnDef as fd
from tqdm import tqdm
from ConstVar import AVG_TOWN_WAGE
from ConstVar import GZW_RATE_CAP
from ConstVar import LOAD_INDEX_LIMITS
from ConstVar import FINANCIAL_INDEX_LIMITS
from ConstVar import GZW_score_converted_growth

"""class"""

warned = [0, 0, 0]  # 用于保证人工成本投入产出指标应计算的报警只打印一次


class Unit(object):
    def __init__(self, var_name, name, package_last_year=np.nan,
                 total_profit_last_year=np.nan, total_profit_last_year_elimination=np.nan,
                 patmi_last_year=np.nan, patmi_last_year_elimination=np.nan,
                 revenue_last_year=np.nan, revenue_last_year_elimination=np.nan,
                 cost_last_year=np.nan, cost_last_year_elimination=np.nan,
                 invest_income_last_year=np.nan, other_income_last_year=np.nan,
                 total_profit=np.nan, total_profit_elimination=np.nan,
                 patmi=np.nan, patmi_elimination=np.nan,
                 revenue=np.nan, revenue_elimination=np.nan,
                 cost=np.nan, cost_elimination=np.nan,
                 invest_income=np.nan, other_income=np.nan,
                 avg_employee_last_year=np.nan, avg_employee=np.nan,
                 key_score=np.nan,
                 eff_index_1_name="", eff_index_2_name="", eff_index_3_name="", eff_index_4_name="",
                 eff_index_1_last_year=np.nan, eff_index_2_last_year=np.nan,
                 eff_index_3_last_year=np.nan, eff_index_4_last_year=np.nan,
                 eff_index_1=np.nan, eff_index_2=np.nan,
                 eff_index_3=np.nan, eff_index_4=np.nan,
                 eff_index_1_weight=np.nan, eff_index_2_weight=np.nan,
                 eff_index_3_weight=np.nan, eff_index_4_weight=np.nan):
        self.var_name = var_name
        self.name = name
        self.category = "Undefined"
        self.subcategory = ""
        self.package_last_year = package_last_year
        self.total_package_3 = np.nan
        self.total_package_final = np.nan
        self.package_2 = np.nan
        self.package_3 = np.nan
        self.package_final = np.nan
        self.defer_3 = np.nan  # 套用国资委速算函数后的预估值
        self.defer_final = np.nan
        self.deduct_3 = np.nan
        self.deduct_final = np.nan
        self.defer_rate_3 = np.nan
        self.defer_rate_final = np.nan
        self.deduct_rate_3 = np.nan
        self.deduct_rate_final = np.nan
        self.rate_1 = np.nan
        self.rate_2 = np.nan
        self.rate_3 = np.nan
        self.rate_final = np.nan
        self.avg_wage_last_year = package_last_year / avg_employee_last_year
        self.avg_wage_final = np.nan
        self.avg_employee_last_year = avg_employee_last_year
        self.avg_employee = avg_employee
        self.tune_total_package_coeff = np.nan  # 微调平账的调整系数:当年总包=实发+递延+扣减
        self.total_profit_last_year = total_profit_last_year
        self.total_profit_last_year_elimination = total_profit_last_year_elimination
        self.patmi_last_year = patmi_last_year  # 归母净利润Profit After Tax and Minority Interests
        self.patmi_last_year_elimination = patmi_last_year_elimination
        self.revenue_last_year = revenue_last_year
        self.revenue_last_year_elimination = revenue_last_year_elimination
        self.cost_last_year = cost_last_year
        self.cost_last_year_elimination = cost_last_year_elimination
        self.invest_income_last_year = invest_income_last_year
        self.other_income_last_year = other_income_last_year
        self.total_profit = total_profit
        self.total_profit_elimination = total_profit_elimination
        self.patmi = patmi
        self.patmi_elimination = patmi_elimination
        self.revenue = revenue
        self.revenue_elimination = revenue_elimination
        self.cost = cost
        self.cost_elimination = cost_elimination
        self.invest_income = invest_income
        self.other_income = other_income
        self.total_profit_growth = (self.total_profit - self.total_profit_last_year) / abs(self.total_profit_last_year)
        self.patmi_growth = (self.patmi - self.patmi_last_year) / abs(self.patmi_last_year)
        self.revenue_growth = (self.revenue - self.revenue_last_year) / abs(self.revenue_last_year)
        self.key_score = key_score
        self.key_score_converted_growth = fd.key_score_convert(self.key_score)
        self.eff_index_1_name = eff_index_1_name
        self.eff_index_2_name = eff_index_2_name
        self.eff_index_3_name = eff_index_3_name
        self.eff_index_4_name = eff_index_4_name
        self.eff_index_1_last_year = self.total_profit_last_year / self.avg_employee_last_year  # 默认人均净利润
        self.eff_index_2_last_year = self.revenue_last_year / self.avg_employee_last_year  # 默认人均营收
        self.eff_index_3_last_year = eff_index_3_last_year
        self.eff_index_4_last_year = eff_index_4_last_year
        self.eff_index_1 = self.total_profit / self.avg_employee
        self.eff_index_2 = self.revenue / self.avg_employee
        self.eff_index_3 = eff_index_3
        self.eff_index_4 = eff_index_4
        self.eff_index_1_weight = eff_index_1_weight
        self.eff_index_2_weight = eff_index_2_weight
        self.eff_index_3_weight = eff_index_3_weight
        self.eff_index_4_weight = eff_index_4_weight
        self.eff_index_1_growth = (self.eff_index_1 - self.eff_index_1_last_year) / abs(self.eff_index_1_last_year)
        self.eff_index_2_growth = (self.eff_index_2 - self.eff_index_2_last_year) / abs(self.eff_index_2_last_year)
        self.eff_index_3_growth = (self.eff_index_3 - self.eff_index_3_last_year) / abs(self.eff_index_3_last_year)
        self.eff_index_4_growth = (self.eff_index_4 - self.eff_index_4_last_year) / abs(self.eff_index_4_last_year)
        eff_indexes_growths = np.array([self.eff_index_1_growth, self.eff_index_2_growth,
                                        self.eff_index_3_growth, self.eff_index_4_growth])
        eff_indexes_weights = np.array([self.eff_index_1_weight, self.eff_index_2_weight,
                                        self.eff_index_3_weight, self.eff_index_4_weight])
        self.eff_growth = np.nansum(eff_indexes_growths * eff_indexes_weights)
        self.cost_income_ratio_last_year = self.cost_last_year / self.revenue_last_year
        self.cost_income_ratio = self.cost / self.revenue
        self.cost_income_ratio_growth = - (self.cost_income_ratio -
                                           self.cost_income_ratio_last_year) / abs(self.cost_income_ratio_last_year)
        # 检查输入参数
        if np.nansum(eff_indexes_weights) != 1:
            raise Warning("%s效率指标权重加和不等于1！" % self.name)

    """第二步：效率调整"""

    def rate_2_cal(self):
        global warned
        if self.category == "Public":
            avg_town_wage_limit = 3
        elif self.category == "Compete" or self.category == "Special":
            avg_town_wage_limit = 2.5
        else:
            raise ValueError('%s call rate_2_cal(): category error' % self.var_name)
        self.rate_2 = self.rate_1
        if self.rate_1 >= 0:
            if self.eff_growth < 0 or self.avg_wage_last_year > AVG_TOWN_WAGE * avg_town_wage_limit:
                self.rate_2 = 0.7 * self.rate_1
            # 人工成本投入产出指标应计算的报警
            elif self.category == "Compete" and self.subcategory == "approved" and warned[0] == 0:
                warned[0] = 1
                tqdm.write("Warning: %s效益提升，去年平均工资<%s*AVG_TOWN_WAGE且劳动生产率指标提升，人工成本投入产出率指标(未计算)可能生效" %
                           (self.var_name, avg_town_wage_limit))
            elif self.category == "Public" and self.subcategory == "approved" and warned[1] == 0:
                warned[1] = 1
                tqdm.write("Warning: %s效益提升，去年平均工资<%s*AVG_TOWN_WAGE且劳动生产率指标提升，人工成本投入产出率指标(未计算)可能生效" %
                           (self.var_name, avg_town_wage_limit))
            elif self.category == "Special" and self.subcategory == "approved" and warned[2] == 0:
                warned[2] = 1
                tqdm.write("Warning: %s效益提升，去年平均工资<%s*AVG_TOWN_WAGE且劳动生产率指标提升，人工成本投入产出率指标(未计算)可能生效" %
                           (self.var_name, avg_town_wage_limit))
        elif self.rate_1 < 0:
            if self.eff_growth > 0 or self.avg_wage_last_year <= AVG_TOWN_WAGE:
                self.rate_2 = 0.4 * self.rate_1
            # 人工成本投入产出指标应计算的报警
            elif self.category == "Compete" and self.subcategory == "approved" and warned[0] == 0:
                warned[0] = 1
                tqdm.write("Warning: %s效益下降，去年平均工资>AVG_TOWN_WAGE且劳动生产率指标下降，人工成本投入产出率指标(未计算)可能生效" %
                           self.var_name)
            elif self.category == "Public" and self.subcategory == "approved" and warned[1] == 0:
                warned[1] = 1
                tqdm.write("Warning: %s效益下降，去年平均工资>AVG_TOWN_WAGE且劳动生产率指标下降，人工成本投入产出率指标(未计算)可能生效" %
                           self.var_name)
            elif self.category == "Special" and self.subcategory == "approved" and warned[2] == 0:
                warned[2] = 1
                tqdm.write("Warning: %s效益下降，去年平均工资>AVG_TOWN_WAGE且劳动生产率指标下降，人工成本投入产出率指标(未计算)可能生效" %
                           self.var_name)
        self.package_2 = self.package_last_year * (1 + self.rate_2)

    """第三步：水平调控"""

    def rate_3_cal(self):  # 对Compete以外的，不涉及deduct；如果算出要递延defer则报警
        self.deduct_rate_3 = 0.0
        self.deduct_3 = 0.0
        if self.rate_2 - self.deduct_rate_3 > GZW_RATE_CAP:
            self.rate_3 = GZW_RATE_CAP
            # 套国资委递延公式
            self.defer_3 = ((1 + self.rate_1) - (1 + self.rate_3)) / \
                           ((1 / self.package_last_year) + 0.5 * 1 / self.total_profit_last_year)
        else:
            self.rate_3 = self.rate_2 - self.deduct_rate_3
            self.defer_3 = 0.0
        self.defer_rate_3 = self.defer_3 / self.package_last_year
        self.package_3 = (1 + self.rate_3) * self.package_last_year
        self.total_package_3 = np.nansum(self.package_3 + self.defer_3 + self.deduct_3)
        if self.defer_3 != 0.0:
            tqdm.write("Warning: %s 有递延" % self.name)

    """第四步：如果是国资委批复，则最终批复 = 第三步计算结果"""

    def copy_3_as_final(self):
        if self.subcategory == "approved":
            self.rate_final = self.rate_3
            self.defer_rate_final = self.defer_rate_3
            self.deduct_rate_final = self.deduct_rate_3
            self.package_final = self.package_3
            self.defer_final = self.defer_3
            self.deduct_final = self.deduct_3
            self.total_package_final = np.nansum(self.package_final + self.defer_final + self.deduct_final)
        else:
            raise ValueError('%s不是国资委批复！' % self.var_name)


class Compete(Unit):
    def __init__(self, var_name, name, package_last_year=np.nan,
                 total_profit_last_year=np.nan, total_profit_last_year_elimination=np.nan,
                 patmi_last_year=np.nan, patmi_last_year_elimination=np.nan,
                 revenue_last_year=np.nan, revenue_last_year_elimination=np.nan,
                 cost_last_year=np.nan, cost_last_year_elimination=np.nan,
                 invest_income_last_year=np.nan, other_income_last_year=np.nan,
                 total_profit=np.nan, total_profit_elimination=np.nan,
                 patmi=np.nan, patmi_elimination=np.nan,
                 revenue=np.nan, revenue_elimination=np.nan,
                 cost=np.nan, cost_elimination=np.nan,
                 invest_income=np.nan, other_income=np.nan,
                 avg_employee_last_year=np.nan, avg_employee=np.nan,
                 key_score=np.nan,
                 eff_index_1_name="", eff_index_2_name="", eff_index_3_name="", eff_index_4_name="",
                 eff_index_1_last_year=np.nan, eff_index_2_last_year=np.nan,
                 eff_index_3_last_year=np.nan, eff_index_4_last_year=np.nan,
                 eff_index_1=np.nan, eff_index_2=np.nan, eff_index_3=np.nan, eff_index_4=np.nan,
                 eff_index_1_weight=np.nan, eff_index_2_weight=np.nan,
                 eff_index_3_weight=np.nan, eff_index_4_weight=np.nan, **kwargs):
        super().__init__(var_name, name, package_last_year,
                         total_profit_last_year, total_profit_last_year_elimination,
                         patmi_last_year, patmi_last_year_elimination,
                         revenue_last_year, revenue_last_year_elimination,
                         cost_last_year, cost_last_year_elimination,
                         invest_income_last_year, other_income_last_year,
                         total_profit, total_profit_elimination,
                         patmi, patmi_elimination,
                         revenue, revenue_elimination,
                         cost, cost_elimination,
                         invest_income, other_income,
                         avg_employee_last_year, avg_employee,
                         key_score,
                         eff_index_1_name, eff_index_2_name, eff_index_3_name, eff_index_4_name,
                         eff_index_1_last_year, eff_index_2_last_year, eff_index_3_last_year, eff_index_4_last_year,
                         eff_index_1, eff_index_2, eff_index_3, eff_index_4,
                         eff_index_1_weight, eff_index_2_weight, eff_index_3_weight, eff_index_4_weight)

        self.category = "Compete"

    def rate_1_cal(self):
        self.rate_1 = 0.5 * self.total_profit_growth + 0.3 * self.patmi_growth + 0.2 * self.revenue_growth

    # 各家单位先扣减40%，然后自己套国资委的递延计算方法，得出工资总额+递延+扣减的总数（后面还需统一微调，即tune()）
    def rate_3_cal(self):
        """目前是先扣减，再递延，但是国资委公式里算出来的是递延+扣减，所以好像应该先算（递延+扣减）然后再扣40%"""
        # 与Units.rate_3_cal()差别仅在与是否扣减40%
        self.deduct_rate_3 = 0.0 if self.rate_2 <= 0 or self.subcategory == "approved" else self.rate_2 * 0.4
        self.deduct_3 = self.package_last_year * self.deduct_rate_3

        if self.rate_2 - self.deduct_rate_3 > GZW_RATE_CAP:
            self.rate_3 = GZW_RATE_CAP
            # 套用国资委递延计算函数
            self.defer_3 = ((1 + self.rate_1) - (1 + self.rate_3)) / \
                           ((1 / self.package_last_year) + 0.5 * 1 / self.total_profit_last_year) - self.deduct_3
        else:
            self.rate_3 = self.rate_2 - self.deduct_rate_3
            self.defer_3 = 0.0
        self.defer_rate_3 = self.defer_3 / self.package_last_year
        self.package_3 = (1 + self.rate_3) * self.package_last_year
        self.total_package_3 = np.nansum(self.package_3 + self.defer_3 + self.deduct_3)


class Public(Unit):
    def __init__(self, var_name, name, package_last_year=np.nan,
                 total_profit_last_year=np.nan, total_profit_last_year_elimination=np.nan,
                 patmi_last_year=np.nan, patmi_last_year_elimination=np.nan,
                 revenue_last_year=np.nan, revenue_last_year_elimination=np.nan,
                 cost_last_year=np.nan, cost_last_year_elimination=np.nan,
                 invest_income_last_year=np.nan, other_income_last_year=np.nan,
                 total_profit=np.nan, total_profit_elimination=np.nan,
                 patmi=np.nan, patmi_elimination=np.nan,
                 revenue=np.nan, revenue_elimination=np.nan,
                 cost=np.nan, cost_elimination=np.nan,
                 invest_income=np.nan, other_income=np.nan,
                 avg_employee_last_year=np.nan, avg_employee=np.nan,
                 key_score=np.nan,
                 eff_index_1_name="", eff_index_2_name="", eff_index_3_name="", eff_index_4_name="",
                 eff_index_1_last_year=np.nan, eff_index_2_last_year=np.nan,
                 eff_index_3_last_year=np.nan, eff_index_4_last_year=np.nan,
                 eff_index_1=np.nan, eff_index_2=np.nan, eff_index_3=np.nan, eff_index_4=np.nan,
                 eff_index_1_weight=np.nan, eff_index_2_weight=np.nan,
                 eff_index_3_weight=np.nan, eff_index_4_weight=np.nan,
                 quality_index_last_year=np.nan, cost_index_last_year=np.nan, operate_index_last_year=np.nan,
                 quality_index=np.nan, cost_index=np.nan, operate_index=np.nan, **kwargs):
        super().__init__(var_name, name, package_last_year,
                         total_profit_last_year, total_profit_last_year_elimination,
                         patmi_last_year, patmi_last_year_elimination,
                         revenue_last_year, revenue_last_year_elimination,
                         cost_last_year, cost_last_year_elimination,
                         invest_income_last_year, other_income_last_year,
                         total_profit, total_profit_elimination,
                         patmi, patmi_elimination,
                         revenue, revenue_elimination,
                         cost, cost_elimination,
                         invest_income, other_income,
                         avg_employee_last_year, avg_employee,
                         key_score,
                         eff_index_1_name, eff_index_2_name, eff_index_3_name, eff_index_4_name,
                         eff_index_1_last_year, eff_index_2_last_year, eff_index_3_last_year, eff_index_4_last_year,
                         eff_index_1, eff_index_2, eff_index_3, eff_index_4,
                         eff_index_1_weight, eff_index_2_weight, eff_index_3_weight, eff_index_4_weight)

        self.category = "Public"
        self.quality_index_last_year = quality_index_last_year
        self.cost_index_last_year = cost_index_last_year
        self.operate_index_last_year = operate_index_last_year
        self.quality_index = quality_index
        self.cost_index = cost_index
        self.operate_index = operate_index
        self.quality_index_growth = (quality_index - quality_index_last_year) / abs(quality_index_last_year)
        # cost/revenue加负号
        self.cost_index_growth = - ((cost_index - cost_index_last_year) / abs(cost_index_last_year))
        self.operate_index_growth = (operate_index - operate_index_last_year) / abs(operate_index_last_year)

    def rate_1_cal(self):
        # 国资委批复标准
        if True:  # self.subcategory == "approved":
            self.rate_1 = 0.5 * self.quality_index_growth + 0.3 * self.cost_index_growth + \
                          0.2 * self.operate_index_growth
        """# 第二种方案：重点工作计划得分：50%，532指标:50%
        else:
            self.rate_1 = 0.5 * self.key_score_converted_growth + 0.25 * self.quality_index_growth + \
                      0.15 * self.cost_index_growth + 0.10 * self.operate_index_growth"""


class Special(Unit):
    def __init__(self, var_name, name, package_last_year=np.nan,
                 total_profit_last_year=np.nan, total_profit_last_year_elimination=np.nan,
                 patmi_last_year=np.nan, patmi_last_year_elimination=np.nan,
                 revenue_last_year=np.nan, revenue_last_year_elimination=np.nan,
                 cost_last_year=np.nan, cost_last_year_elimination=np.nan,
                 invest_income_last_year=np.nan, other_income_last_year=np.nan,
                 total_profit=np.nan, total_profit_elimination=np.nan,
                 patmi=np.nan, patmi_elimination=np.nan,
                 revenue=np.nan, revenue_elimination=np.nan,
                 cost=np.nan, cost_elimination=np.nan,
                 invest_income=np.nan, other_income=np.nan,
                 avg_employee_last_year=np.nan, avg_employee=np.nan,
                 key_score=np.nan,
                 eff_index_1_name="", eff_index_2_name="", eff_index_3_name="", eff_index_4_name="",
                 eff_index_1_last_year=np.nan, eff_index_2_last_year=np.nan,
                 eff_index_3_last_year=np.nan, eff_index_4_last_year=np.nan,
                 eff_index_1=np.nan, eff_index_2=np.nan, eff_index_3=np.nan, eff_index_4=np.nan,
                 eff_index_1_weight=np.nan, eff_index_2_weight=np.nan,
                 eff_index_3_weight=np.nan, eff_index_4_weight=np.nan,
                 load_index_last_year=np.nan, load_index=np.nan,
                 financial_index_name="", **kwargs):
        super().__init__(var_name, name, package_last_year,
                         total_profit_last_year, total_profit_last_year_elimination,
                         patmi_last_year, patmi_last_year_elimination,
                         revenue_last_year, revenue_last_year_elimination,
                         cost_last_year, cost_last_year_elimination,
                         invest_income_last_year, other_income_last_year,
                         total_profit, total_profit_elimination,
                         patmi, patmi_elimination,
                         revenue, revenue_elimination,
                         cost, cost_elimination,
                         invest_income, other_income,
                         avg_employee_last_year, avg_employee,
                         key_score,
                         eff_index_1_name, eff_index_2_name, eff_index_3_name, eff_index_4_name,
                         eff_index_1_last_year, eff_index_2_last_year, eff_index_3_last_year, eff_index_4_last_year,
                         eff_index_1, eff_index_2, eff_index_3, eff_index_4,
                         eff_index_1_weight, eff_index_2_weight, eff_index_3_weight, eff_index_4_weight)

        self.category = "Special"
        self.load_index_last_year = load_index_last_year
        self.load_index = load_index
        self.load_index_growth = load_index / load_index_last_year - 1
        self.financial_index_name = financial_index_name
        """经过与国资委沟通，成本费用占营收比 调整为：成本费用/(营收+投资收益+其他收益)）"""
        self.cost_income_ratio_last_year = self.cost_last_year / (self.revenue_last_year +
                                                                  self.invest_income_last_year +
                                                                  self.other_income_last_year)
        self.cost_income_ratio = self.cost / (self.revenue + self.invest_income + self.other_income)
        self.cost_income_ratio_growth = - ((self.cost_income_ratio -
                                            self.cost_income_ratio_last_year) / abs(self.cost_income_ratio_last_year))

    # 用于国资委批复的计算，对单位不起作用
    def rate_1_cal(self):
        # 计算成本费用占营收比
        self.key_score_converted_growth = GZW_score_converted_growth
        self.rate_1 = 0.5 * GZW_score_converted_growth + 0.3 * self.patmi_growth + 0.2 * self.cost_income_ratio_growth


class SpecialGov(Special):
    def __init__(self, var_name, name, package_last_year=np.nan,
                 total_profit_last_year=np.nan, total_profit_last_year_elimination=np.nan,
                 patmi_last_year=np.nan, patmi_last_year_elimination=np.nan,
                 revenue_last_year=np.nan, revenue_last_year_elimination=np.nan,
                 cost_last_year=np.nan, cost_last_year_elimination=np.nan,
                 invest_income_last_year=np.nan, other_income_last_year=np.nan,
                 total_profit=np.nan, total_profit_elimination=np.nan,
                 patmi=np.nan, patmi_elimination=np.nan,
                 revenue=np.nan, revenue_elimination=np.nan,
                 cost=np.nan, cost_elimination=np.nan,
                 invest_income=np.nan, other_income=np.nan,
                 avg_employee_last_year=np.nan, avg_employee=np.nan,
                 key_score=np.nan,
                 eff_index_1_name="", eff_index_2_name="", eff_index_3_name="", eff_index_4_name="",
                 eff_index_1_last_year=np.nan, eff_index_2_last_year=np.nan,
                 eff_index_3_last_year=np.nan, eff_index_4_last_year=np.nan,
                 eff_index_1=np.nan, eff_index_2=np.nan, eff_index_3=np.nan, eff_index_4=np.nan,
                 eff_index_1_weight=np.nan, eff_index_2_weight=np.nan,
                 eff_index_3_weight=np.nan, eff_index_4_weight=np.nan,
                 load_index_last_year=np.nan, load_index=np.nan,
                 financial_index_name="", **kwargs):
        super().__init__(var_name, name, package_last_year,
                         total_profit_last_year, total_profit_last_year_elimination,
                         patmi_last_year, patmi_last_year_elimination,
                         revenue_last_year, revenue_last_year_elimination,
                         cost_last_year, cost_last_year_elimination,
                         invest_income_last_year, other_income_last_year,
                         total_profit, total_profit_elimination,
                         patmi, patmi_elimination,
                         revenue, revenue_elimination,
                         cost, cost_elimination,
                         invest_income, other_income,
                         avg_employee_last_year, avg_employee,
                         key_score,
                         eff_index_1_name, eff_index_2_name, eff_index_3_name, eff_index_4_name,
                         eff_index_1_last_year, eff_index_2_last_year, eff_index_3_last_year, eff_index_4_last_year,
                         eff_index_1, eff_index_2, eff_index_3, eff_index_4,
                         eff_index_1_weight, eff_index_2_weight, eff_index_3_weight, eff_index_4_weight,
                         load_index_last_year, load_index,
                         financial_index_name)

        self.subcategory = "Gov"
        self.load_index_limited = np.nan

    def rate_1_cal(self):
        if self.load_index_growth < LOAD_INDEX_LIMITS[0]:
            self.load_index_limited = -1
            self.rate_1 = 0.5 * self.key_score_converted_growth + 0.5 * LOAD_INDEX_LIMITS[0]
        elif self.load_index_growth > LOAD_INDEX_LIMITS[1]:
            self.load_index_limited = 1
            self.rate_1 = 0.5 * self.key_score_converted_growth + 0.5 * LOAD_INDEX_LIMITS[1]
        else:
            self.load_index_limited = 0
            self.rate_1 = 0.5 * self.key_score_converted_growth + 0.5 * self.load_index_growth


class SpecialMarket(Special):
    def __init__(self, var_name, name, package_last_year=np.nan,
                 total_profit_last_year=np.nan, total_profit_last_year_elimination=np.nan,
                 patmi_last_year=np.nan, patmi_last_year_elimination=np.nan,
                 revenue_last_year=np.nan, revenue_last_year_elimination=np.nan,
                 cost_last_year=np.nan, cost_last_year_elimination=np.nan,
                 invest_income_last_year=np.nan, other_income_last_year=np.nan,
                 total_profit=np.nan, total_profit_elimination=np.nan,
                 patmi=np.nan, patmi_elimination=np.nan,
                 revenue=np.nan, revenue_elimination=np.nan,
                 cost=np.nan, cost_elimination=np.nan,
                 invest_income=np.nan, other_income=np.nan,
                 avg_employee_last_year=np.nan, avg_employee=np.nan,
                 key_score=np.nan,
                 eff_index_1_name="", eff_index_2_name="", eff_index_3_name="", eff_index_4_name="",
                 eff_index_1_last_year=np.nan, eff_index_2_last_year=np.nan,
                 eff_index_3_last_year=np.nan, eff_index_4_last_year=np.nan,
                 eff_index_1=np.nan, eff_index_2=np.nan, eff_index_3=np.nan, eff_index_4=np.nan,
                 eff_index_1_weight=np.nan, eff_index_2_weight=np.nan,
                 eff_index_3_weight=np.nan, eff_index_4_weight=np.nan,
                 load_index_last_year=np.nan, load_index=np.nan,
                 financial_index_name="", **kwargs):
        super().__init__(var_name, name, package_last_year,
                         total_profit_last_year, total_profit_last_year_elimination,
                         patmi_last_year, patmi_last_year_elimination,
                         revenue_last_year, revenue_last_year_elimination,
                         cost_last_year, cost_last_year_elimination,
                         invest_income_last_year, other_income_last_year,
                         total_profit, total_profit_elimination,
                         patmi, patmi_elimination,
                         revenue, revenue_elimination,
                         cost, cost_elimination,
                         invest_income, other_income,
                         avg_employee_last_year, avg_employee,
                         key_score,
                         eff_index_1_name, eff_index_2_name, eff_index_3_name, eff_index_4_name,
                         eff_index_1_last_year, eff_index_2_last_year, eff_index_3_last_year, eff_index_4_last_year,
                         eff_index_1, eff_index_2, eff_index_3, eff_index_4,
                         eff_index_1_weight, eff_index_2_weight, eff_index_3_weight, eff_index_4_weight,
                         load_index_last_year, load_index,
                         financial_index_name)

        self.subcategory = "Market"
        if self.financial_index_name == "total_profit":
            self.financial_index_growth = self.total_profit_growth
        elif self.financial_index_name == "patmi":
            self.financial_index_growth = self.patmi_growth
        elif self.financial_index_name == "revenue":
            self.financial_index_growth = self.revenue_growth
        else:
            raise ValueError('%s: wrong financial index' % self.name)
        self.financial_index_limited = np.nan

    def rate_1_cal(self):
        if self.financial_index_growth < FINANCIAL_INDEX_LIMITS[0]:
            self.financial_index_limited = -1
            self.rate_1 = 0.5 * self.key_score_converted_growth + 0.5 * FINANCIAL_INDEX_LIMITS[0]
        elif self.financial_index_growth > FINANCIAL_INDEX_LIMITS[1]:
            self.financial_index_limited = 1
            self.rate_1 = 0.5 * self.key_score_converted_growth + 0.5 * FINANCIAL_INDEX_LIMITS[1]
        else:
            self.financial_index_limited = 0
            self.rate_1 = 0.5 * self.key_score_converted_growth + 0.5 * self.financial_index_growth
