# -*- coding: utf-8 -*-
"""Getting BP, DRE E DFC DA CVM

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15to2Bijxp2IBCXaqwuWgH6D3tUxZTh3g

# Libraries
"""

!pip install wget
import numpy as np
import pandas as pd
import wget
from zipfile import ZipFile
from google.colab.data_table import DataTable
import plotly.graph_objects as go

"""# Variables"""

# I opened the site and saw that all companys are clustered together on zip files annually
url_base = 'http://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/'

arquivos_zip = []
# made a loop to get all zip files years available
for ano in range(2010,2022):
  arquivos_zip.append(f'dfp_cia_aberta_{ano}.zip')

arquivos_zip

#downloaded the zip file with wget
for arq in arquivos_zip:
  wget.download(url_base+arq)

for arq in arquivos_zip:
  ZipFile(arq, 'r').extractall('CVM')

!mkdir DADOS_DFP

#performing loop through the zip files, building .csv and compiling by type.
nomes = ['BPA_con', 'BPA_ind','BPP_con','BPP_ind','DFC_MD_con','DFC_MD_ind','DFC_MI_con','DFC_MI_ind','DMPL_con','DMPL_ind','DRE_con','DRE_ind','DVA_con','DVA_ind']
for nome in nomes:
  arquivo = pd.DataFrame()
  for ano in range(2010,2022):
    arquivo = pd.concat([arquivo,pd.read_csv(f'/content/CVM/dfp_cia_aberta_{nome}_{ano}.csv', sep=';', decimal=',', encoding='ISO-8859-1')])
  arquivo.to_csv(f'DADOS_DFP/dfp_cia_aberta_{nome}_2010-2021.csv', index = False)

dre = pd.read_csv('/content/DADOS_DFP/dfp_cia_aberta_DRE_ind_2010-2021.csv')

dre = dre[dre['ORDEM_EXERC'] == "ÚLTIMO"]

dre.head(3)

# build a datatable with CVM code and enterprise name for easy access and recognition.
empresas = dre[['DENOM_CIA','CD_CVM']].drop_duplicates().set_index('CD_CVM')
DataTable(empresas)

empresa = dre[dre['CD_CVM'] == 20257]

empresa.head()

#those are the acounts on income statement
DataTable(empresa[['CD_CONTA', 'DS_CONTA']].drop_duplicates().set_index('CD_CONTA'))

conta = empresa[empresa['CD_CONTA'] == '3.99.02.01']
conta.head()

conta.index = pd.to_datetime(conta['DT_REFER'])
conta.head()

"""***BUILDING P/E RATIO***"""

!pip install yfinance
import yfinance as yf

prices = yf.download('TAEE11.SA', start='2012-01-01')[['Adj Close','Close']]

prices

indicadores = prices.join(conta['VL_CONTA'], how='outer')

indicadores.rename({'VL_CONTA':'LPA'}, axis=1, inplace = True)

indicadores.fillna(method='ffill', inplace=True)
indicadores.dropna(inplace=True)

# Comparing the close price and adjusted close price from yahoo finance api
indicadores['PL'] = indicadores['Close']/indicadores['LPA']
indicadores['PL_Ajustado'] = indicadores['Adj Close']/indicadores['LPA']
indicadores

fig = go.Figure()
fig.add_trace(go.Scatter(x=indicadores.index, y=indicadores['PL'], name = 'PL'))
fig.add_trace(go.Scatter(x=indicadores.index, y=indicadores['PL_Ajustado'], name = 'PL_Ajustado'))
fig.add_trace(go.Scatter(x=indicadores.index, y=indicadores['Close'], name = 'TAEE11'))
fig.add_trace(go.Scatter(x=indicadores.index, y=indicadores['Adj Close'], name = 'TAEE11_Ajustado'))

"""## Results

The graph shows this abrupt jumps and falls because of high LPA paid compared to previous period.
"""