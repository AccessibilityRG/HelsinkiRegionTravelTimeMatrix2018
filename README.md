# Helsinki Region Travel Time Matrix 2018
This repository demonstrates / documents how __[Helsinki Region Travel Time Matrix 2018](http://blogs.helsinki.fi/accessibility/helsinki-region-travel-time-matrix-2018/)__ is calculated. 
Dataset was produced by [Accessibility Research Group / Digital Geography Lab](http://www.helsinki.fi/science/accessibility), University of Helsinki.

__Contents:__

- [What is Helsinki Region Travel Time Matrix 2018?](#What-is-Helsinki-Region-Travel-Time-Matrix-2018)
- [Attributes of Helsinki Region Travel Time Matrix 2018](#attributes)
- [How calculations were done?](#calculations)
  - [Walking](#walk)
  - [Cycling](#cycling)
  - [Public Transport](#pt)
  - [Private car](#car)
- [Licence](#license)
- [How to cite this work?](#how-to-cite)
- [Codes: How to reproduce the results?](#code-repo)
- [Contribution / Contact](#contact)

## What is Helsinki Region Travel Time Matrix 2018?
 
[__Helsinki Region Travel Time Matrix 2018__](http://www.helsinki.fi/science/accessibility/data) is a dataset that contains travel time and distance information of the route that have been calculated from all 250 m x 250 m grid cell centroids (n = 13231) in the Capital Region of Helsinki ([see this map](http://www.helsinki.fi/science/accessibility/tools/YKR/YKR_Identifier.html)) by walking, cycling, public transportation (PT) and private car. Calculations were done separately for two different time of the day using rush hour (08:00-09:00) and midday (12:00-13:00) schedules/traffic conditions. The grid cells are compatible with the statistical grid cells in the YKR (yhdyskuntarakenteen seurantajärjestelmä) data set produced by the Finnish Environment Institute (SYKE). 
   
Dataset is openly available for everyone for free and it can be downloaded from the [Accessibility Research Group website](http://www.helsinki.fi/science/accessibility/data) (under a Creative Commons 4.0 Licence, see [licence text](#license)).
 

## <a name="attributes"></a>Attributes of Helsinki Region Travel Time Matrix 2018

| Attribute | Definition |
| --------- | ---------- | 
| __from_id__   | ID number of the origin grid cell |
| __to_id__     | ID number of the destination grid cell |
| __walk_t__    | Travel time from origin to destination by walking | 
| __walk_d__    | Distance (meters) of the walking route | 
| __bike_f_t__  | Total travel time in minutes from origin to destination by fast cycling (~19 km/h); Includes extra time (1 min) that it takes to take/return bike | 
| __bike_s_t__  | Total travel time in minutes from origin to destination by slow cycling (~12 km/h); Includes extra time (1 min) that it takes to take/return bike | 
| __bike_d__    | Distance in meters of the cycling route | 
| __pt_r_tt__   | Travel time from origin to destination by public transportation in rush hour traffic; whole travel chain has been taken into acount including the waiting time at home | 
| __pt_r_t__    | Travel time from origin to destination by public transportation in rush hour traffic; whole travel chain has been taken into account excluding the waiting time at home | 
| __pt_r_d__    | Distance (meters) of the public transportation route in rush hour traffic |
| __pt_m_tt__   | Travel time from origin to destination by public transportation in midday traffic; whole travel chain has been taken into acount including the waiting time at home |
| __pt_m_t__    | Travel time from origin to destination by public transportation in midday traffic; whole travel chain has been taken into account excluding the waiting time at home | 
| __pt_m_d__    | Distance (meters) of the public transportation route in midday traffic |
| __car_r_t__   | Travel time from origin to destination by private car in rush hour traffic; the whole travel chain has been taken into account |
| __car_r_d__   | Distance (meters) of the private car route in rush hour traffic |
| __car_m_t__   | Travel time from origin to destination by private car in midday traffic; the whole travel chain has been taken into account |
| __car_m_d__   | Distance (meters) of the private car route in midday traffic |
| __car_sl_t__   | Travel time from origin to destination by private car following speed limits without any additional impedances; the whole travel chain has been taken into account |

 
## <a name="calculations"></a>How calculations were done?

### <a name="walk"></a>Walking

__The routes by walking__ were also calculated using the __[MetropAccess-Reititin](http://blogs.helsinki.fi/accessibility/reititin/)__ by disabling all motorized transport modes in the calculation. Thus, all routes are based on the Open Street Map geometry.
The walking speed has been adjusted to 70 meters per minute, which is the default speed in the HRT Journey Planner (also in the calculations by public transportation).

For detailed documentation and instructions how to reproduce the walking results, see [documentation in here](codes/MetropAccess-Reititin).

### <a name="cycling"></a>Cycling

__The routes by cycling__ were calculated using a dedicated open source tool called [**DORA**](https://github.com/DigitalGeographyLab/DORA). The network dataset underneath is [MetropAccess-CyclingNetwork dataset](), which is a modified version from the original Digiroad data provided by Finnish Transport Agency. In the dataset the travel times for the road segments have been modified to be more realistic based on Strava sports application data from the Helsinki region from 2016 and the bike sharing system data from Helsinki from 2017.

For each road segment a separate speed value was calculated for slow and fast cycling. The value for fast cycling is based on a percentual difference  between segment specific Strava speed value and the average speed value for the whole Strava data. This same percentual difference has been applied to calculate the slower speed value for each road segment. The speed value is then the average speed value of bike sharing system users multiplied by the percentual difference value.

The reference value for faster cycling has been 19km/h, which is based on the average speed of Strava sports application users in the Helsinki region. The reference value for slower cycling has been 12km/, which has been the average travel speed of bike sharing system users in Helsinki. Additional 1 minute have been added to the travel time to consider the time for taking (30s) and returning (30s) bike on the origin/destination.

For detailed documentation and instructions how to reproduce the cycling results, see [documentation in here](codes/DORA).

### <a name="pt"></a>Public Transport

__The routes by public transportation__ have been calculated by using the __[MetropAccess-Reititin](http://blogs.helsinki.fi/accessibility/reititin/)__ tool which also takes
into account the whole travel chains from the origin to the destination:

 1. *possible waiting at home before leaving*
 2. *walking from home to the transit stop*
 3. *waiting at the transit stop*
 4. *travel time to next transit stop*
 5. *transport mode change*
 6. *travel time to next transit stop*
 7. *walking to the destination*

Travel times by public transportation have been optimized using 10 different departure times within the calculation hour using so called Golomb ruler. The fastest route from these calculations are selected for the final travel time matrix.

Calculations of 2015 MetropAccess-Travel Time Matrix are __based on schedules of Monday 29.01.2018__:

 - Midday (optimized between 12:00-13:00 ) --> Comparable with previous versions of the Helsinki Region Travel Time Matrix (2013 & 2015).
 - Rush hour (optimized between 08:00-09:00) --> Comparable with 2015 version of the Helsinki Region Travel Time Matrix.
 
For detailed documentation and instructions how to reproduce the public transport results, see [documentation in here](codes/MetropAccess-Reititin).

### <a name="car"></a>Private car

__The routes by car__ have been calculated with a dedicated open source tool called [**DORA**](https://github.com/DigitalGeographyLab/DORA). [MetropAccess-Digiroad dataset](http://blogs.helsinki.fi/accessibility/data/metropaccess-digiroad/) (modified from the original Digiroad data provided by Finnish Transport Agency) has been used as Network Dataset in which the travel times of the road segments are made more realistic by adding crossroad impedances for different road classes.
 
The calculations have been repeated for two times of the day using: 
 - the "midday impedance" (i.e. travel times outside rush hour) 
 - the "rush hour impendance" as impedance in the calculations.

__The whole travel chain__ ( *"door-to-door approach"* ) is taken into account in the calculations: 

 1. *walking time from the real origin to the nearest network location (based on Euclidean distance)* 
 2. *average walking time from the origin to the parking lot*
 3. *travel time from parking lot to destination* 
 4. *average time for searching a parking lot* 
 5. *walking time from parking lot to nearest network location of the destination* 
 6. *walking time from network location to the real destination (based on Euclidean distance)*
 
For detailed documentation and instructions how to reproduce the public transport results, see [documentation in here](codes/DORA).

All calculations for different travel modes were done using the computing resources of CSC-IT Center for Science (https://www.csc.fi/home).

## <a name="license"></a>Licence

Helsinki Region Travel Time Matrix 2018 by Accessibility Research Group / Digital Geography Lab (University of Helsinki) is licensed under a Creative Commons Attribution 4.0 International License. More information about license: http://creativecommons.org/licenses/by/4.0/

If the datasets are being used extensively in scientific research, we welcome the opportunity for co-authorship of papers. Please contact project leader to discuss about the matter.

## <a name="how-to-cite"></a>Citation practices

If you use Helsinki Region Travel Time Matrix 2018 dataset or related tools in your work, we encourage you to cite to our work.

You can cite to our work as follows:

__Data/Tools description:__

 - Tenkanen, H. & T. Toivonen (forthcoming). Multimodal and multitemporal accessibility dataset for planning: travel times and distances in Helsinki Region. *Scientific Data*. 
 - Toivonen, T., M. Salonen, H. Tenkanen, P. Saarsalmi, T. Jaakkola & J. Järvi (2014). 
Joukkoliikenteellä, autolla ja kävellen: Avoin saavutettavuusaineisto pääkaupunkiseudulla. Terra 126: 3, 127-136.

__DOI name for the dataset:__
- Tenkanen, Henrikki, & Toivonen, Tuuli. (2019). Helsinki Region Travel Time Matrix [Data set]. Zenodo. http://doi.org/10.5281/zenodo.3247564

## <a name="code-repo"></a>Codes: How to reproduce the results?

All the codes and analysis steps that have been used to produce the Helsinki Region Travel Time Matrix 2018 are documented separately under [codes -folder](codes/). 

## <a name="contact"></a>Contribution / Contact
__Helsinki Region Travel Time Matrix 2018__ was created by the [Accessibility Research Group](http://www.helsinki.fi/science/accessibility)/[Digital Geography Lab](https://www.helsinki.fi/en/researchgroups/digital-geography-lab) 
at the Department of Geosciences and Geography, University of Helsinki, Finland.
 
**Various people have contributed and made it possible to create this dataset:**

 - [Henrikki Tenkanen](https://www.researchgate.net/profile/Henrikki_Tenkanen) (Postdoctoral researcher, participation in all steps)
 - Jeison Londoño Espinosa (MSc student, dataset production, programming of the DORA tool)
 - Ainokaisa Tarnanen (MSc student, created the cycling network used in this data)
 - Tuuli Toivonen (PI, leader of the research group)
 
**Participated in creating the previous versions of the dataset**:
 - Vuokko Heikinheimo (PhD candidate, dataset production, documentation)
 - Maria Salonen (project manager, participation in all steps)
 - Juha Järvi (BusFaster Ltd, programming and design of the MetropAccess-Reitin)
 - Timo Jaakkola (development of the travel time model for private cars)
 
In addition, we thank [CSC - IT Center for Science](https://www.csc.fi/) for computational resources and help. 
CSC Taito and cPouta computing clusters were used as our workhorses to calculate the travel times/distances (approx. 1 billion routes were calculated) using MetropAccess-Digiroad- and MetropAccess-Reititin Tools.   

