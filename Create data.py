"""
COVID-19 Wastewater Data Analysis for California

This code script focuses on the analysis of COVID-19 wastewater data in California.
It combines data from the SCAN (Sewage-based Epidemiology for COVID-19) program for various cities
in California and integrates it with Eurofins data. The Eurofins data covers specific cities in
the central valley for the years 2021 and part of 2022. The objective is to create a comprehensive
dataset at the county level, including data from the largest wastewater treatment plant (WWTP)
within each county. This dataset will be utilized to compute the Rt (effective reproduction number)
at the county level.

Author: mdaza
Date: 20 Jul, 2023
"""

import pandas as pd
import numpy as np

# Download data if flag 'donwload' is True, otherwise load from local file
donwload = True
if donwload:
    data_all_ww = pd.read_csv("http://publichealth.verily.com/api/csv")
    data_all_ww.to_csv("data/" + 'data.csv')
else:
    data_all_ww = pd.read_csv("data/data.csv")

# Load additional data from files
data_ww_Eurofins = pd.read_csv("data/data_ww_Eurofins.csv", index_col=False)
county_fips = pd.read_csv("data/county_fips.csv", dtype='object')

# Define a dictionary to map FIPS codes to county names
fips_county = {}
for k in range(len(county_fips['County'])):
    fips_county[county_fips["Fips"].values[k]] = county_fips['County'].values[k]
fips_county["06075, 06081"] = "San Francisco"

# Define a mapping of cities to their respective counties
cities_county = {'Davis': 'Yolo', 'UC Davis': 'Yolo', 'Winters': 'Yolo', 'Woodland': 'Yolo', 'Esparto': 'Yolo',
                 'Los Banos': 'Merced', 'Turlock': 'Stanislaus', 'Modesto': 'Stanislaus', 'Merced': 'Merced',
                 'San Rafael': 'Marin', 'Fairfield': 'Solano', 'Sausalito': 'Marin', 'Lancaster': 'Los Angeles',
                 'Paso Robles': 'San Luis Obispo', 'Martinez': 'Contra Costa', 'Lompoc': 'Santa Barbara',
                 'San Diego': 'San Diego', 'Carson': 'Los Angeles', 'Hollister': 'San Benito',
                 'Richmond': 'Contra Costa', 'Napa': 'Napa', 'Playa Del Rey': 'Los Angeles', 'San Mateo': 'San Mateo',
                 'Novato': 'Marin', 'Gilroy': 'Santa Clara', 'San Jose': 'Santa Clara',
                 'San Francisco, CA': 'San Francisco', 'San Francisco': 'San Francisco', 'Sunnyvale': 'Santa Clara',
                 'Palo Alto': 'Santa Clara', 'Sacramento': 'Sacramento',
                 'Santa Cruz': 'Santa Cruz', 'Petaluma': 'Sonoma', 'San Leandro': 'Alameda', 'Vallejo': 'Solano',
                 'Indio': 'Riverside', 'Union City': 'Alameda', 'Mill Valley': 'Marin', 'Laguna Niguel': 'Orange',
                 'Riverside': 'Riverside', 'Ontario': 'San Bernardino', 'Oakland': 'Alameda',
                 'Half Moon Bay': 'San Mateo', 'Pacifica': 'San Mateo', 'Windsor': 'Sonoma', 'Marina': 'Monterey',
                 'Santa Rosa': 'Sonoma',
                 'CODIGA': 'CODIGA', 'Madera': 'Madera', 'Silicon Valley': 'Silicon Valley'}
# Define a list of counties in California with WWTPs
counties_CA = ['Yolo', 'Merced', 'Stanislaus', 'Marin', 'Solano', 'Los Angeles', 'San Luis Obispo', 'Contra Costa',
               'Santa Barbara', 'San Diego',
               'San Benito', 'Napa', 'San Mateo', 'Santa Clara', 'San Francisco', 'Sacramento', 'Santa Cruz', 'Sonoma',
               'Alameda', 'Riverside', 'Orange',
               'San Bernardino', 'Monterey', 'Madera']

# Define a list of cities in Central Valley monitoring for Eurofins
cities_CVHT = ['Los Banos', 'Merced', 'Modesto', 'Turlock', 'Davis', 'Winters', 'Esparto', 'Woodland']

# Define column names for later use
cols = ['date', 'City', 'Zipcode', 'Population_Served', 'Site_Name', 'SC2_N_norm_PMMoV', 'SC2_N_gc_g_dry_weight',
        'PMMoV_gc_g_dry_weight',"County_FIPS"]
cols_SC2 = ['City', 'date', 'SC2_N_norm_PMMoV', 'SC2_N_gc_g_dry_weight', 'PMMoV_gc_g_dry_weight']

