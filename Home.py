"""Main introduction.

Show the network plot.
"""


import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st


st.title("The trajectory by pregnant women for delivery care under Brazil's Unified Health System (SUS)")


path_procs = 'data/procs.csv'
# path_procs ='https://raw.githubusercontent.com/lucaslopes/parturient-trajectory/data/data/procs.csv'


col_year, col_critic, col_capital = st.columns([2, 3, 3])
col_proc, col_socioecon = st.columns([2, 1])


with col_year:
  years = st.selectbox(
    'Ano',
    ('2010-2019', '2010-2011', '2018-2019'),
    index=0)


with col_proc:
  procs = st.multiselect(
    'Procedimentos',
    ['C_', 'C_L', 'C_R', 'N_', 'N_C', 'N_R'],
    ['C_', 'N_'])


with col_critic:
  options = range(1, 5)
  critic = st.multiselect(
    'Criticidade',
    options, options)


with col_capital:
  options = ['0_1', '==', '1_0']
  capitais = st.multiselect(
    'Capitais',
    options, options)


with col_socioecon:
  options = ['<', '=', '>']
  socioecon = st.multiselect(
    'Socioeconômico',
    options, options)


@st.cache
def load_network(years, procs, critic, capitais, socioecon):
  y1, y2 = years.split('-')
  
  if '==' in capitais:
    caps = [c for c in capitais if c != '==']
    caps.extend(['1_1', '0_0'])
  else:  
    caps = capitais.copy()
  
  secon = {
    '>' : [f'{r}_{h}' for r in range(1,6) for h in range(1, 6) if r > h],
    '=' : [f'{r}_{h}' for r in range(1,6) for h in range(1, 6) if r == h],
    '<' : [f'{r}_{h}' for r in range(1,6) for h in range(1, 6) if r < h]}
  secons = list()
  for se in socioecon:
    secons.extend(secon[se])
  
  df_procs = pd.read_csv(path_procs)
  df_procs = df_procs[(
      df_procs['ano'].isin(range(int(y1), int(y2)))
    ) & (
      df_procs['procedimento'].isin(procs)
    ) & (
      df_procs['criticidade'].isin(critic)
    ) & (
      df_procs['capitais'].isin(caps)
    ) & (
      df_procs['socioecon'].isin(secons)
  )]
  
  df_procs = df_procs.drop(['ano', 'procedimento'], axis=1)
  df_procs = df_procs.groupby(
    by=list(df_procs.columns[:-1]), as_index=False).sum()
  df_procs['size'] = np.interp(
    df_procs['count'],
    [0, df_procs['count'].max()],
    [0, 1])
  df_procs['size'] = 2 ** df_procs['size']
  df_procs['size'] = np.interp(
    df_procs['size'],
    [1, df_procs['size'].max()],
    [.02, 20])
  
  return df_procs


# Define a layer to display on a map
layer = pdk.Layer(
  'ArcLayer',
  data=load_network(years, procs, critic, capitais, socioecon),
  get_width='size',
  get_source_position=['origem_longitude', 'origem_latitude'],
  get_target_position=['destino_longitude', 'destino_latitude'],
  get_source_color=[4, 167, 89, 255],
  get_target_color=[255, 204, 40, 255],
  pickable=True,
  auto_highlight=True,
)


# Set the viewport location
view_state = pdk.ViewState(latitude=-15, longitude=-55, zoom=3)


tooltip_text = """{count} Parturiente(s)
  {origem_nome} >> {destino_nome}
  {km (osm)} km (osm) & {min (osm)} min (osm)
  Criticidade: {criticidade}
  Socioeconômico: {socioecon}
  Capitais: {capitais}
"""


# Render
r = pdk.Deck(
  layers=[layer],
  initial_view_state=view_state,
  tooltip={'text': tooltip_text},)
r.picking_radius = 10
st.pydeck_chart(r)


st.write('Network plot. municipios são nós, arestas representam deslocamente entre municipios, peso é distancia * tempo * procedimenotos, infos em cada aresta informa esses valores individualmente')

