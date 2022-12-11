from src.db import db
import pandas as pd
import numpy as np

# 1. setup database
print("\n\n1. setup database, please create database and setup config/database.ini")
## 1.1 create database
## 1.2 setup data base in src/database.ini

# 2. scraping stock data
## by using command command python3 src/stockData.py
print('\n\n2. scraping stock data, please use run "python3 src/stockdata.py"')

# 3. read data
print("\n\n3. read data")
rows = db().read("select * from public.aktien_daten")
i = 0
data = []
for row in rows:
    if row is not None:
        data.append(np.array(row))
        i = i+1
df = pd.DataFrame(data, columns=['name','wkn','land','branche','year','waehrung','kurse','umsatz','ebit','ebt','ergebnis_n_steuer','eigenkapital','gesamtkapital','ergebnis_je_aktie','dividend_je_aktie','umsatz_je_aktie','buchwert_je_aktie','cashflow_je_aktie','bilanzsumme_je_aktie','kgv','kuv','kbv','kcv','dividendenrendite','gewinnrendite','eigenkapitalrendite','umsatzrendite','roi'])
# print(df.head())
print(df.describe())

# 4. clean data
print("\n\n4. clean data")
## 4.1. delete constant data -> name, wkn, etc, except: land, branch, kernzahlen, rendite
df=df.drop(['name','wkn','waehrung','ebit','ebt','ergebnis_n_steuer','eigenkapital','gesamtkapital','ergebnis_je_aktie','dividend_je_aktie','umsatz_je_aktie','buchwert_je_aktie','cashflow_je_aktie','bilanzsumme_je_aktie'],axis=1)
print(df.head())

# 5.prepare data
print("\n\n5. prepare date")

## 5.1. calculate profit after 1 year unis kurse
print("5.1 calculate prifit")
profit = []
for i in range(0,len(df)-1):
    if df.iloc[i,0] == df.iloc[i+1,0]:
        profit.append(float(df.iloc[i+1,3])/float(df.iloc[i,3])-1)
    else:
        profit.append(None)
profit.append(None)
df['profit'] = profit
df = df[df.profit.notnull()]
df=df.drop('kurse',axis=1)
print(df.head())

## 5.2. reduce unique data by scaling data from 0 to 1 with scale width 0.1 result to 10 unique data
print("reduce unique by scaling data")

