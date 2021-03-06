import numpy as np
import FnDef as fd
from tqdm import tqdm
from ConstVar import AVG_TOWN_WAGE
from ConstVar import GZW_RATE_CAP
from ConstVar import GZW_BASE_RATE
from ConstVar import FINANCIAL_INDEX_LIMITS
from ConstVar import GZW_score_converted_growth

"""class"""

warned = [0, 0, 0]  # 用于保证人工成本投入产出指标应计算的报警只打印一次


class Unit(object):
    def __init__(self, var_name, name, package_last_year=np.nan,
                 defer_last_year=np.nan, distributable_last_year=np.nan,
                 total_profit_last_year=np.nan, patmi_self_last_year=np.nan, patmi_BII_last_year=np.nan,
                 revenue_last_year=np.nan, cost_last_year=np.nan,
                 invest_income_last_year=np.nan, other_income_last_year=np.nan, labor_cost_last_year=np.nan,
                 total_profit=np.nan, patmi_self=np.nan, patmi_BII=np.nan,
                 revenue=np.nan, cost=np.nan, invest_income=np.nan, other_income=np.nan, labor_cost=np.nan,
                 avg_employee_last_year=np.nan, avg_employee=np.nan, key_score=np.nan,
                 eff_index_1_weight=np.nan, eff_index_2_weight=np.nan,
                 eff_index_3_weight=np.nan, eff_index_4_weight=np.nan):
        self.var_name = var_name
        self.name = name
        self.category = "Undefined"
        self.subcategory = ""
        self.package_last_year = package_last_year
        self.defer_last_year = defer_last_year
        self.distributable_last_year = distributable_last_year
        self.total_package_3 = np.nan
        self.total_package_final = np.nan
        self.total_package_real = np.nan
        self.package_2 = np.nan
        self.package_3 = np.nan
        self.package_final = np.nan
        self.package_real = np.nan  # 加上上年度本公司递延额度，当年度实际可发工资
        self.defer_3 = np.nan  # 套用国资委速算函数后的预估值
        self.defer_final = np.nan
        self.deduct_3 = np.nan
        self.deduct_final = np.nan
        self.rate_1 = np.nan
        self.rate_2 = np.nan
        self.rate_3 = np.nan
        self.rate_final = np.nan
        self.rate_real = np.nan
        self.defer_rate_3 = np.nan
        self.defer_rate_final = np.nan
        self.deduct_rate_3 = np.nan
        self.deduct_rate_final = np.nan
        self.tune_alpha = np.nan  # 微调平账的调整系数:总额不动，递延×alpha。详见 单位与板块矛盾统筹调整的逻辑.emmx
        self.tune_beta = np.nan  # 微调平账的调整系数:总额和递延都×beta。详见 单位与板块矛盾统筹调整的逻辑.emmx
        self.total_profit_last_year = total_profit_last_year
        self.patmi_self_last_year = patmi_self_last_year  # 归母净利润Profit After Tax and Minority Interests
        self.patmi_BII_last_year = patmi_BII_last_year
        self.revenue_last_year = revenue_last_year
        self.cost_last_year = cost_last_year
        self.invest_income_last_year = invest_income_last_year
        self.other_income_last_year = other_income_last_year
        self.labor_cost_last_year = labor_cost_last_year
        self.total_profit = total_profit
        self.patmi_self = patmi_self
        self.patmi_BII = patmi_BII
        self.revenue = revenue
        self.cost = cost
        self.invest_income = invest_income
        self.other_income = other_income
        self.labor_cost = labor_cost
        self.total_profit_growth = np.divide((self.total_profit - self.total_profit_last_year),
                                             abs(self.total_profit_last_year))
        self.patmi_self_growth = np.divide((self.patmi_self - self.patmi_self_last_year),
                                           abs(self.patmi_self_last_year))
        self.patmi_BII_growth = np.divide((self.patmi_BII - self.patmi_BII_last_year), abs(self.patmi_BII_last_year))
        self.revenue_growth = np.divide((self.revenue - self.revenue_last_year), abs(self.revenue_last_year))
        self.key_score = key_score
        self.key_score_converted_growth = fd.key_score_convert(self.key_score)
        # 除特殊版块对象以外：成本费用占收入比=营业总成本/营收。升高为劣化
        self.cost_income_ratio_last_year = np.divide(self.cost_last_year, self.revenue_last_year)
        self.cost_income_ratio = np.divide(self.cost, self.revenue)
        self.cost_income_ratio_growth = - np.divide((self.cost_income_ratio -
                                                     self.cost_income_ratio_last_year),
                                                    abs(self.cost_income_ratio_last_year))
        self.avg_employee_last_year = avg_employee_last_year
        self.avg_employee = avg_employee
        self.eff_index_1_last_year = np.divide(self.total_profit_last_year, self.avg_employee_last_year)  # 默认人均净利润
        self.eff_index_2_last_year = np.divide(self.patmi_self_last_year, self.avg_employee_last_year)  # 默认人均归母
        self.eff_index_3_last_year = np.divide(self.patmi_BII_last_year, self.avg_employee_last_year)  # 默认人均归母
        self.eff_index_4_last_year = np.divide(self.revenue_last_year, self.avg_employee_last_year)  # 默认人均营收
        self.eff_index_1 = np.divide(self.total_profit, self.avg_employee)
        self.eff_index_2 = np.divide(self.patmi_self, self.avg_employee)
        self.eff_index_3 = np.divide(self.patmi_BII, self.avg_employee)
        self.eff_index_4 = np.divide(self.revenue, self.avg_employee)
        self.eff_index_1_weight = eff_index_1_weight
        self.eff_index_2_weight = eff_index_2_weight
        self.eff_index_3_weight = eff_index_3_weight
        self.eff_index_4_weight = eff_index_4_weight
        self.eff_index_1_growth = np.divide((self.eff_index_1 - self.eff_index_1_last_year),
                                            abs(self.eff_index_1_last_year))
        self.eff_index_2_growth = np.divide((self.eff_index_2 - self.eff_index_2_last_year),
                                            abs(self.eff_index_2_last_year))
        self.eff_index_3_growth = np.divide((self.eff_index_3 - self.eff_index_3_last_year),
                                            abs(self.eff_index_3_last_year))
        self.eff_index_4_growth = np.divide((self.eff_index_4 - self.eff_index_4_last_year),
                                            abs(self.eff_index_4_last_year))
        eff_indexes_growths = np.array([self.eff_index_1_growth, self.eff_index_2_growth,
                                        self.eff_index_3_growth, self.eff_index_4_growth])
        eff_indexes_weights = np.array([self.eff_index_1_weight, self.eff_index_2_weight,
                                        self.eff_index_3_weight, self.eff_index_4_weight])
        # 人事费用率=人工成本/营收。升高为劣化
        self.labor_revenue_ratio_last_year = np.divide(self.labor_cost_last_year, self.revenue_last_year)
        self.labor_revenue_ratio = np.divide(self.labor_cost, self.revenue)
        self.labor_revenue_ratio_growth = - np.divide((self.labor_revenue_ratio -
                                                       self.labor_revenue_ratio_last_year),
                                                      abs(self.labor_revenue_ratio_last_year))
        # 人事费用率=人工成本/营收。升高为优化
        self.profit_labor_ratio_last_year = np.divide(self.total_profit_last_year, self.labor_cost_last_year)
        self.profit_labor_ratio = np.divide(self.total_profit, self.labor_cost)
        self.profit_labor_ratio_growth = np.divide((self.profit_labor_ratio -
                                                    self.profit_labor_ratio_last_year),
                                                   abs(self.profit_labor_ratio_last_year))
        self.eff_growth = np.nansum(eff_indexes_growths * eff_indexes_weights)
        # 平均加权得到人工成本投入产出率
        self.labor_eff_growth = np.nanmean([self.labor_revenue_ratio_growth, self.profit_labor_ratio_growth])
        self.avg_wage_last_year = np.divide(package_last_year, avg_employee_last_year)
        self.avg_wage_final = np.nan
        self.avg_wage_real = np.nan


        # 检查输入参数
        if np.nansum(eff_indexes_weights) != 1:
            raise Warning("%s效率指标权重加和不等于1！" % self.name)

    """第二步：效率调整"""

    def rate_2_cal(self):
        """企业经济效益增长的，对于当年劳动生产率、人工成本投入产出率未提高，
        或者竞争类、特殊功能类企业2019年职工平均工资达到全国城镇单位就业人员平均工资3倍以上，
        城市公共服务类企业达到2.5倍以上的，工资总额增幅不超过经济效益增幅的70%。
        企业经济效益下降的，除受政策调整等非经营性因素影响外，当年工资总额原则上相应下降。
        对于当年劳动生产率、人工成本投入产出率未下降，或者2019年职工平均工资未达到全国城镇单位就业人员平均工资的，
        当年工资总额降幅在经济效益降幅的40%范围内确定。"""
        if self.category == "Public":
            avg_town_wage_limit = 2.5
        elif self.category == "Compete" or self.category == "Special":
            avg_town_wage_limit = 3
        else:
            raise ValueError('%s call rate_2_cal(): category error' % self.var_name)
        self.rate_2 = self.rate_1
        if self.rate_1 >= 0:
            if self.eff_growth < 0 or self.labor_eff_growth < 0 or \
                    self.avg_wage_last_year > AVG_TOWN_WAGE * avg_town_wage_limit:
                self.rate_2 = 0.7 * self.rate_1
        elif self.rate_1 < 0:
            if self.avg_wage_last_year <= AVG_TOWN_WAGE:
                self.rate_2 = 0.4 * self.rate_1
            elif self.eff_growth > 0 and self.labor_eff_growth > 0:
                self.rate_2 = 0.4 * self.rate_1
        self.package_2 = self.package_last_year * (1 + self.rate_2)

    """第三步：水平调控"""

    def rate_3_cal(self):  # 对Compete以外的，不涉及deduct；如果算出要递延defer则报警
        self.deduct_rate_3 = 0.0
        self.deduct_3 = 0.0
        if self.rate_2 - self.deduct_rate_3 > GZW_RATE_CAP:
            self.rate_3 = GZW_RATE_CAP
            # 套国资委递延公式
            # TODO: 此公式只对0.5权重利润总额的有效
            self.defer_3 = ((1 + self.rate_2) - (1 + GZW_RATE_CAP)) / \
                           ((1 / self.package_last_year) + 0.5 * 1 / abs(self.total_profit_last_year))
        else:
            self.rate_3 = self.rate_2 - self.deduct_rate_3
            self.defer_3 = 0.0
        self.defer_rate_3 = self.defer_3 / self.package_last_year
        self.package_3 = (1 + self.rate_3) * self.package_last_year
        self.total_package_3 = np.nansum(self.package_3 + self.defer_3 + self.deduct_3)
        # if self.defer_3 != 0.0:
        #     tqdm.write("Warning: %s 有递延" % self.name)

    """第四步：如果是国资委批复，则最终批复 = 第三步计算结果"""

    def copy_3_as_final(self):
        if self.subcategory == "approved":
            self.rate_final = self.rate_3
            self.defer_rate_final = self.defer_rate_3
            self.deduct_rate_final = self.deduct_rate_3
            self.package_final = self.package_3
            self.package_real = self.package_final + self.defer_last_year + self.distributable_last_year
            self.defer_final = self.defer_3
            self.deduct_final = self.deduct_3
            self.total_package_final = np.nansum([self.package_final, self.defer_final, self.deduct_final])
            self.total_package_real = np.nansum([self.package_real, self.defer_final, self.deduct_final])
        else:
            raise ValueError('%s不是国资委批复！' % self.var_name)


