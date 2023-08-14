"""
Compute the Rt using the Cori approach for all the counties in California.
The Rt (effective reproduction number) is calculated based on wastewater data.
Specifically, the data from the wastewater treatment plant with the highest population served is used.
"""


import pandas as pd
import numpy as np
import epyestim.covid19 as covid19
import matplotlib.pyplot as plt
from datetime import timedelta
import matplotlib.dates as mdates


kk = 4
# Load the daily wastewater data from a saved CSV file
data_all = pd.read_csv("output/data_ww_CA_county_ARIMA.csv")

# Adjust the 'Cases_N' values using a multiplier 'kk'
data_all['Cases_N'] = np.round(kk*data_all['Cases_N'])
data_all = data_all.drop('Unnamed: 0', axis=1)
data_all.rename(columns={'county': 'County', 'date': 'Date'}, inplace=True)

# Get the unique counties present in the dataset
counties = data_all.County.unique()

# Define a function to compute the Rt using the Cori approach
def compute_Rt_Cori(data, county, colname):
    """
    Computes the Rt using the implementation of Cori in Epiestem.

    Args:
        data (DataFrame): DataFrame with columns 'County', 'Cases', 'Cases_pr', 'Cases_N', 'Cases_N_av10'.
        county (str): Name of the county.
        colname (str): Name of the column to compute Rt, e.g., 'Cases', 'Cases_pr', 'Cases_N', 'Cases_N_av10'.

    Returns:
        tuple: A tuple containing the Rt values and the corresponding dates.
            - Rt (DataFrame): DataFrame containing Rt values with columns 'R_mean', 'Q0.025', 'Q0.5', 'Q0.975'.
            - date_Rt (DatetimeIndex): Index of dates corresponding to the Rt values.

    Note:
        - Alert: The dates for plotting are moved 10 days forward.
        - The 'colname' column values are interpolated to handle missing values.

    """
    data_county = data[data.County == county]
    data_county[colname] = data_county[colname].interpolate()

    df = pd.Series(data=data_county[colname].values, index=pd.DatetimeIndex(data_county['Date']))

    df = df.groupby('Date').mean()

    Rt = covid19.r_covid(df)

    date_Rt = pd.date_range(Rt.index[0], Rt.index[-1])
    # Rt is an array [mean, q95, q10]
    return Rt[['R_mean',  'Q0.025',    'Q0.5',   'Q0.975']], date_Rt


# Define a function to compute and save Rt estimations for all counties
def save_rt_estimations():
    """
       Computes Rt estimations for all the counties in the dataset. Rt is computed for the columns
       ['Cases', 'Cases_pr', 'Cases_N', 'Cases_N_av10'].

       Args:
           data (DataFrame): A DataFrame with all the counties and the columns ['Cases', 'Cases_pr', 'Cases_N', 'Cases_N_av10'].
           Nmax (dict): A dictionary with the maximum number of days to compute a valid Rt using Christeen Rt implementation.

       Returns:
           DataFrame: The updated DataFrame 'data' with additional columns containing computed Rt values (mean, median, and quantiles).

       Note:
           The computed Rt values are assigned to the appropriate columns in the 'data' DataFrame based on county and date ranges.
       """


    for county in counties:
        rt_cori, date_cori = compute_Rt_Cori(data=data_all, county=county, colname='Cases_N')
        data_all.loc[(data_all.County == county) &  (date_cori[0]<=pd.to_datetime(data_all.Date)) & (pd.to_datetime(data_all.Date)<= date_cori[-1]), 'Rt_LCI']= rt_cori['Q0.025'].values
        data_all.loc[(data_all.County == county) &  (date_cori[0]<=pd.to_datetime(data_all.Date)) & (pd.to_datetime(data_all.Date)<= date_cori[-1]), 'Rt_UCI']= rt_cori['Q0.975'].values
        data_all.loc[(data_all.County == county) &  (date_cori[0]<=pd.to_datetime(data_all.Date)) & (pd.to_datetime(data_all.Date)<= date_cori[-1]), 'Rt']= rt_cori['Q0.5'].values


    dd=data_all[['Date', 'County', 'Rt', 'Rt_LCI', 'Rt_UCI']].dropna()
    dd.to_csv('output/data_Rt_ww_CA.csv')
    return dd

# Compute and save Rt estimations for all counties
data_Rt = save_rt_estimations()



def plot_Rts(df, ax, color):
    ax.plot(df['Date'], df['Rt'], color=color, ls='dashed', label='Rt')
    ax.fill_between(df['Date'], df['Rt_LCI'], df['Rt_UCI'], color=color, alpha=0.1)
    return ax


def plot_all_counties_Rt():
    counties = data_Rt.County.unique()
    fig, axs_ = plt.subplots(6, 4, figsize=(12, 6), sharex=True, sharey=True)
    axs = axs_.flatten()
    for i in range(24):
        county= counties[i]
        data_rt_county= data_Rt[data_Rt.County==county]
        axs[i] = plot_Rts(df=data_rt_county, ax=axs[i], color='black')
        axs[i].set_title(county, loc='center')

        axs[i].xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

        axs[i].xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1, interval=1))
        axs[i].tick_params(which='major', axis='x')
        plt.setp(axs[i].get_xticklabels(), rotation=0, ha="right", rotation_mode="anchor")

#plot_all_counties_Rt()