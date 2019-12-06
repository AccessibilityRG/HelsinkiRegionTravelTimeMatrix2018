import pandas as pd
import geopandas as gpd
import os, sys
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def connect_to_DB(host, db_name, username, pwd, port):
    conn_string = "host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (host, db_name, username, pwd, port)
    #print(conn_string)
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    return(conn, cursor)

def create_DB_engine(host, db_name, username, pwd, port):
    db_url = r'postgresql://%s:%s@%s:%s/%s' % (username, pwd, host, port, db_name)
    engine = create_engine(db_url)
    return engine

def filePathsToList(source_dir, criteria, fileformat):
    flist = []
    for root, dirs, files in os.walk(source_dir):
        for filename in files:
            if criteria in filename and filename.endswith(fileformat):
                flist.append(os.path.join(root, filename))
    return flist

def findMatchingFile(Walk_fp, targetPaths, mode='pt'):
    search_folder = os.path.dirname(targetPaths[0])
    Walk_ID = os.path.basename(Walk_fp).split('_')[0]
    for targetfile in targetPaths:
        if mode == 'car':
            target_ID = os.path.basename(targetfile).split('_')[2]
        else:
            target_ID = os.path.basename(targetfile).split('_')[0]
        if target_ID == Walk_ID:
            return targetfile
    print("Error: Could not find corresponding target_file for %s in %s" % (Walk_ID, search_folder))
    sys.exit()

def processMatrix(fp, columns, names, nodata_value, columns_to_round):
    # Read data
    data = pd.read_csv(fp, sep=';', encoding='latin-1', low_memory=False, na_values=nodata_value)
    # Select columns
    data = data[columns]
    # Set NoData value to -1
    data = data.fillna(value=-1)
    # Round columns
    for roundcol in columns_to_round:
        data[roundcol] = data[roundcol].round()
    # Rename columns
    data.columns = names
    return data

def process_dora(fp, columns, names, columns_to_round):
    # Read Car Matrix
    data = gpd.read_file(fp)
    # Select columns
    data = data[columns]
    
    # Round columns
    for roundcol in columns_to_round:
        data[roundcol] = data[roundcol].round()

    # Reorder columns
    if 'RUSH' in data.columns:
        data = data[['from_id', 'to_id', 'travel_time', 'distance']]
    else:
        data = data[['from_id', 'to_id', 'travel_time', 'distance']]
        
    # Rename columns
    data.columns = names
    return data

# ============
# PARAMETERS
# ============

POSTGIS_DB_NAME='matrix'
IP_ADDRESS='xx.xx.xx.xx' 
POSTGIS_PORT=5432 
POSTGIS_USERNAME='myusername' 
POSTGIS_PWD='mypwd'
DATA_TABLE='travel_time_matrix_2018'

# PostGIS Authentication crecedentials
db_name, host, port, username, pwd = POSTGIS_DB_NAME, IP_ADDRESS, POSTGIS_PORT, POSTGIS_USERNAME, POSTGIS_PWD

# Create connection to Database (i.e. engine)
engine = create_DB_engine(host, db_name, username, pwd, port)

# Set schema
Base.metadata.create_all(engine)

# File paths
extrafp = "data/BufferCells.txt"
pt_r_dir = "data/pt_rush_hour_2018"
pt_m_dir = "data/pt_midday_2018"
walk_dir = "data/walking_2018"
car_r_dir = "data/car_rush_hour_2018"
car_m_dir = "data/car_midday_2018"
bike_f_dir = "data/bike_fast_2018"
bike_s_dir = "data/bike_slow_2018"

