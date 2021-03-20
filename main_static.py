#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# import math
# import sys

import numpy as np
import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'

"""Unit: 万元，人"""

"""const"""
GZW_BASE_RATE = 0.03  # 国资委公布的工资总额增幅基准线
GZW_AVG_RATE = 0.2 / 3  # 上年度市管企业在岗职工平均工资增幅
GZW_RATE_CAP = 3 * GZW_AVG_RATE  # 超过3倍部分计入递延
AVG_TOWN_WAGE = 9.0501  # 全国城镇单位就业人员平均工资（2019）
LOAD_INDEX_LIMITS_MULTIPLIER = pd.Series([-2, 2])  # 工作量指标区间乘数
LOAD_INDEX_LIMITS = LOAD_INDEX_LIMITS_MULTIPLIER * GZW_BASE_RATE
FINANCIAL_INDEX_LIMITS_MULTIPLIER = pd.Series([-3, 3])  # 经济效益指标区间乘数
FINANCIAL_INDEX_LIMITS = FINANCIAL_INDEX_LIMITS_MULTIPLIER * GZW_BASE_RATE
TOLERANCE = 1E-8  # 比较时使用，去除计算误差

"""var"""
GZW_score_converted_growth = 0.03  # 国资委考核京投重大任务完成率转换的增幅

"""function"""


# 重点工作计划如何折算为增幅指标
def key_score_convert(key_score):
    """线性折算"""
    key_score_converted_growth = (key_score - 80) / 20 * GZW_BASE_RATE
    return key_score_converted_growth


