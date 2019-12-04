# -*- coding: utf-8 -*-
"""
travel_time_validations_and_visualizations_by_all_travel_modes.py

Calculate travel time differences by different travel modes.

Created on Thu Jun 13 17:55:54 2019

@author: hentenka
"""
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import shapiro

def adjustGridlines(ax, grid_linewidth, xlines=True, ylines=True):
    if xlines:
        gridlines = ax.get_xgridlines()
    if ylines and xlines:
        gridlines.extend( ax.get_ygridlines() )

    for line in gridlines:
                line.set_linewidth(grid_linewidth)
                line.set_linestyle('dotted')
    ax.grid(True)
    return ax

def adjustBoxStyle(fig, bp, ocolor='black', fcolor='#3881b9', falpha=0.9, owidth=0.75, wfliers=True, wcolor = 'black', wstyle = 'dotted', wwidth = 0.5, walpha = 0.9, ccolor = 'black', cwidth = 0.75, calpha = 0.9, mcolor = 'black', mwidth = 1.2, malpha = 1.0):
   
    # Box style
    # ---------
    for box in bp['boxes']:
        # change outline color
        box.set( color=ocolor, linewidth=owidth)
        # change fill color
        box.set( facecolor = fcolor , alpha=falpha)
        
    # Whisker style
    # -------------
    
    for whisker in bp['whiskers']:
        whisker.set(color=wcolor, linewidth=wwidth, linestyle=wstyle, alpha=walpha)
        
    # Caps style
    # ----------
    
    # Change color and linewidth of the caps
    for cap in bp['caps']:
        cap.set(color=ccolor, linewidth=cwidth, alpha=calpha)
        
    # Median style
        # ------------

    ## change color and linewidth of the medians
    for median in bp['medians']:
        median.set(color=mcolor, linewidth=mwidth, alpha=malpha)
    
    # Draw the Figure (so that tick labels are shown properly)
    # More discussion here: http://stackoverflow.com/questions/41122923/getting-tick-labels-in-matplotlib
    fig.canvas.draw()
    
    return fig

# Set style
sns.set(style='whitegrid')

# Filepaths
base_dir = "validation"
matrix_fp = os.path.join(base_dir, 'Matrix_2018_sample_results_all_modes.csv')
otp_fp = os.path.join(base_dir, 'OTP_results_for_validation_Jan_29_2018_rush_hour_otm.csv')
google_fp = os.path.join(base_dir, 'GoogleMaps_100_locations_rush_hour_7am.csv')
bike_fp = os.path.join(base_dir, 'OTP_results_for_validation_Jan_29_2018_fast_biker.csv')
walk_fp = os.path.join(base_dir, 'OTP_results_for_validation_Jan_29_2018_walk.csv')

# Read matrix and 
matrix = pd.read_csv(matrix_fp, sep=';')
pt_rush = pd.read_csv(otp_fp)
google_rush = pd.read_csv(google_fp)
bike = pd.read_csv(bike_fp)
walk = pd.read_csv(walk_fp)

# Select only relevant columns
matrix_cols = ['from_id', 'to_id', 'pt_r_t', 'car_r_t', 'car_sl_d', 'bike_f_t', 'walk_t', 'walk_d']
otp_cols = ['from_id', 'to_id', 'min_time', 'avg_time', 'median_time', 'start_time']
google_cols = ['from_id', 'to_id', 'fastest_route_max_t', 'fastest_route_min_t']

matrix = matrix[matrix_cols].copy()
pt_rush = pt_rush[otp_cols].copy()
google_rush = google_rush[google_cols].copy()
bike = bike[otp_cols].copy()
walk = walk[otp_cols].copy()

# Rename columns
pt_rush = pt_rush.rename(columns={'min_time':'pt_min_time', 'avg_time': 'pt_avg_time', 
                                    'median_time': 'pt_median_time', 'start_time': 'pt_start_time'})

