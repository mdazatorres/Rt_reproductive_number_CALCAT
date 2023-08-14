
## Rt Estimation from Wastewater Data
We estimate the Rt  using only wastewater data. To estimate the number of cases, we create a proxy from the smoothed SARS-CoV-2 RNA concentration. The process involves the following steps:

1. ARIMA Smoothing: To enhance the accuracy of our wastewater data, we apply an AutoRegressive Integrated Moving Average (ARIMA) model of order 1.
2. Normalization: We normalize the smoothed concentration data by dividing it by the minimum observed concentration in the treatment plant. This normalization ensures that the minimum concentration corresponds to a reference value of 1
3. Scaling: Following normalization, we multiply the normalized concentration by a scalar factor, denoted as k. This step is founded on the assumption that the minimum concentration observed in the treatment plant is roughly indicative of k infected individuals. Notably, the choice of k is not crucial for Rt calculation, as the method is scale-independent.  However, it's worth noting that the selection of the scalar value k can influence the method's sensitivity, particularly for low counts.
4. Rt Calculation: With the wastewater-based proxy for estimated cases, we proceed to calculate Rt using the Epyestim package. This involves evaluating the effective reproduction number using the transformed wastewater data, providing insights into the potential transmission dynamics within the community


### Files:
1. Create_data.py:
   - This file creates a dataset specifically for California counties by combining wastewater data. The following steps are performed in this script:
•	Eurofins data is joined with SCAN data for cities in the Central Valley that have transitioned to Eurofins testing.
•	A dataset is generated containing the data of the largest wastewater treatment plant (WWTP) in each county. This dataset will be used to compute the Rt at the county level.

Output:
•	data_ww_CA.csv: Dataset containing wastewater data for California cities.
•	data_ww_CA_county.csv: Dataset containing wastewater data for California counties. This dataset includes the data of the largest WWTP in each city.

2. INLA_arima.R
This script generates the datasets required for use in Rt_ww_computed_counties.py. It involves computing an ARIMA model (AutoRegressive Integrated Moving Average) using a Bayesian approach.

Input:
data_ww_CA_county.csv
Output: 
data_ww_CA_county_ARIMA.csv


3. Rt_ww_computed_counties.py:
This script calculates the Rt values using the Cori approach for all counties in California. Specifically, it uses data from the wastewater treatment plant with the highest population served to make these estimations.

Imput: 
data_ww_CA_county_ARIMA.cs
Output:
   - data_Rt_ww_CA.csv
 Dataset containing computed Rt values for all counties in California. This data set is used in CalCAT
Dictionary
- Date: The date corresponding to  Rt computed
- County: The name of the county in California for which the Rt estimation was made.
- Rt: The estimated Reproduction Number (Rt) for the specific county on the given date. 
- Rt_LCI: The Lower Confidence Interval (LCI) associated with the Rt estimation. It represents the lower bound of the confidence interval for the Rt value, indicating the range of uncertainty.
- Rt_UCI: The Upper Confidence Interval (UCI) associated with the Rt estimation. It represents the upper bound of the confidence interval for the Rt value, indicating the range of uncertainty.

Note:
Before to run this file you need run:
1. Create data.py
2.  INLA_WWTP.R 








![image](https://github.com/mdazatorres/Rt_reproductive_number_CALCAT/assets/39836676/07036941-c77b-49a0-b6e2-3a78460bea02)
