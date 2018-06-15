# -*- coding: utf-8 -*-
"""
Plot best 10 % accessibility areas.

Created on Fri Jun 15 09:59:00 2018

@author: hentenka
"""
import geopandas as gpd
import pysal as ps
import os
import matplotlib.pyplot as plt
from shapely.ops import polygonize
from shapely.geometry import MultiPolygon
import matplotlib.patches as patches

# Filepaths
data_dir = r"C:\HY-Data\HENTENKA\KOODIT\HelsinkiRegionMatrix2018\data"
carr_fp = os.path.join(data_dir, "Car_r_best_10_percent_2018.shp")
ptr_fp = os.path.join(data_dir, "PT_r_best_10_percent_2018.shp")
bikef_fp = os.path.join(data_dir, "Bike_f_best_10_percent_2018.shp")
roads_fp = os.path.join(data_dir, "pääväylät.shp")
metro_fp = os.path.join(data_dir, "Full_metro_line_eastWest.shp")
coast_fp = os.path.join(data_dir, "rantaviiva_polygon.shp")
rails_fp = os.path.join(data_dir, "rautatie.shp")
lakes_fp = os.path.join(data_dir, "lakes.shp")
borders_fp = os.path.join(data_dir, "city_borders.shp")

# Output filepaths
overlap_out = r"C:\HY-Data\HENTENKA\KOODIT\HelsinkiRegionMatrix2018\Figures\Overlap\All_modes_rushHour_best_10_percent_areas_v10.png"


# Read files
car = gpd.read_file(carr_fp)
pt = gpd.read_file(ptr_fp)
bike = gpd.read_file(bikef_fp)
roads = gpd.read_file(roads_fp)
metro = gpd.read_file(metro_fp)
coast = gpd.read_file(coast_fp)
rails = gpd.read_file(rails_fp)
lakes = gpd.read_file(lakes_fp)
borders = gpd.read_file(borders_fp)

# Ensure the same projection
CRS = car.crs
pt = pt.to_crs(CRS)
bike = bike.to_crs(CRS)
metro = metro.to_crs(CRS)
roads = roads.to_crs(CRS)
coast = coast.to_crs(CRS)
rails = rails.to_crs(CRS)
lakes = lakes.to_crs(CRS)
borders = borders.to_crs(CRS)

# Merge coastline polygons
coast = gpd.GeoDataFrame([[coast.unary_union]], columns=['geometry'], crs=CRS)

# Create a simplified contour line for cycling
bike['dis_id'] = 0
bike_c = bike.dissolve(by='dis_id')
bike_c['boundary'] = bike_c.boundary
smooth_geom = bike_c['boundary'].values[0].buffer(700, join_style=1).buffer(-700.0, join_style=1)
bike_s = gpd.GeoDataFrame([[smooth_geom]], columns=['geometry'], crs=CRS)
bounds = MultiPolygon(list(polygonize(bike_s.boundary.values[0]))).buffer(0)
bike_f = gpd.GeoDataFrame([[bounds]], columns=['geometry'], crs=CRS)

# Parameters
car_colormap = None
car_color = 'blue'
pt_color = 'red'
metro_color = 'red'
rail_color = 'black'
alpha = 0.7
#scheme = "quantiles"
water_color = '#808080'
roads_color = "#404040"
bike_ecolor = 'orange'
bike_fcolor = 'none'

# Font family
ffamily = 'Arial'
fsize = 7
fweight = 'normal'

# Plot everything on top of each other
ax = car.plot(color=car_color, alpha=alpha)
ax = pt.plot(ax=ax, color=pt_color, alpha=alpha)
# Use simplified outline only
#ax = bike_f.plot(ax=ax, facecolor='none', alpha=0.99, edgecolor='orange', lw=3, linestyle='--')
ax = bike.plot(ax=ax, facecolor=bike_fcolor, alpha=0.99, edgecolor=bike_ecolor, lw=0.3, linestyle='-')
ax = borders.plot(ax=ax, facecolor='none', lw=0.7, edgecolor='gray', linestyle='--')
ax = coast.plot(ax=ax, color=water_color, linewidth=0)
ax = roads.plot(ax=ax, lw=1.0, color=roads_color, alpha=0.8)
ax = metro.plot(ax=ax, lw=1.5, color=metro_color)
ax = rails.plot(ax=ax, lw=1.25, linestyle='-', color='white')
ax = rails.plot(ax=ax, lw=1.25, linestyle='--', color=rail_color)
ax = lakes.plot(ax=ax, color=water_color, linewidth=0)

# X and y limits for the map
xleft_lim, xright_lim = 360900, 404000
ylow_lim, yup_lim = 6665000, 6699900

