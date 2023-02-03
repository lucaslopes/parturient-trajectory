"""Análise de Tendência

Tendência dos casos que tiveram que se deslocar do município de residência, dentro do estado do RJ, considerando a porcentagem dos casos de deslocamento dividido por todos os partos ano a ano de 2010 a 2019 com 3 linhas: total, normal e cesárea.
"""

import streamlit as st
import pandas as pd
import plotly.express as px


def group_df(df):
  return df.groupby(
    by=list(df.columns)[:-1],
    as_index=False,
  ).sum()

def sort_df(df: pd.DataFrame):
  return df.sort_values(
    by=list(df.columns)[:-1],
  ).reset_index(drop=True)


path_procs = 'data/procs.csv'
df = pd.read_csv(path_procs)

filtro_parto = df['procedimento'].isin(['N_', 'C_'])
flt_orig = df['origem_nomeclatura'].str.contains('/RJ/')
flt_dest = df['destino_nomeclatura'].str.contains('/RJ/')

cols = [
  'ano',
  'procedimento',
  'criticidade',
  'count',
]

df = df[filtro_parto & flt_orig][cols]# & flt_dest][cols]
df['criticidade'] = df['criticidade'] > 0

df_ambos = df.copy()
df_ambos['procedimento'] = 'N&C'
df = pd.concat([df, df_ambos])

df_total = df.copy()
df_critic = df[df['criticidade'] == True]

for df in [df_critic, df_total]:
  df.drop(['criticidade'], axis=1, inplace=True)

df_total = group_df(df_total)
df_critic = group_df(df_critic)

df = pd.merge(
  left=df_total,
  right=df_critic,
  how='left',
  on=list(df_total.columns)[:-1],
  suffixes=['_total', '_critic'],
)

df = sort_df(df)
df['percent'] = df['count_critic'] /  df['count_total']

st.dataframe(df)

fig = px.scatter(
    data_frame=df,
    x='ano',
    y='percent',
    color='procedimento',
    # range_y=[0, .5],
    log_y=True,
    trendline="ols"
  )

results = px.get_trendline_results(fig)
info = results.px_fit_results.iloc[0].summary()

st.plotly_chart(fig)
st.write(info)