bike = bike.rename(columns={'min_time':'bike_min_time', 'avg_time': 'bike_avg_time', 
                                    'median_time': 'bike_median_time', 'start_time': 'bike_start_time'})

walk = walk.rename(columns={'min_time':'walk_min_time', 'avg_time': 'walk_avg_time', 
                                    'median_time': 'walk_median_time', 'start_time': 'walk_start_time'})

    
# Make table join
data = matrix.merge(pt_rush, on=['from_id', 'to_id'])
data = data.merge(google_rush, on=['from_id', 'to_id'])
data = data.merge(walk, on=['from_id', 'to_id'])
data = data.merge(bike, on=['from_id', 'to_id'])

# Selection
pt_selection = data[['pt_r_t', 'pt_min_time']].copy()
car_selection = data[['car_r_t', 'car_sl_d', 'fastest_route_max_t', 'fastest_route_min_t']].copy()
bike_selection = data[['bike_f_t', 'bike_min_time', 'walk_d']].copy()
walk_selection = data[['walk_t', 'walk_min_time']].copy()

# Select rows that has values
pt_selection = pt_selection.loc[pt_selection['pt_r_t'] >= 0]
car_selection = car_selection.loc[car_selection['car_sl_d'] >= 0]
bike_selection = bike_selection.loc[bike_selection['bike_f_t']>=0]
walk_selection = walk_selection.loc[walk_selection['walk_t']>=0]

# It is necessary to add parking search time and walking time to Google results as well according Door-to-door principle. 
# Let's add 3 minutes which is approximate to whole region
car_selection['fastest_route_max_t_dd'] = car_selection['fastest_route_max_t'] + 3
car_selection['fastest_route_min_t_dd'] = car_selection['fastest_route_min_t'] + 3

# Calculate also cycling routing times based on normal OSM street network (i.e. without modified Strava Network)
cycling_speed = 19 # (kmph)
bike_selection['bike_f_t_osm'] = (((bike_selection['walk_d']/1000)/19)*60).round(0)

# Add 1 minute for this to consider the time it takes to lock/unlock the bike
bike_selection['bike_f_t_osm'] = bike_selection['bike_f_t_osm'] + 1


# Calculate average travel times for DORA and Google based on 
# minimum travel times (freeflow according speedlimits) and maximum travel times (congestion levels accounted)
# Calculate average time from Google and DORA
car_selection['DORA_avg_t'] = (car_selection['car_r_t'] + car_selection['car_sl_d']) / 2
car_selection['Google_avg_t'] = (car_selection['fastest_route_max_t_dd'] + car_selection['fastest_route_min_t_dd']) / 2

# Summary
pt_selection.describe()
car_selection.describe()
walk_selection.describe()
bike_selection.describe()

# Rename columns
pt_selection = pt_selection.rename(columns={'pt_r_t': 'MetropAccess-Reititin', 
                                      'pt_min_time': 'OpenTripPlanner'})
    
car_selection = car_selection.rename(columns={'DORA_avg_t': 'DORA', 'Google_avg_t': 'Google Maps'})

# Generate boxplot
fig, axarray = plt.subplots(nrows=1, ncols=4, figsize=(16, 4), sharey=False)
ptx = axarray[0]
carx = axarray[1]
walkx = axarray[2]
bikex = axarray[3]

# PUBLIC TRANSPORT
# ================
ptbox = pt_selection.boxplot(ax=ptx, column=['MetropAccess-Reititin', 'OpenTripPlanner'],
                          vert=True, patch_artist=True, return_type='dict', showfliers=False)

ptx.set_ylim(0, 130)

# Adjust gridlines
ptx = adjustGridlines(ax=ptx, grid_linewidth=0.2, xlines=True, ylines=False)
# Adjust Boxplot appearance
facecolor = 'gray' #'#FFE4C4' #"#C2D8E9"
fig = adjustBoxStyle(fig=fig, bp=ptbox, fcolor=facecolor, falpha=1.0, mwidth=3, mcolor='red', owidth=1)

