import geopandas as gpd
import pandas as pd

start_path = ''

#read in election results
fp = start_path + 'princeton_gerrymandering_project/mapping/VA/openelections-results-va/raw/20161108__va__general__precinct__raw.csv'

elec = pd.read_csv(fp)

elec = elec [['office', 'district','parent_jurisdiction', 'jurisdiction']]
elec = elec[elec.jurisdiction != '## Provisional']
elec = elec[elec.jurisdiction != '# AB - Central Absentee Precinct']

elec['loc_prec'] = elec['parent_jurisdiction'] + ' ' + elec['jurisdiction']
elec = elec[pd.notnull(elec['district'])]

splits = {}

for loc_prec in elec['loc_prec'].unique():
    prec = elec.loc[elec['loc_prec'] == loc_prec]
    dists = prec['district'].unique()
    if len(dists) > 1:
        splits[loc_prec] = dists
    
split_prec = pd.DataFrame.from_dict(splits, orient = 'index')

split_prec.to_csv('')