import pandas as pd
path = 'datasets/plz_einwohner.xlsx'
try:
    raw = pd.read_excel(path, sheet_name='T5', header=None, engine='openpyxl')
    for i in range(0,20):
        print(i, raw.iloc[i].tolist())
except Exception as e:
    print('ERROR', e)