# Set title
ptx.set_title('Public Transport')

# PRIVATE CAR
# ================
carbox = car_selection.boxplot(ax=carx, column=['DORA', 'Google Maps'],
                          vert=True, patch_artist=True, return_type='dict', showfliers=False)

carx.set_ylim(0, 60)

# Adjust gridlines
carx = adjustGridlines(ax=carx, grid_linewidth=0.2, xlines=True, ylines=False)
# Adjust Boxplot appearance
facecolor = 'gray' #'#FFE4C4' #"#C2D8E9"
fig = adjustBoxStyle(fig=fig, bp=carbox, fcolor=facecolor, falpha=1.0, mwidth=3, mcolor='red', owidth=1)

# Set title
carx.set_title('Car')

# Walking
# ==============
walk_data = walk_selection.rename(columns={'walk_t': 'MetropAccess-Reititin', 'walk_min_time': 'OpenTripPlanner'})
walkbox = walk_data.boxplot(ax=walkx, column=['MetropAccess-Reititin', 'OpenTripPlanner'],
                          vert=True, patch_artist=True, return_type='dict', showfliers=False)

walkx.set_ylim(0, 600)

# Adjust gridlines
walkx = adjustGridlines(ax=walkx, grid_linewidth=0.2, xlines=True, ylines=False)
# Adjust Boxplot appearance
facecolor = 'gray' #'#FFE4C4' #"#C2D8E9"
fig = adjustBoxStyle(fig=fig, bp=walkbox, fcolor=facecolor, falpha=1.0, mwidth=3, mcolor='red', owidth=1)

# Set title
walkx.set_title('Walking')

# Cycling
# ==============
bike_data = bike_selection.rename(columns={'bike_f_t': 'DORA\nStrava', 
                                           'bike_min_time': 'OpenTripPlanner',
                                           'bike_f_t_osm': 'DORA\nOSM'})
bikebox = bike_data.boxplot(ax=bikex, column=['DORA\nOSM', 'OpenTripPlanner', 'DORA\nStrava'],
                          vert=True, patch_artist=True, return_type='dict', showfliers=False)

bikex.set_ylim(0, 160)

# Adjust gridlines
bikex = adjustGridlines(ax=bikex, grid_linewidth=0.2, xlines=True, ylines=False)
# Adjust Boxplot appearance
facecolor = 'gray' #'#FFE4C4' #"#C2D8E9"
fig = adjustBoxStyle(fig=fig, bp=bikebox, fcolor=facecolor, falpha=1.0, mwidth=3, mcolor='red', owidth=1)

# Set title
bikex.set_title('Cycling')

# =============================
# VISUALIZE
# =============================

# -----------------
# Histograms
# -----------------

# Create histograms
fig, axarray = plt.subplots(nrows=1, ncols=2, figsize=(10,5), sharey=False)
ax1, ax2 = axarray
# Histograms
reit = pt_selection.loc[pt_selection['MetropAccess-Reititin'] < 120]
reit = reit[pt_selection['OpenTripPlanner'] < 120]
ax1 = reit.plot(ax=ax1, kind='hist', bins=114, alpha=0.8)
ax1.set_xlabel('Time', fontsize=15)
ax1.set_ylabel('Frequency', fontsize=15)
ax1.xaxis.set_tick_params(labelsize=13)
ax1.yaxis.set_tick_params(labelsize=13)
ax1 = adjustGridlines(ax=ax1, grid_linewidth=0.2, xlines=True, ylines=False)

carhist = car_selection.loc[car_selection['DORA'] < 70].copy()
carhist = carhist.loc[carhist['Google Maps'] < 70]

# Add parking time
#carhist['Here Maps'] = carhist['Here Maps']

