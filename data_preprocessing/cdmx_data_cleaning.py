import numpy as np
import pandas as pd


url = "https://archivo.datos.cdmx.gob.mx/fiscalia-general-de-justicia/victimas-en-carpetas-de-investigacion-fgj/da_victimas_completa_marzo_2023.csv"
data_cdmx = pd.read_csv(url)


#sort out delicts that happened outside of cdmx
boolean_mask = data_cdmx['municipio_hechos'].isnull()
data = data_cdmx[boolean_mask].reset_index(drop=True)

#sort out crimes that were not commited against persons but companies
boolean_mask = data['TipoPersona'] == 'FISICA'
data = data[boolean_mask].reset_index(drop=True)

#columns to drop
columns_to_drop = ['idCarpeta', 'Año_inicio', 'Mes_inicio', 'FechaInicio',
                   'CalidadJuridica', 'HoraInicio',
                  'fgj_colonia_registro', 'municipio_hechos',
                  'TipoPersona', 'competencia','HoraHecho'
                  ]

data = data.drop(columns_to_drop, axis=1)

## DATA CLEANING

# Remove duplicate rows
data = data.drop_duplicates()


# Remove Ano Hecho below 2019
data = data[data["Año_hecho"] > 2018]


# Remove age higher than 100 and replace all missing ages by mean age
data['Edad'] = np.where(data['Edad'] > 100, np.nan, data['Edad'])

data['Edad'] = np.where(data['Edad'].isna(), data["Edad"].mean(), data['Edad'])


# Remove rows with missing gender
data = data[data["Sexo"].notna()]


# Assign missing latitude and longitude, set wrong longitudes to 0
data['latitud'] = np.where(data['latitud'].isna(), 0, data['latitud'])

data['longitud'] = np.where(data['longitud'].isna(), 0, data['longitud'])

data['longitud'] = np.where(data['longitud'] == data["latitud"], 0, data['longitud'])


#dataset to clasify according to new defined categories
new_cats = pd.read_csv('/Users/pieterdietrich/code/eldiepi/safety_map/data/new_categories4.csv')

#renaming of the columns
new_cats.rename(columns={"Unnamed: 0": "Delito", "Unnamed: 1": "new_cats"},inplace=True)

data_new_cats = pd.merge(data, new_cats,how='left', on='Delito')

#droping the raws with 'ignore' category
boolean_mask = data_new_cats['new_cats'] != 'ignore'
data_new_cats = data_new_cats[boolean_mask].reset_index(drop=True)

#Drop old Category and delict columns
data_new_cats.drop(columns=['Categoria', 'Delito'], axis=1, inplace=True)


data_new_cats.rename(columns={"new_cats": "Category",
                              "Año_hecho": "Year",
                              "Sexo": "Sex",
                              "Edad": "Age",
                              "Mes_hecho": "Month",
                              "latitud": "Latitude",
                              "longitud": "Longitude",
                              "FechaHecho": "Date"
                              },inplace=True)

data_new_cats['Neighborhood'] = data_new_cats['alcaldia_hechos'].str.cat(data_new_cats['colonia_datos'], sep=' || ')

data_new_cats.drop(columns=['alcaldia_hechos', 'colonia_datos'], axis=1, inplace=True)

data_new_cats['Year'] = data_new_cats['Year'].astype(int)

clean_data = data_new_cats

clean_data.to_csv('/Users/pieterdietrich/code/AngelEscobedo1712/Safety-Map/Clean and Preprocessed Data/clean_data.csv', index=False)


print('finish')