# 创建板块批复对象
def create_approved_obj(section_units_df):
    if section_units_df.category[0] == "Compete":
        """竞争板块总额中不进行关联交易剔除"""
        approved_obj = Compete(var_name="compete_approved", name="竞争性板块国资委批复",
                               package_last_year=section_units_df.package_last_year.sum(),
                               total_profit_last_year=section_units_df.total_profit_last_year.sum(),
                               patmi_last_year=section_units_df.patmi_last_year.sum(),
                               revenue_last_year=section_units_df.revenue_last_year.sum(),
                               cost_last_year=section_units_df.cost_last_year.sum(),
                               invest_income_last_year=section_units_df.invest_income_last_year.sum(),
                               other_income_last_year=section_units_df.other_income_last_year.sum(),
                               total_profit=section_units_df.total_profit.sum(),
                               patmi=section_units_df.patmi.sum(),
                               revenue=section_units_df.revenue.sum(),
                               cost=section_units_df.cost.sum(),
                               invest_income=section_units_df.invest_income.sum(),
                               other_income=section_units_df.other_income.sum(),
                               avg_employee_last_year=section_units_df.avg_employee_last_year.sum(),
                               avg_employee=section_units_df.avg_employee.sum(),
                               eff_index_1_name="人均利润", eff_index_2_name="人均营收",
                               eff_index_1_weight=0.5, eff_index_2_weight=0.5)
        # 由于没有写人工成本投入产出率联动指标的逻辑，所以如果国资委批复不触发70%条款，就得修改程序
    elif section_units_df.category[0] == "Public":
        """公共服务类板块总额中不进行关联交易剔除"""
        approved_obj = Public(var_name="public_approved", name="公共服务性板块国资委批复",
                              package_last_year=section_units_df.package_last_year.sum(),
                              total_profit_last_year=section_units_df.total_profit_last_year.sum(),
                              patmi_last_year=section_units_df.patmi_last_year.sum(),
                              revenue_last_year=section_units_df.revenue_last_year.sum(),
                              cost_last_year=section_units_df.cost_last_year.sum(),
                              invest_income_last_year=section_units_df.invest_income_last_year.sum(),
                              other_income_last_year=section_units_df.other_income_last_year.sum(),
                              total_profit=section_units_df.total_profit.sum(),
                              patmi=section_units_df.patmi.sum(),
                              revenue=section_units_df.revenue.sum(),
                              cost=section_units_df.cost.sum(),
                              invest_income=section_units_df.invest_income.sum(),
                              other_income=section_units_df.other_income.sum(),
                              avg_employee_last_year=section_units_df.avg_employee_last_year.sum(),
                              avg_employee=section_units_df.avg_employee.sum(),
                              eff_index_1_name="人均利润", eff_index_2_name="人均营收",
                              eff_index_1_weight=0.5, eff_index_2_weight=0.5,  # eff_indexes未确定，如果未触及70%条款则需修改
                              quality_index_last_year=section_units_df.quality_index_last_year.sum(),
                              cost_index_last_year=section_units_df.cost_index_last_year.sum(),
                              operate_index_last_year=section_units_df.operate_index_last_year.sum(),
                              quality_index=section_units_df.quality_index.sum(),
                              cost_index=section_units_df.cost_index.sum(),
                              operate_index=section_units_df.operate_index.sum())
    elif section_units_df.category[0] == "Special":
        """【特殊功能板块进行关联交易剔除！！！】"""
        approved_obj = Special(var_name="special_approved", name="特殊功能性板块国资委批复",
                               package_last_year=section_units_df.package_last_year.sum(),
                               total_profit_last_year=(section_units_df.total_profit_last_year.sum() +
                                                       section_units_df.total_profit_last_year_elimination.sum()),
                               patmi_last_year=(section_units_df.patmi_last_year.sum() +
                                                section_units_df.patmi_last_year_elimination.sum()),
                               revenue_last_year=(section_units_df.revenue_last_year.sum() +
                                                  section_units_df.revenue_last_year_elimination.sum()),
                               cost_last_year=(section_units_df.cost_last_year.sum() +
                                               section_units_df.cost_last_year_elimination.sum()),
                               invest_income_last_year=section_units_df.invest_income_last_year.sum(),
                               other_income_last_year=section_units_df.other_income_last_year.sum(),
                               total_profit=(section_units_df.total_profit.sum() +
                                             section_units_df.total_profit_elimination.sum()),
                               patmi=(section_units_df.patmi.sum() +
                                      section_units_df.patmi_elimination.sum()),
                               revenue=(section_units_df.revenue.sum() +
                                        section_units_df.revenue_elimination.sum()),
                               cost=(section_units_df.cost.sum() +
                                     section_units_df.cost_elimination.sum()),
                               invest_income=section_units_df.invest_income.sum(),
                               other_income=section_units_df.other_income.sum(),
                               avg_employee_last_year=section_units_df.avg_employee_last_year.sum(),
                               avg_employee=section_units_df.avg_employee.sum(),
                               eff_index_1_name="人均利润", eff_index_2_name="人均营收",
                               eff_index_1_weight=0.5, eff_index_2_weight=0.5)  # eff_indexes未确定，如果未触及70%条款则需修改
    else:
        raise ValueError("%s: category error" % section_units_df.category[0])
    approved_obj.subcategory = "approved"
    return approved_obj


# 平账微调
def tune(section_units_df, section_total_package_3, approved_package, approved_defer):
    df = section_units_df
    tune_1 = (approved_package + approved_defer) / section_total_package_3
    for j in df.index:
        # 版块总包限制在批复总包以内
        df.loc[j, "total_package_final"] = df.loc[j, "total_package_3"] * tune_1 if tune_1 < 1 else \
            df.loc[j, "total_package_3"]
        # 对竞争性板块执行扣除
        df.loc[j, "deduct_final"] = (df.loc[j, "total_package_final"] - df.loc[j, "package_last_year"]) * 0.4 if \
            (df.loc[j, "total_package_final"] - df.loc[j, "package_last_year"]) > 0 and df.category[
                0] == "Compete" else 0.0
        # 计算工资总额，将竞争性板块限制在去年总额*(1+GZW_RATE_CAP)以内
        df.loc[j, "package_final"] = df.loc[j, "package_last_year"] * (1 + GZW_RATE_CAP) if \
            df.loc[j, "total_package_final"] - df.loc[j, "deduct_final"] > \
            df.loc[j, "package_last_year"] * (1 + GZW_RATE_CAP) and df.category[0] == "Compete" else \
            df.loc[j, "total_package_final"] - df.loc[j, "deduct_final"]
        # 计算递延=总包-总额-扣减
        df.loc[j, "defer_final"] = df.loc[j, "total_package_final"] - df.loc[j, "package_final"] - df.loc[
            j, "deduct_final"]
        # 计算总包的微调系数
        df.loc[j, "tune_total_package_coeff"] = df.loc[j, "total_package_final"] / df.loc[j, "total_package_3"]
    # 检查错误
    if df.total_package_final.sum() > approved_package + approved_defer + TOLERANCE or \
            df.package_final.sum() > approved_package + TOLERANCE:
        print(df)
        raise ValueError('%s call tune(): 微调平账时出错！' % section_units_df.name[0])
    return df