# Define a function to preprocess and filter data for all of California
def data_ww_all_CA():
    "In SCAN data set the data from Davis and uc davis are with the same label in column city, \
    because them we changed it using the columns Site_Name"
    data_CA_ww = data_all_ww[(data_all_ww.State == 'California') & (data_all_ww.City !="CODIGA")]
    data_CA_ww = data_CA_ww.rename(columns={'Collection_Date': 'date'})
    data_CA_ww["date"] = pd.to_datetime(data_CA_ww['date'])
    data_CA_ww = data_CA_ww[cols]
    data_CA_ww.loc[data_CA_ww['Site_Name'] == 'UC Davis', 'City'] = 'UC Davis'
    data_CA_ww.loc[data_CA_ww['Site_Name'] == 'UC Davis', 'County_FIPS'] = '06113'
    data_CA_ww = data_CA_ww.reset_index()[cols]
    return data_CA_ww

# Define a function to combine data from different sources and regions
def create_CA_ww_data(data_ww_Eurofins):
    "We joint the data from eurofins with data provide by SCAN. From Los Banos, Turlock, 'Winters, 'Esparto, 'Woodland, Modesto and Merced"
    data_ww_Eurofins = data_ww_Eurofins.rename(
        columns={'N_norm_PMMoV': 'SC2_N_norm_PMMoV', 'N Gene gc/g dry weight': 'SC2_N_gc_g_dry_weight',
                 'N Gene gc/g dry weight UCI': 'SC2_N_gc_g_dry_weight_UCI',
                 'N Gene gc/g dry weight LCI': 'SC2_N_gc_g_dry_weight_LCI',
                 'PMMoV gc/g dry weight': 'PMMoV_gc_g_dry_weight',
                 'PMMoV gc/g dry weight UCI': 'PMMoV_gc_g_dry_weight_UCI',
                 'PMMoV gc/g dry weight LCI': 'PMMoV_gc_g_dry_weight_LCI'})
    data_ww_Eurofins['date'] = pd.to_datetime(data_ww_Eurofins['SampleDate'])
    data_ww_Eurofins = data_ww_Eurofins[cols_SC2]
    data_CA_ww = data_ww_all_CA()[cols]  # [cols_SC2]

    cities_CVHT1 = ['Los Banos', 'Turlock', 'Winters', 'Esparto', 'Woodland']
    cities_CVHT2 = ['Merced', 'Modesto']
    data_ww_Euf1 = data_ww_Eurofins[data_ww_Eurofins.City.isin(cities_CVHT1)]
    data_ww_Euf2 = data_ww_Eurofins[data_ww_Eurofins.City.isin(cities_CVHT2)]
    data_ww_Euf2 = data_ww_Euf2[data_ww_Euf2.date > '2022-04-30']

    data_ww_scan_eur = pd.concat([data_CA_ww, data_ww_Euf1, data_ww_Euf2], sort=True)

    data_ww_scan_eur = data_ww_scan_eur.sort_values(by=['City', 'date'])
    data_ww_scan_eur.loc[:, 'County'] = data_ww_scan_eur['City'].apply(lambda x: cities_county[x])
    data_ww_scan_eur.to_csv("output/" + "data_ww_CA.csv", index=False)
    return data_ww_scan_eur


# Define a function to create data for cities with the largest population served in each county
def Create_CA_ww_data_largest_pop():
    data_all_ww = create_CA_ww_data(data_ww_Eurofins)
    # we selected the cities with the largest population served in each county
    cities = []
    for i, county in enumerate(counties_CA):
        data_county = data_all_ww[data_all_ww.County == county]
        pop_seved = data_county["Population_Served"].max()
        cities.append(data_county.loc[data_county.Population_Served == pop_seved, "City"].iloc[0])

    # Only one WWTP for each county
    data_ww = data_all_ww[data_all_ww.City.isin(cities)]
    Data_all = pd.DataFrame({})  # ,columns=var_names)

    for county in counties_CA:

        data_wasw_i = data_ww.loc[data_ww.County == county, ['date', 'SC2_N_norm_PMMoV', "SC2_N_gc_g_dry_weight"]]
        data_wasw_i['N'] = data_wasw_i['SC2_N_gc_g_dry_weight']

        data_wasw_i.index = pd.to_datetime(data_wasw_i.date)

        data_wasw_i['SC2_N_norm_PMMoV'] = data_wasw_i['SC2_N_norm_PMMoV'].replace(to_replace=0, value=data_wasw_i['SC2_N_norm_PMMoV'][data_wasw_i['SC2_N_norm_PMMoV']!=0].min()/2) # Replace 0 by min
        data_wasw_i['N'] = data_wasw_i['N'].replace(to_replace=0, value=data_wasw_i['N'][data_wasw_i['N']!=0].min()/2)

        Data_full = data_wasw_i.groupby(pd.Grouper(freq="D")).mean() # Median
        Data_full["county"] = county
        Data_all = pd.concat([Data_all, Data_full], ignore_index=False)
    Data_all['date']=Data_all.index
    Data_all.to_csv("output/" + "data_ww_CA_county.csv", index=False)

    return Data_all


#data_all_ww= create_CA_ww_data(data_ww_Eurofins)
data_all_ww_county= Create_CA_ww_data_largest_pop()