# Read input matrix filepaths
pt_r_paths = filePathsToList(pt_r_dir, criteria='pt', fileformat='.txt')
pt_m_paths = filePathsToList(pt_m_dir, criteria='pt', fileformat='.txt')
Walkpaths = filePathsToList(walk_dir, criteria='walk', fileformat='.txt')
car_r_paths = filePathsToList(car_r_dir, criteria='car', fileformat='.geojson')
car_m_paths = filePathsToList(car_m_dir, criteria='car', fileformat='.geojson')
bike_f_paths = filePathsToList(bike_f_dir, criteria='bike', fileformat='.geojson')
bike_s_paths = filePathsToList(bike_s_dir, criteria='bike', fileformat='.geojson')

# Read Extra grid cells
extra = pd.read_csv(extrafp, sep='\t', usecols=['ID'])

# Necessary columns in raw data
pt_cols = ['from_id', 'to_id', 'total_route_time', 'route_time', 'route_distance']
walk_cols = ['from_id', 'to_id', 'total_route_time', 'route_distance']
car_r_cols = ['ykr_from_id', 'ykr_to_id', 'travel_time', 'distance']
car_m_cols = ['ykr_from_id', 'ykr_to_id', 'travel_time', 'distance']
bike_f_cols = ['ykr_from_id', 'ykr_to_id', 'travel_time', 'distance']
bike_s_cols = ['ykr_from_id', 'ykr_to_id', 'travel_time', 'distance']

# Columns in final output
walk_m_names = ['from_id', 'to_id', 'walk_t', 'walk_d']
pt_r_names = ['from_id', 'to_id', 'pt_r_tt', 'pt_r_t', 'pt_r_d']
pt_m_names = ['from_id', 'to_id', 'pt_m_tt', 'pt_m_t', 'pt_m_d']
car_r_names = ['from_id', 'to_id', 'car_r_t', 'car_r_d']
car_m_names = ['from_id', 'to_id', 'car_m_t', 'car_m_d']
bike_f_names = ['from_id', 'to_id', 'bike_f_t', 'bike_d']
bike_s_names = ['from_id', 'to_id', 'bike_s_t', 'bike_d']

# Nodata value in MetropAccess-Reititin
nodata_value = -99999.99

# Start index (for reboot/parallel purposes)
start_idx = 0

# End index
end_idx = 293

