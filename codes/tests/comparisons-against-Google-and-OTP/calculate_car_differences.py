# -*- coding: utf-8 -*-
"""
calculate_car_differences.py

Calculate travel time differences based on Private car (DORA vs Google Maps)

Created on Thu Jun 13 17:55:54 2019

@author: hentenka
"""
import pandas as pd
import os

# Filepaths
base_dir = r"C:\HY-DATA\hentenka\KOODIT\Uni\manuscripts\2019_TravelTimeMatrix\data\validation\results"
matrix_fp = os.path.join(base_dir, 'matrix18', 'Matrix_2018_sample_results_all_modes.csv')
here_rush_fp = os.path.join(base_dir, 'car', 'GoogleMaps_100_locations_rush_hour_7am.csv')
    
# Read data
matrix = pd.read_csv(matrix_fp, sep=';')
car = pd.read_csv(here_rush_fp, sep=',')

# Make table join
matrix_cols = ['from_id', 'to_id', 'car_r_t', 'car_sl_d']
car_cols = ['from_id', 'to_id', 'fastest_route_max_t', 'fastest_route_min_t']
data = matrix[matrix_cols].merge(car[car_cols], on=['from_id', 'to_id'])

# It is necessary to add parking search time and walking time to Here results as well. Let's add 3 minutes which is approximate to whole region
data['fastest_route_max_t_dd'] = data['fastest_route_max_t'] + 3
data['fastest_route_min_t_dd'] = data['fastest_route_min_t'] + 3

# Drop no data values
data = data.loc[data['car_r_t']>=0]

# Calculate difference
data['difference'] = data['car_r_t'] - data['fastest_route_max_t_dd']
data = data.sort_values(by='car_r_t')
data = data.reset_index(drop=True)
data['index'] = data.index
data.plot(x='index', y='difference')

# Calculate difference based on freeflow
data['difference'] = data['car_sl_d'] - data['fastest_route_min_t']
data = data.sort_values(by='car_sl_d')
data = data.reset_index(drop=True)
data['index'] = data.index
data.plot(x='index', y='difference')

# Calculate average time from Google and DORA
data['DORA_avg_t'] = (data['car_r_t'] + data['car_sl_d']) / 2
data['Google_avg_t'] = (data['fastest_route_max_t_dd'] + data['fastest_route_min_t_dd']) / 2
data['difference'] = data['DORA_avg_t'] - data['Google_avg_t']
data = data.sort_values(by='DORA_avg_t')
data = data.reset_index(drop=True)
data['index'] = data.index
data.plot(x='index', y='difference')

