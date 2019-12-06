import psycopg2
import pandas as pd
import geopandas as gpd
import os
from base import POSTGIS_DB_NAME, IP_ADDRESS, POSTGIS_PORT, POSTGIS_USERNAME, POSTGIS_PWD, DATA_TABLE

def connect_to_DB(host, db_name, username, pwd, port):
    conn_string = "host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (host, db_name, username, pwd, port)
    #print(conn_string)
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    return(conn, cursor)

def createMatrixIndexes(cursor, conn):
    # Create Index for 'to_id' and 'from_id'
    sql = "CREATE INDEX fromididx ON %s (from_id)" % DATA_TABLE
    cursor.execute(sql)
    conn.commit()
    sql = "CREATE INDEX toididx ON %s (to_id)" % DATA_TABLE
    cursor.execute(sql)
    conn.commit()

def createMatrixFolder(outDir, to_id):
    dirname = "%sxxx" % str(to_id)[:4]
    fullpath = os.path.join(outDir, dirname)
    if not os.path.isdir(fullpath):
        os.makedirs(fullpath)
    return fullpath

    

# PostGIS Authentication crecedentials
db_name, host, port, username, pwd = POSTGIS_DB_NAME, IP_ADDRESS, POSTGIS_PORT, POSTGIS_USERNAME, POSTGIS_PWD

# Create connection to Database
conn, cursor = connect_to_DB(host, db_name, username, pwd, port)

# File paths
ykr_fp = "data/MetropAccess_YKR_grid_EurefFIN.shp"
outDir = "HelsinkiRegionTravelTimeMatrix2018"
src_table = "travel_time_matrix_2018"

# Read YKR_grid
ykr = gpd.read_file(ykr_fp)

# --------------------------
# PARSE RESULTS
# --------------------------

# Start & end index for processing (useful if needed to restart processing for some reason)
start_idx = 0
end_idx = 13231

# Create Index for 'to_id' and 'from_id'
createMatrixIndexes(cursor, conn)

# Iterate over individual YKR_IDs and create
for index, row in ykr.iterrows():
    if index >= start_idx and index < end_idx:
        # Get to_id
        to_id = row['YKR_ID']
        print("Processing ID: %s" % to_id) 

        # Get unique 'to_id' values from the db
        sql = """SELECT * FROM %s
                   WHERE to_id = %s;""" % (src_table, to_id)

        # Read data into DataFrame
        data = pd.read_sql_query(sql, conn)

        # Join ('outer') with YKR_ID to find out missing values and sort the values
        data = ykr[['YKR_ID']].merge(data, left_on='YKR_ID', right_on='from_id', how='outer')

        # Drop dublicate values
        data = data.drop_duplicates(subset='YKR_ID')

        # Set 'YKR_ID' value for 'from_id'
        data['from_id'] = data['YKR_ID']

        # Fill NaN values with -1
        data = data.fillna(value=-1)

        # Select output data
        datacols = ['from_id', 'to_id', 'walk_t', 'walk_d', 'bike_f_t', 'bike_s_t', 'bike_d', 'pt_r_tt', 'pt_r_t', 'pt_r_d', 'pt_m_tt', 'pt_m_t',
                    'pt_m_d', 'car_r_t', 'car_r_d', 'car_m_t', 'car_m_d', 'car_sl_t']
        data = data[datacols]

        # Create folder if does not exist
        targetDir = createMatrixFolder(outDir, to_id)
        # Create filename
        outname = "travel_times_to_%s.txt" % to_id
        # Outputpath
        outfile = os.path.join(targetDir, outname)
        # Write results to disk
        data.to_csv(outfile, sep=';', index=False, mode='w', float_format="%.0f")