class Compete(Unit):
    def __init__(self, var_name, name, package_last_year=np.nan,
                 defer_last_year=np.nan, distributable_last_year=np.nan,
                 total_profit_last_year=np.nan, patmi_self_last_year=np.nan, patmi_BII_last_year=np.nan,
                 revenue_last_year=np.nan, cost_last_year=np.nan,
                 invest_income_last_year=np.nan, other_income_last_year=np.nan, labor_cost_last_year=np.nan,
                 total_profit=np.nan, patmi_self=np.nan, patmi_BII=np.nan,
                 revenue=np.nan, cost=np.nan,
                 invest_income=np.nan, other_income=np.nan, labor_cost=np.nan,
                 avg_employee_last_year=np.nan, avg_employee=np.nan,
                 key_score=np.nan,
                 eff_index_1_weight=np.nan, eff_index_2_weight=np.nan,
                 eff_index_3_weight=np.nan, eff_index_4_weight=np.nan, **kwargs):
        super().__init__(var_name, name, package_last_year, defer_last_year, distributable_last_year,
                         total_profit_last_year, patmi_self_last_year, patmi_BII_last_year,
                         revenue_last_year, cost_last_year, invest_income_last_year, other_income_last_year,
                         labor_cost_last_year,
                         total_profit, patmi_self, patmi_BII, revenue, cost, invest_income, other_income, labor_cost,
                         avg_employee_last_year, avg_employee, key_score,
                         eff_index_1_weight, eff_index_2_weight, eff_index_3_weight, eff_index_4_weight)

        self.category = "Compete"

    def rate_1_cal(self):
        self.rate_1 = 0.5 * self.total_profit_growth + 0.3 * self.patmi_BII_growth + 0.2 * self.revenue_growth

    # 各家单位先扣减40%，然后自己套国资委的递延计算方法，得出工资总额+递延+扣减的总数（后面还需统一微调，即tune()）
    def rate_3_cal(self):
        # 先算（递延+扣减）然后再扣减40%
        # 与Units.rate_3_cal()差别仅在与是否扣减40%
        if self.rate_2 > GZW_RATE_CAP:
            # 若需要递延，则套用国资委递延计算函数，计算递延+扣减的总值
            defer_plus_deduct = ((1 + self.rate_2) - (1 + GZW_RATE_CAP)) / \
                                ((1 / self.package_last_year) + 0.5 * 1 / abs(self.total_profit_last_year))
            # 扣减值 = （递延+扣减+当年度工资帽）*40%；国资委批复不扣减
            self.deduct_rate_3 = (defer_plus_deduct / self.package_last_year + GZW_RATE_CAP) * 0.4 if \
                self.subcategory != "approved" else 0.0
            # 当年工资增幅 = min（扣减后剩余额度，工资帽）；国资委批复不扣减
            self.rate_3 = min(GZW_RATE_CAP, (defer_plus_deduct / self.package_last_year + GZW_RATE_CAP) * 0.6) if \
                self.subcategory != "approved" else GZW_RATE_CAP
            self.defer_rate_3 = defer_plus_deduct / self.package_last_year + GZW_RATE_CAP - self.deduct_rate_3 - self.rate_3
        else:
            # 没到工资帽则不用递延。降工资则不扣减。增工资则直接扣减40%
            self.deduct_rate_3 = 0.0 if self.rate_2 <= 0 or self.subcategory == "approved" else self.rate_2 * 0.4
            self.rate_3 = self.rate_2 - self.deduct_rate_3
            self.defer_rate_3 = 0.0
        self.package_3 = (1 + self.rate_3) * self.package_last_year
        self.defer_3 = self.defer_rate_3 * self.package_last_year
        self.deduct_3 = self.deduct_rate_3 * self.package_last_year
        self.total_package_3 = np.nansum([self.package_3, self.defer_3, self.deduct_3])


