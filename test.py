import pandas as pd
df = pd.DataFrame({"A": [1, 2, 3]})
for i, data in df.iterrows():
    data.A = 2 if data.A <= 2 else data.A

a1_last = 10
a2_last = 5
A_last = a1_last + a2_last

t1 = a1_last * 0.9
t2 = a2_last * 0.9
t = t1 + t2

T = A_last * 1.1
A = A_last * 1.1
B = T - A


t1_1 = t1 * T/t if T/t < 1 else t1
t2_1 = t2 * T/t if T/t < 1 else t2

c1 = (t1_1 - a1_last) * 0.4 if t1_1 - a1_last > 0 else 0
c2 = (t2_1 - a2_last) * 0.4 if t2_1 - a2_last > 0 else 0

a1 = a1_last * 1.2 if t1_1 - c1 > a1_last * 1.2 else t1_1 - c1
a2 = a2_last * 1.2 if t2_1 - c2 > a2_last * 1.2 else t2_1 - c2

a = a1 + a2

a1_1 = a1 * A/a if A/a < 1 else a1
a2_1 = a2 * A/a if A/a < 1 else a2

b1 = t1_1 - a1_1 - c1
b2 = t2_1 - a2_1 - c2

print("a1:%.1f\t\tb1:%.1f\t\tc1:%.1f\t\tt1:%.1f" % (a1_1, b1, c1, t1_1))
print("a2:%.1f\t\tb2:%.1f\t\tc2:%.1f\t\tt2:%.1f" % (a2_1, b2, c2, t2_1))
print("a :%.1f\t\tb :%.1f\t\tc :%.1f\t\tt :%.1f" % (a1_1+a2_1, b1+b2, c1+c2, t1_1+t2_1))
print("A :%.1f\t\tB :%.1f\t\t\t\t\tT :%.1f" % (A, B, T))