# 创建板块合计对象
def create_section_obj(section_units_df):
    if section_units_df.category[0] == "Compete":
        section_obj = Compete(var_name="compete_section", name="竞争性板块合计",
                              package_last_year=section_units_df.package_last_year.sum(),
                              total_profit_last_year=section_units_df.total_profit_last_year.sum(),
                              patmi_last_year=section_units_df.patmi_last_year.sum(),
                              revenue_last_year=section_units_df.revenue_last_year.sum(),
                              cost_last_year=section_units_df.cost_last_year.sum(),
                              invest_income_last_year=section_units_df.invest_income_last_year.sum(),
                              other_income_last_year=section_units_df.other_income_last_year.sum(),
                              total_profit=section_units_df.total_profit.sum(),
                              patmi=section_units_df.patmi.sum(),
                              revenue=section_units_df.revenue.sum(),
                              cost=section_units_df.cost.sum(),
                              invest_income=section_units_df.invest_income.sum(),
                              other_income=section_units_df.other_income.sum(),
                              avg_employee_last_year=section_units_df.avg_employee_last_year.sum(),
                              avg_employee=section_units_df.avg_employee.sum(),
                              eff_index_1_name="人均利润", eff_index_2_name="人均营收",
                              eff_index_1_weight=0.5, eff_index_2_weight=0.5)
    elif section_units_df.category[0] == "Public":
        section_obj = Public(var_name="public_section", name="公共服务性板块合计",
                             package_last_year=section_units_df.package_last_year.sum(),
                             total_profit_last_year=section_units_df.total_profit_last_year.sum(),
                             patmi_last_year=section_units_df.patmi_last_year.sum(),
                             revenue_last_year=section_units_df.revenue_last_year.sum(),
                             cost_last_year=section_units_df.cost_last_year.sum(),
                             invest_income_last_year=section_units_df.invest_income_last_year.sum(),
                             other_income_last_year=section_units_df.other_income_last_year.sum(),
                             total_profit=section_units_df.total_profit.sum(),
                             patmi=section_units_df.patmi.sum(),
                             revenue=section_units_df.revenue.sum(),
                             cost=section_units_df.cost.sum(),
                             invest_income=section_units_df.invest_income.sum(),
                             other_income=section_units_df.other_income.sum(),
                             avg_employee_last_year=section_units_df.avg_employee_last_year.sum(),
                             avg_employee=section_units_df.avg_employee.sum(),
                             eff_index_1_name="人均利润", eff_index_2_name="人均营收",
                             eff_index_1_weight=0.5, eff_index_2_weight=0.5)
    elif section_units_df.category[0] == "Special":
        section_obj = Special(var_name="special_section", name="特殊功能性板块合计",
                              package_last_year=section_units_df.package_last_year.sum(),
                              total_profit_last_year=(section_units_df.total_profit_last_year.sum() +
                                                      section_units_df.total_profit_last_year_elimination.sum()),
                              patmi_last_year=(section_units_df.patmi_last_year.sum() +
                                               section_units_df.patmi_last_year_elimination.sum()),
                              revenue_last_year=(section_units_df.revenue_last_year.sum() +
                                                 section_units_df.revenue_last_year_elimination.sum()),
                              cost_last_year=(section_units_df.cost_last_year.sum() +
                                              section_units_df.cost_last_year_elimination.sum()),
                              invest_income_last_year=section_units_df.invest_income_last_year.sum(),
                              other_income_last_year=section_units_df.other_income_last_year.sum(),
                              total_profit=(section_units_df.total_profit.sum() +
                                            section_units_df.total_profit_elimination.sum()),
                              patmi=(section_units_df.patmi.sum() +
                                     section_units_df.patmi_elimination.sum()),
                              revenue=(section_units_df.revenue.sum() +
                                       section_units_df.revenue_elimination.sum()),
                              cost=(section_units_df.cost.sum() +
                                    section_units_df.cost_elimination.sum()),
                              invest_income=section_units_df.invest_income.sum(),
                              other_income=section_units_df.other_income.sum(),
                              avg_employee_last_year=section_units_df.avg_employee_last_year.sum(),
                              avg_employee=section_units_df.avg_employee.sum(),
                              eff_index_1_name="人均利润", eff_index_2_name="人均营收",
                              eff_index_1_weight=0.5, eff_index_2_weight=0.5)
    else:
        raise ValueError("%s call create_section_obj(): category error" % section_units_df.category[0])
    section_obj.subcategory = "section"
    return section_obj


