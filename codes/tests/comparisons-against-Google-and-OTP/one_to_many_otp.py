#!/usr/bin/jython
"""
one_to_many_otp.py

Functions to conduct one to many routings using OpenTripPlanner. One to many routings
are fast to calculate but you get only limited information about the routes with them.
You get only travel time, walking distance, number of boardings. 
If multiple departure times have been defined, the tool will calculate accessibility 
profiles having information about minumum, maximum, mean, median and standard deviation 
of the travel times. 

Notice: 
    Uses Jython for running the OTP. Jython syntax follows Python 2. 
    This makes it possible to use the tool also in HPC clusters where it is not possible 
    to have a separate process (i.e. the OTP server) running using screen.

How to run:
    
    This tool needs to be run from the command line. You need to pass the required 
    input information using arguments.
    
    Examples:
    ---------
        
    # Launch on Windows (with semicolon separater between jython and OTP):
    # Needs to be launched from: /mrouter/bin/
    $ java -cp otp-1.3.0-shaded.jar;jython27.jar org.python.util.jython test_otp.py -g C:\HY-DATA\HENTENKA\KOODIT\Mapple\Jython\Turku -o C:\HY-DATA\HENTENKA\KOODIT\Mapple\Projects\Turun_kaupunki\data\origin-destination\origins\csv\Turku_origs_0.csv -d C:\HY-DATA\HENTENKA\KOODIT\Mapple\Projects\Turun_kaupunki\data\origin-destination\origins\batches500\Turku_origs_0.csv -O C:\HY-DATA\HENTENKA\KOODIT\Mapple\Jython\results -n matrix_test -i ID -I ID

    # Launch on Linux (with colon separater between jython and OTP):
    # Needs to be launched from: /mrouter/bin/
    $ java -cp otp-1.3.0-shaded.jar:jython27.jar org.python.util.jython test_otp.py

Author:
    Dr. Henrikki Tenkanen, Mapple Analytics Ltd.

"""
from __future__ import print_function
from org.opentripplanner.scripting.api import OtpsEntryPoint
import argparse
import csv
import os
import math
import time
import json

def mean(data):
    return sum(data)/len(data)

def variance(data):
    # Use the Computational Formula for Variance.
    n = len(data)
    if n == 1:
        return 0
    ss = sum(x**2 for x in data) - (sum(data)**2)/n
    return ss/(n-1)

def standard_deviation(data):
    if len(data) == 0:
        return 0
    return math.sqrt(variance(data))

