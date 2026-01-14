import sys
import numpy as np
import pandas as pd
from scipy.stats.mstats import theilslopes
import matplotlib.pyplot as plt

def main():
    file_name = "HomeWork_Regression_2024_v1.xlsx"
    spreed_sheet = "VMres3"
    x_column = "T(s)"
    y_column = "allocated heap"
    df = pd.read_excel(file_name, sheet_name = spreed_sheet)
    x = np.array(df[x_column])
    y = np.array(df[y_column])
    slope, intercept, low, up = theilslopes(y, x, 0.95)
    print("Slope: {}. Interval: [{},{}]  Intercept: {}".format(slope, low, up, intercept))

    plt.scatter(x, y, label='Data Points')
    plt.plot(x, slope * x + intercept, color='red', label='Theil-Sen Line')
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.title('Theil-Sen Regression')
    plt.legend()
    plt.show()

    heap_1gb = 1 * 1024 * 1024 * 1024 
    time_to_saturate = (heap_1gb - intercept) / (slope +- (up-low)/2)
    print("Time to saturate 1GB of heap: {:.2f} seconds".format(time_to_saturate))

if __name__ == "__main__":

    main()