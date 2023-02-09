import pandas as pd
from pathlib import Path

base_path = f'{Path.home()}/Databases/LOCALIDADES/'
path_locals = base_path + 'localidades.csv.gzip'
path_procs = 'data/procs.csv'

df_procs = pd.read_csv(path_procs)
df = pd.read_csv(path_locals)

df['nome'] = df.apply(
  lambda row: f"{row['nome_municipio']} ({row['uf']})", axis=1)

for ref in ['origem', 'destino']:
  col = f'{ref}_nomeclatura'
  df_nomec = df_procs[[col]]
  df_nomec = df_nomec.merge(
    right=df,
    left_on=f'{ref}_nomeclatura',
    right_on='nomeclatura',
    how='left',
  )
  df_procs[f'{ref}_nome'] = df_nomec['nome']

cols_order = [
  'origem', 'destino', 'origem_nomeclatura', 'destino_nomeclatura',
  'origem_nome', 'destino_nome', 'procedimento', 'ano', 'km (osm)', 'min (osm)', 'criticidade', 'capitais',
  'socioecon', 'origem_latitude', 'origem_longitude', 'destino_latitude',
  'destino_longitude', 'count']

df_procs = df_procs[cols_order]

# df_procs.to_csv(path_procs, float_format='%.4f', index=False)