def median(data):
    n = len(data)
    if n < 1:
            return None
    if n % 2 == 1:
            return sorted(data)[n//2]
    else:
            return sum(sorted(data)[n//2-1:n//2+1])/2.0
        
def run(origs_fp, dests_fp, graph_dir, output_dir, name_prefix, conf, id_orig_col, id_dest_col):
    """Run one to many routings with OTP"""
    
    # Parse router and graph
    graph_root = os.path.dirname(graph_dir)
    router_name = os.path.basename(graph_dir)
    
    # Time
    year, month, day, hour = conf['year'], conf['month'], conf['day'], conf['hour']
    
    # Departure minutes (can/should be multiple when calculating accessibility profile)
    minutes = conf['minutes']
    
    otp = OtpsEntryPoint.fromArgs([ "--graphs", graph_root, "--router", router_name ])
    
    # set up routing
    router = otp.getRouter()
    r = otp.createRequest()
    
    # Travel modes
    r.setModes( conf['modes'] )

    # Maximum walk distance
    r.setMaxWalkDistance( conf['max_walk'] )
    
    # Timeout for routing
    r.setMaxTimeSec( conf['isochrone_timeout'] ) 
    
    # Include any waiting time it output
    r.setClampInitialWait(0)

    # Walk speed
    r.setWalkSpeedMs(conf['walk_speed'])

    # Bike speed
    r.setBikeSpeedMs(conf['bike_speed'])

    # Create a CSV output
    out_table = otp.createCSVOutput()
    out_table.setHeader(['from_id', 'to_id', 'start_time', 'from_x', 'from_y', 'to_x', 'to_y', 'min_time', 'max_time', 'avg_time', 'median_time', 'std_time', 'walk_dist', 'boardings'])
    
    # Start time
    init_time = time.time()
    
    # Load CSV 
    # Returns iterable which is an array of 
    dests = otp.loadCSVPopulation(dests_fp, 'lat', 'lon')
    
    # Get destination IDs
    dest_ids = []
    for dest in dests:
        dest_ids.append(int(dest.getFloatData(id_dest_col)))
        
    with open(origs_fp) as csv_origs:
            
        origs = csv.DictReader(csv_origs)

        for orig in origs:

            # Get orig id
            orig_id = orig[id_orig_col]

            # Get origin coordinates
            origlat = float(orig['lat'])
            origlon = float(orig['lon'])

            print("Routing from %s" % (orig_id))

            # Dictionary for accessibility profiles
            ap = {}

            for idx, minute in enumerate(minutes):
                print(year, month, day, hour, minute)

                # Set origin for routing
                r.setOrigin(origlat, origlon)

                # Set departure time
                r.setDateTime(year, month, day, hour, minute, 00)  # departure date / time

                # Parse time
                starttime = "{year}-{month}-{day} {hour}:{minute}:{second}".format(year=year, month=str(month).zfill(2),
                                                                                   day=day, hour=str(hour).zfill(2),
                                                                                   minute=str(minute).zfill(2),
                                                                                   second="00")

                # Route from this origin
                spt = router.plan(r)

                # Evaluate
                try:
                    results = spt.eval(dests)
                except AttributeError:
                    # If cannot route from given origin - add NoData rows for all destinations and continue
                    print("Cannot route from origin %s" % orig_id)
                    for destid in dest_ids:
                        # NoData value
                        nd = -1
                        # Add NoData row to profile
                        if destid not in ap.keys():
                            ap[destid] = dict(t=[nd], d=[nd], start=[starttime], b=[nd], lat=[nd], lon=[nd])
                        else:
                            ap[destid]['t'].append(nd)
                            ap[destid]['d'].append(nd)
                            ap[destid]['start'].append(starttime)
                            ap[destid]['b'].append(nd)
                            ap[destid]['lat'].append(nd)
                            ap[destid]['lon'].append(nd)
                    continue

                if results is not None:
                    # Travel times
                    times = [int(round(result.getTime() / 60 + 0.5)) if result.getTime() is not None else -1 for result
                             in results]

                    # Destination ids
                    ids = [int(result.getIndividual().getFloatData('ID')) for result in results]

                    # Destination lats and lons
                    lats = [result.getIndividual().getLocation().getLat() for result in results]
                    lons = [result.getIndividual().getLocation().getLon() for result in results]

                    # Number of boardings
                    # If 0 - the route has been done only by walking
                    # If 1 - one pt line was used
                    # If 2 - one transfer was made
                    # If 3 - 2 transfers was made
                    boardings = [result.getBoardings() for result in results]

                    # Walk distances in meters
                    # walk_dist = [int(round(result.getWalkDistance() + 0.5)) if result.getTime() is not None else -1 for result in results]
                    walk_dists = [result.getWalkDistance() for result in results]

                    # Write result
                    for destid, travel_time, walk_dist, boarding, destlat, destlon in zip(ids, times, walk_dists,
                                                                                          boardings, lats, lons):

                        # Add row to profile
                        if destid not in ap.keys():
                            ap[destid] = dict(t=[travel_time], d=[walk_dist], start=[starttime], b=[boarding],
                                              lat=[destlat], lon=[destlon])
                        else:
                            ap[destid]['t'].append(travel_time)
                            ap[destid]['d'].append(walk_dist)
                            ap[destid]['start'].append(starttime)
                            ap[destid]['b'].append(boarding)
                            ap[destid]['lat'].append(destlat)
                            ap[destid]['lon'].append(destlat)

            # Calculate statistics for all destinations
            for destid, profile in ap.items():
                # Shortest time
                min_time = min(profile['t'])

                # Get id of the fastest route
                fastest_route_idx = profile['t'].index(min_time)

                # Get start time of the fastest route
                starttime = profile['start'][fastest_route_idx]

                # Get walk distance of the fastest route
                walk_dist = profile['d'][fastest_route_idx]

                # Get number of boardings of the fastest route
                boarding = profile['b'][fastest_route_idx]

                # Get latitude and longitude
                destlat = profile['lat'][fastest_route_idx]
                destlon = profile['lon'][fastest_route_idx]

                # Longest time
                max_time = max(profile['t'])
                # Average time
                avg_time = mean(profile['t'])  # int(sum(profile['t']) / len(profile['t']) + 0.5)
                # Median time
                median_time = median(profile['t'])
                # Std time
                std_time = standard_deviation(profile['t'])

                # print destid, starttime, walk_dist, min_time, max_time, avg_time, median_time, std_time

                # Add row
                # Add zero row if origin is same as the destination
                if int(destid) == int(orig_id):
                    out_table.addRow(
                        [orig_id, destid, starttime, origlon, origlat, destlon, destlat, 0, 0, 0, 0, 0, 0, 0])
                else:
                    out_table.addRow(
                        [orig_id, destid, starttime, origlon, origlat, destlon, destlat, min_time, max_time, avg_time,
                         median_time, std_time, walk_dist, boarding])

        # Save the result
        outname = "%s.csv" % name_prefix
        outfp = os.path.join(output_dir, outname)
        out_table.save(outfp)

        # Time
        endtime = time.time()

        print("Saved results to: %s" % outfp)
        print("It took ", int(endtime - init_time) / 60, "minutes.")

        
if __name__ == "__main__":
    
    # Initialize arguments
    ap = argparse.ArgumentParser()
    
    # Define the arguments
    ap.add_argument("-g", "--graphs", required=True,
                    help="Path to the root directory containing the OpenTripPlanner graph.")
    ap.add_argument("-o", "--origins", required=True,
                    help="Path to the shapefile containing the origin points in WGS84 projection.")
    ap.add_argument("-d", "--destinations", required=True, 
                    help="Path to the shapefile containing the destination points in WGS84 projection.")
    ap.add_argument("-c", "--conf", required=False, default=None,
                    help="Path to the configuration file (e.g. conf.json) containing parameters used in routing.")
    ap.add_argument("-O", "--outdir", required=True, 
                    help="Path to the directory where the results will be stored.")
    ap.add_argument("-n", "--name", required=True, 
                    help="Name prefix that will be used in the filename of the result files.")
    ap.add_argument("-i", "--idorigs", required=False, default=None,
                    help="Custom id column from origins that will be saved into results.")
    ap.add_argument("-I", "--iddests", required=False, default=None,
                    help="Custom id column from destinations that will be saved into results.")
    
    # Parse the arguments
    args = vars(ap.parse_args())
    graph_dir = args['graphs']
    origins = args['origins']
    destinations = args['destinations']
    conf = args['conf']
    outdir = args['outdir']
    outname = args['name']
    id_origs = args['idorigs']
    id_dests = args['iddests']
    
    # Read routing parameters from JSON
    conf = json.loads(open(conf).read())

    # Run
    run(origs_fp=origins, dests_fp=destinations, 
        graph_dir=graph_dir, 
        output_dir=outdir, name_prefix=outname,
        conf=conf, id_orig_col=id_origs, id_dest_col=id_dests)
    
    # Run with
    "java -cp otp.jar;jython.jar org.python.util.jython test_otp.py -g C:\HY-DATA\HENTENKA\KOODIT\Mapple\Jython\Turku -o C:\HY-DATA\HENTENKA\KOODIT\Mapple\Projects\Turun_kaupunki\data\origin-destination\origins\csv\Turku_origs_0.csv -d C:\HY-DATA\HENTENKA\KOODIT\Mapple\Projects\Turun_kaupunki\data\origin-destination\origins\batches500\Turku_origs_0.csv -O C:\HY-DATA\HENTENKA\KOODIT\Mapple\Jython\results -n matrix_test -i ID -I ID"
        