ax2 = carhist[['DORA', 'Google Maps']].plot(ax=ax2, kind='hist', bins=70, alpha=0.8)
ax2.set_xlabel('Time', fontsize=15)
ax2.set_ylabel('Frequency', fontsize=15)
ax2.xaxis.set_tick_params(labelsize=13)
ax2.yaxis.set_tick_params(labelsize=13)
ax2 = adjustGridlines(ax=ax2, grid_linewidth=0.2, xlines=True, ylines=False)


# -----------------------
# Tripwise differences
# -----------------------

# ==================
# Public transport

reit = pt_selection.loc[pt_selection['MetropAccess-Reititin'] < 120]
reit = reit[reit['OpenTripPlanner'] < 120]

# Calculate difference
reit['diff'] = reit['MetropAccess-Reititin'] - reit['OpenTripPlanner']
reit['diff'].plot()

# Sort by travel time
reits = reit.sort_values(by='MetropAccess-Reititin')
reits = reits.reset_index(drop=True)
reits['index'] = reits.index
reits['time'] = reits['MetropAccess-Reititin']

fig = plt.figure()
ax1 = fig.add_subplot(111)
ax2 = ax1.twiny()

reits['diff'].plot(ax=ax1, lw=0.2, color='gray') #'#6495ED')

# Get tick locations
tick_locations = []
minutes = [15, 30, 45, 60, 75, 90, 105, 120]
found_minutes = []

for idx, row in reits.iterrows():
    t = row['time']
    if t in minutes:
        if t not in found_minutes:
            found_minutes.append(t)
            tick_locations.append(row['index'])

ax2.set_xticks(tick_locations)
ax2.set_xticklabels(list(map(str, minutes)))

# Zero line
ax1.plot([0,9400], [0, 0], color='r')

# +- 5 minutes
ax1.plot([0,9400], [5, 5], color='black', linestyle='dashed', dashes=(5, 5))
ax1.plot([0,9400], [-5, -5], color='black', linestyle='dashed', dashes=(5, 5))

# Aesthetics
ax1.set_xlabel('Trip #', fontsize=20, family='Arial', labelpad=10)
ax2.set_xlabel('Travel time (minutes)', fontsize=24, family='Arial', labelpad=10)
ax1.set_ylabel('< -- Time difference -- >', fontsize=24, family='Arial', labelpad=10)

tick_size = 20
ax1.xaxis.set_tick_params(labelsize=tick_size)
ax1.yaxis.set_tick_params(labelsize=tick_size)
ax2.xaxis.set_tick_params(labelsize=tick_size)
ax1 = adjustGridlines(ax=ax1, grid_linewidth=0.2, xlines=True, ylines=False)

# Adjust ylim
ax1.set_ylim(-30,30)

# ================
# CAR

# Calculate difference
carhist['diff'] = carhist['DORA'] - carhist['Google Maps']
#carhist['diff'].plot()

# Sort by travel time
carhist = carhist.sort_values(by='DORA')
carhist = carhist.reset_index(drop=True)
carhist['index'] = carhist.index
carhist['time'] = carhist['DORA']

fig = plt.figure()
ax1 = fig.add_subplot(111)
ax2 = ax1.twiny()

#carhist.plot(x='index', y='diff', ax=ax1, color='#6495ED', kind='scatter') #'#6495ED')
carhist['diff'].plot(ax=ax1, lw=0.2, color='gray') #'#6495ED')             

# Get tick locations
tick_locations = []
minutes = [10, 20, 30, 40, 50]
found_minutes = []

for idx, row in carhist.iterrows():
    t = row['time']
    if t in minutes:
        if t not in found_minutes:
            found_minutes.append(t)
            tick_locations.append(row['index'])

ax2.set_xticks(tick_locations)
ax2.set_xticklabels(list(map(str, minutes)))

# Zero line
ax1.plot([0,9400], [0, 0], color='r')

# +- 5 minutes
ax1.plot([0,9400], [5, 5], color='black', linestyle='dashed', dashes=(5, 5))
ax1.plot([0,9400], [-5, -5], color='black', linestyle='dashed', dashes=(5, 5))

