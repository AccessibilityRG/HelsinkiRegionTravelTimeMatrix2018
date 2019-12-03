# Travel time/distance calculations with MetropAccess-Reititin 

This document demonstrates step by step, how public transport and walking travel times/distances were calculated using MetropAccess-Reititin -tool.

### Contents
 - [Installations / Configurations](#installations---configurations)
    - [Installing MetropAccess-Reititin + dependencies to Taito](#installing-metropaccess-reititin--dependencies-to-taito)
        - [Nodejs](#nodejs)
        - [MetropAccess-Reititin](#install-metropaccess-reititin)
    
    - [Creating an array job for Taito using Reititin](#array-job-reititin)
        - [Necessary steps](#necessary-steps)
        - [Array job files that were used for Helsinki Region Travel Time/Co2 Matrix 2018](#array-jobs)
 
 - [Running the public transport / walking calculations in Taito](#running-the-public-transport-calculations-in-taito)
   - Preparations:
     - [Origin-Destination locations](#origin-destination-locations)
     - [Configurations for the routings](#configurations-for-the-routings)
     - [Batch job files for distributing/executing the analyses in Taito](#batch-job--files-for-executing-the-analyses) 
   - Analyses:
     - [Basic syntax for running MetropAccess-Reititin](#basic-syntax-for-running-metropaccess-reititin)
     - [Batch jobs used for PT/walking analyses](#array-jobs)
     - [Reproducing the data with other HPC infrastucture](#reproducing-the-data-with-other-hpc-infrastructure)

## Installations  / Configurations

Public transport calculations were conducted with Taito Supercomputer provided by CSC Finland. Here you can find the documentation regarding configurations and installations in Taito so that it is possible to run MetropAccess-Reititin in Taito. 
Our calculation problem is of type ['embarassingly parallel'](https://en.wikipedia.org/wiki/Embarrassingly_parallel), i.e. it is possible to distribute the calculations to as many computing cores as possible. We use [Taito Array Jobs](https://research.csc.fi/taito-array-jobs) for this purpose. 

### Installing MetropAccess-Reititin + dependencies to Taito

MetropAccess-Reititin is written in Javascript and running it locally requires node.js to be installed.  

<a name='nodejs'></a> **Install *node.js* to Taito**:

   - Create folders for nodejs to appl_taito:
   
         $ mkdir -p $USERAPPL/nodejs
         
   - Download the version 4.1.2 of node.js (source files) and extract it (here files will be located in *node-v4.1.2* ==> Change accordingly to what is the version you use):
          
          $ cd $USERAPPL/nodejs
          $ wget https://nodejs.org/download/release/v4.1.2/node-v4.1.2.tar.gz
          $ tar xf node-v4.1.2.tar.gz
                      
   - Install node.js:
   
      - <a name='swap'></a>Swap from Intel to GCC compiler ( *this step is needed every time you use MetropAccess-Reititin in Taito* ):
            
             $ module swap intel gcc
            
      - Configure and install nodejs (we use version 4.1.2 here --> there have been some building problems with certain nodejs versions)
      
             $ cd $USERAPPL/nodejs/node-v4.1.2
             $ ./configure --prefix=$USERAPPL/nodejs/node-v4.1.2
             $ make
             $ make install
           
   - <a name='node-path'></a>Export node path to system path ( *this step has to be done every time you start using MetropAccess-Reititin in Taito* )
   
         $ export PATH=${PATH}:${USERAPPL}/nodejs/node-v4.1.2/bin
          
   - Check that node works (should open a node shell ==> exit by pressing **CNTRL + C** two times)
     
         $ node
       
### Install MetropAccess-Reititin

  - Make directory for MetropAccess-Reititin:
        
         $ mkdir $USERAPPL/reititin
       
  - Download the Linux version of the MetropAccess-Reititin:
  
        $ cd $USERAPPL/reititin
        $ wget http://www.helsinki.fi/science/accessibility/tools/MetropAccess-Reititin/MetropAccess-Reititin_Linux.tar.gz
         
  - Extract the contents
         
        $ tar xf MetropAccess-Reititin_Linux.tar.gz
         
  - Check that reititin works in Taito (should start making a test routing) 
  
        $ cd $USERAPPL/reititin/reititin/build
        $ ./route.sh
      

### Creating an array job for Taito using Reititin

Running MetropAccess-Reititin in parallel in Taito can be done easily using Taito **Array Jobs**.
Using array jobs it is possible to divide the calculations to multiple separate jobs running on a different CPU. 
A guide how to create an array job in Taito can be found from [here](https://research.csc.fi/taito-array-jobs).   

### Steps for distributing the MetropAccess-Reititin runs with array jobs

The calculations with MetropAccess-Reititin are distributed into 294 subtasks using Taito Supercomputer. This distribution work is controlled with specific `*.lsf` -files (Slurm batch job files) that reminds normal Linux shell files where you can execute things line by line, but the batch job files has some specific parameters that can be used to distribute the work into multiple cores/nodes in Taito (see [more documentation from here](https://research.csc.fi/csc-guide-batch-jobs)). The generic steps for running an array job in Taito is as follows (see the actual job-files from next section).

  1. Define the job range and other Taito related parameters (starting with #SBATCH keyword)
  2. [Swap from Intel compiler to GCC](#swap)
  3. [Export node path to system path](#node-path)
  4. Define MetropAccess-Reititin specific parameters:
     - Kalkati-path
     - Path to MetropAccess-Reititin configuration file
     - Path to folder where origin and destination files are located
     - Name for the result file     

## Running the Public Transport calculations in Taito

### Origin-destination locations

Our travel time/distance calculations were divided into 294 individual subtasks where each task included MetropAccess-Reititin routings from 50 origin locations that are within a single *origin-file.txt* ([see an example of a origin file](data/1_Origs_WGS84.txt)) to 14645\* destination locations ([see the destination file](data/destPoints_WGS84.txt)). All the origin and destination files that were used with MetropAccess-Reititin are [here](data/). The origin and destination locations represent the centroids of the [250 meter grid](data/MetropAccess_YKR_grid.geojson) that can be used for visualizing the travel times.

\* *the origin-destination files include extra cells around the region (2 km buffer) for testing purposes, that are excluded from the final dataset containing 13 231 grid cells.*

### Configurations for the routings

Controlling the routing parameters with MetropAccess-Reititin happens with dedicated configuration files where it is possible to adjust various aspects in the analyses, such as time of the day, date of the analysis and walking speed. These files are passed for MetropAccess-Reititin tool as one of input parameters when executing the tool (see next sections).   

The configuration files used to produce the Helsinki Region Travel Time Matrix:

  - [Walking: conf2018_walking_allDay.json](job-files/conf2018_walking_allDay.json)
  - [Public Transport, midday - conf2018_pt_midday.json](conf2018_pt_midday.json)
  - [Public Transport, rush hour - conf2018_pt_rushhour.json](job-files/conf2018_pt_rushhour.json)

### Batch job -files for executing the analyses

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
