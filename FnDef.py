from ConstVar import GZW_BASE_RATE
from ConstVar import GZW_RATE_CAP
from ConstVar import TOLERANCE
from scipy.stats import truncnorm
from tqdm import tqdm
import pandas as pd
import numpy as np

"""function"""


# 重点工作计划如何折算为增幅指标
def key_score_convert(key_score, base_rate=GZW_BASE_RATE):
    """线性折算"""
    """110分：6%，110分：3%"""
    key_score_converted_growth = (key_score - 90) / 10 * base_rate
    return key_score_converted_growth


# 根据输入的参数，生成一个随机的列表
def randomize_inputs(inputs_mean_df, inputs_sd_df, inputs_lower_df, inputs_upper_df):
    def f(mean, sd, lower, upper):
        if type(mean) == int or type(mean) == float:
            if not np.isnan(sd) and sd > 0:
                mean = float(mean)
                a = np.nanmax([(lower - mean) / sd, -np.inf])
                b = np.nanmin([(upper - mean) / sd, np.inf])
                try:
                    return truncnorm.rvs(a=a, b=b, loc=mean, scale=sd, size=1)[0]
                except Exception as inst:
                    print(type(inst))  # the exception instance
                    print(inst)  # __str__ allows args to be printed directly,
                    print("mean=%.2f, sd=%.2f, lower=%.2f, upper=%.2f" % (mean, sd, lower, upper))
                    quit("Error in running truncnorm()! Please check your inputs files!")
            else:
                return mean
        else:
            return mean
    vec_f = np.vectorize(f)
    inputs_randomized = pd.DataFrame(vec_f(inputs_mean_df, inputs_sd_df, inputs_lower_df, inputs_upper_df))
    inputs_randomized.columns = inputs_mean_df.columns
    inputs_randomized = inputs_randomized.astype(inputs_mean_df.dtypes.to_dict())
    return inputs_randomized


