#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import warnings
from tqdm import tqdm  # 进度条
from multiprocessing import Pool
from functools import partial
from ClassDef import Compete  # 竞争类板块对象
from ClassDef import Public  # 公共服务类板块对象
from ClassDef import Special  # 特殊功能类类板块对象（此处用于壳公司与抵消对象）
from ClassDef import SpecialGov  # 特殊功能类类板块对象（政府型）
from ClassDef import SpecialMarket  # 特殊功能类类板块对象（经营型）
from FnDef import randomize_inputs  # 根据输入的参数，生成一个随机的列表
from FnDef import create_approved_obj  # 创建板块批复对象
from FnDef import tune  # 平账微调
from FnDef import create_section_obj  # 创建板块合计对象
from FnDef import section_cal  # 各单位rate_1~3计算完成后，创建section板块对象后计算版块数据
from FnDef import section_concat  # 将板块对象section合并入对应板块列表
from FnDef import rate_final_cal  # 最后收尾计算
from ConstVar import SAMPLE_SIZE  # 随机采样个数
from ConstVar import THREAD_NO  # 线程数
from ConstVar import FILE_SUFFIX  #

pd.options.mode.chained_assignment = None  # default='warn'
warnings.filterwarnings('ignore', category=RuntimeWarning)

"""Unit: 万元，人"""

"""线程内部过程"""


def do(thread, df1, df2, df3, df4):
    # 开始循环
    thread_results_df = pd.DataFrame()
    progress_bar = tqdm(total=SAMPLE_SIZE)
    for k in range(SAMPLE_SIZE):
        inputs = randomize_inputs(df1, df2, df3, df4)
        # 将"减：京投大合并"的财务数据处理为: "京投大合并" * -1
        if "dahebing_minus" in inputs["var_name"].values:
            inputs.loc[inputs.var_name == "dahebing_minus", "revenue_last_year":"employee_cost"] = \
                - inputs.loc[inputs.var_name == "dahebing", "revenue_last_year":"employee_cost"].values
        # 构造各单位实例
        for i, data in inputs.iterrows():
            class_name = data['category'] + data['subcategory']
            exec(data['var_name'] + "=" + class_name + """(var_name=data['var_name'], name=data['name'], \
                         package_last_year=data['package_last_year'], \
                         defer_last_year=data['defer_last_year'], \
                         distributable_last_year=data['distributable_last_year'], \
                         total_profit_last_year=data['total_profit_last_year'], \
                         patmi_self_last_year=data['patmi_self_last_year'], \
                         patmi_BII_last_year=data['patmi_BII_last_year'], \
                         revenue_last_year=data['revenue_last_year'], \
                         cost_last_year=data['cost_last_year'], \
                         invest_income_last_year=data['invest_income_last_year'], \
                         other_income_last_year=data['other_income_last_year'], \
                         labor_cost_last_year=data['labor_cost_last_year'], \
                         total_profit=data['total_profit'], \
                         patmi_self=data['patmi_self'], \
                         patmi_BII=data['patmi_BII'], \
                         revenue=data['revenue'], \
                         cost=data['cost'], \
                         invest_income=data['invest_income'], \
                         other_income=data['other_income'], \
                         labor_cost=data['labor_cost'], \
                         avg_employee_last_year=data['avg_employee_last_year'], \
                         avg_employee=data['avg_employee'], \
                         key_score=data['key_score'], \
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
            section_df_list[i] = tune(section_df_list[i],
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
        thread_results_df = thread_results_df.append(results_df)
        # update progress bar
        progress_bar.update(1)
    return thread_results_df


"""main"""
if __name__ == '__main__':
    # 读取输入条件，四个表格分别为：平均值、标准差、下界、上界。非数值则只采用inputs_mean中的值
    df_mean = pd.read_csv('inputs' + FILE_SUFFIX + '_mean.csv', converters={'subcategory': str}).astype("float", errors='ignore')
    df_sd = pd.read_csv('inputs' + FILE_SUFFIX + '_sd.csv', converters={'subcategory': str}).astype("float", errors='ignore')
    df_lower = pd.read_csv('inputs' + FILE_SUFFIX + '_lower.csv', converters={'subcategory': str}).astype("float", errors='ignore')
    df_upper = pd.read_csv('inputs' + FILE_SUFFIX + '_upper.csv', converters={'subcategory': str}).astype("float", errors='ignore')

    """多线程运行"""
    partial_do = partial(do, df1=df_mean, df2=df_sd, df3=df_lower, df4=df_upper)
    pool = Pool(THREAD_NO)  # Create a multiprocessing Pool
    all_results_df = pd.concat(pool.map(partial_do, range(THREAD_NO)))  # process data_inputs iterable with pool
    """输出csv"""
    print("\n采样完成，开始输出！")
    all_results_df.to_csv("results" + FILE_SUFFIX + "-MC.csv", encoding="UTF-8", float_format='%.5f', index=False)
    # all_results_df.to_excel("results.xlsx", sheet_name="all", encoding="UTF-8", engine='xlsxwriter', float_format='%.5f'
    # , index=False)
    print("输出完成，程序结束！")
