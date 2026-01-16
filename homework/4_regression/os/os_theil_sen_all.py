import numpy as np
import pandas as pd
from scipy.stats.mstats import theilslopes
from tabulate import tabulate

def main():
    file_name = "..\\homework_regression.xls"

    sheet_name_1 = "os1"
    sheet_name_2 = "os2"
    sheet_name_3 = "os3"

    x_column = "TIME"
    
    # Leggi i dataframe
    df1 = pd.read_excel(file_name, sheet_name = sheet_name_1)
    df2 = pd.read_excel(file_name, sheet_name = sheet_name_2)
    df3 = pd.read_excel(file_name, sheet_name = sheet_name_3)

    dfs = [df1, df2, df3]
    sheet_names = [sheet_name_1, sheet_name_2, sheet_name_3]
    
    # Identifica automaticamente le colonne Y per ogni dataset (escludendo TIME e colonne Unnamed)
    def get_metric_columns(df):
        return [col for col in df.columns if col != 'TIME' and not col.startswith('Unnamed')]
    
    # Lista per raccogliere i risultati
    results = []
    
    print(f"\n{'='*80}")
    print("ANALISI os1, os2, os3 - TABELLA RISULTATI THEIL-SEN")
    print(f"Variabile X: {x_column}")
    print(f"{'='*80}\n")
    
    for i, df in enumerate(dfs):
        sheet = sheet_names[i]
        y_columns = get_metric_columns(df)
        
        print(f"\n--- Analisi {sheet} ---")
        print(f"Metriche trovate: {', '.join(y_columns)}")
        
        for element in y_columns:
            # Crea un dataframe temporaneo e rimuovi righe con NaN
            temp_df = df[[x_column, element]].dropna()
            x = np.array(temp_df[x_column])
            y = np.array(temp_df[element])
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
    csv_file = "os_results_table.csv"
    df_results.to_csv(csv_file, index=False)
    print(f"\n✓ Tabella salvata in: {csv_file}")
    
    # Salva anche in formato Excel con formattazione
    excel_file = "os_results_table.xlsx"
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
            row['Metric'],
            row['Slope'],
            f"[{row['Interval_Low']}, {row['Interval_Up']}]",
            row['Trend']
        ])
    
    print(tabulate(simple_table, 
                   headers=['Sheet', 'Metric', 'Slope', 'Interval (95%)', 'Trend'],
                   tablefmt='pipe'))
    
    # CONFRONTO TRA DATASET (parte fondamentale)
    print(f"\n{'='*80}")
    print("CONFRONTO TRA OS1, OS2, OS3 PER TIPO DI METRICA")
    print(f"{'='*80}\n")
    
    # Raggruppa metriche per tipo (VmSize, VmData, RSS, byte_letti, byte_scritti)
    metric_types = {
        'VmSize': [],
        'VmData': [],
        'RSS': [],
        'byte_letti': [],
        'byte_scritti': []
    }
    
    # Classifica ogni metrica nel suo tipo
    for _, row in df_results.iterrows():
        metric = row['Metric']
        if 'VmSize' in metric:
            metric_types['VmSize'].append(row)
        elif 'VmData' in metric:
            metric_types['VmData'].append(row)
        elif 'RSS' in metric:
            metric_types['RSS'].append(row)
        elif 'letti' in metric:
            metric_types['byte_letti'].append(row)
        elif 'scritti' in metric:
            metric_types['byte_scritti'].append(row)
    
    for metric_type, rows in metric_types.items():
        if not rows:
            continue
            
        print(f"\n📊 {metric_type}:")
        
        comparison_table = []
        slopes_values = []
        
        for row in rows:
            comparison_table.append([
                row['Sheet'],
                row['Metric'],
                row['Slope'],
                f"[{row['Interval_Low']}, {row['Interval_Up']}]",
                row['Trend']
            ])
            slopes_values.append((row['Sheet'], float(row['Slope'])))
        
        print(tabulate(comparison_table,
                      headers=['Dataset', 'Metric', 'Slope', 'Interval (95%)', 'Trend'],
                      tablefmt='simple'))
        
        # Identifica quale ha lo slope maggiore (in valore assoluto per trend marcato)
        slopes_values.sort(key=lambda x: abs(x[1]), reverse=True)
        max_ds = slopes_values[0][0]
        max_slope = slopes_values[0][1]
        
        if abs(max_slope) > 1e-6:  # Solo se non è praticamente zero
            if max_slope > 0:
                print(f"   → {max_ds} ha il trend CRESCENTE più marcato (slope = {max_slope:.6f})")
            else:
                print(f"   → {max_ds} ha il trend DECRESCENTE più marcato (slope = {max_slope:.6f})")
        else:
            print(f"   → Tutti i dataset mostrano trend molto deboli o assenti")
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    main()