# 基本计算完成后，创建section板块对象后计算版块数据
def section_cal(section_obj, section_units_df):
    [obj, df] = [section_obj, section_units_df]
    obj.total_package_3 = df.total_package_3.sum()
    obj.total_package_final = df.total_package_final.sum()
    obj.package_2 = df.package_2.sum()
    obj.package_3 = df.package_3.sum()
    obj.package_final = df.package_final.sum()
    obj.defer_3 = df.defer_3.sum()
    obj.defer_final = df.defer_final.sum()
    obj.deduct_3 = df.deduct_3.sum()
    obj.deduct_final = df.deduct_final.sum()
    obj.defer_rate_3 = obj.defer_3 / obj.package_last_year
    obj.deduct_rate_3 = obj.deduct_3 / obj.package_last_year
    obj.rate_2 = obj.package_2 / obj.package_last_year - 1
    obj.rate_3 = obj.package_3 / obj.package_last_year - 1
    obj.avg_wage_last_year = (df.avg_wage_last_year * df.avg_employee).sum() / obj.avg_employee
    obj.tune_total_package_coeff = obj.total_package_final / obj.total_package_3
    return 0


# 将板块对象section合并入对应板块列表
def section_concat(section_units_df, obj):
    df = pd.concat([section_units_df, pd.DataFrame(obj.__dict__, index=[obj.var_name])])
    return df


# 最后计算
def rate_final_cal(df):
    df.rate_final = df.package_final / df.package_last_year - 1
    df.defer_rate_final = df.defer_final / df.package_last_year
    df.deduct_rate_final = df.deduct_final / df.package_last_year
    df.avg_wage_final = df.package_final / df.avg_employee
    return df


