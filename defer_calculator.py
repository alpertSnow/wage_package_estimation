"""输入数据，计算递延额度"""
print("输入相关数据，依据市国资委公式计算递延额度")
package_last_year = float(input("上年实际总额（万元）："))
rate_2 = float(input("工资总额测算增幅（递延前）："))
package = float(input("本年实际发放总额（万元）："))
total_profit_last_year = float(input("上年利润总额（万元）："))
defer_3 = ((1 + rate_2) - package/package_last_year) / ((1 / package_last_year) + 0.5 * 1 / abs(total_profit_last_year))
print("当年递延额度（万元）：%.2f" % defer_3)
