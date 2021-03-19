#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# import math
# import sys
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

"""Unit: 元，人"""

"""const"""
GZW_BASE_RATE = 0.03  # 国资委公布的工资总额增幅基准线
GZW_AVG_RATE = 0.2/3  # 上年度市管企业在岗职工平均工资增幅
GZW_RATE_CAP = 3 * GZW_AVG_RATE  # 超过3倍部分计入递延
AVG_TOWN_WAGE = 90000  # 全国城镇单位就业人员平均工资（上年度？）
LOAD_INDEX_LIMITS_MULTIPLIER = pd.Series([-2, 2])  # 工作量指标区间乘数
LOAD_INDEX_LIMITS = LOAD_INDEX_LIMITS_MULTIPLIER * GZW_BASE_RATE
FINANCIAL_INDEX_LIMITS_MULTIPLIER = pd.Series([-3, 3])  # 经济效益指标区间乘数
FINANCIAL_INDEX_LIMITS = FINANCIAL_INDEX_LIMITS_MULTIPLIER * GZW_BASE_RATE
CATEGORIES = ["Compete", "Public", "Special"]
PACKAGES_LAST_YEAR = {CATEGORIES[0]: 999.9, CATEGORIES[1]: 888, CATEGORIES[2]: 777}  # ：上年度国资委批复总额

"""var"""

"""function"""


def key_score_convert(key_score):
    """线性折算"""
    key_score_converted_growth = (key_score - 80) / 20 * GZW_BASE_RATE
    return key_score_converted_growth


"""class"""


class Unit(object):
    def __init__(self, var_name, name, package_last_year=np.nan,
                 total_profit_last_year=np.nan, patmi_last_year=np.nan, revenue_last_year=np.nan,
                 total_profit=np.nan, patmi=np.nan, revenue=np.nan,
                 avg_employee_last_year=np.nan, avg_employee=np.nan,
                 key_score=np.nan,
                 eff_index_1_name="", eff_index_2_name="", eff_index_3_name="", eff_index_4_name="",
                 eff_index_1_last_year=np.nan, eff_index_2_last_year=np.nan,
                 eff_index_3_last_year=np.nan, eff_index_4_last_year=np.nan,
                 eff_index_1=np.nan, eff_index_2=np.nan, eff_index_3=np.nan, eff_index_4=np.nan,
                 eff_index_1_weight=np.nan, eff_index_2_weight=np.nan,
                 eff_index_3_weight=np.nan, eff_index_4_weight=np.nan):
        self.var_name = var_name
        self.name = name
        self.category = "Undefined"
        self.subcategory = ""
        self.package_last_year = package_last_year
        self.package_3 = np.nan
        self.package_final = np.nan
        self.defer_3 = 0.0
        self.defer_final = 0.0
        self.deduct_3 = 0.0
        self.deduct_final = 0.0
        self.defer_rate_3 = 0.0
        self.defer_rate_final = 0.0
        self.deduct_rate_3 = 0.0
        self.deduct_rate_final = 0.0
        self.rate_1 = np.nan
        self.rate_2 = np.nan
        self.rate_3 = np.nan
        self.rate_final = np.nan
        self.avg_wage_1 = np.nan
        self.avg_wage_final = np.nan
        self.avg_employee_last_year = avg_employee_last_year
        self.avg_employee = avg_employee
        self.tune_package_coeff = np.nan  # 微调平账的调整系数:工资总额（当年可发）
        self.tune_defer_coeff = np.nan  # 微调平账的调整系数：递延
        self.tune_deduct_coeff = np.nan  # 微调平账的调整系数：竞争性板块扣减
        self.total_profit_last_year = total_profit_last_year
        self.patmi_last_year = patmi_last_year  # 归母净利润Profit After Tax and Minority Interests
        self.revenue_last_year = revenue_last_year
        self.total_profit = total_profit
        self.patmi = patmi
        self.revenue = revenue
        self.total_profit_growth = (self.total_profit - self.total_profit_last_year) / abs(self.total_profit_last_year)
        self.patmi_growth = (self.patmi - self.patmi_last_year) / abs(self.patmi_last_year)
        self.revenue_growth = (self.revenue - self.revenue_last_year) / abs(self.revenue_last_year)
        self.key_score = key_score
        self.key_score_converted_growth = key_score_convert(self.key_score)
        self.eff_index_1_name = eff_index_1_name
        self.eff_index_2_name = eff_index_2_name
        self.eff_index_3_name = eff_index_3_name
        self.eff_index_4_name = eff_index_4_name
        self.eff_index_1_last_year = self.total_profit_last_year / self.avg_employee_last_year
        self.eff_index_2_last_year = self.revenue_last_year / self.avg_employee_last_year
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

    """第二步：效率调整"""

    def rate_2_cal(self):
        if self.category == "Undefined":
            raise ValueError('undefined category')
        elif self.category == "Public":
            avg_town_wage_limit = 3
        else:
            avg_town_wage_limit = 2.5

        self.avg_wage_1 = self.package_last_year * (1 + self.rate_1) / self.avg_employee
        self.rate_2 = self.rate_1
        if self.rate_1 >= 0:
            if self.eff_growth < 0 or self.avg_wage_1 > AVG_TOWN_WAGE * avg_town_wage_limit:
                self.rate_2 = 0.7 * self.rate_1
        elif self.rate_1 < 0:
            if self.eff_growth > 0 or self.avg_wage_1 <= AVG_TOWN_WAGE:
                self.rate_2 = 0.4 * self.rate_1

    """第三步：水平调控"""
    # Compete 40% off
    def deduct_3_cal(self):
        if self.category == "Undefined":
            raise ValueError('undefined category')
        elif self.category == "Compete" and self.rate_2 > 0:
            self.deduct_rate_3 = 0.4 * self.rate_2
        else:
            self.deduct_rate_3 = 0.0
        self.deduct_3 = self.package_last_year * self.deduct_rate_3

    def rate_3_cal(self):
        if (self.rate_2 - self.deduct_rate_3) > GZW_RATE_CAP:
            self.rate_3 = GZW_RATE_CAP
        else:
            self.rate_3 = self.rate_2 - self.deduct_rate_3
        self.package_3 = self.package_last_year * (1 + self.rate_3)
        self.defer_rate_3 = self.rate_2 - self.deduct_rate_3 - self.rate_3
        self.defer_3 = self.package_last_year * self.defer_rate_3

    """第四步：如果是国资委批复，则最终批复 = 第三步计算结果"""
    def copy_3_as_final(self):
        if self.subcategory == "approved":
            pass
        else:
            raise ValueError('该对象不是国资委批复！')
        self.rate_final = self.rate_3
        self.defer_rate_final = self.defer_rate_3
        self.deduct_rate_final = self.deduct_rate_3
        self.package_final = self.package_3
        self.defer_final = self.defer_3
        self.deduct_final = self.deduct_3


