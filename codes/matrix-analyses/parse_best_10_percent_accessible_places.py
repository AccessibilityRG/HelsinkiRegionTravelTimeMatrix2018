# -*- coding: utf-8 -*-
"""
Extract best 10 % cells with different transport modes

Created on Thu Jun 14 09:55:22 2018

Author:
    Henrikki Tenkanen
"""

import geopandas as gpd
import os
# Filepaths
ddir = r"C:\HY-DATA\HENTENKA\KOODIT\Matrix2018\data"
fp = os.path.join(ddir, "Most_accessible_places_2015.shp")
carr_out = os.path.join(ddir, "Car_r_best_10_percent_2015.shp")
carm_out = os.path.join(ddir, "Car_m_best_10_percent_2015.shp")
ptr_out = os.path.join(ddir, "PT_r_best_10_percent_2015.shp")
ptm_out = os.path.join(ddir, "PT_m_best_10_percent_2015.shp")

# Read data
data = gpd.read_file(fp)

def parse_best_10_percent(df, col):
    # If the data contains less than 10 minute values, remove them as there cannot be such median values
    min_val = df[col].min()
    if min_val <= 10:
        df = df.loc[df[col]>10]
    # Length
    cnt = len(df)
    
    # Threshold position of the 10 percent (rounding up)
    pos = int(cnt*0.1 + 0.5)
    
    # Sort by the median travel times
    df = df.sort_values(by=col)
    
    # Reset index
    df = df.reset_index(drop=True)
    
    # Check what is the travel time at the 10 % position
    pos_t = df.loc[pos, col]
    
    # Select only such grids that are below or equal to the 10 % position travel time
    df = df.loc[df[col] <= pos_t]
    
    return df
    
# Order values
pt_r = parse_best_10_percent(data, col='ptrmedian')
pt_m = parse_best_10_percent(data, col='ptmmedian')
car_r = parse_best_10_percent(data, col='carrmedian')
car_m = parse_best_10_percent(data, col='carmmedian')

# Save to file
pt_r.to_file(ptr_out)
pt_m.to_file(ptm_out)
car_r.to_file(carr_out)
car_m.to_file(carm_out)