class Public(Unit):
    def __init__(self, var_name, name, package_last_year=np.nan,
                 defer_last_year=np.nan, distributable_last_year=np.nan,
                 total_profit_last_year=np.nan, patmi_self_last_year=np.nan, patmi_BII_last_year=np.nan,
                 revenue_last_year=np.nan, cost_last_year=np.nan,
                 invest_income_last_year=np.nan, other_income_last_year=np.nan, labor_cost_last_year=np.nan,
                 total_profit=np.nan, patmi_self=np.nan, patmi_BII=np.nan,
                 revenue=np.nan, cost=np.nan, invest_income=np.nan, other_income=np.nan, labor_cost=np.nan,
                 avg_employee_last_year=np.nan, avg_employee=np.nan, key_score=np.nan,
                 eff_index_1_weight=np.nan, eff_index_2_weight=np.nan,
                 eff_index_3_weight=np.nan, eff_index_4_weight=np.nan,
                 quality_index_last_year=np.nan, cost_index_last_year=np.nan, operate_index_last_year=np.nan,
                 quality_index=np.nan, cost_index=np.nan, operate_index=np.nan, **kwargs):
        super().__init__(var_name, name, package_last_year, defer_last_year, distributable_last_year,
                         total_profit_last_year, patmi_self_last_year, patmi_BII_last_year,
                         revenue_last_year, cost_last_year, invest_income_last_year, other_income_last_year,
                         labor_cost_last_year,
                         total_profit, patmi_self, patmi_BII, revenue, cost, invest_income, other_income, labor_cost,
                         avg_employee_last_year, avg_employee, key_score,
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
                 defer_last_year=np.nan, distributable_last_year=np.nan,
                 total_profit_last_year=np.nan, patmi_self_last_year=np.nan, patmi_BII_last_year=np.nan,
                 revenue_last_year=np.nan, cost_last_year=np.nan,
                 invest_income_last_year=np.nan, other_income_last_year=np.nan, labor_cost_last_year=np.nan,
                 total_profit=np.nan, patmi_self=np.nan, patmi_BII=np.nan,
                 revenue=np.nan, cost=np.nan, invest_income=np.nan, other_income=np.nan, labor_cost=np.nan,
                 avg_employee_last_year=np.nan, avg_employee=np.nan, key_score=np.nan,
                 eff_index_1_weight=np.nan, eff_index_2_weight=np.nan,
                 eff_index_3_weight=np.nan, eff_index_4_weight=np.nan,
                 financial_index_name="", **kwargs):
        super().__init__(var_name, name, package_last_year, defer_last_year, distributable_last_year,
                         total_profit_last_year, patmi_self_last_year, patmi_BII_last_year,
                         revenue_last_year, cost_last_year, invest_income_last_year, other_income_last_year,
                         labor_cost_last_year,
                         total_profit, patmi_self, patmi_BII, revenue, cost, invest_income, other_income, labor_cost,
                         avg_employee_last_year, avg_employee, key_score,
                         eff_index_1_weight, eff_index_2_weight, eff_index_3_weight, eff_index_4_weight)

        self.category = "Special"
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
        self.rate_1 = 0.5 * GZW_score_converted_growth + 0.3 * self.patmi_BII_growth + 0.2 * self.cost_income_ratio_growth