class Compete(Unit):
    def __init__(self, var_name, name, package_last_year=np.nan,
                 total_profit_last_year=np.nan, patmi_last_year=np.nan, revenue_last_year=np.nan,
                 total_profit=np.nan, patmi=np.nan, revenue=np.nan,
                 avg_employee_last_year=np.nan, avg_employee=np.nan,
                 key_score=np.nan,
                 eff_index_1_name="", eff_index_2_name="", eff_index_3_name="", eff_index_4_name="",
                 eff_index_1_last_year=np.nan, eff_index_2_last_year=np.nan,
                 eff_index_3_last_year=np.nan, eff_index_4_last_year=np.nan,
                 eff_index_1=np.nan, eff_index_2=np.nan, eff_index_3=np.nan, eff_index_4=np.nan,
                 eff_index_1_weight=np.nan, eff_index_2_weight=np.nan,
                 eff_index_3_weight=np.nan, eff_index_4_weight=np.nan, **kwargs):
        super().__init__(var_name, name, package_last_year,
                         total_profit_last_year, patmi_last_year, revenue_last_year,
                         total_profit, patmi, revenue,
                         avg_employee_last_year, avg_employee,
                         key_score,
                         eff_index_1_name, eff_index_2_name, eff_index_3_name, eff_index_4_name,
                         eff_index_1_last_year, eff_index_2_last_year, eff_index_3_last_year, eff_index_4_last_year,
                         eff_index_1, eff_index_2, eff_index_3, eff_index_4,
                         eff_index_1_weight, eff_index_2_weight, eff_index_3_weight, eff_index_4_weight)

        self.category = "Compete"

    def rate_1_cal(self):
        self.rate_1 = 0.5 * self.total_profit_growth + 0.3 * self.patmi_growth + 0.2 * self.revenue_growth


