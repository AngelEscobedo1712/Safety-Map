import streamlit as st
import datetime
import requests
import folium
from google.cloud import bigquery

# Create a BigQuery client
client = bigquery.Client()

# Define BigQuery project ID, dataset ID, and table ID
project_id = "lucky-rookery-385417"
dataset_id = "safety_map_new"
table_id = "data_preprocessed"
column_name = "alcaldia_colonia"

# Construct the BigQuery table reference
table_ref = client.dataset(dataset_id).table(table_id)
# Query to retrieve the column data







# safety_map front

st.markdown("""
    # Mexico City - Safety Map

    ## Be not part of the statistics

    As much we are loving CDMX we are aware of the fact that it is not the safest place on earth. Therefore we want to provide you
    with a safety map for this amazing city. The intention of our idea is to give you a clear overview of the neighborhoods where you
    eat tacos and trink mezcal tranquilito and where better not to go.



    Our data data includes all registered crimes in Colonias of CDMX from  **2019 to 2023**

    To be transparent from the beginning you can find the data for our project public available [here](https://datos.cdmx.gob.mx/dataset/victimas-en-carpetas-de-investigacion-fgj#:~:text=Descargar-,V%C3%ADctimas%20en%20Carpetas%20de%20Investigaci%C3%B3n%20(completa),-CSV)

""")

###add map

st.title("Historical crime data")

map =folium.Map(location=[19.4326, -99.1332], zoom_start=11, tiles= 'Stamen Toner')


###add drop downs

#select year
year = ['2019', '2020', '2021', '2022', '2023']

selected_option = st.selectbox('Select a year:', year)


#select month
months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"]

selected_option = st.selectbox('Select a month:', months)



##select colonia (names queried from Big Query)
query = f"SELECT DISTINCT {column_name} FROM `{project_id}.{dataset_id}.{table_id}`"
# Execute the query and fetch the results
query_job = client.query(query)
rows = query_job.result()
# Extract the column values into a Python list
colonias = [row[column_name] for row in rows]

selected_option = st.selectbox('Select a Colonia:', colonias)

##select crime
crime = ['Burglary', 'Danger of well being','Domestic violence','Fraud','Homicide','Property damage',
         'Robbery with violence','Robbery without violence','Sexual crime'
]
selected_option = st.selectbox('Select a Crime:', crime)


folium_map = map._repr_html_()
st.components.v1.html(folium_map, width=700, height=500)
