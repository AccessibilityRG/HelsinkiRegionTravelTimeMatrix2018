# Public transport calculations with MetropAccess-Reititin 

This document demonstrates step by step, how public transport and walking travel times/distances were calculated using MetropAccess-Reititin -tool.

### Contents
 - [Installations / Configurations](#installations---configurations)
    - [Installing MetropAccess-Reititin + dependencies to Taito](#installing-metropaccess-reititin--dependencies-to-taito)
        - [Nodejs](#nodejs)
        - [MetropAccess-Reititin](#install-metropaccess-reititin)
    
    - [Creating an array job for Taito using Reititin](#array-job-reititin)
        - [Necessary steps](#necessary-steps)
        - [Array job files that were used for Helsinki Region Travel Time/Co2 Matrix 2018](#array-jobs)

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

### Necessary steps for creating an Array Job (\*.lsf -file) for MetropAccess-Reititin

The generic steps for running an array job in Taito is as follows (see the actual job-files from next section).

  1. Define the job range and other Taito related parameters (starting with #SBATCH keyword)
  2. [Swap from Intel compiler to GCC](#swap)
  3. [Export node path to system path](#node-path)
  4. Define MetropAccess-Reititin specific parameters:
     - Kalkati-path
     - Path to MetropAccess-Reititin configuration file
     - Path to folder where origin and destination files are located
     - Name for the result file
     

## Running the Public Transport calculations in Taito

Our calculations was divided on 293 individual subtasks where each task included MetropAccess-Reititin route optimizations from 50 origin locations that are within a single *origin-file.txt*
([an example of a origin file](../../data/PT/Subsets/1_Matrix2015_Origs_WGS84.txt)) to 14 645 destination locations ([see the destination file](../../data/PT/destPoints.txt)). All public transportation origin and destination files that were used in calculations are [here](../../data/PT/). 

<a name='array-jobs'></a>**Here are the array job files that were used when calculating the Helsinki Region Travel Time/CO2 Matrices (2015)**:

  - [Walking](reititin_massaAjo_2015_allday_kavely.lsf)
  - Public Transport:
      - [Rush-hour](reititin_massaAjo_2015_rushhour_joukkoliikenne.lsf)
      - [Midday](reititin_massaAjo_2015_midday_joukkoliikenne.lsf)
  
    
Running the calculations in Taito is done with command (example by walking):

         $ sbatch reititin_massaAjo_2015_allday_kavely.lsf
      

You can check the progress of the tasks with command:


         $ squeue -U $USER