# 创建板块批复对象
def create_approved_obj(section_units_df):
    from ClassDef import Compete
    from ClassDef import Public
    from ClassDef import Special
    if section_units_df.category[0] == "Compete":
        """竞争板块总额中不进行关联交易剔除"""
        approved_obj = Compete(var_name="compete_approved", name="竞争性板块国资委批复",
                               package_last_year=section_units_df.package_last_year.sum(),
                               defer_last_year=section_units_df.defer_last_year.sum(),
                               distributable_last_year=section_units_df.distributable_last_year.sum(),
                               total_profit_last_year=section_units_df.total_profit_last_year.sum(),
                               patmi_self_last_year=section_units_df.patmi_self_last_year.sum(),
                               patmi_BII_last_year=section_units_df.patmi_BII_last_year.sum(),
                               revenue_last_year=section_units_df.revenue_last_year.sum(),
                               cost_last_year=section_units_df.cost_last_year.sum(),
                               invest_income_last_year=section_units_df.invest_income_last_year.sum(),
                               other_income_last_year=section_units_df.other_income_last_year.sum(),
                               total_profit=section_units_df.total_profit.sum(),
                               patmi_self=section_units_df.patmi_self.sum(),
                               patmi_BII=section_units_df.patmi_BII.sum(),
                               revenue=section_units_df.revenue.sum(),
                               cost=section_units_df.cost.sum(),
                               invest_income=section_units_df.invest_income.sum(),
                               other_income=section_units_df.other_income.sum(),
                               avg_employee_last_year=section_units_df.avg_employee_last_year.sum(),
                               avg_employee=section_units_df.avg_employee.sum(),
                               eff_index_1_weight=section_units_df.eff_index_1_weight[0],
                               eff_index_2_weight=section_units_df.eff_index_2_weight[0],
                               eff_index_3_weight=section_units_df.eff_index_3_weight[0],
                               eff_index_4_weight=section_units_df.eff_index_4_weight[0])
    elif section_units_df.category[0] == "Public":
        """公共服务类板块总额中不进行关联交易剔除"""
        approved_obj = Public(var_name="public_approved", name="公共服务性板块国资委批复",
                              package_last_year=section_units_df.package_last_year.sum(),
                              defer_last_year=section_units_df.defer_last_year.sum(),
                              distributable_last_year=section_units_df.distributable_last_year.sum(),
                              total_profit_last_year=section_units_df.total_profit_last_year.sum(),
                              patmi_self_last_year=section_units_df.patmi_self_last_year.sum(),
                              patmi_BII_last_year=section_units_df.patmi_BII_last_year.sum(),
                              revenue_last_year=section_units_df.revenue_last_year.sum(),
                              cost_last_year=section_units_df.cost_last_year.sum(),
                              invest_income_last_year=section_units_df.invest_income_last_year.sum(),
                              other_income_last_year=section_units_df.other_income_last_year.sum(),
                              total_profit=section_units_df.total_profit.sum(),
                              patmi_self=section_units_df.patmi_self.sum(),
                              patmi_BII=section_units_df.patmi_BII.sum(),
                              revenue=section_units_df.revenue.sum(),
                              cost=section_units_df.cost.sum(),
                              invest_income=section_units_df.invest_income.sum(),
                              other_income=section_units_df.other_income.sum(),
                              avg_employee_last_year=section_units_df.avg_employee_last_year.sum(),
                              avg_employee=section_units_df.avg_employee.sum(),
                              eff_index_1_weight=section_units_df.eff_index_1_weight[0],
                              eff_index_2_weight=section_units_df.eff_index_2_weight[0],
                              eff_index_3_weight=section_units_df.eff_index_3_weight[0],
                              eff_index_4_weight=section_units_df.eff_index_4_weight[0],
                              quality_index_last_year=section_units_df.quality_index_last_year.sum(),
                              cost_index_last_year=section_units_df.cost_index_last_year.sum(),
                              operate_index_last_year=section_units_df.operate_index_last_year.sum(),
                              quality_index=section_units_df.quality_index.sum(),
                              cost_index=section_units_df.cost_index.sum(),
                              operate_index=section_units_df.operate_index.sum())
    elif section_units_df.category[0] == "Special":

        approved_obj = Special(var_name="special_approved", name="特殊功能性板块国资委批复",
                               package_last_year=section_units_df.package_last_year.sum(),
                               defer_last_year=section_units_df.defer_last_year.sum(),
                               distributable_last_year=section_units_df.distributable_last_year.sum(),
                               total_profit_last_year=section_units_df.total_profit_last_year.sum(),
                               patmi_self_last_year=section_units_df.patmi_self_last_year.sum(),
                               patmi_BII_last_year=section_units_df.patmi_BII_last_year.sum(),
                               revenue_last_year=section_units_df.revenue_last_year.sum(),
                               cost_last_year=section_units_df.cost_last_year.sum(),
                               invest_income_last_year=section_units_df.invest_income_last_year.sum(),
                               other_income_last_year=section_units_df.other_income_last_year.sum(),
                               total_profit=section_units_df.total_profit.sum(),
                               patmi_self=section_units_df.patmi_self.sum(),
                               patmi_BII=section_units_df.patmi_BII.sum(),
                               revenue=section_units_df.revenue.sum(),
                               cost=section_units_df.cost.sum(),
                               invest_income=section_units_df.invest_income.sum(),
                               other_income=section_units_df.other_income.sum(),
                               avg_employee_last_year=section_units_df.avg_employee_last_year.sum(),
                               avg_employee=section_units_df.avg_employee.sum(),
                               eff_index_1_weight=section_units_df.eff_index_1_weight[0],
                               eff_index_2_weight=section_units_df.eff_index_2_weight[0],
                               eff_index_3_weight=section_units_df.eff_index_3_weight[0],
                               eff_index_4_weight=section_units_df.eff_index_4_weight[0])
    else:
        raise ValueError("%s: category error" % section_units_df.category[0])
    approved_obj.subcategory = "approved"
    return approved_obj


