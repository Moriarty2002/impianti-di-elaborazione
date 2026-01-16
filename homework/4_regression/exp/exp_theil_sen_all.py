import numpy as np
import pandas as pd
from scipy.stats.mstats import theilslopes
from tabulate import tabulate

def main():
    file_name = "..\\homework_regression.xls"

    sheet_name_1 = "EXP1"
    sheet_name_2 = "EXP2"

    x_column = "observation"
    y_column = ["nmail", "byte rec", "byte sent"]

    df1 = pd.read_excel(file_name, sheet_name = sheet_name_1)
    df2 = pd.read_excel(file_name, sheet_name = sheet_name_2)

    dfs = [df1, df2]
    sheet_names = [sheet_name_1, sheet_name_2]
    
    # Lista per raccogliere i risultati
    results = []
    
    print(f"\n{'='*80}")
    print("ANALISI EXP1 E EXP2 - TABELLA RISULTATI THEIL-SEN")
    print(f"{'='*80}\n")
    
    for i, df in enumerate(dfs):
        sheet = sheet_names[i]
        print(f"\n--- Analisi {sheet} ---")
        
        for element in y_column:
            x = np.array(df[x_column])
            y = np.array(df[element])
            slope, intercept, low, up = theilslopes(y, x, 0.95)
            
            # Determina il trend
            if low <= 0 <= up:
                trend = "Non significativo"
                trend_symbol = "⚠️"
            elif slope > 0:
                trend = "Crescente"
                trend_symbol = "↗"
            else:
                trend = "Decrescente"
                trend_symbol = "↘"
            
            # Aggiungi ai risultati
            results.append({
                "Sheet": sheet,
                "Metric": element,
                "Slope": f"{slope:.6f}",
                "Interval_Low": f"{low:.6f}",
                "Interval_Up": f"{up:.6f}",
                "Intercept": f"{intercept:.2f}",
                "Trend": f"{trend_symbol} {trend}"
            })
            
            print(f"\n{element}:")
            print(f"  Slope: {slope:.6f}")
            print(f"  Interval: [{low:.6f}, {up:.6f}]")
            print(f"  Intercept: {intercept:.2f}")
            print(f"  Trend: {trend_symbol} {trend}")
    
    # Crea DataFrame
    df_results = pd.DataFrame(results)
    
    # Stampa tabella formattata
    print(f"\n{'='*80}")
    print("TABELLA COMPLESSIVA RISULTATI")
    print(f"{'='*80}\n")
    
    # Tabella con tabulate (più leggibile)
    print(tabulate(df_results, headers='keys', tablefmt='grid', showindex=False))
    
    # Salva in CSV
    csv_file = "exp_results_table.csv"
    df_results.to_csv(csv_file, index=False)
    print(f"\n✓ Tabella salvata in: {csv_file}")
    
    # Salva anche in formato Excel con formattazione
    excel_file = "exp_results_table.xlsx"
    df_results.to_excel(excel_file, index=False, sheet_name="Risultati")
    print(f"✓ Tabella salvata in: {excel_file}")
    
    # Tabella semplificata per report
    print(f"\n{'='*80}")
    print("TABELLA SEMPLIFICATA (per report)")
    print(f"{'='*80}\n")
    
    simple_table = []
    for _, row in df_results.iterrows():
        simple_table.append([
            row['Sheet'],
            row['Variable'],
            row['Slope'],
            f"[{row['Interval_Low']}, {row['Interval_Up']}]",
            row['Trend']
        ])
    
    print(tabulate(simple_table, 
                   headers=['Sheet', 'Variable', 'Slope', 'Interval (95%)', 'Trend'],
                   tablefmt='pipe'))
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    main()