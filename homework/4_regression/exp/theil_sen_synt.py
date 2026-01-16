import pandas as pd
import numpy as np
from scipy.stats.mstats import theilslopes
import matplotlib.pyplot as plt

# Configurazione
file_name = "..\\homework_regression.xls"
sheet = "EXP1"  # Cambia in "EXP2" per il secondo homework

# Leggi dati
df = pd.read_excel(file_name, sheet_name=sheet)

# Variabili da analizzare
variables = ["nmail", "byte rec", "byte sent"]
x = df["observation"].values

print(f"\n{'='*60}")
print(f"ANALISI {sheet}")
print(f"{'='*60}")

for var in variables:
    y = df[var].values
    
    # Theil-Sen con intervallo confidenza 95%
    slope, intercept, low, up = theilslopes(y, x, 0.95)
    
    print(f"\n{var}:")
    print(f"  Slope: {slope:.6f}")
    print(f"  Interval: [{low:.6f}, {up:.6f}]")
    print(f"  Intercept: {intercept:.2f}")
    
    # Verifica significatività (intervallo contiene 0?)
    if low <= 0 <= up:
        print(f"  ⚠️  Trend NON significativo (intervallo contiene 0)")
    elif slope > 0:
        print(f"  ✓ Trend CRESCENTE significativo")
    else:
        print(f"  ✓ Trend DECRESCENTE significativo")
    

print(f"\n{'='*60}\n")