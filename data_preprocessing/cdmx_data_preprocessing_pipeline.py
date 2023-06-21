import pandas as pd
import json

def download_data():
    url = 'https://storage.googleapis.com/safetymap/data_new_cats.csv'
    clean_data = pd.read_csv(url)
    return clean_data

data = download_data()

data['alcaldia_colonia'] = data['alcaldia_hechos'].str.cat(data['colonia_datos'], sep=' || ')

#add year/month colum
data['año_mes_hecho'] = pd.to_datetime(data['FechaHecho']).dt.to_period('M')

#drop uncessary columns
data.drop(columns=['Año_hecho', 'Mes_hecho', 'FechaHecho', 'HoraHecho', 'alcaldia_hechos', 'colonia_datos'], inplace=True)

#group by Category and Colonia
grouped_df = data.groupby(['año_mes_hecho', 'Categoria', 'alcaldia_colonia']).size().reset_index(name='count')

#Change dtype
grouped_df['año_mes_hecho'] = grouped_df['año_mes_hecho'].astype(str)

grouped_df['año_mes_hecho'] = pd.to_datetime(grouped_df['año_mes_hecho'], format='%Y-%m')

#create a df with the complete date range
complete_dates= pd.date_range(start=grouped_df['año_mes_hecho'].min(), end = grouped_df['año_mes_hecho'].max(), freq = 'MS')

# Create all combinations of dates and colonia dates
idx = pd.MultiIndex.from_product([grouped_df['alcaldia_colonia'].unique(), complete_dates, grouped_df['Categoria'].unique()], names=['alcaldia_colonia', 'año_mes_hecho', 'Categoria'])
complete_df = pd.DataFrame(index=idx).reset_index()

#merge combinations with actual data
colonias_date_complete_df = complete_df.merge(grouped_df, how='left', on=['alcaldia_colonia', 'año_mes_hecho', 'Categoria'])


#replace NaNs by 0
colonias_date_complete_df['count'].fillna(0, inplace=True)


#Create A column for every crime category
columns_colonias_date_complete_df = colonias_date_complete_df.pivot_table('count', ['alcaldia_colonia', 'año_mes_hecho'], 'Categoria')
columns_colonias_date_complete_df.reset_index(inplace=True)
columns_colonias_date_complete_df.columns.names = ['Index']

#Create unique IDs for each colonia
columns_colonias_date_complete_df['colonia_id'] = pd.factorize(columns_colonias_date_complete_df['alcaldia_colonia'])[0] + 1

#create a dictionary with the ids for each colonia which we are going to use from now on
codes, uniques = pd.factorize(columns_colonias_date_complete_df['alcaldia_colonia'].unique())

codes += 1
colonia_id_dict = dict(zip(uniques, codes))


#Convert floats to integer

columns_to_convert =['burglary', 'danger of well-being',
       'domestic violence', 'fraud', 'homicide', 'property damage',
       'robbery with violence', 'robbery without violence', 'sexual crime',
       'threats']
columns_colonias_date_complete_df[columns_to_convert] = columns_colonias_date_complete_df[columns_to_convert].astype(int)

columns_colonias_date_complete_df
