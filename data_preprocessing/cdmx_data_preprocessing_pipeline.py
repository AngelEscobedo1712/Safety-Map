import numpy as np
import pandas as pd


def download_data():
    url = 'https://storage.googleapis.com/safety-map-model/clean_data.csv'
    clean_data = pd.read_csv(url)
    return clean_data


print("Data was succesfully downloaded")
clean_data = download_data()

clean_data['Date'] = pd.to_datetime(clean_data['Date'])

clean_data['year_month'] = clean_data['Date'].dt.strftime('%Y-%m')

clean_data.drop(columns= 'Date')

#group by Category and Colonia
grouped_df = clean_data.groupby(['year_month', 'Category', 'Neighborhood']).size().reset_index(name='Count')
grouped_df['year_month'] = pd.to_datetime(grouped_df['year_month'], format='%Y-%m')

#create a df with the complete date range
complete_dates= pd.date_range(start=grouped_df['year_month'].min(), end = grouped_df['year_month'].max(), freq = 'MS')

grouped_df['year_month'] = pd.to_datetime(grouped_df['year_month'], format='%Y-%m')

#create a df with the complete date range
complete_dates= pd.date_range(start=grouped_df['year_month'].min(), end = grouped_df['year_month'].max(), freq = 'MS')

# Create all combinations of dates and colonia dates
idx = pd.MultiIndex.from_product([grouped_df['Neighborhood'].unique(), complete_dates, grouped_df['Category'].unique()], names=['Neighborhood', 'year_month', 'Category'])
complete_df = pd.DataFrame(index=idx).reset_index()

#merge combinations with actual data
colonias_date_complete_df = complete_df.merge(grouped_df, how='left', on=['Neighborhood', 'year_month', 'Category'])

#replace NaNs by 0
colonias_date_complete_df['Count'].fillna(0, inplace=True)

#Create A column for every crime category
columns_colonias_date_complete_df = colonias_date_complete_df.pivot_table('Count', ['Neighborhood', 'year_month'], 'Category')
columns_colonias_date_complete_df.reset_index(inplace=True)
columns_colonias_date_complete_df.columns.names = ['Index']

#Create unique IDs for each colonia
columns_colonias_date_complete_df['Neighborhood_ID'] = pd.factorize(columns_colonias_date_complete_df['Neighborhood'])[0] + 1

#create a dictionary with the ids for each colonia which we are going to use from now on
codes, uniques = pd.factorize(columns_colonias_date_complete_df['Neighborhood'].unique())

codes += 1
colonia_id_dict = dict(zip(uniques, codes))

#Convert floats to integer

columns_to_convert =['burglary', 'danger of well-being',
       'domestic violence', 'fraud', 'homicide', 'property damage',
       'robbery with violence', 'robbery without violence', 'sexual crime',
       'threats']
columns_colonias_date_complete_df[columns_to_convert] = columns_colonias_date_complete_df[columns_to_convert].astype(int)


columns_colonias_date_complete_df.to_csv('/Users/pieterdietrich/code/AngelEscobedo1712/Safety-Map/Clean and Preprocessed Data/preprocessed_data.csv', index=False)


print('preprocessed_data was downloaded')
