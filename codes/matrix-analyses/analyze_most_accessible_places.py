# -*- coding: utf-8 -*-
"""
Analyze the most accessible areas with PT and Car. 


Created on Wed Jun 13 13:38:04 2018

@author: hentenka
"""
import pandas as pd
import geopandas as gpd
from glob import glob
import os

# Filepaths
matrix_dir = r"C:\HY-Data\HENTENKA\Data\HelsinkiTravelTimeMatrix2018_2\5785xxx"
files = glob(os.path.join(matrix_dir, '*', 'travel*.txt'), recursive=True)
ykr_fp = r"C:\HY-Data\HENTENKA\Data\MetropAccess_YKR_grid\MetropAccess_YKR_grid_EurefFIN.shp"
outfp = r"C:\HY-Data\HENTENKA\KOODIT\HelsinkiRegionMatrix2018\data\Most_accessible_places_2018.shp"

# Read grid
ykr = gpd.read_file(ykr_fp)

# DataFrame for the results
results = pd.DataFrame()

# Iterate over files and calculate median
for idx, fp in enumerate(files):
    print(idx)
    # Read file
    data = pd.read_csv(fp, sep=';', na_values=[-1])
    
    # To id
    to_id = data.head(1)['to_id'].values[0]
    
    # Calculate the median value for different travel modes
    # PT
    median_r_pt = data['pt_r_t'].median()
    median_m_pt = data['pt_m_t'].median()
    # Car
    median_r_car = data['car_r_t'].median()
    median_m_car = data['car_r_t'].median()
    # Bike
    median_f_bike = data['bike_f_t'].median()
    median_s_bike = data['bike_s_t'].median()
    
    # Add to results
    results = results.append([[to_id, median_m_pt, median_r_pt, median_m_car, median_r_car, median_f_bike, median_s_bike]], ignore_index=True)
    
# Add column names
results.columns = ['to_id', 'ptrmedian', 'ptmmedian', 'carrmedian', 'carmmedian', 'bikfmedian', 'biksmedian']

# Join
join = ykr.merge(results, left_on='YKR_ID', right_on='to_id')

# Save to file
join.to_file(outfp)

