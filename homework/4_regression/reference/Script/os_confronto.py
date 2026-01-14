import sys
import numpy as np
import pandas as pd
from scipy.stats.mstats import theilslopes
import matplotlib.pyplot as plt

def main():
    file_name = "HomeWork_Regression_2024_v1.xlsx"

    os1 = "os1"
    os2 = "os2"
    os3 = "os3"

    x_column = "TIME"
    y_column = ["LIN_VmSize", "LIN_VmData", "LIN_RSS", "LIN_byte_letti__sec", "LIN_byte_scritti__sec"]

    df1 = pd.read_excel(file_name, sheet_name = os1)
    df2 = pd.read_excel(file_name, sheet_name = os2)
    df3 = pd.read_excel(file_name, sheet_name = os3)

    dfs = [df1, df2, df3]
    i = 1
    for df in dfs:
        for element in y_column:
            x = np.array(df[x_column])
            y = np.array(df[element])
            slope, intercept, low, up = theilslopes(y, x, 0.95)
            print("os" + str(i) + " " + element)
            print("Slope: {}. Interval: [{},{}]  Intercept: {}".format(slope, low, up, intercept))
        i+=1

if __name__ == "__main__":

    main()