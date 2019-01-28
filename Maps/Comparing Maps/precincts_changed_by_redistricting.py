import sys
sys.path.append('/gerrymander-geoprocessing/areal_interpolation')
from areal_interpolation import areal_interpolation as ai
import geopandas as gpd

start_path =''

#load in precinct, special master, and enacted maps
precincts = gpd.read_file(start_path + 'VA-gerrymander/Maps/Relevant precincts/BH_updated_Precincts.shp')
sm = gpd.read_file(start_path + 'VA-gerrymander/Maps/Special Master Map/Court Order Map/Groffman_Court_Order.shp')
enacted = gpd.read_file(start_path + 'VA-gerrymander/Maps/Enacted map/enacted.shp')
enacted['OBJECTID']=enacted['OBJECTID'].astype(str)

#assign labels
precincts = ai.aggregate(precincts, enacted, target_columns=['OBJECTID'])[0] # this takes a while
precincts = ai.aggregate(precincts, sm, target_columns=['District_N'])[0]

#select precicnts where new district is different than old district
changed = precincts.loc[precincts['OBJECTID'] != precincts['District_N']]
#change column names and get rid of extra columns
changed['Enacted']=changed['OBJECTID']
changed['Special Master']=changed['District_N']
changed = changed[['precinct', 'locality', 'Enacted', 'Special Master']]
changed['precinct']=changed['precinct'].str.title()
#save to file
save_path =''
changed.to_csv(save_path, index=False)