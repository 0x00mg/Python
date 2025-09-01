import pandas as pd
import math

# 1. Načítanie excel tabuľky (hlavička je v druhom riadku)
file_path = "<subor excel>"
df = pd.read_excel(file_path, header=1)

# 2. Funkcia na preklad písmena na názov stĺpca
def get_col_by_letter(df, letter):
    col_index = ord(letter.upper()) - ord("A")
    return df.columns[col_index]

# Definícia stĺpcov
numeric_cols = [
    get_col_by_letter(df, "K"),  # Buy Market Cap
    get_col_by_letter(df, "M"),  # Buy Liquidity
    get_col_by_letter(df, "O"),  # Buy Volume
    get_col_by_letter(df, "Q")   # Buy Holders
]

# 3. Filtrujeme profitabilné a neprofitabilné obchody
take_profit_col = df.columns[36]  # stĺpec "Sell Reason"
df_profit = df[df[take_profit_col].astype(str).str.lower().str.strip() == "take profit"].copy()
df_non_profit = df[df[take_profit_col].astype(str).str.lower().str.strip() != "take profit"].copy()

# 4. Počty obchodov
total_trades = len(df)
profit_trades = len(df_profit)
non_profit_trades = len(df_non_profit)

print(f"\nCelkový počet obchodov: {total_trades}")
print(f"Počet profitabilných obchodov: {profit_trades}")
print(f"Počet neprofitabilných obchodov: {non_profit_trades}")

# 5. Rozsahy všetkých obchodov (od-do)
print("\nRozsahy všetkých obchodov:")
for col in numeric_cols:
    col_data = pd.to_numeric(df[col], errors='coerce').dropna()
    print(f"{col}: {int(col_data.min())}-{int(col_data.max())}")

# 6. Funkcia na binovanie
def create_bins(series, step):
    min_val = math.floor(series.min() / step) * step
    max_val = math.ceil(series.max() / step) * step
    bins = list(range(min_val, max_val + step, step))
    return pd.cut(series, bins=bins)

# Pomocná funkcia na prevod intervalu do "x-y" formátu
def interval_to_string(interval):
    return f"{int(interval.left)}-{int(interval.right)}"

# 7. Binovanie pre všetky sety (df, profit, non-profit)
steps = [1000, 2000, 500, 5]
for df_set in [df, df_profit, df_non_profit]:
    for col, step in zip(numeric_cols, steps):
        df_set[f"{col} Bin"] = create_bins(pd.to_numeric(df_set[col], errors='coerce').dropna(), step)

# 8. Presné názvy stĺpcov binov
bin_cols = [f"{col} Bin" for col in numeric_cols]

# 9. Vypočítame všetky kombinácie a ich profitabilitu
all_combos = df.groupby(bin_cols, observed=True).size().reset_index(name='total_count')

all_combos['profit_count'] = all_combos.apply(
    lambda row: df_profit[
        (df_profit[bin_cols[0]] == row[bin_cols[0]]) &
        (df_profit[bin_cols[1]] == row[bin_cols[1]]) &
        (df_profit[bin_cols[2]] == row[bin_cols[2]]) &
        (df_profit[bin_cols[3]] == row[bin_cols[3]])
    ].shape[0], axis=1
)

all_combos['non_profit_count'] = all_combos.apply(
    lambda row: df_non_profit[
        (df_non_profit[bin_cols[0]] == row[bin_cols[0]]) &
        (df_non_profit[bin_cols[1]] == row[bin_cols[1]]) &
        (df_non_profit[bin_cols[2]] == row[bin_cols[2]]) &
        (df_non_profit[bin_cols[3]] == row[bin_cols[3]])
    ].shape[0], axis=1
)

# 10. Vyberieme kombináciu s najlepším pomerom profitabilných > neprofitabilných
best_combo = all_combos[all_combos['profit_count'] > all_combos['non_profit_count']]
best_combo = best_combo.sort_values(by='profit_count', ascending=False).iloc[0]

# 11. Výpis výsledku
print("\nNajlepšia kombinácia binov (profit > non-profit):")
for col in numeric_cols:
    print(f"{col}: {interval_to_string(best_combo[f'{col} Bin'])}")

print(f"Počet profitabilných obchodov: {best_combo['profit_count']}")
print(f"Počet neprofitabilných obchodov: {best_combo['non_profit_count']}")
print(f"Celkový počet obchodov v tejto kombinácii: {best_combo['total_count']}")

