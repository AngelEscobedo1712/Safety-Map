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
                  'fgj_colonia_registro', 'municipio_hechos']

data = data.drop(columns_to_drop, axis=1)

## DATA CLEANING

# Remove duplicate rows
data = data.drop_duplicates()


# Remove Ano Hecho below 2019
data = data[data["Año_hecho"] > 2018]


# Remove age higher than 100 and replace all missing ages by mean age
data['Edad'] = np.where(data['Edad'] > 100, np.nan, data['Edad'])

data['Edad'] = np.where(data['Edad'].isna(), data["Edad"].mean(), data['Edad'])


# Create Unknown gender category
data['Sexo'] = np.where(data['Sexo'].isna(), "Unknown", data['Sexo'])

# Very few gender unknowns, would drop


# Assign missing latitude and longitude, set wrong longitudes to 0
data['latitud'] = np.where(data['latitud'].isna(), 0, data['latitud'])

data['longitud'] = np.where(data['longitud'].isna(), 0, data['longitud'])

data['longitud'] = np.where(data['longitud'] == data["latitud"], 0, data['longitud'])
