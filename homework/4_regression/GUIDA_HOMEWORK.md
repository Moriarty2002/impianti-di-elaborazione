# GUIDA COMPLETA HOMEWORK REGRESSIONE

## Indice
1. [Introduzione](#introduzione)
2. [Strumenti Necessari](#strumenti-necessari)
3. [Procedura Generale](#procedura-generale)
4. [HOMEWORK 1-2: EXP1 e EXP2](#homework-1-2-exp1-e-exp2)
5. [HOMEWORK 3-4-5: os1, os2, os3](#homework-3-4-5-os1-os2-os3)
6. [HOMEWORK 6-7-8: VMres1, VMres2, VMres3](#homework-6-7-8-vmres1-vmres2-vmres3)
7. [Checklist Finale](#checklist-finale)

---

## Introduzione

Questa guida ti accompagna passo per passo nello svolgimento degli homework di regressione, seguendo l'approccio utilizzato nella presentazione di riferimento (`reference/presentazione.pdf`).

**Obiettivo**: Rilevare e stimare eventuali trend utilizzando modelli regressivi lineari semplici, parametrici e/o non parametrici.

**File dati**: `HomeWork_Regression.xls`

**Fogli disponibili**:
- EXP1, EXP2: Nuovi esperimenti (sostituiscono il vecchio "Cloud")
- os1, os2, os3: Dati sistema operativo Linux
- VMres1, VMres2, VMres3: Dati Virtual Machine (heap Java)

---

## Strumenti Necessari

### Software
1. **JMP** - Per analisi statistiche e test visivi
2. **Python** - Per stima parametri Theil-Sen
3. **Excel/Calc** - Per visualizzazione dati

### Librerie Python (già installate)
```bash
pandas, numpy, scipy, matplotlib
```

### Script disponibili nella cartella `reference/Script/`
- `os_confronto.py` - Template per analisi os1/os2/os3
- `theil-sen.py` - Template per analisi VMres con failure prediction

---

## Procedura Generale

### FASE 1: ANALISI IN JMP

Questa procedura va ripetuta per ogni coppia (X, Y) da analizzare:

#### Step 1.1 - Importare i dati
1. Apri **JMP**
2. `File` → `Open` → Seleziona `HomeWork_Regression.xls`
3. Scegli il foglio da analizzare (es. EXP1, os1, VMres1)

#### Step 1.2 - Fit della regressione lineare
1. `Analyze` → `Fit Y by X`
2. Assegna le variabili:
   - **X, Factor**: Variabile indipendente (predittore)
   - **Y, Response**: Variabile dipendente (risposta)
3. Clicca `OK`
4. Nel pannello risultati, clicca sulla freccia rossa accanto a "Bivariate Fit"
5. Seleziona `Fit Line` (o `Linear Fit`)

**Screenshot da salvare**: Scatter plot con retta di regressione OLS

#### Step 1.3 - Salvare i residui
1. Nel pannello "Linear Fit", clicca sulla freccia rossa
2. `Save Columns` → `Residuals`
3. JMP crea automaticamente una colonna "Residuals" nella tabella dati

#### Step 1.4 - Test di normalità dei residui
1. `Analyze` → `Distribution`
2. Seleziona la colonna **Residuals** e mettila in `Y, Columns`
3. Clicca `OK`
4. Nel pannello rosso accanto a "Residuals":
   - Clicca sulla freccia rossa
   - `Continuous Fit` → `Normal`
5. Sempre nella freccia rossa:
   - `Test Normality` → Seleziona **Shapiro-Wilk W Test** (o KSL)

**Interpretazione**:
- **QQ-plot**: Se i punti sono allineati sulla diagonale → residui normali
- **p-value del test**: 
  - Se **p-value < 0.05** → Residui NON normali (rigetta H₀)
  - Se **p-value ≥ 0.05** → Residui normali

**Screenshot da salvare**: QQ-plot e risultato test Shapiro-Wilk

#### Step 1.5 - Test di omoschedasticità (solo se residui normali)

⚠️ **Esegui questo step SOLO se i residui sono risultati normali**

1. Torna alla regressione lineare (Step 1.2)
2. Nel pannello "Linear Fit", clicca sulla freccia rossa
3. `Save Columns` → `Predicted Values`
4. `Analyze` → `Fit Y by X`
5. Assegna:
   - **X**: Predicted (valori predetti)
   - **Y**: Residuals
6. Clicca `OK`

**Interpretazione** (test visivo):
- Dispersione costante attorno allo zero → **Omoschedastici**
- Dispersione a "imbuto" o pattern → **Eteroschedastici**

**Screenshot da salvare**: Plot residui vs fitted values

#### Step 1.6 - Decisione del metodo statistico

Sulla base dei risultati ottenuti:

| Normalità | Omoschedasticità | Metodo da usare |
|-----------|------------------|-----------------|
| ✓ SÌ | ✓ SÌ | **OLS (Ordinary Least Squares)** - Usa i parametri già calcolati da JMP |
| ✓ SÌ | ✗ NO | **Test di Welch** + stima **Theil-Sen** (vai a Step 1.7 e poi Python) |
| ✗ NO | - | **Mann-Kendall** + stima **Theil-Sen** (vai a Step 1.7 e poi Python) |

#### Step 1.7 - Test di Mann-Kendall (solo se residui NON normali)

⚠️ **Esegui questo step SOLO se i residui NON sono normali**

**Metodo 1 - In JMP** (più semplice):
1. Torna alla tabella dati
2. `Analyze` → `Specialized Modeling` → `Time Series`
3. Oppure: nella regressione, freccia rossa → `Row Diagnostics` → `Test for Trend`

**Metodo 2 - Con MATLAB** (script fornito):
1. Usa lo script `ktaub.m` nella cartella `reference/`
2. Fornisci i dati X e Y

**Interpretazione**:
- **Kendall Tau (τ)**: valore tra -1 e +1
  - Vicino a **+1**: forte trend crescente
  - Vicino a **-1**: forte trend decrescente
  - Vicino a **0**: nessun trend monotono
- **p-value**:
  - Se **p-value < 0.05** → Trend statisticamente significativo
  - Se **p-value ≥ 0.05** → Trend NON significativo

**Screenshot da salvare**: Risultato test Mann-Kendall (Tau e p-value)

---

### FASE 2: STIMA PARAMETRI CON PYTHON (Theil-Sen)

Se hai rilevato un trend (parametrico o non parametrico), stima i parametri robusti con **Theil-Sen**.

#### Quando usare Theil-Sen:
- Residui NON normali → sempre
- Residui normali ma NON omoschedastici → sì
- Residui normali E omoschedastici → opzionale (OLS va bene)

#### Script da usare come template:
- Per **os1/os2/os3**: `reference/Script/os_confronto.py`
- Per **VMres1/VMres2/VMres3**: `reference/Script/theil-sen.py`

#### Output da interpretare:
```
Slope: 0.031572
Interval: [0.030716, 0.032321]
Intercept: 738854.39
```

- **Slope**: Coefficiente angolare (pendenza) della retta
  - Positivo → trend crescente
  - Negativo → trend decrescente
  - Vicino a 0 → trend debole/assente
- **Interval [low, up]**: Intervallo di confidenza 95% per lo slope
  - Se **contiene lo 0** → trend NON significativo
  - Se **non contiene lo 0** → trend significativo
- **Intercept**: Valore di Y quando X=0

---

## HOMEWORK 1-2: EXP1 e EXP2

### Traccia
> Rilevare e stimare eventuali trend su ognuna delle tre variabili **nmail**, **byte rec** e **byte sent**, utilizzando modelli regressivi lineari semplici, parametrici e/o non parametrici.

### Variabili
- **X (predittore)**: `observation` (numero osservazione)
- **Y (risposta)**: `nmail`, `byte rec`, `byte sent` (analizzate separatamente)

### Procedura

#### Per EXP1:

**Analisi 1.1 - nmail**
1. **JMP**: Fit Y by X con X=`observation`, Y=`nmail`
2. Salva residui
3. Test Shapiro-Wilk sui residui → annota risultato (normale/non normale)
4. Se normale: test omoschedasticità
5. Se non normale: Mann-Kendall
6. **Python**: Stima Theil-Sen (vedi script sotto)

**Analisi 1.2 - byte rec**
1. Ripeti step 1-6 con Y=`byte rec`

**Analisi 1.3 - byte sent**
1. Ripeti step 1-6 con Y=`byte sent`

#### Per EXP2:

Ripeti le stesse 3 analisi (2.1, 2.2, 2.3) per il foglio EXP2.

### Script Python per EXP1 e EXP2

```python
import pandas as pd
import numpy as np
from scipy.stats.mstats import theilslopes
import matplotlib.pyplot as plt

# Configurazione
file_name = "HomeWork_Regression.xls"
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
    
    # Plot (opzionale)
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, alpha=0.5, label='Dati')
    plt.plot(x, slope * x + intercept, 'r-', linewidth=2, label='Theil-Sen')
    plt.xlabel('observation')
    plt.ylabel(var)
    plt.title(f'{sheet} - {var}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(f'{sheet}_{var.replace(" ", "_")}_theilsen.png', dpi=150)
    plt.close()

print(f"\n{'='*60}\n")
```

### Output da consegnare
1. **File JMP** salvato con tutte le analisi
2. **Screenshot JMP** (per EXP1 e EXP2):
   - 3 scatter plot con regressione OLS
   - 3 QQ-plot dei residui
   - 3 test Shapiro-Wilk
   - 3 test Mann-Kendall (se applicati)
3. **Tabella risultati Python**:
   ```
   | Sheet | Variable  | Slope    | Interval        | Trend         |
   |-------|-----------|----------|-----------------|---------------|
   | EXP1  | nmail     | ...      | [...]           | Crescente     |
   | EXP1  | byte rec  | ...      | [...]           | Non signif.   |
   | EXP1  | byte sent | ...      | [...]           | Decrescente   |
   | EXP2  | nmail     | ...      | [...]           | ...           |
   | ...   | ...       | ...      | ...             | ...           |
   ```
4. **Interpretazione**: Per ogni variabile, spiega se c'è un trend e cosa significa nel contesto del problema

---

## HOMEWORK 3-4-5: os1, os2, os3

### Traccia
> Rilevare e stimare eventuali trend sulle 5 variabili utilizzando modelli regressivi lineari semplici, parametrici e/o non parametrici. Farlo per i tre dataset os1, os2 e os3. **Confrontare i trend individuati nei tre dataset.**

### Variabili
- **X (predittore)**: `TIME` (tempo in secondi)
- **Y (risposta)**: Le 5 colonne di metriche (i nomi variano leggermente tra i dataset, verifica in Excel)
  - Esempio os1: `LIN1_VmSize`, `LIN1_VmData`, `LIN1_RSS`, `LIN1_byte_letti_I_O`, `LIN1_byte_letti_I_O1`

### Procedura

#### Per os1:

**Analisi 3.1-3.5** (una per variabile):
1. **JMP**: Fit Y by X con X=`TIME`, Y=[variabile]
2. Salva residui
3. Test Shapiro-Wilk → Dalla presentazione di riferimento, i residui sono risultati NON normali
4. Mann-Kendall per verificare trend
5. **Python**: Stima Theil-Sen

#### Per os2 e os3:
Ripeti le stesse 5 analisi per ciascun dataset.

**Totale**: 5 variabili × 3 dataset = **15 analisi**

### Script Python per os1, os2, os3

Usa e adatta lo script `reference/Script/os_confronto.py`:

```python
import pandas as pd
import numpy as np
from scipy.stats.mstats import theilslopes

# Configurazione
file_name = "HomeWork_Regression.xls"
datasets = ["os1", "os2", "os3"]
x_column = "TIME"

# IMPORTANTE: Verifica i nomi esatti delle colonne nel tuo Excel!
# Questi sono esempi, potrebbero essere diversi
y_columns = [
    "LIN1_VmSize",           # O simile
    "LIN1_VmData",           # O simile
    "LIN1_RSS",              # O simile
    "LIN1_byte_letti_I_O",   # O simile
    "LIN1_byte_letti_I_O1"   # O simile (seconda colonna I/O)
]

# Tabella per raccogliere i risultati
results = []

print(f"\n{'='*80}")
print("ANALISI OS1, OS2, OS3 - CONFRONTO TREND")
print(f"{'='*80}\n")

for ds in datasets:
    print(f"\n--- Dataset: {ds} ---")
    df = pd.read_excel(file_name, sheet_name=ds)
    
    # Verifica quali colonne esistono (potrebbero avere nomi diversi)
    print(f"Colonne disponibili: {list(df.columns)}")
    
    x = df[x_column].values
    
    for var in y_columns:
        # Verifica se la colonna esiste
        if var not in df.columns:
            print(f"⚠️  Colonna '{var}' non trovata in {ds}, saltata")
            continue
            
        y = df[var].values
        
        # Theil-Sen
        slope, intercept, low, up = theilslopes(y, x, 0.95)
        
        # Salva risultati
        results.append({
            "Dataset": ds,
            "Variable": var,
            "Slope": slope,
            "Low": low,
            "Up": up,
            "Intercept": intercept
        })
        
        print(f"\n{var}:")
        print(f"  Slope: {slope:.8f}")
        print(f"  Interval: [{low:.8f}, {up:.8f}]")
        print(f"  Intercept: {intercept:.2f}")
        
        # Significatività
        if low <= 0 <= up:
            print(f"  ⚠️  Trend NON significativo")
        elif slope > 0:
            print(f"  ✓ Trend CRESCENTE")
        else:
            print(f"  ✓ Trend DECRESCENTE")

# Crea DataFrame per confronto
df_results = pd.DataFrame(results)

# Stampa tabella comparativa
print(f"\n{'='*80}")
print("TABELLA COMPARATIVA")
print(f"{'='*80}\n")
print(df_results.to_string(index=False))

# Salva tabella
df_results.to_csv("os_confronto_risultati.csv", index=False)
print(f"\n✓ Tabella salvata in 'os_confronto_risultati.csv'")

# Analisi comparativa per variabile
print(f"\n{'='*80}")
print("CONFRONTO PER VARIABILE")
print(f"{'='*80}\n")

for var in y_columns:
    var_data = df_results[df_results["Variable"] == var]
    if len(var_data) == 0:
        continue
        
    print(f"\n{var}:")
    for _, row in var_data.iterrows():
        print(f"  {row['Dataset']}: slope = {row['Slope']:.6f} [{row['Low']:.6f}, {row['Up']:.6f}]")
    
    # Identifica quale ha lo slope maggiore
    max_slope_idx = var_data["Slope"].idxmax()
    max_ds = var_data.loc[max_slope_idx, "Dataset"]
    print(f"  → {max_ds} ha il trend più marcato per {var}")

print(f"\n{'='*80}\n")
```

### Confronto tra dataset (FONDAMENTALE)

Dopo aver raccolto tutti i risultati, confronta **per ogni variabile** i trend nei 3 dataset:

**Esempio per VmSize**:
```
VmSize:
  os1: slope = 0.031572 [0.030716, 0.032321]
  os2: slope = 0.001913 [0.000000, 0.002085]
  os3: slope = 0.021659 [0.021274, 0.022027]
  
→ os1 ha il trend crescente più marcato
→ os2 ha crescita molto lenta
→ Gli intervalli NON si sovrappongono → trend significativamente diversi
```

### Output da consegnare
1. **File JMP** con tutte le 15 analisi
2. **Screenshot JMP** (5 × 3 = 15 totali):
   - Scatter plot + regressione
   - QQ-plot residui
   - Test Shapiro-Wilk
   - Test Mann-Kendall
3. **Tabella comparativa** (da Python):
   - Slope per ogni variabile nei 3 dataset
   - Intervalli di confidenza
4. **File CSV** con risultati (`os_confronto_risultati.csv`)
5. **Interpretazione del confronto**:
   - Quale OS mostra maggior consumo memoria (VmSize/VmData/RSS)?
   - Quale ha più I/O (byte letti/scritti)?
   - I trend sono coerenti tra i dataset?

---

## HOMEWORK 6-7-8: VMres1, VMres2, VMres3

### Traccia
> Supponendo di avere un limite massimo alla memoria heap di **1 GByte**. Rilevare un eventuale trend di consumo dello heap nell'esperimento. Se rilevato il trend, stimare il tempo in cui lo heap satura (**failure prediction**).

### Variabili
- **X (predittore)**: `T(s)` (tempo in secondi)
- **Y (risposta)**: `Allocated Heap` (heap allocato in byte)

### Procedura

#### Per VMres1:

1. **JMP**: Fit Y by X con X=`T(s)`, Y=`Allocated Heap`
2. Salva residui
3. Test Shapiro-Wilk → Dalla presentazione, i residui sono NON normali
4. Mann-Kendall per confermare trend
5. **Python**: 
   - Stima Theil-Sen
   - Calcola tempo per saturare 1 GB
   - Plot con limite 1 GB visualizzato

#### Per VMres2 e VMres3:
Ripeti gli stessi step.

### Script Python per VMres (Failure Prediction)

Usa e adatta lo script `reference/Script/theil-sen.py`:

```python
import pandas as pd
import numpy as np
from scipy.stats.mstats import theilslopes
import matplotlib.pyplot as plt

# Configurazione
file_name = "HomeWork_Regression.xls"
datasets = ["VMres1", "VMres2", "VMres3"]
x_column = "T(s)"
y_column = "Allocated Heap"  # Verifica il nome esatto nel tuo Excel

# Limite 1 GB in byte
LIMIT_1GB = 1 * 1024 * 1024 * 1024  # 1,073,741,824 byte

print(f"\n{'='*80}")
print("ANALISI VMRES - FAILURE PREDICTION")
print(f"Limite heap: {LIMIT_1GB:,} byte (1 GB)")
print(f"{'='*80}\n")

results = []

for ds in datasets:
    print(f"\n{'='*60}")
    print(f"{ds}")
    print(f"{'='*60}")
    
    # Leggi dati
    df = pd.read_excel(file_name, sheet_name=ds)
    
    # Verifica nome colonna (potrebbe essere diverso)
    print(f"Colonne disponibili: {list(df.columns)}")
    
    x = df[x_column].values
    y = df[y_column].values
    
    # Theil-Sen
    slope, intercept, low, up = theilslopes(y, x, 0.95)
    
    print(f"\nParametri regressione:")
    print(f"  Slope: {slope:.6f}")
    print(f"  Interval: [{low:.6f}, {up:.6f}]")
    print(f"  Intercept: {intercept:.2f}")
    
    # Calcolo tempo saturazione
    # Formula: T = (Limit - intercept) / slope
    
    if slope <= 0:
        print(f"\n⚠️  ATTENZIONE: Slope negativo o nullo! Nessun trend di crescita.")
        print(f"   Lo heap NON saturerà mai il limite di 1 GB")
        continue
    
    # Tempo medio
    time_saturate = (LIMIT_1GB - intercept) / slope
    
    # Calcolo incertezza usando intervallo confidenza slope
    # Tempo massimo (con slope minimo)
    time_max = (LIMIT_1GB - intercept) / low
    # Tempo minimo (con slope massimo)
    time_min = (LIMIT_1GB - intercept) / up
    
    # Incertezza
    uncertainty = (time_max - time_min) / 2
    
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
        "Dataset": ds,
        "Slope": slope,
        "Low": low,
        "Up": up,
        "Intercept": intercept,
        "Time_seconds": time_saturate,
        "Time_years": sec_to_years,
        "Uncertainty_years": unc_years
    })
    
    # Plot
    plt.figure(figsize=(12, 7))
    
    # Scatter dati
    plt.scatter(x, y, alpha=0.6, s=50, label='Dati osservati', color='blue')
    
    # Retta Theil-Sen
    x_pred = np.linspace(x.min(), time_saturate * 1.1, 1000)
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
    plt.plot(time_saturate, LIMIT_1GB, 'go', markersize=12, 
             label=f'Saturazione: {sec_to_years:.1f} anni')
    
    # Etichette
    plt.xlabel('Tempo T(s)', fontsize=12)
    plt.ylabel('Allocated Heap (byte)', fontsize=12)
    plt.title(f'{ds} - Failure Prediction\n'
              f'Tempo stimato: {sec_to_years:.1f} ± {unc_years:.1f} anni', 
              fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    # Formatta asse y per leggibilità
    ax = plt.gca()
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.0f}M'))
    
    # Salva
    plt.tight_layout()
    plt.savefig(f'{ds}_failure_prediction.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\n✓ Plot salvato: {ds}_failure_prediction.png")

# Tabella comparativa
print(f"\n{'='*80}")
print("CONFRONTO TRA VMRES1, VMRES2, VMRES3")
print(f"{'='*80}\n")

df_results = pd.DataFrame(results)
print(df_results.to_string(index=False))

# Identifica quale satura prima
if len(df_results) > 0:
    min_time_idx = df_results["Time_years"].idxmin()
    fastest = df_results.loc[min_time_idx, "Dataset"]
    fastest_time = df_results.loc[min_time_idx, "Time_years"]
    
    print(f"\n🔥 {fastest} satura per PRIMO il limite di 1 GB")
    print(f"   Tempo: {fastest_time:.1f} anni")
    
    max_time_idx = df_results["Time_years"].idxmax()
    slowest = df_results.loc[max_time_idx, "Dataset"]
    slowest_time = df_results.loc[max_time_idx, "Time_years"]
    
    print(f"\n🐌 {slowest} satura per ULTIMO")
    print(f"   Tempo: {slowest_time:.1f} anni")
    
    diff = slowest_time - fastest_time
    print(f"\n⏰ Differenza: {diff:.1f} anni")

# Salva tabella
df_results.to_csv("vmres_failure_prediction_risultati.csv", index=False)
print(f"\n✓ Tabella salvata in 'vmres_failure_prediction_risultati.csv'")

print(f"\n{'='*80}\n")
```

### Output da consegnare
1. **File JMP** con le 3 analisi
2. **Screenshot JMP** (per VMres1, 2, 3):
   - Scatter plot + regressione
   - QQ-plot residui
   - Test Shapiro-Wilk
   - Test Mann-Kendall
3. **Plot Python** con:
   - Dati osservati
   - Retta Theil-Sen
   - Intervallo confidenza
   - Limite 1 GB evidenziato
   - Punto di saturazione
4. **Tabella comparativa**:
   ```
   | Dataset | Slope    | Time (anni) | Incertezza |
   |---------|----------|-------------|------------|
   | VMres1  | 0.691    | 49.0        | ± 8.8      |
   | VMres2  | 2.903    | 11.7        | ± 0.8      |
   | VMres3  | ...      | ...         | ...        |
   ```
5. **Interpretazione**:
   - Quale esperimento satura prima?
   - Le stime sono realistiche?
   - Quale ha il consumo più rapido di heap?

---

## Checklist Finale

### Per ogni homework completato devi avere:

#### ✅ Analisi JMP
- [ ] File `.jmp` salvato con tutte le analisi
- [ ] Screenshot scatter plot + regressione OLS
- [ ] Screenshot QQ-plot residui
- [ ] Screenshot test Shapiro-Wilk (o KSL)
- [ ] Screenshot test omoschedasticità (se applicabile)
- [ ] Screenshot test Mann-Kendall (se applicabile)

#### ✅ Analisi Python
- [ ] Script Python eseguito e testato
- [ ] Output console salvato
- [ ] Tabella risultati con parametri Theil-Sen
- [ ] Plot generati (per VMres)
- [ ] File CSV risultati salvati

#### ✅ Interpretazione
- [ ] Spiegazione dei risultati ottenuti
- [ ] Identificazione trend (crescente/decrescente/assente)
- [ ] Significatività statistica verificata
- [ ] Confronto tra dataset (per os e VMres)
- [ ] Risposta alle domande della traccia

#### ✅ Documentazione
- [ ] Report finale che unisce JMP e Python
- [ ] Grafici e tabelle ben etichettati
- [ ] Conclusioni per ogni homework
- [ ] Bibliografia/riferimenti (se richiesti)

---

## Note Finali

### Differenze rispetto alla vecchia presentazione
- **Homework Cloud rimosso** → Sostituito con EXP1 ed EXP2
- **Stessa metodologia**: JMP per test + Python per Theil-Sen
- **Stessi test**: Shapiro-Wilk, Mann-Kendall, Theil-Sen

### Suggerimenti
1. **Lavora in ordine**: Completa prima EXP1, poi EXP2, poi os1-2-3, infine VMres
2. **Documenta tutto**: Screenshot e risultati vanno salvati subito
3. **Verifica nomi colonne**: I nomi nel tuo Excel potrebbero essere leggermente diversi
4. **Interpreta sempre**: Non limitarti ai numeri, spiega cosa significano

### Risorse utili
- `reference/linee_guida.txt` - Procedura riassuntiva
- `reference/presentazione.pdf` - Esempio completo vecchia versione
- `reference/Script/` - Script Python template

---

**Buon lavoro! 🚀**
