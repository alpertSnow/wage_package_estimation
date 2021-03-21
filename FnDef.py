from ConstVar import GZW_BASE_RATE
from ConstVar import GZW_RATE_CAP
from ConstVar import TOLERANCE
import pandas as pd

"""function"""


# 重点工作计划如何折算为增幅指标
def key_score_convert(key_score):
    """线性折算"""
    key_score_converted_growth = (key_score - 80) / 20 * GZW_BASE_RATE
    return key_score_converted_growth


# 创建板块批复对象
def create_approved_obj(section_units_df):
    from ClassDef import Compete
    from ClassDef import Public
    from ClassDef import Special
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
    from ClassDef import Compete
    from ClassDef import Public
    from ClassDef import Special
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