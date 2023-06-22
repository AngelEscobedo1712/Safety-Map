import streamlit as st
import datetime
import requests
import folium
from google.cloud import bigquery
from streamlit_folium import st_folium

# Create a BigQuery client
client = bigquery.Client()

# Define BigQuery project ID, dataset ID, and table ID
project_id = "lucky-rookery-385417"
dataset_id = "safety_map_new"
table_id = "map_data"
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

##select colonia (names queried from Big Query)
query = f"SELECT DISTINCT {column_name} FROM `{project_id}.{dataset_id}.{table_id}`"
# Execute the query and fetch the results
query_job = client.query(query)
rows = query_job.result()
# Extract the column values into a Python list
colonias = [row[column_name] for row in rows]


###add drop downs
dropdown_values = {
    'year_column': [2019, 2020, 2021, 2022, 2023],
    'month_column': list(range(1, 13)),
    'alcaldia_colonia': colonias,
    'Categoria': ['fraud', 'threats', 'threats', 'burglary', 'homicide',
    'sexual crime', 'property damage', 'domestic violence', 'danger of well-being',
    'robbery with violence', 'robbery without violence']
}



# Collect selected values from the dropdown menus
selected_values = {}
for dropdown_label, dropdown_options in dropdown_values.items():
    selected_values[dropdown_label] = st.selectbox(dropdown_label, dropdown_options)

# Fetch the relevant data from BigQuery based on the selected values
where_conditions = []
for dropdown_label, selected_value in selected_values.items():
    if isinstance(selected_value, str):
        where_conditions.append(f"{dropdown_label} = '{selected_value}'")
    else:
        where_conditions.append(f"{dropdown_label} = {selected_value}")


where_clause = " AND ".join(where_conditions)

# Prepare the parameterized query
query = f"""
    SELECT latitud, longitud
    FROM `{dataset_id}.{table_id}`
    WHERE {where_clause}
"""

# Set query parameters with converted values
query_parameters = [bigquery.ScalarQueryParameter(f"value{i}", "STRING", str(value)) for i, value in enumerate(selected_values.values())]

# Run the query with parameterized values
job_config = bigquery.QueryJobConfig()
job_config.query_parameters = query_parameters
query_job = client.query(query, job_config=job_config)
dataframe = query_job.to_dataframe()

# Create a Folium map
map_center = [dataframe['latitud'].iloc[0], dataframe['longitud'].iloc[0]]
m = folium.Map(location=map_center, zoom_start=10)

# Add markers to the map
for _, row in dataframe.iterrows():
    folium.Marker([row['latitud'], row['longitud']]).add_to(map)

# Display the map
st_folium = st_folium(map, width = 700)
