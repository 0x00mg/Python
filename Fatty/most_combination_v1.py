# script na filtrovanie obchodov z csv fatty sniping bota
# pred pouzitim je potreba csv upravit na samostatne stlpce


import pandas as pd
import math

# 1. Načítanie excel tabuľky (hlavička je v druhom riadku)
file_path = "<subor excel>"
df = pd.read_excel(file_path, header=1)  # header=1 -> druhý riadok

# 2. Funkcia na preklad písmena na názov stĺpca
def get_col_by_letter(df, letter):
    col_index = ord(letter.upper()) - ord("A")
    return df.columns[col_index]

# Definícia stĺpcov (podľa písmen z Excelu)
numeric_cols = [
    get_col_by_letter(df, "K"),  # Buy Market Cap
    get_col_by_letter(df, "M"),  # Buy Liquidity
    get_col_by_letter(df, "O"),  # Buy Volume
    get_col_by_letter(df, "Q")   # Buy Holders
]

# Filtrujeme stĺpec s "take profit" / "Sell Reason"
take_profit_col = df.columns[36]  # podľa indexu 36
df_profit = df[df[take_profit_col].astype(str).str.lower().str.strip() == "take profit"].copy()
df_non_profit = df[df[take_profit_col].astype(str).str.lower().str.strip() != "take profit"].copy()

# 3. Funkcia na binovanie
def create_bins(series, step):
    min_val = math.floor(series.min() / step) * step
    max_val = math.ceil(series.max() / step) * step
    bins = list(range(min_val, max_val + step, step))
    return pd.cut(series, bins=bins)

# Pomocná funkcia na prevod intervalu do "x-y" formátu
def interval_to_string(interval):
    return f"{int(interval.left)}-{int(interval.right)}"

# Vytvorenie binov pre profitabilné obchody
df_profit['Market Cap Bin'] = create_bins(pd.to_numeric(df_profit[numeric_cols[0]], errors='coerce').dropna(), 1000)
df_profit['Liquidity Bin']   = create_bins(pd.to_numeric(df_profit[numeric_cols[1]], errors='coerce').dropna(), 1000)
df_profit['Volume Bin']      = create_bins(pd.to_numeric(df_profit[numeric_cols[2]], errors='coerce').dropna(), 500)
df_profit['Holders Bin']     = create_bins(pd.to_numeric(df_profit[numeric_cols[3]], errors='coerce').dropna(), 5)

# 4. Najčastejšia kombinácia binov pre profitabilné obchody
combo_counts = df_profit.groupby(
    ['Market Cap Bin', 'Liquidity Bin', 'Volume Bin', 'Holders Bin'],
    observed=True
).size()

most_common_combo = combo_counts.idxmax()
most_common_count = combo_counts.max()

print("\nNajčastejšia kombinácia rozsahov pre profitabilné obchody:")
print(f"Buy Market Cap: {interval_to_string(most_common_combo[0])}")
print(f"Buy Liquidity: {interval_to_string(most_common_combo[1])}")
print(f"Buy Volume: {interval_to_string(most_common_combo[2])}")
print(f"Buy Holders: {interval_to_string(most_common_combo[3])}")
print(f"Počet obchodov v tejto kombinácii: {most_common_count}")

# 5. Počet neprofitabilných obchodov, ktoré spadajú do rovnakých binov
df_non_profit['Market Cap Bin'] = create_bins(pd.to_numeric(df_non_profit[numeric_cols[0]], errors='coerce').dropna(), 1000)
df_non_profit['Liquidity Bin']   = create_bins(pd.to_numeric(df_non_profit[numeric_cols[1]], errors='coerce').dropna(), 1000)
df_non_profit['Volume Bin']      = create_bins(pd.to_numeric(df_non_profit[numeric_cols[2]], errors='coerce').dropna(), 500)
df_non_profit['Holders Bin']     = create_bins(pd.to_numeric(df_non_profit[numeric_cols[3]], errors='coerce').dropna(), 5)

non_profit_count = df_non_profit[
    (df_non_profit['Market Cap Bin'] == most_common_combo[0]) &
    (df_non_profit['Liquidity Bin'] == most_common_combo[1]) &
    (df_non_profit['Volume Bin'] == most_common_combo[2]) &
    (df_non_profit['Holders Bin'] == most_common_combo[3])
].shape[0]

print(f"Počet neprofitabilných obchodov v týchto rozsahoch: {non_profit_count}")

