"""Main introduction.

Show the network plot.
"""


import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st


st.title("Trajectory by pregnant women for delivery care under Brazil's Unified Health System (SUS)")


path_procs = 'data/procs.csv.gzip'
df_procs = pd.read_csv(path_procs)


years = st.multiselect(
  'Ano',
  sorted(df_procs['ano'].unique()),
  [2018, 2019],
)

procs = st.multiselect(
  'Procedimentos',
  sorted(df_procs['procedimento'].unique()),
  ['C_', 'N_'],
)

critic = st.multiselect(
  'Criticidade',
  sorted(df_procs['criticidade'].unique()),
  [1, 2],
)

capitais = st.multiselect(
  'Capitais',
  sorted(df_procs['capitais'].unique()),
  ['0_1'],
)

socioecon = st.multiselect(
  'Socioeconômico',
  sorted(df_procs['socioecon'].unique()),
  ['1_5', '2_5', '3_5', '1_4', '2_4', '3_4'],
)

@st.cache
def load_network(years, procs):
  df_procs = pd.read_csv(path_procs)
  df_procs = df_procs[(
      df_procs['ano'].isin(years)
    ) & (
      df_procs['procedimento'].isin(procs)
    ) & (
      df_procs['criticidade'].isin(critic)
    ) & (
      df_procs['capitais'].isin(capitais)
    ) & (
      df_procs['socioecon'].isin(socioecon)
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
    data=load_network(years, procs),
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
  {origem_nomeclatura} >> {destino_nomeclatura}
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