# Trade Reconciliation — Solution

This repository contains the solution for the trade reconciliation exercise.

## Included Files

- `Trade Reconciliation — Juan Carvajal.ipynb`: Notebook with the reconciliation code and analysis.
- `clearer_trade_data.xlsx`: Excel file with data required for reconciliation.
- `internal_trade_data.xlsx`: Excel file with data required for reconciliation.
- `result_trade_reconciliation.csv`: Output file generated after running the code.

## Solution Overview

The goal of this exercise was to reconcile trade data from two different sources. The approach taken was:

- Load both Excel files using pandas.
- Clean and preprocess the data to ensure consistent formats.
- Match trades based on key identifiers (such as trade IDs, dates, and amounts).
- Identify discrepancies and generate a reconciliation report.
- Save the final result as `result_trade_reconciliation.csv`.

The notebook contains detailed steps, explanations, and code to reproduce the reconciliation.

## Requirements to Run the Code

To run the notebook successfully, you need:

1. Python installed (recommended Python 3.7 or higher).
2. Jupyter Notebook or JupyterLab installed.
3. Required libraries installed, which you can install with:

```bash
pip install pandas openpyxl

