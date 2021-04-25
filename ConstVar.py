"""Unit: 万元，人"""
import pandas as pd

"""const"""
GZW_BASE_RATE = 0.03  # 国资委公布的工资总额增幅基准线
GZW_AVG_RATE = 0.2 / 3  # 上年度市管企业在岗职工平均工资增幅
GZW_RATE_CAP = 3 * GZW_AVG_RATE  # 超过3倍部分计入递延
AVG_TOWN_WAGE = 9.0501  # 全国城镇单位就业人员平均工资（2019）
LOAD_INDEX_LIMITS_MULTIPLIER = pd.Series([-2, 2])  # 工作量指标区间乘数
LOAD_INDEX_LIMITS = LOAD_INDEX_LIMITS_MULTIPLIER * GZW_BASE_RATE
FINANCIAL_INDEX_LIMITS_MULTIPLIER = pd.Series([-1, 1])  # 经济效益指标区间乘数
FINANCIAL_INDEX_LIMITS = FINANCIAL_INDEX_LIMITS_MULTIPLIER * GZW_BASE_RATE
TOLERANCE = 1E-8  # 比较时使用，去除计算误差
SAMPLE_SIZE = 250  # 随机采样个数(in a thread)
THREAD_NO = 4  # 线程数

"""var"""
GZW_score_converted_growth = 0.03  # 国资委考核京投重大任务完成率转换的增幅