"""class"""


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
        self.key_score_converted_growth = key_score_convert(self.key_score)
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
        if self.category == "Public":
            avg_town_wage_limit = 3
        elif self.category == "Compete" or self.category == "Special":
            avg_town_wage_limit = 2.5
        else:
            raise ValueError('%s call rate_2_cal(): category error' % self.var_name)
        self.avg_wage_last_year = self.package_last_year / self.avg_employee_last_year
        self.rate_2 = self.rate_1
        if self.rate_1 >= 0:
            if self.eff_growth < 0 or self.avg_wage_last_year > AVG_TOWN_WAGE * avg_town_wage_limit:
                self.rate_2 = 0.7 * self.rate_1
            elif self.subcategory == "approved":
                print("Warning: %s效益提升，去年平均工资<%s*AVG_TOWN_WAGE且劳动生产率指标提升，人工成本投入产出率指标(未计算)可能生效" %
                      (self.var_name, avg_town_wage_limit))
        elif self.rate_1 < 0:
            if self.eff_growth > 0 or self.avg_wage_last_year <= AVG_TOWN_WAGE:
                self.rate_2 = 0.4 * self.rate_1
            elif self.subcategory == "approved":
                print("Warning: %s效益下降，去年平均工资>AVG_TOWN_WAGE且劳动生产率指标下降，人工成本投入产出率指标(未计算)可能生效" %
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
            raise Warning("%s 有递延" % self.name)

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


"""main"""
if __name__ == '__main__':
    inputs = pd.read_csv('inputs.csv', converters={'subcategory': str})
    # 构造各单位实例
    for i, data in inputs.iterrows():
        class_name = data['category'] + data['subcategory']
        exec(data['var_name'] + "=" + class_name + """(var_name=data['var_name'], name=data['name'], \
             package_last_year=data['package_last_year'], \
             total_profit_last_year=data['total_profit_last_year'], \
             total_profit_last_year_elimination=data['total_profit_last_year_elimination'], \
             patmi_last_year=data['patmi_last_year'], \
             patmi_last_year_elimination=data['patmi_last_year_elimination'], \
             revenue_last_year=data['revenue_last_year'], \
             revenue_last_year_elimination=data['revenue_last_year_elimination'], \
             cost_last_year=data['cost_last_year'], \
             cost_last_year_elimination=data['cost_last_year_elimination'], \
             invest_income_last_year=data['invest_income_last_year'], \
             other_income_last_year=data['other_income_last_year'], \
             total_profit=data['total_profit'], \
             total_profit_elimination=data['total_profit_elimination'], \
             patmi=data['patmi'], \
             patmi_elimination=data['patmi_elimination'], \
             revenue=data['revenue'], \
             revenue_elimination=data['revenue_elimination'], \
             cost=data['cost'], \
             cost_elimination=data['cost_elimination'], \
             invest_income=data['invest_income'], \
             other_income=data['other_income'], \
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

    # 创建单位实例的列表
    all_var_name_string = ','.join(list(inputs['var_name']))
    all_units = eval('[' + all_var_name_string + ']')

    # 分别计算rate_1到rate_3，并将所有实例的结果保存为units_df，剩余部分不再在单位实例中计算，而是在df中计算
    units_df = pd.DataFrame()
    for p in all_units:
        p.rate_1_cal()
        p.rate_2_cal()
        p.rate_3_cal()
        units_df = pd.concat([units_df, pd.DataFrame(p.__dict__, index=[p.var_name])])

    """合并板块后进行最终计算"""
    # init
    section_names = inputs.category.unique()
    section_df_list = []
    approved_obj_list = []
    section_obj_list = []
    section_total_package_3_list = []
    results_df = pd.DataFrame()

    # 计算板块国资委批复额度
    for i in range(len(section_names)):
        # 摘出各板块单位的表格
        section_df_list.append(units_df[units_df["category"] == section_names[i]])

        # 创建版块批复对象
        approved_obj_list.append(create_approved_obj(section_df_list[i]))

        # 计算各板块国资委批复额度
        approved_obj_list[i].rate_1_cal()
        approved_obj_list[i].rate_2_cal()
        approved_obj_list[i].rate_3_cal()
        approved_obj_list[i].copy_3_as_final()

        # 计算版块平账微调前的总包
        section_total_package_3_list.append(section_df_list[i].total_package_3.sum())

        # 微调平账
        section_df_list[i] = tune(section_df_list[i], section_total_package_3_list[i],
                                  approved_obj_list[i].package_final, approved_obj_list[i].defer_final)
        # 创建版块合计对象
        section_obj_list.append(create_section_obj(section_df_list[i]))

        # 计算版块合计数据
        section_cal(section_obj_list[i], section_df_list[i])

        # 将版块数据和版块批复数据合并入版块列表
        section_df_list[i] = section_concat(section_df_list[i], section_obj_list[i])
        section_df_list[i] = section_concat(section_df_list[i], approved_obj_list[i])

        # 将板块列表合并为最终输出表
        results_df = pd.concat([results_df, section_df_list[i]])

    # 最后几个数值的计算
    results_df = rate_final_cal(results_df)

    """输出csv"""
    results_df.to_csv("results.csv", encoding="UTF-8", float_format='%.5f')
    results_df.to_excel("results.xlsx", sheet_name="all", encoding="UTF-8", engine='xlsxwriter', float_format='%.5f')