class SpecialGov(Special):
    def __init__(self, var_name, name, package_last_year=np.nan,
                 defer_last_year=np.nan, distributable_last_year=np.nan,
                 total_profit_last_year=np.nan, patmi_self_last_year=np.nan, patmi_BII_last_year=np.nan,
                 revenue_last_year=np.nan, cost_last_year=np.nan,
                 invest_income_last_year=np.nan, other_income_last_year=np.nan, labor_cost_last_year=np.nan,
                 total_profit=np.nan, patmi_self=np.nan, patmi_BII=np.nan,
                 revenue=np.nan, cost=np.nan, invest_income=np.nan, other_income=np.nan, labor_cost=np.nan,
                 avg_employee_last_year=np.nan, avg_employee=np.nan, key_score=np.nan,
                 eff_index_1_weight=np.nan, eff_index_2_weight=np.nan,
                 eff_index_3_weight=np.nan, eff_index_4_weight=np.nan,
                 financial_index_name="", **kwargs):
        super().__init__(var_name, name, package_last_year, defer_last_year, distributable_last_year,
                         total_profit_last_year, patmi_self_last_year, patmi_BII_last_year,
                         revenue_last_year, cost_last_year, invest_income_last_year, other_income_last_year,
                         labor_cost_last_year,
                         total_profit, patmi_self, patmi_BII, revenue, cost, invest_income, other_income, labor_cost,
                         avg_employee_last_year, avg_employee, key_score,
                         eff_index_1_weight, eff_index_2_weight, eff_index_3_weight, eff_index_4_weight,
                         financial_index_name)

        self.subcategory = "Gov"

    def rate_1_cal(self):
        self.rate_1 = self.key_score_converted_growth

    # 对于特殊功能板块，人均生产率指标不生效
    def rate_2_cal(self):
        self.rate_2 = self.rate_1
        self.package_2 = self.package_last_year * (1 + self.rate_2)


