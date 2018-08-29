## Accompanying data and analysis for "A Fresh Start for Virginia Districting"
### Ben Williams, William T. Adler, and Samuel S.-H. Wang, of the [Princeton Gerrymandering Project](http://gerrymander.princeton.edu/)
### Additional work by Connor Moffatt and Jacob Wachspress
<p align="center"><a href="https://rawgit.com/PrincetonUniversity/VA-gerrymander/master/Maps/Interactive/map_comparison.html"><img src="Maps/Reform map/reform_preview.png" width="700"></a></p>
<p align="center">Click to explore the maps interactively.</p>

This repository contains a Reform Map drawn by the Princeton Gerrymandering Project to remedy the unconstitutional districts recently struck down as racial gerrymanders in Bethune-Hill v. Va. State Bd. of Elections (opinion [here](http://electionlawblog.org/wp-content/uploads/Virginia.pdf)). 
On August 30, 2018, the General Assembly will enter a special session to consider proposals from both political parties and the public on how the afflicted districts should be remedied.
We present our map, and its underlying data, as an option for legislators to consider.
Our map was not drawn by someone well-versed in redistricting software, nor was it drawn with any particular desired outcome.
Rather, it sought to restore constitutional order to the district boundaries while drawing districts that were more compact, preserved cities and counties where possible, and followed natural geographic boundaries.
In Hampton Roads, where water is ever present, we sought to ensure that bridges connected every part of a district.
Any underlying partisan effects of the map are incidental and, frankly, unimportant.
What matters is that this map—unlike the map currently in effect—wasn't drawn with a desired outcome in mind.
We did not seek to engineer political outcomes for either political party.
We simply looked at the geography before us, and made our best effort at a fair map.
Rather than making piecemeal changes to the existing map with its ingrained infirmities, we believe legislators should use our map as a base point for any new maps they introduce in the General Assembly.
From our map, they can make changes to comply with other criteria as desired, but their final product will still have originated from a place of fundamental fairness and impartiality.
And that is something all Virginians deserve.

## The Process
While a student at William & Mary Law School, Ben participated in a class which was tasked with a hypothetical redrawing of the 11 challenged districts in the (then-pending) Bethune-Hill case. A press release can be found [here](https://law.wm.edu/news/stories/2017/law-and-undergraduate-students-use-gis-tools-to-redraw-11-virginia-house-districts.php). 
Because of his familiarity with the political geography of this region of Virginia (as a resident of the area as recently as May 2018), and his previous use of ArcGIS in redrawing these very same districts, Ben was tasked with drawing our team's Reform Map. 
In drawing the map, he had access to the following data: 
  - The existing districting plan, as enacted by the Virginia General Assembly in 2011
  - Precinct boundaries for all counties in the 33 impacted districts (the 11 districts that needed to be redrawn, and the 22 districts immediately adjacent to them
  - Census block information within each of the above precincts.
  - Election results at the precinct level, disaggregated to the block level, for the 2016 Presidential Election and the 2017 Lieutenant Governor election (two recent elections which captured with high certainty the minority candidate-of-choice). While he also had access to data from the 2017 Gubernatorial and 2017 Attorney General elections, he did not consider them in the creation of this map.
  - Demographic data from the census at the census block level (including, importantly for this case, the African-American voting age population of the blocks and precincts)
  - A hydrologic map of major rivers, the Chesapeake Bay, and the Atlantic Ocean
  - A road map of Virginia, including everything from major highways to city streets

He did not have access to the addresses of incumbents or potential challengers. Because Virginia does not register voters on the basis of party, he also lacked such data.
  
His process was as follows: 
  1) Redraw the district boundaries to roughly coincide with city & county boundaries. While some consideration to the cores of prior districts is given, the constitutional deficiencies in the existing map diminishes this as a priority.
  2) Check the total population number of each district to assess the degree of population inequality in each district. The districts at this point are likely very malapportioned and need to be adjusted considerably. 
  3) By looking at the population numbers in adjacent precincts, make adjustments as needed to bring the districts to within +/- 1% ideal population, which is the population deviation used in the 2011 plan and is the deviation used in the 67 districts not being changed in this redraw. 
  4) If there is no possible way to achieve +/- 1% population equality by moving precincts alone, move to the census block level and move individual blocks as needed. Care should be taken to split as few precincts as practicable while honoring other criteria. 
  5) Once the districts are all within +/- 1% population, check the demographic data and past election result data in the districts protected by the Voting Rights Act (VRA) to see if there is a sufficient population of minority voters to ensure that the minority community has the opportunity to elect their candidate of choice. In our redraw, we identified Hillary Clinton in 2016 (primary and general elections for President) and Justin Fairfax in 2017 (primary and general elections for Virginia Lieutenant Governor) as the minority candidates of choice. This can be done via an ecological inference analysis (NOTE: Our analysis is still ongoing. For purposes of this map, we made an educated guess on the % BVAP needed to give minority communities the opportunity to elect candidates of their choosing at between 40% and 45%, depending on the partisan performance of the district. Once this analysis is completed the data will be shared here). The District Court in the [Bethune-Hill opinion](http://electionlawblog.org/wp-content/uploads/Virginia.pdf#page=88) noted that a BVAP of 45% was more than sufficient to elect the minority candidate of choice (frequently by massive margins) in each of the 11 unconstitutional districts.
  6) Make adjustments to the district borders as needed to ensure that all districts are equipopulous. Do not check the partisan performance of the districts not protected by the VRA. 
  7) Perform a final check to make sure all of the VRA districts are compliant and that other federal and state criteria (one person, one vote; compactness; contiguity) are satisfied. 