# Create custom legend for the plot
bwidht = 3000
bheight = 1300

# Legend box for Car, PT and Bike
ptxy = (xleft_lim + 4000 + 500, yup_lim - 1500)
carxy = (xleft_lim + 4000 + 500*10, yup_lim - 1500)
bikexy = (xleft_lim + 4000 + 500*10*1.9, yup_lim - 1500)

ptbox = patches.Rectangle(xy=ptxy, width=bwidht, height=bheight, facecolor=pt_color, alpha=alpha)
carbox = patches.Rectangle(xy=carxy, width=bwidht, height=bheight, facecolor=car_color, alpha=alpha)
bikebox = patches.Rectangle(xy=bikexy, width=bwidht, height=bheight, lw=2, edgecolor=bike_ecolor, facecolor=bike_fcolor, alpha=0.99)

ax.text(x=ptxy[0]+ 450, y=ptxy[1] + 2000, s="PT", family=ffamily, weight=fweight, fontsize=fsize)
ax.text(x=carxy[0]+ 450, y=carxy[1] + 2000, s="Car", family=ffamily, weight=fweight, fontsize=fsize)
ax.text(x=bikexy[0]+ 400, y=bikexy[1] + 2000, s="Bike", family=ffamily, weight=fweight, fontsize=fsize)

# Legend boxes for combinations of Car, PT, and Bike
# Car + PT
xycp = xy=(xleft_lim + 500*10*5, yup_lim - 1500)
carpt_box_c = patches.Rectangle(xy=xycp, width=bwidht, height=bheight, facecolor=car_color, alpha=alpha)
carpt_box_p = patches.Rectangle(xy=xycp, width=bwidht, height=bheight, facecolor=pt_color, alpha=alpha)

# Car + Bike
xycb = (xleft_lim + 500*10*6, yup_lim - 1500)
bikecar_box_c = patches.Rectangle(xy=xycb, width=bwidht, height=bheight, facecolor=car_color, alpha=alpha)
bikecar_box_b = patches.Rectangle(xy=xycb, width=bwidht, height=bheight, lw=2, edgecolor=bike_ecolor, facecolor=bike_fcolor, alpha=0.99)

# PT + Bike
xypb = (xleft_lim + 500*10*7, yup_lim - 1500)
bikept_box_p = patches.Rectangle(xy=xypb, width=bwidht, height=bheight, facecolor=pt_color, alpha=alpha)
bikept_box_b = patches.Rectangle(xy=xypb, width=bwidht, height=bheight, lw=2, edgecolor=bike_ecolor, facecolor=bike_fcolor, alpha=0.99)

# Car + PT + Bike
xycpb = (xleft_lim + 500*10*8, yup_lim - 1500)
bikecarpt_box_c = patches.Rectangle(xy=xycpb, width=bwidht, height=bheight, facecolor=car_color, alpha=alpha)
bikecarpt_box_p = patches.Rectangle(xy=xycpb, width=bwidht, height=bheight, facecolor=pt_color, alpha=alpha)
bikecarpt_box_b = patches.Rectangle(xy=xycpb, width=bwidht, height=bheight, lw=2, edgecolor=bike_ecolor, facecolor=bike_fcolor, alpha=0.99)

ax.text(x=xycp[0] - 250, y=xycp[1] + 2000, s="PT & Car", family=ffamily, weight=fweight, fontsize=fsize)
ax.text(x=xycb[0] - 550, y=xycb[1] + 2000, s="Car & Bike", family=ffamily, weight=fweight, fontsize=fsize)
ax.text(x=xypb[0] - 550, y=xypb[1] + 2000, s="PT & Bike", family=ffamily, weight=fweight, fontsize=fsize)
ax.text(x=xycpb[0] - 550, y=xycpb[1] + 2000, s="Car & PT & Bike", family=ffamily, weight=fweight, fontsize=fsize)


# Add the patches to the Axes
ax.add_patch(ptbox)
ax.add_patch(carbox)
ax.add_patch(bikebox)

ax.add_patch(carpt_box_c)
ax.add_patch(carpt_box_p)

ax.add_patch(bikecar_box_c)
ax.add_patch(bikecar_box_b)

ax.add_patch(bikept_box_p)
ax.add_patch(bikept_box_b)

ax.add_patch(bikecarpt_box_c)
ax.add_patch(bikecarpt_box_p)
ax.add_patch(bikecarpt_box_b)

# Set x/y limits
ax.set_xlim([xleft_lim, xright_lim])
ax.set_ylim([ylow_lim, yup_lim])
plt.axis('off')
#plt.tight_layout()
plt.savefig(overlap_out, dpi=500)