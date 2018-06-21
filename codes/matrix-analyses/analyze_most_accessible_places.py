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
matrix_dir = r"C:\HY-DATA\HENTENKA\Data\HelsinkiRegion_TravelTimeMatrix2014"
files = glob(os.path.join(matrix_dir, '*', 'travel*.txt'), recursive=True)
ykr_fp = r"C:\HY-DATA\HENTENKA\Data\MetropAccess_YKR_grid\MetropAccess_YKR_grid_EurefFIN.shp"
outfp = r"C:\HY-DATA\HENTENKA\KOODIT\Matrix2018\data\Most_accessible_places_2013.shp"

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
    median_m_pt = data['pt_m_t'].median()
    # Car
    median_m_car = data['car_m_t'].median()
   
    # Add to results
    results = results.append([[to_id, median_m_pt, median_m_car, ]], ignore_index=True)
    
# Add column names
results.columns = ['YKR_ID', 'ptmmedian', 'carmmedian']

# Join
join = results.merge(ykr, on='YKR_ID')

# Geo
geo = gpd.GeoDataFrame(join)
geo.crs = ykr.crs
geo.to_file(outfp)
