import numpy as np
import pandas as pd
from scipy.stats.mstats import theilslopes
from tabulate import tabulate
import matplotlib.pyplot as plt

def main():
    file_name = "..\\homework_regression.xls"

    sheet_name_1 = "VMres1"
    sheet_name_2 = "VMres2"
    sheet_name_3 = "VMres3"
    
    # Limite 1 GB in byte
    LIMIT_1GB = 1 * 1024 * 1024 * 1024  # 1,073,741,824 byte

    df1 = pd.read_excel(file_name, sheet_name = sheet_name_1)
    df2 = pd.read_excel(file_name, sheet_name = sheet_name_2)
    df3 = pd.read_excel(file_name, sheet_name = sheet_name_3)

    dfs = [df1, df2, df3]
    sheet_names = [sheet_name_1, sheet_name_2, sheet_name_3]
    
    # Funzione per trovare le colonne corrette (nomi possono variare)
    def find_columns(df):
        # Trova colonna tempo (contiene 'T' o 's')
        x_col = None
        for col in df.columns:
            if 'T' in col and 's' in col:
                x_col = col
                break
        
        # Trova colonna heap (contiene 'heap' o 'Heap')
        y_col = None
        for col in df.columns:
            if 'heap' in col.lower():
                y_col = col
                break
        
        return x_col, y_col
    
    # Lista per raccogliere i risultati
    results = []
    
    print(f"\n{'='*80}")
    print("ANALISI VMres1, VMres2, VMres3 - FAILURE PREDICTION")
    print(f"Limite heap: {LIMIT_1GB:,} byte (1 GB)")
    print(f"{'='*80}\n")
    
    for i, df in enumerate(dfs):
        sheet = sheet_names[i]
        
        # Trova i nomi corretti delle colonne
        x_column, y_column = find_columns(df)
        
        if x_column is None or y_column is None:
            print(f"\n⚠️  Errore: Colonne non trovate in {sheet}")
            print(f"   Colonne disponibili: {list(df.columns)}")
            continue
        
        print(f"\n{'='*80}")
        print(f"Analisi {sheet}")
        print(f"Colonna X: {x_column}, Colonna Y: {y_column}")
        print(f"{'='*80}")
        
        # Rimuovi NaN
        temp_df = df[[x_column, y_column]].dropna()
        x = np.array(temp_df[x_column])
        y = np.array(temp_df[y_column])
        
        # Theil-Sen con intervallo confidenza 95%
        slope, intercept, low, up = theilslopes(y, x, 0.95)
        
        print(f"\nParametri regressione Theil-Sen:")
        print(f"  Slope: {slope:.6f} byte/secondo")
        print(f"  Interval: [{low:.6f}, {up:.6f}]")
        print(f"  Intercept: {intercept:.2f} byte")
        
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
        
        print(f"  Trend: {trend_symbol} {trend}")
        
        # Calcolo tempo saturazione solo se slope > 0
        if slope <= 0:
            print(f"\n⚠️  ATTENZIONE: Slope negativo o nullo!")
            print(f"   Lo heap NON saturerà mai il limite di 1 GB")
            
            results.append({
                "Sheet": sheet,
                "Slope": f"{slope:.6f}",
                "Interval_Low": f"{low:.6f}",
                "Interval_Up": f"{up:.6f}",
                "Intercept": f"{intercept:.2f}",
                "Trend": f"{trend_symbol} {trend}",
                "Time_seconds": "N/A",
                "Time_years": "N/A",
                "Uncertainty_years": "N/A"
            })
            continue
        
        # Calcolo tempo saturazione
        # Formula: T = (Limit - intercept) / slope
        time_saturate = (LIMIT_1GB - intercept) / slope
        
        # Calcolo incertezza usando intervallo confidenza slope
        # Tempo massimo (con slope minimo)
        time_max = (LIMIT_1GB - intercept) / low if low > 0 else float('inf')
        # Tempo minimo (con slope massimo)
        time_min = (LIMIT_1GB - intercept) / up if up > 0 else 0
        
        # Incertezza
        uncertainty = abs(time_max - time_min) / 2
        
        # Conversioni temporali
        sec_to_min = time_saturate / 60
        sec_to_hours = time_saturate / 3600
        sec_to_days = time_saturate / (3600 * 24)
        sec_to_years = time_saturate / (3600 * 24 * 365.25)
        
        unc_years = uncertainty / (3600 * 24 * 365.25)
        
        print(f"\n⏱️  TEMPO STIMATO PER SATURARE 1 GB:")
        print(f"  {time_saturate:,.0f} ± {uncertainty:,.0f} secondi")
        print(f"  {sec_to_min:,.0f} minuti")
        print(f"  {sec_to_hours:,.1f} ore")
        print(f"  {sec_to_days:,.1f} giorni")
        print(f"  {sec_to_years:.1f} ± {unc_years:.1f} anni")
        
        # Salva risultati
        results.append({
            "Sheet": sheet,
            "Slope": f"{slope:.6f}",
            "Interval_Low": f"{low:.6f}",
            "Interval_Up": f"{up:.6f}",
            "Intercept": f"{intercept:.2f}",
            "Trend": f"{trend_symbol} {trend}",
            "Time_seconds": f"{time_saturate:.0f}",
            "Time_years": f"{sec_to_years:.2f}",
            "Uncertainty_years": f"{unc_years:.2f}"
        })
        
        # Plot
        plt.figure(figsize=(12, 7))
        
        # Scatter dati
        plt.scatter(x, y, alpha=0.6, s=50, label='Dati osservati', color='blue')
        
        # Retta Theil-Sen
        if time_saturate > x.max():
            x_pred = np.linspace(x.min(), time_saturate * 1.1, 1000)
        else:
            x_pred = np.linspace(x.min(), x.max() * 1.5, 1000)
        y_pred = slope * x_pred + intercept
        plt.plot(x_pred, y_pred, 'r-', linewidth=2, label=f'Theil-Sen (slope={slope:.4f})')
        
        # Rette con intervallo confidenza
        y_pred_low = low * x_pred + intercept
        y_pred_up = up * x_pred + intercept
        plt.fill_between(x_pred, y_pred_low, y_pred_up, alpha=0.2, color='red', 
                         label='Intervallo confidenza 95%')
        
        # Limite 1 GB
        plt.axhline(LIMIT_1GB, color='green', linestyle='--', linewidth=2, 
                    label=f'Limite 1 GB ({LIMIT_1GB:,} byte)')
        
        # Punto di saturazione
        if time_saturate < x_pred.max():
            plt.plot(time_saturate, LIMIT_1GB, 'go', markersize=12, 
                     label=f'Saturazione: {sec_to_years:.1f} anni')
        
        # Etichette
        plt.xlabel('Tempo T(s)', fontsize=12)
        plt.ylabel('Allocated Heap (byte)', fontsize=12)
        plt.title(f'{sheet} - Failure Prediction\n'
                  f'Tempo stimato: {sec_to_years:.1f} ± {unc_years:.1f} anni', 
                  fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        
        # Formatta asse y per leggibilità
        ax = plt.gca()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.0f}M'))
        
        # Salva
        plt.tight_layout()
        plt.savefig(f'{sheet}_failure_prediction.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"\n✓ Plot salvato: {sheet}_failure_prediction.png")
    
    # Crea DataFrame
    df_results = pd.DataFrame(results)
    
    # Stampa tabella formattata
    print(f"\n{'='*80}")
    print("TABELLA COMPLESSIVA RISULTATI")
    print(f"{'='*80}\n")
    
    # Tabella con tabulate
    print(tabulate(df_results, headers='keys', tablefmt='grid', showindex=False))
    
    # Salva in CSV
    csv_file = "vmres_results_table.csv"
    df_results.to_csv(csv_file, index=False)
    print(f"\n✓ Tabella salvata in: {csv_file}")
    
    # Salva anche in formato Excel
    excel_file = "vmres_results_table.xlsx"
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
            row['Slope'],
            f"[{row['Interval_Low']}, {row['Interval_Up']}]",
            row['Time_years'] if row['Time_years'] != 'N/A' else 'N/A',
            row['Trend']
        ])
    
    print(tabulate(simple_table, 
                   headers=['Sheet', 'Slope (byte/s)', 'Interval (95%)', 'Tempo (anni)', 'Trend'],
                   tablefmt='pipe'))
    
    # CONFRONTO TRA VMRES
    print(f"\n{'='*80}")
    print("CONFRONTO TRA VMres1, VMres2, VMres3")
    print(f"{'='*80}\n")
    
    # Filtra solo quelli con tempo valido
    valid_results = [r for r in results if r['Time_years'] != 'N/A']
    
    if len(valid_results) > 0:
        # Ordina per tempo di saturazione
        valid_results_sorted = sorted(valid_results, key=lambda x: float(x['Time_years']))
        
        print("Classifica per velocità di saturazione (dal più veloce al più lento):\n")
        
        for idx, r in enumerate(valid_results_sorted, 1):
            time_y = float(r['Time_years'])
            unc_y = float(r['Uncertainty_years'])
            print(f"{idx}. {r['Sheet']}: {time_y:.1f} ± {unc_y:.1f} anni")
        
        # Differenza tra il più veloce e il più lento
        if len(valid_results_sorted) > 1:
            fastest = valid_results_sorted[0]
            slowest = valid_results_sorted[-1]
            diff = float(slowest['Time_years']) - float(fastest['Time_years'])
            
            print(f"\n🔥 {fastest['Sheet']} satura per PRIMO (più veloce)")
            print(f"🐌 {slowest['Sheet']} satura per ULTIMO (più lento)")
            print(f"⏰ Differenza: {diff:.1f} anni")
        
        # PLOT COMPARATIVO
        print(f"\n📊 Creazione plot comparativo...")
        
        # Prepara i dati per il plot comparativo
        plot_data = []
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Blu, Arancione, Verde
        
        for idx, (df, sheet) in enumerate(zip(dfs, sheet_names)):
            # Trova colonne
            x_col, y_col = find_columns(df)
            if x_col and y_col:
                temp_df = df[[x_col, y_col]].dropna()
                x_data = np.array(temp_df[x_col])
                y_data = np.array(temp_df[y_col])
                
                # Trova risultati corrispondenti
                result = next((r for r in results if r['Sheet'] == sheet), None)
                if result and result['Time_years'] != 'N/A':
                    slope = float(result['Slope'])
                    intercept = float(result['Intercept'])
                    low = float(result['Interval_Low'])
                    up = float(result['Interval_Up'])
                    time_sat = float(result['Time_seconds'])
                    
                    plot_data.append({
                        'sheet': sheet,
                        'x': x_data,
                        'y': y_data,
                        'slope': slope,
                        'intercept': intercept,
                        'low': low,
                        'up': up,
                        'time_sat': time_sat,
                        'color': colors[idx % len(colors)]
                    })
        
        if len(plot_data) > 0:
            # Crea figura comparativa
            plt.figure(figsize=(14, 8))
            
            # Plot proiezione fino alla saturazione
            for data in plot_data:
                # Estendi fino al punto di saturazione
                x_pred = np.linspace(0, data['time_sat'] * 1.1, 1000)
                y_pred = data['slope'] * x_pred + data['intercept']
                
                # Plotting con intervallo confidenza
                y_pred_low = data['low'] * x_pred + data['intercept']
                y_pred_up = data['up'] * x_pred + data['intercept']
                
                plt.plot(x_pred, y_pred, '-', linewidth=2.5, 
                        label=f"{data['sheet']}", color=data['color'])
                plt.fill_between(x_pred, y_pred_low, y_pred_up, alpha=0.15, color=data['color'])
                
                # Punto di saturazione
                plt.plot(data['time_sat'], LIMIT_1GB, 'o', markersize=10, 
                        color=data['color'], zorder=15)
                
                # Annotazione tempo
                time_years = data['time_sat'] / (3600 * 24 * 365.25)
                plt.annotate(f'{time_years:.1f} anni', 
                           xy=(data['time_sat'], LIMIT_1GB),
                           xytext=(10, -20), textcoords='offset points',
                           fontsize=9, color=data['color'], fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                                   edgecolor=data['color'], alpha=0.8))
            
            # Limite 1 GB
            plt.axhline(LIMIT_1GB, color='red', linestyle='--', linewidth=2, 
                       label='Limite 1 GB', zorder=10)
            
            plt.xlabel('Tempo T(s)', fontsize=12, fontweight='bold')
            plt.ylabel('Allocated Heap (byte)', fontsize=12, fontweight='bold')
            plt.title('Confronto Proiezione Saturazione Heap: VMres1 vs VMres2 vs VMres3\n(con intervalli confidenza 95%)', 
                     fontsize=14, fontweight='bold')
            plt.legend(fontsize=10, loc='best')
            plt.grid(True, alpha=0.3)
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.0f}M'))
            
            # Imposta limiti y per visualizzare bene il limite 1GB
            plt.ylim([0, LIMIT_1GB * 1.15])
            
            plt.tight_layout()
            comparison_file = "vmres_comparison_plot.png"
            plt.savefig(comparison_file, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"\n✓ Plot comparativo salvato: {comparison_file}")
            
            # Crea anche un plot delle sole rette per confronto diretto
            plt.figure(figsize=(14, 8))
            
            for data in plot_data:
                x_pred = np.linspace(0, data['time_sat'] * 1.05, 1000)
                y_pred = data['slope'] * x_pred + data['intercept']
                
                plt.plot(x_pred, y_pred, '-', linewidth=3, 
                        label=f"{data['sheet']} (slope={data['slope']:.4f} byte/s)", 
                        color=data['color'])
                
                # Punto di saturazione
                plt.plot(data['time_sat'], LIMIT_1GB, 'o', markersize=12, 
                        color=data['color'], zorder=15)
                
                # Annotazione tempo su ogni marker
                time_years = data['time_sat'] / (3600 * 24 * 365.25)
                plt.annotate(f'{time_years:.1f} anni', 
                           xy=(data['time_sat'], LIMIT_1GB),
                           xytext=(15, 15), textcoords='offset points',
                           fontsize=10, color=data['color'], fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                                   edgecolor=data['color'], linewidth=2, alpha=0.9),
                           arrowprops=dict(arrowstyle='->', color=data['color'], 
                                         lw=1.5, connectionstyle='arc3,rad=0.2'))
            
            # Limite 1 GB
            plt.axhline(LIMIT_1GB, color='red', linestyle='--', linewidth=2.5, 
                       label='Limite 1 GB', zorder=10)
            
            plt.xlabel('Tempo T(s)', fontsize=13, fontweight='bold')
            plt.ylabel('Allocated Heap (byte)', fontsize=13, fontweight='bold')
            plt.title('Confronto Diretto Trend Consumo Heap\nVMres1 vs VMres2 vs VMres3', 
                     fontsize=15, fontweight='bold')
            plt.legend(fontsize=11, loc='upper left')
            plt.grid(True, alpha=0.3, linestyle='--')
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.0f}M'))
            
            plt.tight_layout()
            direct_comparison_file = "vmres_trend_comparison.png"
            plt.savefig(direct_comparison_file, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"✓ Plot trend comparativo salvato: {direct_comparison_file}")
    else:
        print("⚠️  Nessun dataset mostra trend di crescita dell'heap")
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    main()
