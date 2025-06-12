import pandas as pd

# === Step 1: Load the Excel files
internal = pd.read_excel("internal_trade_data.xlsx")
clearer = pd.read_excel("clearer_trade_data.xlsx")

# === Step 2: Separate quarterly contract and monthly contracts
q225 = internal[(internal['contract_type'] == 'Outright Quarter') & (internal['contract_period'] == 'Q225')]
monthly = internal[internal['contract_type'] != 'Outright Quarter'].copy()

# === Step 3: Rename monthly 'contract_period' column to 'month' for clarity
monthly.rename(columns={'contract_period': 'month'}, inplace=True)

# === Step 4: Decompose Q225 quarterly contract into monthly legs
if not q225.empty:
    q225_qty = q225.iloc[0]['quantity_mwh']
    q225_price = q225.iloc[0]['price_eur_per_mwh']
    q225_months = ['2025-04', '2025-05', '2025-06']

    # Distribute quantity and price equally across the three months
    q225_monthly = pd.DataFrame({
        'month': q225_months,
        'quantity_mwh': [q225_qty / 3] * 3,
        'price_eur_per_mwh': [q225_price] * 3
    })
else:
    q225_monthly = pd.DataFrame(columns=['month', 'quantity_mwh', 'price_eur_per_mwh'])

# === Step 5: Combine monthly outright trades and decomposed Q225 trades
monthly_all = pd.concat([monthly[['month', 'quantity_mwh', 'price_eur_per_mwh']], q225_monthly], ignore_index=True)

# === Step 6: Aggregate combined internal trades by month
internal_agg = monthly_all.groupby('month').apply(
    lambda x: pd.Series({
        'internal_qty': x['quantity_mwh'].sum(),
        'internal_price': 0 if x['quantity_mwh'].sum() == 0 else (x['quantity_mwh'] * x['price_eur_per_mwh']).sum() / x['quantity_mwh'].sum()
    })
).reset_index()

# === Step 7: Prepare clearer data (rename columns)
clearer.rename(columns={
    'delivery_month': 'month',
    'quantity_mwh': 'clearer_qty',
    'price_eur_per_mwh': 'clearer_price'
}, inplace=True)

# === Step 8: Merge internal aggregated data with clearer data on month
final = pd.merge(internal_agg, clearer, on='month', how='outer')

# === Step 9: Fill missing numeric values with 0
final['internal_qty'] = final['internal_qty'].fillna(0)
final['clearer_qty'] = final['clearer_qty'].fillna(0)
final['internal_price'] = final['internal_price'].fillna(0)
final['clearer_price'] = final['clearer_price'].fillna(0)

# === Step 10: Calculate quantity difference and matching check
final['qty_diff'] = final['internal_qty'] - final['clearer_qty']
final['qty_match'] = final['qty_diff'].apply(lambda x: '✅' if abs(x) < 1e-6 else '❌')

# === Step 11: Calculate price difference and matching check
final['price_diff'] = final['internal_price'] - final['clearer_price']
final['price_match'] = final['price_diff'].apply(lambda x: '✅' if abs(x) < 0.01 else '❌')

# === Step 12: Round numerical columns for better readability
cols_to_round = ['internal_price', 'clearer_price', 'qty_diff', 'price_diff']
final[cols_to_round] = final[cols_to_round].round(2)

# === Final output columns selection
output = final[['month', 'internal_qty', 'clearer_qty', 'qty_match', 'qty_diff', 'internal_price', 'clearer_price', 'price_match', 'price_diff']]

print(output.to_string(index=False))