class Public(Unit):
    def __init__(self, var_name, name, package_last_year=np.nan,
                 total_profit_last_year=np.nan, patmi_last_year=np.nan, revenue_last_year=np.nan,
                 total_profit=np.nan, patmi=np.nan, revenue=np.nan,
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
                         total_profit_last_year, patmi_last_year, revenue_last_year,
                         total_profit, patmi, revenue,
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
        self.cost_index_growth = (cost_index - cost_index_last_year) / abs(cost_index_last_year)
        self.operate_index_growth = (operate_index - operate_index_last_year) / abs(operate_index_last_year)

    def rate_1_cal(self):
        self.rate_1 = 0.5 * self.key_score_converted_growth + 0.25 * self.quality_index_growth + \
                      0.15 * self.cost_index_growth + 0.10 * self.operate_index_growth


class Special(Unit):
    def __init__(self, var_name, name, package_last_year=np.nan,
                 total_profit_last_year=np.nan, patmi_last_year=np.nan, revenue_last_year=np.nan,
                 total_profit=np.nan, patmi=np.nan, revenue=np.nan,
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
                         total_profit_last_year, patmi_last_year, revenue_last_year,
                         total_profit, patmi, revenue,
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


class SpecialGov(Special):
    def __init__(self, var_name, name, package_last_year=np.nan,
                 total_profit_last_year=np.nan, patmi_last_year=np.nan, revenue_last_year=np.nan,
                 total_profit=np.nan, patmi=np.nan, revenue=np.nan,
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
                         total_profit_last_year, patmi_last_year, revenue_last_year,
                         total_profit, patmi, revenue,
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
            self.load_index_growth = LOAD_INDEX_LIMITS[0]
        elif self.load_index_growth > LOAD_INDEX_LIMITS[1]:
            self.load_index_limited = 1
            self.load_index_growth = LOAD_INDEX_LIMITS[1]
        else:
            self.load_index_limited = 0

        self.rate_1 = 0.5 * self.key_score_converted_growth + 0.5 * self.load_index_growth


class SpecialMarket(Special):
    def __init__(self, var_name, name, package_last_year=np.nan,
                 total_profit_last_year=np.nan, patmi_last_year=np.nan, revenue_last_year=np.nan,
                 total_profit=np.nan, patmi=np.nan, revenue=np.nan,
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
                         total_profit_last_year, patmi_last_year, revenue_last_year,
                         total_profit, patmi, revenue,
                         avg_employee_last_year, avg_employee,
                         key_score,
                         eff_index_1_name, eff_index_2_name, eff_index_3_name, eff_index_4_name,
                         eff_index_1_last_year, eff_index_2_last_year, eff_index_3_last_year, eff_index_4_last_year,
                         eff_index_1, eff_index_2, eff_index_3, eff_index_4,
                         eff_index_1_weight, eff_index_2_weight, eff_index_3_weight, eff_index_4_weight,
                         load_index_last_year, load_index,
                         financial_index_name)

        self.subcategory = "Market"
        self.financial_index_limited = np.nan
        if self.financial_index_name == "total_profit":
            self.financial_index_growth = self.total_profit_growth
        elif self.financial_index_name == "patmi":
            self.financial_index_growth = self.patmi_growth
        elif self.financial_index_name == "revenue":
            self.financial_index_growth = self.revenue_growth
        else:
            raise ValueError('undefined financial index')

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


"""main"""
if __name__ == '__main__':
    inputs = pd.read_csv('database/inputs.csv', converters={'subcategory': str})
    # 构造各单位实例
    for i, data in inputs.iterrows():
        class_name = data['category'] + data['subcategory']
        exec(data['var_name'] + "=" + class_name + """(var_name=data['var_name'], name=data['name'], \
             package_last_year=data['package_last_year'], \
             total_profit_last_year=data['total_profit_last_year'], \
             patmi_last_year=data['patmi_last_year'], \
             revenue_last_year=data['revenue_last_year'], \
             total_profit=data['total_profit'], \
             patmi=data['patmi'], \
             revenue=data['revenue'], \
             avg_employee_last_year=data['avg_employee_last_year'], \
             avg_employee=data['avg_employee'], \
             key_score=data['key_score'], \
             eff_index_1_name=data['eff_index_1_name'], \
             eff_index_2_name=data['eff_index_2_name'], \
             eff_index_3_name=data['eff_index_3_name'], \
             eff_index_4_name=data['eff_index_4_name'], \
             eff_index_1_last_year=data['eff_index_1_last_year'], \
             eff_index_2_last_year=data['eff_index_2_last_year'], \
             eff_index_3_last_year=data['eff_index_3_last_year'], \
             eff_index_4_last_year=data['eff_index_4_last_year'], \
             eff_index_1=data['eff_index_1'], \
             eff_index_2=data['eff_index_2'], \
             eff_index_3=data['eff_index_3'], \
             eff_index_4=data['eff_index_4'], \
             eff_index_1_weight=data['eff_index_1_weight'], \
             eff_index_2_weight=data['eff_index_2_weight'], \
             eff_index_3_weight=data['eff_index_3_weight'], \
             eff_index_4_weight=data['eff_index_4_weight'], \
             quality_index_last_year=data['quality_index_last_year'], \
             cost_index_last_year=data['cost_index_last_year'], \
             operate_index_last_year=data['operate_index_last_year'], \
             quality_index=data['quality_index'], \
             cost_index=data['cost_index'], \
             operate_index=data['operate_index'], \
             load_index_last_year=data['load_index_last_year'], \
             load_index=data['load_index'], \
             financial_index_name=data['financial_index_name'])""")

    # 单位实例的列表
    all_var_name_string = ','.join(list(inputs['var_name']))
    all_units = eval('[' + all_var_name_string + ']')
    """compete_var_name_string = ','.join(list(inputs[inputs["category"] == 'Compete']['var_name']))
    compete_units = eval('[' + compete_var_name_string + ']')
    public_var_name_string = ','.join(list(inputs[inputs["category"] == 'Public']['var_name']))
    public_units = eval('[' + public_var_name_string + ']')
    special_var_name_string = ','.join(list(inputs[inputs["category"] == 'Special']['var_name']))
    special_units = eval('[' + special_var_name_string + ']')"""

    # 分别计算到rate_3, 并将所有实例的结果保存为units_df
    units_df = pd.DataFrame()
    for p in all_units:
        p.rate_1_cal()
        p.rate_2_cal()
        p.deduct_3_cal()
        p.rate_3_cal()
        units_df = pd.concat([units_df, pd.DataFrame(p.__dict__, index=[p.var_name])])

    """计算竞争类板块的整体批复情况"""
    compete_df = units_df[units_df["category"] == "Compete"]
    compete_approved = Compete(var_name="compete_approved", name="竞争性板块国资委批复",
                               package_last_year=PACKAGES_LAST_YEAR[compete_df.category[0]],
                               total_profit_last_year=compete_df.total_profit_last_year.sum(),
                               patmi_last_year=compete_df.patmi_last_year.sum(),
                               revenue_last_year=compete_df.revenue_last_year.sum(),
                               total_profit=compete_df.total_profit.sum(),
                               patmi=compete_df.patmi.sum(),
                               revenue=compete_df.revenue.sum(),
                               avg_employee_last_year=compete_df.avg_employee_last_year.sum(),
                               avg_employee=compete_df.avg_employee.sum(),
                               eff_index_1_name="人均利润", eff_index_2_name="人均营收",
                               eff_index_1_weight=0.5, eff_index_2_weight=0.5)
    # 计算板块国资委批复额度
    compete_approved.subcategory = "approved"
    compete_approved.rate_1_cal()
    compete_approved.rate_2_cal()
    compete_approved.rate_3_cal()
    compete_approved.copy_3_as_final()

    """根据批复情况，调整竞争类板块的实际批复，"""
    # calculate tune_coeff: 超出总额则调平，小于总额则多余的作为板块递延
    if compete_approved.package_3 < compete_df.package_2.sum():
        compete_df.tune_coeff = compete_approved.package_3 / compete_df.package_2.sum()
    else:
        compete_df.tune_coeff = 1.0
    compete_df.package_final = compete_df.package_2 * compete_df.tune_coeff  # 单位最终工资总额=第三步总额*调整系数
    compete_approved.package_final = compete_df.package_final.sum()  # 板块最终工资总额=sum(单位最终工资总额)
    compete_approved.defer_3 = compete_approved.package_3 - compete_approved.package_final

    # 将板块对象section合并入对应板块列表
    compete_df = pd.concat([compete_df, pd.DataFrame(compete_approved.__dict__, index=[compete_approved.var_name])])

    # 最后计算
    compete_df.rate_final = compete_df.package_final / compete_df.package_last_year
    compete_df.avg_wage_final = compete_df.package_final / compete_df.avg_employee

    for p in all_units:
        print({p.name: p.rate_3})
    pass