# ---------------------------------------------------------------------------------------------
# Iterate over input matrices and create MetropAccess-TravelTimeMatrix results files (unsorted)
# ---------------------------------------------------------------------------------------------
for fileidx, matrix_fp in enumerate(Walkpaths):
    if fileidx >= start_idx and fileidx < end_idx:
        print("---------------------------------\nIndex: %s\n" % fileidx, os.path.basename(matrix_fp), "\n"*2)
        
        # ----------
        # WALK
        # ----------
        # Process Walk data
        print("Processing walk..")
        walk = processMatrix(fp=matrix_fp, columns=walk_cols, names=walk_m_names, nodata_value=nodata_value, columns_to_round=['total_route_time', 'route_distance'])
            
        # -------------
        # PT Rush hour
        # -------------
        print("Processing PT rush hour..")
        # Find corresponding PT rush hour data
        pt_r_fp = findMatchingFile(matrix_fp, pt_r_paths)
        # Process PT rush hour
        pt_r = processMatrix(fp=pt_r_fp, columns=pt_cols, names=pt_r_names, nodata_value=nodata_value, columns_to_round=['total_route_time', 'route_time', 'route_distance'])
        
        # -------------
        # PT Midday
        # -------------
        print("Processing PT midday..")    
        # Find corresponding PT rush hour data
        pt_m_fp = findMatchingFile(matrix_fp, pt_m_paths)
        # Process PT midday 
        pt_m = processMatrix(fp=pt_m_fp, columns=pt_cols, names=pt_m_names, nodata_value=nodata_value, columns_to_round=['total_route_time', 'route_time', 'route_distance'])

        # ----------------------
        # Car Rush hour
        # ----------------------
        print("Processing Car Rush hour..")        
        # Read corresponding Car rush hour / midday data
        car_r_fp = findMatchingFile(matrix_fp, car_r_paths, mode='car')
        # Process Car Midday
        car_r = process_dora(fp=car_r_fp, columns=car_r_cols, names=car_r_names, columns_to_round=['travel_time', 'distance'])

        # ----------------------
        # Car Midday
        # ----------------------
        print("Processing Car midday..")        
        # Read corresponding Car rush hour / midday data
        car_m_fp = findMatchingFile(matrix_fp, car_m_paths, mode='car')
        # Process Car Midday
        car_m = process_dora(fp=car_m_fp, columns=car_m_cols, names=car_m_names, columns_to_round=['travel_time', 'distance'])
        
        # ----------------------
        # Bike Fast
        # ----------------------
        print("Processing Fast biker..")        
        # Read corresponding data
        bike_f_fp = findMatchingFile(matrix_fp, bike_f_paths, mode='bicycle')
        # Process bike
        bike_f = process_dora(fp=bike_f_fp, columns=bike_f_cols, names=bike_f_names, columns_to_round=['travel_time', 'distance'])
        
        # ----------------------
        # Bike slow
        # ----------------------
        print("Processing Slow biker..")        
        # Read corresponding data
        bike_s_fp = findMatchingFile(matrix_fp, bike_s_paths, mode='bicycle')
        # Process bike
        bike_s = process_dora(fp=bike_s_fp, columns=bike_s_cols, names=bike_s_names, columns_to_round=['travel_time', 'distance'])

        # --------------------------
        # Create Travel Time Matrix
        # --------------------------
        print("Creating Travel Time Matrix..")    
        # Join Datasets together
        data = walk.merge(pt_r, on=['from_id', 'to_id'])
        data = data.merge(pt_m, on=['from_id', 'to_id'])
        data = data.merge(car_r, on=['from_id', 'to_id'])
        data = data.merge(car_m, on=['from_id', 'to_id'])
        data = data.merge(bike_f, on=['from_id', 'to_id'])
        data = data.merge(bike_s, on=['from_id', 'to_id'])
            
        # Exclude rows that belongs to Extra grid
        data = data.ix[~data['to_id'].isin(extra['ID'].values)]
        data = data.ix[~data['from_id'].isin(extra['ID'].values)]
        
        # Ensure correct column order
        data = data[['from_id', 'to_id', 'walk_t', 'walk_d', 'bike_f_t', 'bike_s_t', 'bike_d', 
                     'pt_r_tt', 'pt_r_t', 'pt_r_d','pt_m_tt', 'pt_m_t', 'pt_m_d', 
                     'car_r_t', 'car_r_d', 'car_m_t', 'car_m_d', 'car_sl_t']]

        # Prepare zero values for rows where 'from_id' equals 'to_id' ==> I.e. no movement
        # --------------------------------------------------------------------------------
        # Number of columns
        colLength = len(data.columns)
        # The amount of zeros that will be inserted ==> all columns except 'from_id' and 'to_id' 
        zeros_cnt = colLength-2
        # Create a list with zeros
        zeros = [0 for zero in range(zeros_cnt)]
        
        # Save Files to disk
        # ------------------
        print("Saving Travel Time Matrix..")    

        # Group by 'to_id'
        grouped = data.groupby('to_id')

        # Iterete over 'to_id' groups and save data to disk
        for to_id, values in grouped:

            # ---------------------------------------
            # Set values to zero if from_id == to_id
            # ---------------------------------------
            if to_id in values['from_id'].values:
                # Select value
                fromID_equals_toID = values.ix[values['from_id'] == to_id]['from_id']
                # Get index
                fromID_equals_toID_idx = fromID_equals_toID.index
                # Create zero-values list
                zerovalues = [int(fromID_equals_toID), to_id] + zeros
                # Insert the values in the DataFrame
                values.ix[fromID_equals_toID_idx] = zerovalues
                print("Replaced internal cell values for %s" % to_id)
                
            # --------------------------
            # Write results to PostGIS
            # --------------------------
            values.to_sql(DATA_TABLE, engine, if_exists='append', index=False)

