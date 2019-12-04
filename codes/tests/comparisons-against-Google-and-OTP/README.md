# Travel time comparisons

For validation results, see the article:

 - Tenkanen, H. & T. Toivonen. Helsinki Region Travel Time Matrix: Multidimensional accessibility data to support spatial planning and decision making. *Scientific Data*.

-----

Comparisons between DORA and MetropAccess-Reititin against Google and OpenTripPlanner are used to estimate the data quality.

A systematic assessment of the data quality was done by comparing the travel time estimates 
to other data sources based on a random sample of 100 locations in the region. 

To estimate the data quality of our public transport travel time estimates, 
we calculated routes between all sample points (9 900 origin-destination connections) 
with MetropAccess-Reititin and OpenTripPlanner using the same 
schedules as we used with MetropAccess-Reititin: January 29th 2018 at 7 am with 10 different departure times 
according Golomb ruler (see Methods section). 

For private car, we compared our rush hour car travel times to drive times obtained from Google Maps website. 
Travel time estimates from Google Maps takes into account traffic conditions on the roads at different times of the day, 
and provides typical travel times for given hour of the day. Travel times on Google Maps are reported as 
time ranges (such as, “typical travel time is 22-28 minutes”) where the lower value represents time without congestion effect, 
and the upper value represents travel time in which congestion has affected the trip duration. 
We calculated arithmetic mean travel time based on the lower and upper values of Google’s travel time estimates 
following the traffic conditions of Monday 6th of May 2019 (a normal workday). Furthermore, additional 3 minutes were added to 
these travel times to approximate the time it takes to find a parking lot, 
and walk to/from the car (following the door-to-door approach). These values were then compared against average travel time estimates 
based on DORA tool. The average travel times by DORA were also calculated as an arithmetic mean based 
on the freeflow (column car_sl_t) and rush hour travel times (column car_r_t). 

## Steps to produce validation data with OpenTripPlanner

You can reproduce the validation data by OpenTripPlanner with following steps:

 1. Build the OTP graph for Helsinki Region by running [build_otp_graph.py](build_otp_graph.py)
 2. Calculate walking times with OTP by running [run_otp_validation_tests_walk.py](run_otp_validation_tests_walk.py)
 3. Calculate cycling times with OTP by running [run_otp_validation_tests_bike.py](run_otp_validation_tests_bike.py)
 4. Calculate public transport times with OTP by running [run_otp_validation_tests_pt.py](run_otp_validation_tests_pt.py)

After these steps, you should have travel time estimates by walking, cycling and public transport in [validation](validation) directory.

## Steps to produce validation data from Google maps

Before running the following tool, you need to have [ChromeDriver](https://chromedriver.chromium.org/downloads) and 
Python packages [Selenium](https://selenium-python.readthedocs.io/installation.html) and [Pandas](https://pandas.pydata.org/) installed.

To reproduce the validation data from Google Maps run the following script:
 
 1. [retrieve_car_travel_times_from_google_maps.py](retrieve_car_travel_times_from_google_maps.py)

After running the script, you should have travel time estimates by car in [validation](validation) directory.

## Calculate travel time differences against Helsinki Region Travel Time Matrix

For calculating and plotting the travel time differences between travel time estimates 
in Helsinki Region Travel Time Matrix and estimates obtained from Google Maps and OpenTripPlanner
run the following script:

 1. [travel_time_validations_and_visualizations_by_all_travel_modes.py](travel_time_validations_and_visualizations_by_all_travel_modes.py)