import geopandas as gpd
import pandas as pd
import sys
sys.path.append('/Users/wtadler/Repos/gerrymander-geoprocessing/areal_interpolation')
import areal_interpolation as ai

# SET PATHS

census_blocks = '/Volumes/GoogleDrive/Team Drives/princeton_gerrymandering_project/mapping/VA/2010 Census/Census Blocks with Population/tabblock2010_51_pophu.shp'

P10_table = '/Volumes/GoogleDrive/Team Drives/princeton_gerrymandering_project/mapping/VA/2010 Census/P10 Race for 18+ Population by Block/nhgis0003_ds172_2010_block.csv'

BH_precincts = '/Volumes/GoogleDrive/Team Drives/princeton_gerrymandering_project/mapping/VA/Bethune Hill/BH_precincts.shp'

house_districts = '/Volumes/GoogleDrive/Team Drives/princeton_gerrymandering_project/mapping/VA/House of Delegates map (census)/cb_2017_51_sldl_500k.shp'


# 1) Load census block geographies, join with BVAP and non-B VAP

blocks = gpd.read_file(census_blocks)

race = pd.read_csv(P10_table)[1:]

# column codes
bvap = 'H74004'
vap = 'H74001'

blocks['GISJOIN'] = 'G' + blocks['STATEFP10'] + blocks['COUNTYFP10'].apply(lambda x: x.zfill(4)) + blocks['TRACTCE10'].apply(lambda x: x.zfill(7)) + blocks['BLOCKCE'].apply(lambda x: x.zfill(4))

blocks_w_race = blocks.merge(race.loc[:, ['GISJOIN', bvap, vap]], on='GISJOIN')
blocks_w_race = blocks_w_race.rename(columns={bvap: 'BVAP', vap: 'VAP'})
blocks_w_race = blocks_w_race.astype({'BVAP': int, 'VAP': int})

# 2) Load precinct data with election result, merge them with census block data
precincts = gpd.read_file(BH_precincts)

precincts_w_race = ai.aggregate(blocks_w_race, precincts, source_columns=['BVAP', 'VAP'], method='greatest_area')[1]


# 3) load House geographies, assign districts to precincts, filte
house = gpd.read_file(house_districts)

precincts_w_race_and_districts = ai.aggregate(precincts_w_race, house, target_columns=['NAME'])[0]

# filter to only include precincts in affected and adjacent districts according to VPAP
# https://www.vpap.org/visuals/visual/ruling-could-impact-1-3-house-districts/
affected = [63, 69, 70, 71, 74, 77, 80, 89, 90, 92, 95]
adjacent = [27, 55, 61, 62, 64, 66, 68, 72, 73, 75, 76, 78, 79, 81, 83, 85, 91, 93, 94, 96, 97, 100]
relevant_districts = affected + adjacent

relevant_precincts = precincts_w_race_and_districts[precincts_w_race_and_districts['NAME'].isin([str(i) for i in relevant_districts])]

# proportion of the voting age population that is black
relevant_precincts['prop_BVAP'] = relevant_precincts['BVAP'] / relevant_precincts['VAP']

# proportion of the total vote for Ds and Rs that went to the D in 4 elections:
# 2017: Gov., Lt. Gov., Atty. Gen.
# 2016: Pres.
relevant_precincts['prop_D_G'] = relevant_precincts['G_DEM_17_y'] / (relevant_precincts['G_DEM_17_y'] + relevant_precincts['G_REP_17_y'])
relevant_precincts['prop_D_LG'] = relevant_precincts['LG_DEM_1_1'] / (relevant_precincts['LG_DEM_1_1'] + relevant_precincts['LG_REP_1_1'])
relevant_precincts['prop_D_AG'] = relevant_precincts['AG_DEM_1_1'] / (relevant_precincts['AG_DEM_1_1'] + relevant_precincts['AG_REP_1_1'])
relevant_precincts['prop_D_P'] = relevant_precincts['P_DEM_16_y'] / (relevant_precincts['P_DEM_16_y'] + relevant_precincts['P_REP_16_y'])

relevant_precincts.to_file('BH_precincts_with_BVAP_VAP.shp')