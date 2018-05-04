# Matrix 2018 todo list

Here are the practical steps that needs to be done to compile HelsinkiRegionTravelTimeMatrix 2018.

The final product that we will share as the Helsinki Region Travel Time Matrix is a compressed zip file that contains
around 13 300 textfiles that are distributed into subfolders (see the structure from old version of the Matrix [here](https://blogs.helsinki.fi/accessibility/helsinki-region-travel-time-matrix-2015/)). Each text file contain travel time and distance information from all YKR-grid cells to a specific
target location with four different travel modes.

A single text file such as `travel_times_to_5975312.txt` should contain following information (an example):

```
from_id;to_id;walk_t;walk_d;pt_r_tt;pt_r_t;pt_r_d;pt_m_tt;pt_m_t;pt_m_d;car_r_t;car_r_d;car_m_t;car_m_d;bike_s_t;bike_f_t;bike_d
5785640;5975312;511;35737;177;146;41819;191;159;51258;62;46353;55;46353;168;107;35737
5785641;5975312;492;34431;171;149;42025;189;162;51464;63;46564;55;46564;162;103;34431
5785642;5975312;493;34510;171;151;42142;190;164;51582;70;45965;62;44189;163;104;34510
...
...
```

## Steps for producing the matrix

Producing the Travel Time Matrix 2018 requires following steps:

1. Calculate the travel times with car, bike, walking and PT using two different timelevels (midday / rushhour) or two different kind of cyclist (fast / slow)
2. Gather all data into same location (a local computer with enough disk space)
3. Push all data from the raw result files into a single PostgreSQL table with required columns (from_id, to_id ,walk_t, walk_d, pt_r_tt, pt_r_t, pt_r_d, pt_m_tt, pt_m_t, pt_m_d, car_r_t, car_r_d, car_m_t, car_m_d, bike_s_t, bike_f_t, bike_d)

   - There is a ready made script from last Matrix that can be used as a template for parsing the necessary information from the result files of different transport modes (needs some modification to read the data from new car and bike routing results. See [this script](https://github.com/AccessibilityRG/HelsinkiRegionTravelTimeMatrix2015/blob/master/codes/Python-PostGIS/Matriisi2015_Compiler_accessibility_PostGIS.py)
   - An example of how the PT raw result file looks can be seen from [here](samples/Laru_test.txt)

4. Once all the data is in the PostgreSQL table, create the Helsinki Region Matrix by modifying [this script](https://github.com/AccessibilityRG/HelsinkiRegionTravelTimeMatrix2015/blob/master/codes/Python-PostGIS/Matrix2015_Parse_TextMatrix_from_PostGIS.py)

   - Todo: Add columns for `bike_s_t, bike_f_t, bike_d`

5. Once all data is compiled run some test visualizations with different travel modes to see that the travel times and patterns look more or less intuitive

   - Elias and other locals can help interpreting the results

6. Update the licence information and the metadata for 2018 version of the Matrix

   - An example of the old metadata that can be used as template can be read from [METADATA_Helsinki-Region-Travel-Time-Matrix-2015.txt](samples/METADATA_Helsinki-Region-Travel-Time-Matrix-2015.txt).
   - **Notice:** The details about the tool that has been used to calculate the car and bike travel times needs to be updated (the information can be similar but updated with the information about the new routing tool)
   - Update the people who were involved in producing the matrix, i.e. Jeison, Elias, Henrikki and Tuuli (add Juha, Maria, Timo, Ainokaisa, Vuokko to people who have been contributing previously)
   - Update the latest publications list (ask Tuuli about these)
   - Overall, ask help from Tuuli if needed when writing the metadata
   - Create DOI for the dataset in Researchgate (you can get a DOI from there), see template from Henrikki's profile for Helsinki Region Travel Time Matrix 2015)

7. Once, the Travel Time Matrix is done, compress the folder into a Zip file with all text files distributed into a subfolders (e.g. `5990xxx`). Place the metadata file into the root of the matrix folder.

8. The travel time matrix (`HelsinkiRegion_TravelTimeMatrix2018.zip`) should be uploaded into our website under the folder `www.helsinki.fi/science/accessibility/data/helsinki-region-travel-time-matrix/2018`

   - Vuokko should be able to access that folder from her computer easily so ask help from Vuokko to place the zip file there.

9. Prepare documentation for the blogsite with updated information about the changed tools and added transport mode.

10. Prepare a slideshow showing the differences between previous matrix and the current one (Elias can help with this)

   - How accessibility differs especially after the new Länsi-metro line (but also the ones that were [presented in the last Matrix](https://www.slideshare.net/AccessibilityRG/what-changes-can-be-observed-between-helsinki-region-travel-time-matrix-2013-and-2015)).
   - Prepare a similar slideshow

11. Release and promote! :)
