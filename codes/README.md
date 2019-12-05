# Codes: How to reproduce the data?

All the instructions on how to install and use the tools, as well as processing codes and associated documentation are 
organized into the following directories:

 - [MetropAccess-Reititin](MetropAccess-Reititin) -directory contains all the data and documentation related to travel time/distance 
 analyses by **public transport** and **walking**
   - [MetropAccess-Reititin-compiler]() -directory contains documentation and tools for parsing data from the MetropAccess-Reititin results and compiling the data for Helsinki Region Travel Time Matrix.
 - [DORA](DORA) -directory contains all the data and documentation related to travel time/distance 
 analyses by **private car** and **cycling**
   - [DORA-matrix-compiler](DORA-matrix-compiler) -directory contains documentation and tools for parsing data from the DORA results and compiling the data for Helsinki Region Travel Time Matrix. 
 - [tests](tests) -directory contains documentation and scripts related to validation of the data and tools. 
 
 
## Validation

### Travel time matrix against OpenTripPlanner and Google

We have conducted systematic comparisons between our time estimates and estimates obtained from other similar routing tools (OpenTripPlanner and Google Maps).
You can find the scripts and data for producing the validation results in [**here**](tests/comparisons-against-Google-and-OTP).

### DORA tool vs previous ArcGIS tool to produce car travel times

A systematic comparison between the current DORA routing tool (for car) and the previous ArcGIS -based routing tool (that was used to produce the data for years 2013 and 2015) was conducted and the results can be read from [**here**](tests/DORA-validation).
