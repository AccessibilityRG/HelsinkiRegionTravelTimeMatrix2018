# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 15:47:54 2019

@author: hentenka
"""
import pandas as pd
from selenium import webdriver
import time
import random

# Specify Chrome driver (you can fetch the latest version from: https://chromedriver.chromium.org/downloads)
browser = webdriver.Chrome("bin/chromedriver.exe")

# Maximize window
browser.maximize_window()

# Filepath
fp = "data/validation_sample_100_points.csv"
outfp = "validation/GoogleMaps_100_locations_rush_hour_7am.csv"
data = pd.read_csv(fp)

# Container for results
results = pd.DataFrame()

istart = 0
i2start = 0
restarted = False

# Iterate over pages
for i, orig in data.iterrows():
    orig_lat, orig_lon = orig['lat'], orig['lon']
    orig_id = orig['ID']
    for i2, dest in data.iterrows():
        dest_lat, dest_lon = dest['lat'], dest['lon']        
        dest_id = dest['ID']
        print("[%s,%s] Get times from %s to %s .." % (i, i2, orig_id, dest_id))
        
        # Skip self routes
        if orig_lat == dest_lat and orig_lon == dest_lon:
            continue
    
        # Parse url
        url = "https://www.google.fi/maps/dir/'{orig_lat},{orig_lon}'/'{dest_lat},{dest_lon}'/data=!4m13!4m12!1m3!2m2!1d25.0950992!2d60.3474427!1m3!2m2!1d24.7449117!2d60.169053!2m3!6e0!7e2!8j1557126000".format(
                orig_lat=orig_lat, orig_lon=orig_lon,
                dest_lat=dest_lat, dest_lon=dest_lon)
     
        # Fetch and render the page
        browser.get(url)
        
        time.sleep(1)
        
        # Get section with travel times
        time_info = browser.find_elements_by_xpath("//span[@jstcache=310]")
        dist_info = browser.find_elements_by_xpath('//div[@jstcache=315]')
        arrive_info = browser.find_elements_by_xpath("//span[@jstcache=312]")
        
        # Parse times
        times = [t.text for t in time_info]
        if len(dist_info) > 0:    
            dists = [d.text for d in dist_info]
        else:
            dists = [None for x in range(len(times))]
        if len(arrive_info) > 0:
            arrives = [a.text for a in arrive_info]
        else:
            arrives = [None for x in range(len(times))]
            
        # Add to results
        for t, d, a in zip(times, dists, arrives):
            results = results.append({'from_id': orig_id, 'to_id': dest_id,
                                      'time': t, 'dist': d, 'arrive': a}, ignore_index=True)
        
    
        # Get random sleep time so we don't look like a bot
        sleep_time = random.uniform(0.5,2)
        time.sleep(sleep_time)

# Convert ids to integers
id_cols = ['from_id', 'to_id']
for col in id_cols:
    results[col] = results[col].astype(int)

   
# Parse results
# =============

# Convert distances to numbers
results['dist'] = results['dist'].str.replace('miles', '')
results['dist'] = results['dist'].str.replace('mile', '')
results['dist_miles'] = None
for idx, row in results.iterrows():
    if row['dist'] != '':
        dist_m = float(row['dist'])
    else:
        dist_m = None
    results.loc[idx, 'dist_miles'] = dist_m

# Convert miles to kilometers
results['dist_km'] = results['dist_miles'] * 1.60934

# Parse minimum travel times
# --------------------------
results['min_time'] = None

for idx, row in results.iterrows():
    if row['time'] == '':
        min_time = None
    else:
        min_time = int(row['time'].split('-')[0].replace('min', ''))
    results.loc[idx, 'min_time'] = min_time

# Parse maximum travel times
# --------------------------
results['max_time'] = None

for idx, row in results.iterrows():
    if row['time'] == '':
        max_time = None
    else:
        split = row['time'].split('-')
        # If only single time is reported use that also as max time
        if len(split) == 1:
            max_time = int(split[0].replace('min', ''))
        else:
            txt = split[1]
            if 'h' in txt:
                tsplit = txt.split('h')
                hours = int(tsplit[0])
                minutes_txt = tsplit[1].replace('min', '')
                if minutes_txt != '':
                    minutes = int(minutes_txt)
                else:
                    minutes = 0
                # Convert to minutes
                hminutes = hours*60
                max_time = minutes + hminutes
            else:
                max_time = int(txt.replace('min', ''))
    results.loc[idx, 'max_time'] = max_time
    
# Group results by from_id and to_id to find fastest routes
grouped = results.groupby(['from_id', 'to_id'])

# Aggregated results
final_results = pd.DataFrame()

for (from_id, to_id), rows in grouped:
    # Get fastest and slowest route
    fastest_route = rows.loc[rows['min_time'] == rows['min_time'].min()]
    slowest_route = rows.loc[rows['min_time'] == rows['min_time'].max()]
    
    # Get attributes from fastest route
    fastest_min_time = fastest_route['min_time'].values[0]
    fastest_max_time = fastest_route['max_time'].values[0]
    fastest_dist_km = fastest_route['dist_km'].values[0]
    
    # Get attributes from slowest route
    slowest_min_time = slowest_route['min_time'].values[0]
    slowest_max_time = slowest_route['max_time'].values[0]
    slowest_dist_km = slowest_route['dist_km'].values[0]
    
    # Add data to container
    final_results = final_results.append({
            'from_id': from_id,
            'to_id': to_id,
            # Data from the fastest route
            'fastest_route_min_t': fastest_min_time,
            'fastest_route_max_t': fastest_max_time,
            'fastest_route_d': round(fastest_dist_km * 1000, 0),
            
            # Data from the slowest route
            'slowest_route_min_t': slowest_min_time,
            'slowest_route_max_t': slowest_max_time,
            'slowest_route_d': round(slowest_dist_km * 1000, 0),                        
            }, ignore_index=True)

# Fill NaN with 999999
final_results = final_results.fillna(999999)
    
# Convert columns to integers
for col in final_results.columns:
    final_results[col] = final_results[col].astype(int)

# Save to disk
final_results.to_csv(outfp, index=False)
