# Helsinki Region Travel Time Matrix 2018
This repository demonstrates / documents how __[Helsinki Region Travel Time Matrix 2018](http://blogs.helsinki.fi/accessibility/helsinki-region-travel-time-matrix-2018/)__ is calculated. 
Dataset was produced by [Accessibility Research Group / Digital Geography Lab](http://www.helsinki.fi/science/accessibility), University of Helsinki.

__Contents:__

- [What is Helsinki Region Travel Time Matrix 2018?](#What-is-Helsinki-Region-Travel-Time-Matrix-2018)
- [Attributes of Helsinki Region Travel Time Matrix 2018](#attributes)
- [How calculations were done?](#calculations)
  - [Public Transport](#pt)
  - [Walking](#walk)
  - [Private car](#car)
- [Licence](#license)
- [How to cite this work?](#how-to-cite)
- [Codes](#code-repo)
- [Contribution / Contact](#contact)

## What is Helsinki Region Travel Time Matrix 2018?
 
[__Helsinki Region Travel Time Matrix 2018__](http://www.helsinki.fi/science/accessibility/data) is a dataset that contains travel time and distance information of the routes
that have been calculated from all 250 m x 250 m grid cell centroids (n = 13231) in the Capital Region of Helsinki 
([see this map](http://www.helsinki.fi/science/accessibility/tools/YKR/YKR_Identifier.html)) by walking, public transportation (PT) and private car. 
Calculations were done separately for two different time of the day using rush hour (08:00-09:00) and midday (12:00-13:00) schedules/traffic conditions. 
The grid cells are compatible with the statistical grid cells in the YKR (yhdyskuntarakenteen seurantajärjestelmä) data set produced by the Finnish Environment Institute (SYKE). 
   
Dataset is openly available for everyone for free and it can be downloaded from the [Accessibility Research Group website](http://www.helsinki.fi/science/accessibility/data) (under a Creative Commons 4.0 Licence, see [licence text](#license)).

Helsinki Region Travel Time Matrix 2015 is closely related to __[Helsinki Region Travel CO2 Matrix 2015](http://www.helsinki.fi/science/accessibility/data/)__ 
that is also produced by Accessibility Research Group. 
More information on how the Helsinki Region Travel CO2 Matrix 2015 was calculated can be found [from here](https://github.com/AccessibilityRG/HelsinkiRegionTravelCO2Matrix2015). 
 
__Scientific examples__ of the approach used here can be read from the following articles:

- Laatikainen, T., H. Tenkanen, M. Kyttä & T. Toivonen (2015). [Comparing conventional and PPGIS approaches in measuring equality of access to urban aquatic environments.](http://www.sciencedirect.com/science/article/pii/S0169204615001590) Landscape and Urban Planning 144, 22–33.
- Toivonen, T., M. Salonen, H. Tenkanen, P. Saarsalmi, T. Jaakkola & J. Järvi (2014). [Joukkoliikenteellä, autolla ja kävellen: Avoin saavutettavuusaineisto pääkaupunkiseudulla.](http://www.helsinki.fi/science/accessibility/publications/Toivonen_etal_2014_terra.pdf) Terra 126: 3, 127-136. 
- Salonen, M. & Toivonen, T. (2013). [Modelling travel time in urban networks: comparable measures for private car and public transport.](http://www.sciencedirect.com/science/article/pii/S096669231300121X) Journal of Transport Geography 31, 143–153.
- Jaakkola, T. (2013). [Paikkatietopohjainen menetelmä autoilun ajoaikojen ja kokonaismatka-aikojen mallintamiseen – esimerkkinä pääkaupunkiseutu.](http://www.helsinki.fi/science/accessibility/publications/TimoJaakkola_Paikkatietopohjainen_menetelma_autoilun_ajoaikojen_ja_kokonaismatka-aikojen_mallintamiseen.pdf) Pro gradu -tutkielma. Helsingin yliopisto. 
Geotieteiden ja maantieteen laitos.
- Lahtinen, J., Salonen, M. & Toivonen, T. (2013). [Facility allocation strategies and the sustainability of service delivery: 
Modelling library patronage patterns and their related CO2-emissions](http://www.sciencedirect.com/science/article/pii/S014362281300163X). Applied Geography 44, 43-52.
- Jäppinen,  S., Toivonen, T. & Salonen, M. (2013). [Modelling the potential effect of shared bicycles on public transport travel times in Greater Helsinki: An open data approach.](http://www.sciencedirect.com/science/article/pii/S014362281300132X) Applied Geography 43, 13-24.
- Salonen, M., Toivonen, T. & Vaattovaara, M. (2012). Arkiliikkumisen vaihtoehdoista monikeskuksistuvassa metropolissa: Kaksi näkökulmaa palvelujen saavutettavuuteen pääkaupunkiseudulla.
Yhdyskuntasuunnittelu 3/2012

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

Travel times by public transportation have been optimized using 10 different departure times within the calculation hour using so called Golomb ruler.
The fastest route from these calculations are selected for the final travel time matrix.

Calculations of 2015 MetropAccess-Travel Time Matrix are __based on schedules of Monday 29.01.2018__:

 - Midday (optimized between 12:00-13:00 ) --> Comparable with previous versions of the Helsinki Region Travel Time Matrix (2013 & 2015).
 - Rush hour (optimized between 08:00-09:00) --> Comparable with 2015 version of the Helsinki Region Travel Time Matrix.
 
For detailed documentation and instructions how to reproduce the results, see [documentation in here](codes/MetropAccess-Reititin).

### <a name="walk"></a>Walking

__The routes by walking__ were also calculated using the __[MetropAccess-Reititin](http://blogs.helsinki.fi/accessibility/reititin/)__ by disabling all motorized transport modes in the calculation. Thus, all routes are based on the Open Street Map geometry.
The walking speed has been adjusted to 70 meters per minute, which is the default speed in the HRT Journey Planner (also in the calculations by public transportation).

### <a name="car"></a>Private car

__The routes by car__ have been calculated with a dedicated open source tool called [**DORA**](https://github.com/DigitalGeographyLab/DORA). [MetropAccess-Digiroad dataset](http://blogs.helsinki.fi/accessibility/data/metropaccess-digiroad/) (modified from the original Digiroad data provided by Finnish Transport Agency)
has been used as Network Dataset in which the travel times of the road segments are made more realistic by adding crossroad impedances for different road classes.
 
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

All calculations were done using the computing resources of CSC-IT Center for Science (https://www.csc.fi/home).

## <a name="license"></a>Licence

Helsinki Region Travel Time Matrix 2018 by Accessibility Research Group / Digital Geography Lab (University of Helsinki) is licensed under a Creative Commons Attribution 4.0 International License. More information about license: http://creativecommons.org/licenses/by/4.0/

If the datasets are being used extensively in scientific research, we welcome the opportunity for co-authorship of papers. Please contact project leader to discuss about the matter.

## <a name="how-to-cite"></a>Citation practices

If you use Helsinki Region Travel Time Matrix 2018 dataset or related tools in your work, we encourage you to cite to our work.

You can cite to our work as follows:

__Data/Tools description:__

 - Tenkanen, H. & T. Toivonen (upcoming). Multimodal and multitemporal accessibility dataset for planning: travel times and distances in Helsinki Region. *Scientific Data*. 
 - Toivonen, T., M. Salonen, H. Tenkanen, P. Saarsalmi, T. Jaakkola & J. Järvi (2014). 
Joukkoliikenteellä, autolla ja kävellen: Avoin saavutettavuusaineisto pääkaupunkiseudulla. Terra 126: 3, 127-136.

__DOI name for the dataset:__
- Tenkanen, Henrikki, & Toivonen, Tuuli. (2019). Helsinki Region Travel Time Matrix [Data set]. Zenodo. http://doi.org/10.5281/zenodo.3247564

## <a name="code-repo"></a>Codes to reproduce the results

All the codes and analysis steps that have been used to produce the Helsinki Region Travel Time Matrix 2018 are documented separately in [here](codes/). 

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

