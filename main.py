from src.db import db
import pandas as pd
import numpy as np

db = db()

rows = db.read("select * from public.aktien_daten")
i = 0
data = []
for row in rows:
    if row is not None:
        data.append(np.array(row))
        i = i+1
# print(data)
dataset = pd.DataFrame(data, columns=['name','wkn','land','branche','year','waehrung','kurse','umsatz','ebit','ebt','ergebnis_n_steuer','eigenkapital','gesamtkapital','ergebnis_je_aktie','dividend_je_aktie','umsatz_je_aktie','buchwert_je_aktie','cashflow_je_aktie','bilanzsumme_je_aktie','kgv','kuv','kbv','kcv','dividendenrendite','gewinnrendite','eigenkapitalrendite','umsatzrendite','roi'])
print(dataset.head())
print(dataset.describe())

