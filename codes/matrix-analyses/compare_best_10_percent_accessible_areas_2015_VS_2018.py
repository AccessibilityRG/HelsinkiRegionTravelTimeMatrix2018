# -*- coding: utf-8 -*-
"""
Compare best 10 % accessibility areas between 2015 and 2018.

Requirements:
    geopandas-1.0.0.dev
    shapely-1.6.2
    matplotlib-2.0.0
    
Created on:
    June 16th 2018

Author:
    Henrikki Tenkanen, Digital Geography Lab, University of Helsinki
    
"""
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from shapely.ops import polygonize
from shapely.geometry import MultiPolygon
import matplotlib.patches as patches

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

def create_custom_legend(ax, xleft_lim, yup_lim):

    # Create custom legend for the plot
    bwidht = 3000
    bheight = 1300
    
    # Legend box for Car, PT and Bike
    ptxy = (xleft_lim + 4000 + 500, yup_lim - 1500)
    carxy = (xleft_lim + 4000 + 500*10, yup_lim - 1500)
        
    ptbox = patches.Rectangle(xy=ptxy, width=bwidht, height=bheight, facecolor=pt_color, alpha=alpha)
    carbox = patches.Rectangle(xy=carxy, width=bwidht, height=bheight, facecolor=car_color, alpha=alpha)
        
    # Legend boxes for combinations of Car, PT, and Bike
    # Car + PT
    xycp = (xleft_lim + 500*10*5, yup_lim - 1500)
    carpt_box_c = patches.Rectangle(xy=xycp, width=bwidht, height=bheight, facecolor=car_color, alpha=alpha)
    carpt_box_p = patches.Rectangle(xy=xycp, width=bwidht, height=bheight, facecolor=pt_color, alpha=alpha)
    
    
    
    # Add the patches to the Axes
    ax.add_patch(ptbox)
    ax.add_patch(carbox)
    
    ax.add_patch(carpt_box_c)
    ax.add_patch(carpt_box_p)
    
    return ax

def set_limits_pks(ax):
    # X and y limits for the map
    xleft_lim, xright_lim = 360900, 404000
    ylow_lim, yup_lim = 6665000, 6699900
    
    # Set x/y limits
    ax.set_xlim([xleft_lim, xright_lim])
    ax.set_ylim([ylow_lim, yup_lim])
    return ax
    
def plot_comparison(df1, df2, df1_color='orange', df2_color='gray', outfp=None):
    # Plot everything on top of each other
    ax = df1.plot(color=df1_color, alpha=alpha, legend=True)
    ax = df2.plot(ax=ax, color=df2_color, alpha=alpha, legend=True)
    ax = plot_environment(ax=ax)
    
    ax = set_limits_pks(ax)
    
def plot_environment(ax):
    ax = borders.plot(ax=ax, facecolor='none', lw=0.7, edgecolor='gray', linestyle='--')
    ax = coast.plot(ax=ax, color=water_color, linewidth=0)
    ax = roads.plot(ax=ax, lw=1.0, color=roads_color, alpha=0.8)
    ax = metro.plot(ax=ax, lw=1.5, color=metro_color)
    ax = rails.plot(ax=ax, lw=1.25, linestyle='-', color='white')
    ax = rails.plot(ax=ax, lw=1.25, linestyle='--', color=rail_color)
    ax = lakes.plot(ax=ax, color=water_color, linewidth=0)
    return ax
    
def detect_changes(df1, df2, join_col='YKR_ID'):
    no_change = df1.merge(df2[[join_col]], on=join_col, how='inner')
    no_change_ids = list(no_change[join_col])
    
    nochange_in_df = df2.loc[df2[join_col].isin(no_change_ids)]
    change_in_df1 = df1.loc[~df1[join_col].isin(no_change_ids)]
    change_in_df2 = df2.loc[~df2[join_col].isin(no_change_ids)]
    return nochange_in_df, change_in_df1, change_in_df2
    
