## Accompanying data and analysis for "[Lawmakers should fix inequitable district lines](https://pilotonline.com/opinion/columnist/guest/article_7a44a308-abb4-11e8-bec1-0361d680b78f.html)", _The Virginian-Pilot_, August 30, 2018
### Ben Williams, William T. Adler, and Samuel S.-H. Wang, of the [Princeton Gerrymandering Project](http://gerrymander.princeton.edu/)
### Additional work by Connor Moffatt and Jacob Wachspress

[![Reform map](Maps/Reform%20map/updated_preview.PNG)](https://rawgit.com/PrincetonUniversity/VA-gerrymander/master/Maps/Interactive/map_comparison.html)
<p align="center">Click to explore the maps interactively.</p>

This repository contains a map drawn by the Princeton Gerrymandering Project to remedy the unconstitutional districts recently struck down as racial gerrymanders in Bethune-Hill v. Va. State Bd. of Elections (opinion [here](http://electionlawblog.org/wp-content/uploads/Virginia.pdf)). 
It is intended to accompany the op-ed in _The Virginian-Pilot_, "[Lawmakers should fix inequitable district lines](https://pilotonline.com/opinion/columnist/guest/article_7a44a308-abb4-11e8-bec1-0361d680b78f.html)".
On August 30, 2018, the General Assembly will enter a special session to consider proposals from both political parties and the public on how the afflicted districts should be remedied.
This map, and its underlying data, are presented as an option for legislators to consider.
It restores constitutional order to the district boundaries while creating districts that are more compact, better preserving cities and counties, and more closely following natural geographic boundaries, than the enacted map.
Any underlying partisan effects of the map are incidental and, frankly, unimportant.
What matters is that this map—unlike the map currently in effect—was not drawn with a desired outcome in mind.
It was drawn not to engineer political outcomes but to be a fair map given the geography of the state.
Rather than making piecemeal changes to the existing map with its ingrained infirmities, we believe legislators should use this map as a base point for any new maps they introduce in the General Assembly.
From the map, legislators can make changes to comply with other criteria as desired, but the final product will still have originated from a place of fundamental fairness and impartiality.
And that is something all Virginians deserve.

## The Process
While a student at William & Mary Law School, one of the authors (Ben Williams) participated in a class that redrew the 11 challenged districts in the (then-pending) Bethune-Hill case.
A press release can be found [here](https://law.wm.edu/news/stories/2017/law-and-undergraduate-students-use-gis-tools-to-redraw-11-virginia-house-districts.php). 
Because of his familiarity with the political geography of this region of Virginia (as a resident of the area as recently as May 2018), and his previous experience redrawing these very same districts, Ben was tasked with drawing the Reform Map. 
In drawing the map, he had access to the following data: 
  - The existing districting plan, as enacted by the Virginia General Assembly in 2011
  - [Precinct boundaries for all counties in the 33 impacted districts](Maps/Relevant%20precincts) (the 11 districts that needed to be redrawn, and the 22 districts immediately adjacent to them
  - Election results at the precinct level, disaggregated to the block level, for the 2016 Presidential Election and the 2017 Lieutenant Governor election (two recent elections which captured with high certainty the minority candidate-of-choice). While he also had access to data from the 2017 Gubernatorial and 2017 Attorney General elections, he did not consider them in the creation of this map.
  - Demographic data from the census at the census block level (including, importantly for this case, the African-American voting age population of the blocks and precincts)
  - A hydrologic map of major rivers, the Chesapeake Bay, and the Atlantic Ocean
  - A road map of Virginia, including everything from major highways to city streets

He did not have access to the addresses of incumbents or potential challengers. Because Virginia does not register voters on the basis of party, he also lacked such data.
  
His process was as follows: 
  1) Redraw the district boundaries to roughly coincide with city & county boundaries. While some consideration to the cores of prior districts is given, the constitutional deficiencies in the existing map diminishes this as a priority.
  2) Check the total population number of each district to assess the degree of population inequality in each district. The districts at this point are likely very malapportioned and need to be adjusted considerably. 
  3) By looking at the population numbers in adjacent precincts, make adjustments as needed to bring the districts to within ±1% ideal population, which is the population deviation used in the 2011 plan and is the deviation used in the 67 districts not being changed in this redraw. 
  4) If there is no possible way to achieve ±1% population equality by moving precincts alone, move to the census block level and move individual blocks as needed. Care should be taken to split as few precincts as practicable while honoring other criteria. 
  5) Once the districts are all within ±1% population, check the demographic data and past election result data in the districts protected by the Voting Rights Act (VRA) to see if there is a sufficient population of minority voters to ensure that the minority community has the opportunity to elect their candidate of choice. In our redraw, we identified Hillary Clinton in 2016 (primary and general elections for President) and Justin Fairfax in 2017 (primary and general elections for Virginia Lieutenant Governor) as the minority candidates of choice.
  6) Change districts to make sure there is at least one major roadway connecting the various sections of the district. It should be possible to drive to all parts of the district without leaving the district itself. 
  7) Make adjustments to the district borders as needed to ensure that all districts are equipopulous. Do not check the partisan performance of the districts not protected by the VRA. 
  8) Perform a final check to make sure all of the VRA districts are compliant and that other federal and state criteria (one person, one vote; compactness; contiguity) are satisfied. 
