# Travel time/distance calculations with DORA
 
This document demonstrates how car and cycling travel times/distances were calculated using [DORA -tool](https://github.com/DigitalGeographyLab/DORA).

### Contents
 - [Installations / Configurations](#installations---configurations)
   - [Installing DORA + Dependencies](#installing-dora--dependencies)
     - [Required Python packages](#required-python-packages)
     - [Install DORA](#install-dora)
 - [Running the car / cycling calculations with DORA](#running-the-public-transport-calculations-in-taito)
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

## Running the car/cycling calculations on Linux

### Assigning intersection delays for the road network

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

### Populating the PostgreSQL with road network data



### Origin-destination locations

Our travel time/distance calculations were divided into 293 individual subtasks where each task included DORA routings from 50 origin locations that are within a single *origin-file.geojson* ([see an example of a origin file](data/Origin-subsets/1_Origs_WGS84.geojson)) to 13231 destination locations ([see the destination file](data/destination_Points_WGS84.geojson)). All the origin and destination files that were used with DORA are [here](data/). The origin and destination locations represent the centroids of the [250 meter grid](data/MetropAccess_YKR_grid.geojson) that can be used for visualizing the travel times.

### Configurations for the routings

Controlling the routing parameters with DORA happens with dedicated configuration files where it is possible to adjust various aspects in the analyses, such as the impedance (cost/weight attribute) used for finding the shortest paths.   

The configuration files used to produce the Helsinki Region Travel Time Matrix with car/cycling:



#### Basic syntax for running MetropAccess-Reititin

The basic syntax for running the MetropAccess-Reititin is as follows (in Linux):

`$ route.sh {origin-text-file.txt} {destination-text-file.txt} --out-avg={result-file.txt} --base-path={kalkati-schedule-data-directory} --conf={routing-configuration-file.json}`

\* *On Windows, everything works in a similar manner except instead of calling `route.sh`, you should call `route.bat`.*

#### Array jobs

The following batch job files (\*.lsf) are used to distribute the calculations and which produce the Helsinki Region Travel Time Matrix (2018):

  - [Walking - reititin_massaAjo_2018_allday_kavely.lsf](job-files/reititin_2018_allday_walking.lsf)
  - Public Transport:
      - [Rush-hour - reititin_massaAjo_2018_rushhour_joukkoliikenne.lsf](job-files/reititin_2018_rushhour_joukkoliikenne.lsf)
      - [Midday - reititin_massaAjo_2018_midday_joukkoliikenne.lsf](job-files/reititin_2018_midday_joukkoliikenne.lsf)

These \*.lsf files contains all steps that were used to produce the travel time and distance information for public transport/walking. Each of the executable files follow the same basic steps described in [Steps for distributing the MetropAccess-Reititin runs with array jobs](#steps-for-distributing-the-metropaccess-reititin-runs-with-array-jobs). 

Executing the calculations in Taito is done with command (example by public transport at midday):

         $ sbatch reititin_massaAjo_2018_midday_PT.lsf
      

You can check the progress of the tasks with command:

         $ squeue -U $USER
         
The result files will be saved into the directory defined in the \*.lsf file with following parameter:

```
# Path to Results
RESULTS=$WRKDIR/Results/Matrix2018/Midday/PT
```

#### Reproducing the data with other HPC infrastructure

The documentation here focuses on demonstrating how the calculations were done using SLURM batch job system at CSC Finland. However, it is certainly possible to use any HPC (High Performance Computing) infrastructure that supports SLURM (Simple Linux Utility for Resource Management System), and it possible to set it up for example in Amazon Web Services (see [documentation here](https://aws.amazon.com/blogs/compute/deploying-a-burstable-and-event-driven-hpc-cluster-on-aws-using-slurm-part-1/)).