class SpecialMarket(Special):
    def __init__(self, var_name, name, package_last_year=np.nan,
                 defer_last_year=np.nan, distributable_last_year=np.nan,
                 total_profit_last_year=np.nan, patmi_self_last_year=np.nan, patmi_BII_last_year=np.nan,
                 revenue_last_year=np.nan, cost_last_year=np.nan,
                 invest_income_last_year=np.nan, other_income_last_year=np.nan, labor_cost_last_year=np.nan,
                 total_profit=np.nan, patmi_self=np.nan, patmi_BII=np.nan,
                 revenue=np.nan, cost=np.nan, invest_income=np.nan, other_income=np.nan, labor_cost=np.nan,
                 avg_employee_last_year=np.nan, avg_employee=np.nan, key_score=np.nan,
                 eff_index_1_weight=np.nan, eff_index_2_weight=np.nan,
                 eff_index_3_weight=np.nan, eff_index_4_weight=np.nan,
                 financial_index_name="", **kwargs):
        super().__init__(var_name, name, package_last_year, defer_last_year, distributable_last_year,
                         total_profit_last_year, patmi_self_last_year, patmi_BII_last_year,
                         revenue_last_year, cost_last_year, invest_income_last_year, other_income_last_year,
                         labor_cost_last_year,
                         total_profit, patmi_self, patmi_BII, revenue, cost, invest_income, other_income, labor_cost,
                         avg_employee_last_year, avg_employee, key_score,
                         eff_index_1_weight, eff_index_2_weight, eff_index_3_weight, eff_index_4_weight,
                         financial_index_name)

        self.subcategory = "Market"
        if self.financial_index_name == "total_profit":
            self.financial_index_growth = self.total_profit_growth
        elif self.financial_index_name == "patmi_self":
            self.financial_index_growth = self.patmi_self_growth
        elif self.financial_index_name == "patmi_BII":
            self.financial_index_growth = self.patmi_BII_growth
        elif self.financial_index_name == "revenue":
            self.financial_index_growth = self.revenue_growth
        else:
            raise ValueError('%s: wrong financial index' % self.name)
        self.financial_index_limited = np.nan

    """公司人力资源部每年根据市国资委核定我公司特殊功能类板块整体工资总额增幅情况确定基准增幅。
    各经营单位归母净利润每增长（下降）5%，工资总额增幅增加（减少）0.5%，增加（减少）最多不超过1.5%；
    年底经营业绩考核得分在100分基准上每增加（扣减）1分，工资总额增幅增加（减少）0.15%。"""
    def rate_1_cal(self):
        if 0.2 * self.financial_index_growth < FINANCIAL_INDEX_LIMITS[0]:
            self.financial_index_limited = -1
            self.rate_1 = 0.5 * self.key_score_converted_growth + 0.5 * (FINANCIAL_INDEX_LIMITS[0] + GZW_BASE_RATE)
        elif 0.2 * self.financial_index_growth > FINANCIAL_INDEX_LIMITS[1]:
            self.financial_index_limited = 1
            self.rate_1 = 0.5 * self.key_score_converted_growth + 0.5 * (FINANCIAL_INDEX_LIMITS[1] + GZW_BASE_RATE)
        else:
            self.financial_index_limited = 0
            self.rate_1 = 0.5 * self.key_score_converted_growth + 0.5 * (0.2 * self.financial_index_growth + GZW_BASE_RATE)

    # 对于特殊功能板块，人均生产率指标不生效
    def rate_2_cal(self):
        self.rate_2 = self.rate_1
        self.package_2 = self.package_last_year * (1 + self.rate_2)
