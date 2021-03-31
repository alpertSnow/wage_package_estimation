import pandas as pd
from multiprocessing import Pool
from scipy.stats import norm
from functools import partial


def do(i, a):
    list_a = norm.rvs(size=3) + a
    list_b = norm.rvs(size=3)
    df = pd.DataFrame({"A": list_a, "B": list_b})
    return df


if __name__ == '__main__':
    a1 = 1
    partial_do = partial(do, a=a1)
    pool = Pool(3)  # Create a multiprocessing Pool
    res = pd.concat(pool.map(partial_do, range(3)))  # process data_inputs iterable with pool
    print(res)
