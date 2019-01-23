# Project Description

Precinct boundaries matched to 2016, 2017, and 2018 general, state-wide elections.

## Background and sources
All precinct boundaries in this shapefile were collected and processed by the Princeton Gerrymandering Project.

Once collected, maps were verified and combined into one single shapefile for the entire state. Then, election results were matched to these current precincts and merged into the attribute table.

For counties in which no maps were sent to us from county officials, namely Lee and Sussex Counties, 2010 Census VTDs were used since they matched perfectly with precinct names in election returns and no documented boundary changes were posted online.

## Assumptions and Processing
This shapefile is still in progress. A final round of boundary verification is planned, but has not been initiated yet. Currently, these boundaries are only as accurate as the maps sent to us from county officials.

In many counties, absentee votes are reported at the county level, rather than by precinct. In this case, we diss aggregated absentee vote totals across all precincts in the county proportionally. The code for this can be found [here](https://github.com/PrincetonUniversity/gerrymander-geoprocessing/blob/master/elec_candidates_to_elec_prec.py).

Provisional votes are also often reported at the county level, but we did not add them into these totals.

## Election Key
'G18DHOR', 'G18RHOR', 'G18OHOR' are General 2018 Democratic, Republican, and other House of Representatives

'G18OSEN', 'G18DSEN', 'G18RSEN', are General 2018 D, R, and other Senate

'G17DGOV', 'G17RGOV', 'G17OGOV' are General 2017 D, R, and other Governor

'G17DLTG',  'G17RLTG' are General 2017 D and R Lieutenant Governor

'G17DATG', 'G17RATG' are General 2017 D and R Attorney General

'G17DHOD', 'G17RHOD', 'G17OHOD' are General 2017 D, R, and other House of Delegates

'G16DPRS', 'G16RPRS', 'G16OPRS' are General 2016 D, R, and other President

'G16DHOR', 'G16RHOR', 'G16OHOR' are General 2016 D, R, and other House of Representatives


## Built With

* [Google Team Drive](https://gsuite.google.com/learning-center/products/drive/get-started-team-drive/#!/) - For file storage, organization, and collaboration
* [gerrymander-geoprocessing](https://github.com/PrincetonUniversity/gerrymander-geoprocessing) - For automation and processing
* [QGIS](https://qgis.org/en/site/) - For digital map work



## License

This shapefile is licensed under the GNU Affero Public License - see the [LICENSE.md](https://github.com/PrincetonUniversity/VA-gerrymander/blob/master/LICENSE) file for more information

## Acknowledgments

* Connor Moffatt, Jacob Watchspress, Hannah Wheelen, John O'Neil, Ben Williams, and Will Adler contributed to the collection and processing of this file.
* None of this would have been possible without the cooperation of officials in every county and independent city in the state of Virginia.