# 平账微调
def tune(section_units_df, approved_package, approved_defer):
    df = section_units_df
    section_total_package_3 = df.total_package_3.sum()
    section_distributable_last_year = df.distributable_last_year.sum()
    if (approved_package + approved_defer + section_distributable_last_year) < section_total_package_3:
        tune_1 = (approved_package + approved_defer + section_distributable_last_year) / section_total_package_3
    else:
        tune_1 = 1

    for j in df.index:
        # 分配上年度可分配工资总额，将版块总包限制在批复总包+可支配额度以内
        df.loc[j, "total_package_final"] = df.loc[j, "total_package_3"] * tune_1
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
        # 计算实际可发工资总额=final总额+本单位上年度递延
        df.loc[j, "package_real"] = np.nansum([df.loc[j, "package_final"], df.loc[j, "defer_last_year"]])
        # 计算总包的微调系数
        df.loc[j, "tune_total_package_coeff"] = tune_1
    # 检查错误
    if df.total_package_final.sum() > approved_package + approved_defer + section_distributable_last_year + TOLERANCE:
        tqdm.write(df)
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
                              defer_last_year=section_units_df.defer_last_year.sum(),
                              distributable_last_year=section_units_df.distributable_last_year.sum(),
                              total_profit_last_year=section_units_df.total_profit_last_year.sum(),
                              patmi_self_last_year=section_units_df.patmi_self_last_year.sum(),
                              patmi_BII_last_year=section_units_df.patmi_BII_last_year.sum(),
                              revenue_last_year=section_units_df.revenue_last_year.sum(),
                              cost_last_year=section_units_df.cost_last_year.sum(),
                              invest_income_last_year=section_units_df.invest_income_last_year.sum(),
                              other_income_last_year=section_units_df.other_income_last_year.sum(),
                              total_profit=section_units_df.total_profit.sum(),
                              patmi_self=section_units_df.patmi_self.sum(),
                              patmi_BII=section_units_df.patmi_BII.sum(),
                              revenue=section_units_df.revenue.sum(),
                              cost=section_units_df.cost.sum(),
                              invest_income=section_units_df.invest_income.sum(),
                              other_income=section_units_df.other_income.sum(),
                              avg_employee_last_year=section_units_df.avg_employee_last_year.sum(),
                              avg_employee=section_units_df.avg_employee.sum(),
                              eff_index_1_weight=section_units_df.eff_index_1_weight[0],
                              eff_index_2_weight=section_units_df.eff_index_2_weight[0],
                              eff_index_3_weight=section_units_df.eff_index_3_weight[0],
                              eff_index_4_weight=section_units_df.eff_index_4_weight[0])
    elif section_units_df.category[0] == "Public":
        section_obj = Public(var_name="public_section", name="公共服务性板块合计",
                             package_last_year=section_units_df.package_last_year.sum(),
                             defer_last_year=section_units_df.defer_last_year.sum(),
                             distributable_last_year=section_units_df.distributable_last_year.sum(),
                             total_profit_last_year=section_units_df.total_profit_last_year.sum(),
                             patmi_self_last_year=section_units_df.patmi_self_last_year.sum(),
                             patmi_BII_last_year=section_units_df.patmi_BII_last_year.sum(),
                             revenue_last_year=section_units_df.revenue_last_year.sum(),
                             cost_last_year=section_units_df.cost_last_year.sum(),
                             invest_income_last_year=section_units_df.invest_income_last_year.sum(),
                             other_income_last_year=section_units_df.other_income_last_year.sum(),
                             total_profit=section_units_df.total_profit.sum(),
                             patmi_self=section_units_df.patmi_self.sum(),
                             patmi_BII=section_units_df.patmi_BII.sum(),
                             revenue=section_units_df.revenue.sum(),
                             cost=section_units_df.cost.sum(),
                             invest_income=section_units_df.invest_income.sum(),
                             other_income=section_units_df.other_income.sum(),
                             avg_employee_last_year=section_units_df.avg_employee_last_year.sum(),
                             avg_employee=section_units_df.avg_employee.sum(),
                             eff_index_1_weight=section_units_df.eff_index_1_weight[0],
                             eff_index_2_weight=section_units_df.eff_index_2_weight[0],
                             eff_index_3_weight=section_units_df.eff_index_3_weight[0],
                             eff_index_4_weight=section_units_df.eff_index_4_weight[0])
    elif section_units_df.category[0] == "Special":
        section_obj = Special(var_name="special_section", name="特殊功能性板块合计",
                              package_last_year=section_units_df.package_last_year.sum(),
                              defer_last_year=section_units_df.defer_last_year.sum(),
                              distributable_last_year=section_units_df.distributable_last_year.sum(),
                              total_profit_last_year=section_units_df.total_profit_last_year.sum(),
                              patmi_self_last_year=section_units_df.patmi_self_last_year.sum(),
                              patmi_BII_last_year=section_units_df.patmi_self_last_year.sum(),
                              revenue_last_year=section_units_df.revenue_last_year.sum(),
                              cost_last_year=section_units_df.cost_last_year.sum(),
                              invest_income_last_year=section_units_df.invest_income_last_year.sum(),
                              other_income_last_year=section_units_df.other_income_last_year.sum(),
                              total_profit=section_units_df.total_profit.sum(),
                              patmi_self=section_units_df.patmi_self.sum(),
                              patmi_BII=section_units_df.patmi_BII.sum(),
                              revenue=section_units_df.revenue.sum(),
                              cost=section_units_df.cost.sum(),
                              invest_income=section_units_df.invest_income.sum(),
                              other_income=section_units_df.other_income.sum(),
                              avg_employee_last_year=section_units_df.avg_employee_last_year.sum(),
                              avg_employee=section_units_df.avg_employee.sum(),
                              eff_index_1_weight=section_units_df.eff_index_1_weight[0],
                              eff_index_2_weight=section_units_df.eff_index_2_weight[0],
                              eff_index_3_weight=section_units_df.eff_index_3_weight[0],
                              eff_index_4_weight=section_units_df.eff_index_4_weight[0])
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
    obj.package_real = df.package_real.sum()
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
    df.rate_real = df.package_real / df.package_last_year - 1
    df.defer_rate_final = df.defer_final / df.package_last_year
    df.deduct_rate_final = df.deduct_final / df.package_last_year
    df.avg_wage_final = df.package_final / df.avg_employee
    df.avg_wage_real = df.package_real / df.avg_employee
    return df