# Aesthetics
ax1.set_xlabel('Trip #', fontsize=20, family='Arial', labelpad=10)
ax2.set_xlabel('Travel time (minutes)', fontsize=24, family='Arial', labelpad=10)
ax1.set_ylabel('< -- Time difference -- >', fontsize=24, family='Arial', labelpad=10)

tick_size = 20
ax1.xaxis.set_tick_params(labelsize=tick_size)
ax1.yaxis.set_tick_params(labelsize=tick_size)
ax2.xaxis.set_tick_params(labelsize=tick_size)
ax1 = adjustGridlines(ax=ax1, grid_linewidth=0.2, xlines=True, ylines=False)

# Adjust ylim
ax1.set_ylim(-30,30)

# ==================
# Cycling
# ==================

# Rename columns
bike_selection = bike_selection.rename(columns={'bike_f_t': 'DORA', 
                                      'bike_min_time': 'OpenTripPlanner'})

breit = bike_selection.loc[bike_selection['DORA'] < 120]
breit = breit[breit['OpenTripPlanner'] < 120]

# Calculate difference
breit['diff'] = breit['DORA'] - breit['OpenTripPlanner']
#breit['diff'].plot()

# Sort by travel time
breits = breit.sort_values(by='DORA')
breits = breits.reset_index(drop=True)
breits['index'] = breits.index
breits['time'] = breits['DORA']

fig = plt.figure()
ax1 = fig.add_subplot(111)
ax2 = ax1.twiny()

breits['diff'].plot(ax=ax1, lw=0.2, color='gray') #'#6495ED')

# Get tick locations
tick_locations = []
minutes = [15, 30, 45, 60, 75, 90, 105, 120]
found_minutes = []

for idx, row in breits.iterrows():
    t = row['time']
    if t in minutes:
        if t not in found_minutes:
            found_minutes.append(t)
            tick_locations.append(row['index'])

ax2.set_xticks(tick_locations)
ax2.set_xticklabels(list(map(str, minutes)))

# Zero line
ax1.plot([0,9400], [0, 0], color='r')

# +- 5 minutes
ax1.plot([0,9400], [5, 5], color='black', linestyle='dashed', dashes=(5, 5))
ax1.plot([0,9400], [-5, -5], color='black', linestyle='dashed', dashes=(5, 5))

# Aesthetics
ax1.set_xlabel('Trip #', fontsize=20, family='Arial', labelpad=10)
ax2.set_xlabel('Travel time (minutes)', fontsize=24, family='Arial', labelpad=10)
ax1.set_ylabel('< -- Time difference -- >', fontsize=24, family='Arial', labelpad=10)

tick_size = 20
ax1.xaxis.set_tick_params(labelsize=tick_size)
ax1.yaxis.set_tick_params(labelsize=tick_size)
ax2.xaxis.set_tick_params(labelsize=tick_size)
ax1 = adjustGridlines(ax=ax1, grid_linewidth=0.2, xlines=True, ylines=False)

# Adjust ylim
ax1.set_ylim(-30,30)

# =====================================================
# Cycling with normal OSM only (no Strava adjustments)
# =====================================================

# Rename columns
bike_selection_osm = bike_selection.rename(columns={'bike_f_t_osm': 'DORA without Strava', 
                                      'bike_min_time': 'OpenTripPlanner'})

breit = bike_selection_osm.loc[bike_selection_osm['DORA without Strava'] < 120]
breit = breit[breit['OpenTripPlanner'] < 120]

# Calculate difference
breit['diff'] = breit['DORA without Strava'] - breit['OpenTripPlanner']
#breit['diff'].plot()

# Sort by travel time
breits = breit.sort_values(by='DORA without Strava')
breits = breits.reset_index(drop=True)
breits['index'] = breits.index
breits['time'] = breits['DORA without Strava']

fig = plt.figure()
ax1 = fig.add_subplot(111)
ax2 = ax1.twiny()

breits['diff'].plot(ax=ax1, lw=0.2, color='gray') #'#6495ED')

