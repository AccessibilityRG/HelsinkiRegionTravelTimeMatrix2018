# Travel time/distance calculations with DORA
 
This document demonstrates how car and cycling travel times/distances were calculated using [DORA -tool](https://github.com/DigitalGeographyLab/DORA).

### Contents
 - [Installations / Configurations](#installations---configurations)
   - [Installing DORA + Dependencies](#installing-dora--dependencies)
     - [Required Python packages](#required-python-packages)
     - [Install DORA](#install-dora)
 - [Running the car / cycling calculations with DORA](#running-the-carcycling-calculations-with-dora)
   - Preparations:
     - [Origin-Destination locations](#origin-destination-locations)
     - [Configurations for the routings](#configurations-for-the-routings)
   - Analyses:
     - [Basic syntax for running MetropAccess-Reititin](#basic-syntax-for-running-metropaccess-reititin)
     - [Distributing the work](#distributing-the-work)
     

## Installations  / Configurations

Car / cycling calculations were conducted with cPouta computing environment provided by CSC Finland. Here you can find the documentation regarding configurations and installations so that it is possible to run DORA on a Linux machine. 
Our calculation problem is of type ['embarassingly parallel'](https://en.wikipedia.org/wiki/Embarrassingly_parallel), i.e. it is possible to distribute the calculations to as many servers as possible. However, PostgreSQL/PostGIS with **routing capabilities** is not optimal for distributing the work, as [pgRouting](https://pgrouting.org/) (a routing tool built for PostGIS) does not work with [Postgres-XL](https://www.postgres-xl.org/) that would provide easily scalable solutions for creating a PostgreSQL/PostGIS computing cluster and distributing the workload.

### Installing DORA + dependencies

Door-to-door Routing Analyst or DORA for short is an open source multi modal routing tool. It uses the door-to-door approach when retrieving travel times where the whole travel chain is taken into account. DORA is implemented with the open source database software PostgreSQL and its spatial extension PostGIS and it's making use of the routing library pgRouting. It can be used to route car, cycling and walking routes and is able to read any road network setup in a database with pgRouting (v2.3.2) extension.  

#### Required Python packages

We recommend using [conda package manager](https://www.anaconda.com/distribution/) (available in Anaconda Python distribution) for installing the required Python libraries.
*For windows, Microsoft Visual C++ 9.0 is required. Get it from [here][microsoft-vistual-c++]*.

Install Python packages with conda/pip:

```
$ conda install -c conda-forge owslib pyproj psycopg2 geopandas networkx
$ conda install -c anaconda joblib psutil
$ pip install nvector
```
\* *nvector (not available in conda repositories)*

#### Install DORA

You can install DORA by cloning it's repository (with Git) to your computer and adding its location to your system path, as follows:

```
$ git clone https://github.com/DigitalGeographyLab/DORA.git
``` 

Add the directory of the `DORA` repository that you downloaded in the previous step into the [__main__.py] file (you should find it from `/../DORA/src/main/__main__.py`).

In that file, you should modify the `sys.path.append('/dgl/codes/DORA/')` in a way that it points to your local DORA directory, such as:
````python
sys.path.append('/my_username/my_softwares/DORA/')
````

## Preprocessing steps before routing
### CAR: Assigning intersection delays for the road network

Before populating the database with Digiroad data (road network used with driving), we create new cost attributes into the data that takes into account the deceleration effect of congestion to driving speeds in cities. This is done by using a so called intersection delay model that was developed for Helsinki Region based on [floating-car data](https://en.wikipedia.org/wiki/Floating_car_data) (documented in [Jaakkola 2013](https://blogs.helsinki.fi/accessibility/files/2019/12/TimoJaakkola_Paikkatietopohjainen_menetelma_autoilun_ajoaikojen_ja_kokonaismatka-aikojen_mallintamiseen.pdf)), and assigning for each road segment three different drivethrough times:
 
 1. Speed limit based drive-through time
 2. Drive-through time according rush hour traffic
 3. Drive-through time according midday traffic
 
 For calculating the intersection delayd drive-through impedances, we developed a dedicated Python tool called [digiroad2_intersection_delay_tool.py](digiroad-preprocessor/digiroad2_intersection_delay_tool.py). The tool should be used with openly available [Digiroad road network data](https://vayla.fi/web/en/open-data/digiroad/data) using the K-delivery format of the Digiroad data (see [details from here](https://vayla.fi/web/en/open-data/digiroad/data)).  The tool requires three files from the Digiroad: 
  1. DR_LINKKI_K ("road segments")
  2. DR_NOPEUSRAJOITUS_K ("road segments with speed limit information")
  3. DR_LIIKENNEVALO ("traffic signals")
  
You should modify the filepaths at the end of the [code](digiroad-preprocessor/digiroad2_intersection_delay_tool.py) by adjusting the following lines:
```
# =================
# File paths
# =================
data_folder = "/my_user/My_Digiroad_Data_Folder"
link_fp = os.path.join(data_folder, "DR_LINKKI_K.shp")
limits_fp = os.path.join(data_folder, "DR_NOPEUSRAJOITUS_K.shp")
signals_fp = os.path.join(data_folder, "DR_LIIKENNEVALO.shp")
```
After modifying this you can run the tool e.g. from command prompt by calling:

`$ python digiroad2_intersection_delay_tool.py`

### BIKE: Preprocessing of the cycling network

For cycling analyses, we built a customized routing network called [MetropAccess-CyclingNetwork](data/MetropAccess-CyclingNetwork.zip) by utilizing GPS data from Strava sport tracker application from year 2016 (see [a sample of the network here](data/MetropAccess-CyclingNetwork_EPSG_4326_sample.geojson)). The Strava dataset is based on data from 5223 unique users. We first linked the GPS points to the closest streets with customized map matching techniques 20,21. Then we identified the roads that are most commonly used by cyclists and calculated user based cycling speeds for different road segments. Finally, we aggregated this information into an average travel speed per segment. 

Further details on how the Strava data was processed can be found from [Tarnanen (2017)](https://blogs.helsinki.fi/accessibility/files/2017/11/Gradu_Tarnanen_A.pdf), and [Tarnanen, Salonen, Willberg & Toivonen (2017)](https://www.hel.fi/static/liitteet/kaupunkiymparisto/julkaisut/julkaisut/julkaisu-16-17.pdf). Python scripts that were used to preprocess the cycling network can be found from [here](https://github.com/ainoT/pyoraily-matka-aikamalli). 

### Populating the PostgreSQL with road network data

Before it is possible to use DORA for travel time analyses, it is required to populate the PostGIS tables with street network datasets for car and cycling. The following sections documents how to do these steps. 

#### Digiroad

After the Digiroad data has been adjusted by assigning the intersection delays (see above), you can populate the PostGIS table with the road network and initialize the routing network for processing. A good tutorial on how to populate the PostGIS database for routing can be found from [here](https://mixedbredie.github.io/pgrouting-workshop/). We used `ogr2ogr` to populate the data into the database with following commands (comes with [GDAL](https://gdal.org/programs/ogr2ogr.html) that is installed together with required Python libraries).

Add the Digiroad network to PostGIS database (`"my_database"` needs to exist, and it should NOT have a table called `intersection_delayed_digiroad`):

`$ ogr2ogr -select "AJOSUUNTA, KmH, Pituus, Digiroa_aa, Keskpva_aa, Ruuhka_aa" -where "AJOSUUNTA<>''" -nlt PROMOTE_TO_MULTI -f PostgreSQL PG:dbname=my_database intersection_delayd_Digiroad.shp`

where `AJOSUUNTA` is allowed driving direction, `KmH` is the speed limit for the given road segment, `Pituus` is length of the road segment (in meters), `Digiroa_aa` is the drive-through time in minutes based on speed limits, `Keskpva_aa` is the drive-through time in minutes based on midday traffic conditions, and `Ruuhka_aa` is the drive-through time in minutes based on rush hour traffic conditions.

After the car network data has been successfully uploaded to the database, you need to modify the table by adding new columns to the table that represents the source and target nodes on each edge (first/last vertex of each line). The following SQL commands should be run inside the database:

- Create new columns
  ```
  ALTER TABLE public.intersection_delayed_digiroad
    ADD COLUMN source integer,
    ADD COLUMN target integer,
    ADD COLUMN x1 double precision,
    ADD COLUMN y1 double precision,
    ADD COLUMN x2 double precision,
    ADD COLUMN y2 double precision;
  ```

- Get the start/end points of the lines (i.e. nodes)
   ```
   UPDATE public.intersection_delayed_digiroad
      SET x1 = st_x(st_startpoint(geometry)),
        y1 = st_y(st_startpoint(geometry)),
        x2 = st_x(st_endpoint(geometry)),
        y2 = st_y(st_endpoint(geometry));
   ```
- create a routable network from it with [pg_routing](http://pgrouting.org/) -extension of PostGIS:
   ```
   SELECT public.pgr_createTopology('public.intersection_delayed_digiroad', 100, 'geometry', 'gid', 'source', 'target');
   ```
After these steps the car network is ready for routing with DORA.   
  
#### Cycling 

Populating the cycling tables in PostGIS follows more or less the same steps as with car. 

Add the Digiroad network to PostGIS database (`"my_database"` needs to exist, and it should NOT have a table called `metropaccess_cyclingnetwork`):

`$ ogr2ogr -select "Pituus, pros, Fast_speed, Slow_speed, Fast_time, Slow_time" -nlt PROMOTE_TO_MULTI -f PostgreSQL PG:dbname=my_database MetropAccess-CyclingNetwork.shp`

- Create new columns
  ```
  ALTER TABLE public.metropaccess_cyclingnetwork
    ADD COLUMN source integer,
    ADD COLUMN target integer,
    ADD COLUMN x1 double precision,
    ADD COLUMN y1 double precision,
    ADD COLUMN x2 double precision,
    ADD COLUMN y2 double precision;
  ```

- Get the start/end points of the lines (i.e. nodes)
   ```
   UPDATE public.metropaccess_cyclingnetwork
      SET x1 = st_x(st_startpoint(geometry)),
        y1 = st_y(st_startpoint(geometry)),
        x2 = st_x(st_endpoint(geometry)),
        y2 = st_y(st_endpoint(geometry));
   ```
- create a routable network from it with [pg_routing](http://pgrouting.org/) -extension of PostGIS:
   ```
   SELECT public.pgr_createTopology('public.metropaccess_cyclingnetwork', 100, 'geometry', 'gid', 'source', 'target');
   ```
After these steps the cycling network is ready for routing with DORA.

## Running the car/cycling calculations with DORA
### Origin-destination locations

Our travel time/distance calculations were divided into 293 individual subtasks where each task included DORA routings from 50 origin locations that are within a single *origin-file.geojson* ([see an example of a origin file](data/Origin-subsets/1_Origs_WGS84.geojson)) to 13231 destination locations ([see the destination file](data/destination_Points_WGS84.geojson)). All the origin and destination files that were used with DORA are [here](data/). The origin and destination locations represent the centroids of the [250 meter grid](data/MetropAccess_YKR_grid.geojson) that can be used for visualizing the travel times.

### Configurations for the routings

Controlling the routing parameters with DORA happens with dedicated configuration files where it is possible to adjust various aspects in the analyses, such as the impedance (cost/weight attribute) used for finding the shortest paths.   

The configuration files used to produce the Helsinki Region Travel Time Matrix with car/cycling:

### Running the analyses with DORA

### Basic syntax for running DORA

Running DORA can be conducted with following command:
```$ python -m src.main -s <../startPointsFolder> -e <../endPointsFolder> -o <../outputFolder> -t BICYCLE -c BICYCLE_FAST_TIME --summary --is_entry_list
```
where:

 - ```-s```: Path to the Geojson file containing the set of __origin__ points (or the directory containing a set of Geojsons).

- ```-e```: Path to the Geojson file containing the set of __target__ points (or the directory containing a set of Geojsons).

- ```-o```: Path where store the output data.

- ```-t```: Flag to choose the transport mode for the data analysis [PRIVATE_CAR, BICYCLE].

- ```-c```: The impedance/cost attribute to calculate the shortest path.

- ```--route```: Store in the output folder the geojson files with the fastest route LineString features.

- ```--summary```: Store in the output folder the csv files containing the fastest travel time summary per each pair of entry points.

- ```--is_entry_list```: Define if the ```-s``` and ```-e``` are folders paths and not file paths.


Impedance/Cost ```-c``` attribute accepted values:

  * DISTANCE (Both PRIVATE_CAR and BICYCLE)
  * RUSH_HOUR_DELAY (PRIVATE_CAR only)
  * MIDDAY_DELAY_TIME (PRIVATE_CAR only)
  * DAY_AVG_DELAY_TIME (PRIVATE_CAR only)
  * SPEED_LIMIT_TIME (PRIVATE_CAR only)
  * BICYCLE_FAST_TIME (BICYCLE only)
  * BICYCLE_SLOW_TIME (BICYCLE only)
