import pandas as pd

# === Step 1: Load the Excel files
internal = pd.read_excel("internal_trade_data.xlsx")
clearer = pd.read_excel("clearer_trade_data.xlsx")

# === Step 2: Identify and extract Q225 contract
q225 = internal[(internal['contract_type'] == 'Outright Quarter') & (internal['contract_period'] == 'Q225')]
monthly = internal[internal['contract_type'] != 'Outright Quarter'].copy()

# === Step 3: Rename monthly period
monthly.rename(columns={'contract_period': 'month'}, inplace=True)

# === Step 4: Aggregate monthly internal trades
internal_agg = monthly.groupby('month').agg(
    internal_qty=('quantity_mwh', 'sum'),
    internal_price=('price_eur_per_mwh', 'mean')
).reset_index()

# === Step 5: Create Q225 breakdown
if not q225.empty:
    q225_qty = q225.iloc[0]['quantity_mwh']
    q225_price = q225.iloc[0]['price_eur_per_mwh']
    q225_months = ['2025-04', '2025-05', '2025-06']
    
    q225_df = pd.DataFrame({
        'month': q225_months,
        'from_Q225_qty': [q225_qty] * 3,
        'Q225_price': [q225_price] * 3
    })
else:
    q225_df = pd.DataFrame(columns=['month', 'from_Q225_qty', 'Q225_price'])

# === Step 6: Merge internal with Q225
merged = pd.merge(internal_agg, q225_df, on='month', how='outer')

# === Step 7: Handle June alias
merged['month'] = merged['month'].replace({'2025-06': '2025-06 (Q225)'})

# === Step 8: Fill missing values
merged['internal_qty'] = merged['internal_qty'].fillna(0)
merged['from_Q225_qty'] = merged['from_Q225_qty'].fillna(0)
merged['internal_price'] = merged['internal_price'].ffill()

# === Step 9: Prepare clearer data
clearer.rename(columns={
    'delivery_month': 'month',
    'quantity_mwh': 'clearer_qty',
    'price_eur_per_mwh': 'clearer_price'
}, inplace=True)

# === Step 10: Merge all
final = pd.merge(merged, clearer, on='month', how='outer')

# === Step 11: Fill missing
final['internal_qty'] = final['internal_qty'].fillna(0)
final['from_Q225_qty'] = final['from_Q225_qty'].fillna(0)
final['clearer_qty'] = final['clearer_qty'].fillna(0)
final['internal_price'] = final['internal_price'].fillna(0)
final['clearer_price'] = final['clearer_price'].fillna(0)

# === Step 12: Calculate diffs and checks
final['total_internal'] = final['internal_qty'] + final['from_Q225_qty']
final['qty_diff'] = final['total_internal'] - final['clearer_qty']
final['qty_match'] = final.apply(lambda r: '✅' if abs(r['qty_diff']) < 1e-6 else '❌', axis=1)

def match_price(row):
    return '✅' if abs(row['internal_price'] - row['clearer_price']) < 0.01 else '❌'

final['price_diff'] = final['internal_price'] - final['clearer_price']
final['price_match'] = final.apply(match_price, axis=1)

# === Step 13: Round for presentation
cols_to_round = ['internal_price', 'clearer_price', 'qty_diff', 'price_diff']
final[cols_to_round] = final[cols_to_round].round(2)

# === Final Display Table
output = final[['month', 'internal_qty', 'from_Q225_qty', 'clearer_qty',
                'qty_match', 'qty_diff', 'internal_price',
                'clearer_price', 'price_match', 'price_diff']]

print(output.to_string(index=False))