# Get tick locations
tick_locations = []
minutes = [15, 30, 45, 60, 75, 90, 105, 120]
found_minutes = []

for idx, row in breits.iterrows():
    t = row['time']
    if t in minutes:
        if t not in found_minutes:
            found_minutes.append(t)
            tick_locations.append(row['index'])

ax2.set_xticks(tick_locations)
ax2.set_xticklabels(list(map(str, minutes)))

# Zero line
ax1.plot([0,9400], [0, 0], color='r')

# +- 5 minutes
ax1.plot([0,9400], [5, 5], color='black', linestyle='dashed', dashes=(5, 5))
ax1.plot([0,9400], [-5, -5], color='black', linestyle='dashed', dashes=(5, 5))

# Aesthetics
ax1.set_xlabel('Trip #', fontsize=20, family='Arial', labelpad=10)
ax2.set_xlabel('Travel time (minutes)', fontsize=24, family='Arial', labelpad=10)
ax1.set_ylabel('< -- Time difference -- >', fontsize=24, family='Arial', labelpad=10)

tick_size = 20
ax1.xaxis.set_tick_params(labelsize=tick_size)
ax1.yaxis.set_tick_params(labelsize=tick_size)
ax2.xaxis.set_tick_params(labelsize=tick_size)
ax1 = adjustGridlines(ax=ax1, grid_linewidth=0.2, xlines=True, ylines=False)

# Adjust ylim
ax1.set_ylim(-30,30)

# ==================
# Walking
# ==================

# Rename columns
walk_selection = walk_selection.rename(columns={'walk_t': 'MetropAccess-Reititin', 
                                      'walk_min_time': 'OpenTripPlanner'})

wreit = walk_selection.loc[walk_selection['MetropAccess-Reititin'] < 240]
wreit = wreit[walk_selection['OpenTripPlanner'] < 240]

# Calculate difference
wreit['diff'] = wreit['MetropAccess-Reititin'] - wreit['OpenTripPlanner']
#breit['diff'].plot()

# Sort by travel time
wreits = wreit.sort_values(by='MetropAccess-Reititin')
wreits = wreits.reset_index(drop=True)
wreits['index'] = wreits.index
wreits['time'] = wreits['MetropAccess-Reititin']

fig = plt.figure()
ax1 = fig.add_subplot(111)
ax2 = ax1.twiny()

wreits['diff'].plot(ax=ax1, lw=0.2, color='gray') #'#6495ED')

# Get tick locations
tick_locations = []
minutes = [15, 30, 45, 60, 75, 90, 120, 150, 180, 210, 240]
found_minutes = []

for idx, row in wreits.iterrows():
    t = row['time']
    if t in minutes:
        if t not in found_minutes:
            found_minutes.append(t)
            tick_locations.append(row['index'])

ax2.set_xticks(tick_locations)
ax2.set_xticklabels(list(map(str, minutes)))

# Zero line
ax1.plot([0,9400], [0, 0], color='r')

# +- 5 minutes
ax1.plot([0,9400], [5, 5], color='black', linestyle='dashed', dashes=(5, 5))
ax1.plot([0,9400], [-5, -5], color='black', linestyle='dashed', dashes=(5, 5))

# Aesthetics
ax1.set_xlabel('Trip #', fontsize=20, family='Arial', labelpad=10)
ax2.set_xlabel('Travel time (minutes)', fontsize=24, family='Arial', labelpad=10)
ax1.set_ylabel('< -- Time difference -- >', fontsize=24, family='Arial', labelpad=10)

tick_size = 20
ax1.xaxis.set_tick_params(labelsize=tick_size)
ax1.yaxis.set_tick_params(labelsize=tick_size)
ax2.xaxis.set_tick_params(labelsize=tick_size)
ax1 = adjustGridlines(ax=ax1, grid_linewidth=0.2, xlines=True, ylines=False)

# Adjust ylim
ax1.set_ylim(-30,30)
