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