def plot_changes(df1, df2, no_changes, outfp):
    # Plot
    ax = df1.plot(color='blue')
    ax = df2.plot(ax=ax, color='orange')
    ax = no_changes.plot(ax=ax, color='#E0E0E0')
    ax = plot_environment(ax)
    
    # Set x/y limits
    ax = set_limits_pks(ax)
    plt.axis('off')
    plt.savefig(outfp, dpi=500)
    return ax

# Filepaths
data_dir = r"C:\HY-DATA\HENTENKA\KOODIT\Matrix2018\data"
data15_fp = os.path.join(data_dir, "Most_accessible_places_2015.shp")
data18_fp = os.path.join(data_dir, "Most_accessible_places_2018.shp")
roads_fp = os.path.join(data_dir, "main_roads.shp")
metro_fp = os.path.join(data_dir, "Full_metro_line_eastWest.shp")
coast_fp = os.path.join(data_dir, "rantaviiva_polygon.shp")
rails_fp = os.path.join(data_dir, "Full_railway.shp")
lakes_fp = os.path.join(data_dir, "lakes.shp")
borders_fp = os.path.join(data_dir, "city_borders.shp")

# Output filepaths
pt_out = r"C:\HY-DATA\HENTENKA\KOODIT\Matrix2018\Figures\Comparisons\PT_Comparison_2015_VS_2018_most_accessible_10_percent.png"
car_out = r"C:\HY-DATA\HENTENKA\KOODIT\Matrix2018\Figures\Comparisons\Car_Comparison_2015_VS_2018_most_accessible_10_percent.png"

# Read files
d15 = gpd.read_file(data15_fp)
d18 = gpd.read_file(data18_fp)
roads = gpd.read_file(roads_fp)
metro = gpd.read_file(metro_fp)
coast = gpd.read_file(coast_fp)
rails = gpd.read_file(rails_fp)
lakes = gpd.read_file(lakes_fp)
borders = gpd.read_file(borders_fp)

# Ensure the same projection
CRS = d15.crs
d18 = d18.to_crs(CRS)
metro = metro.to_crs(CRS)
roads = roads.to_crs(CRS)
coast = coast.to_crs(CRS)
rails = rails.to_crs(CRS)
lakes = lakes.to_crs(CRS)
borders = borders.to_crs(CRS)

# Merge coastline polygons
coast = gpd.GeoDataFrame([[coast.unary_union]], columns=['geometry'], crs=CRS)

# Parameters
car_colormap = None
car_color = 'blue'
pt_color = 'red'
metro_color = 'red'
rail_color = 'black'
alpha = 1.0
#scheme = "quantiles"
water_color = '#808080'
roads_color = "#404040"
bike_ecolor = 'orange'
bike_fcolor = 'none'

# Font family
ffamily = 'Arial'
fsize = 7
fweight = 'normal'

# Convert datatypes
d18['YKR_ID'] = d18['YKR_ID'].astype(int)
d15['YKR_ID'] = d15['YKR_ID'].astype(int)

# Detect best 10 percent
d18_car = parse_best_10_percent(df=d18, col='carrmedian')
d15_car = parse_best_10_percent(df=d15, col='carrmedian')

d15_pt = parse_best_10_percent(df=d15, col='ptrmedian')
d18_pt = parse_best_10_percent(df=d18, col='ptrmedian')

# Detect where the IDs are the same (i.e. no change between years)
no_change_pt, change_in_15_pt, change_in_18_pt = detect_changes(df1=d15_pt, df2=d18_pt)
no_change_car, change_in_15_car, change_in_18_car = detect_changes(df1=d15_car, df2=d18_car)

# Plot changes
plot_changes(df1=change_in_15_pt, df2=change_in_18_pt, no_changes=no_change_pt, outfp=pt_out)
plot_changes(df1=change_in_15_car, df2=change_in_18_car, no_changes=no_change_car, outfp=car_out)

    