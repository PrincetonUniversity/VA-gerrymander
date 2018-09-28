import geopandas as gpd
import pandas as pd
import sys
sys.path.append('/gerrymander-geoprocessing/areal_interpolation')
import areal_interpolation as ai
import tabulate

start_path = ''

maps = {'reform': {'name': 'PGP Reform map',
                   'path': start_path + 'Maps/Reform map/Districts map bethune-hill final.shp',
                   'district_colname': 'DISTRICT',
                   'show': True},
        'enacted': {'name': 'Enacted map',
                    'path': start_path + 'Maps/Enacted map/enacted.shp',
                    'district_colname': 'ID',
                    'show': False},
        'dems':    {'name': 'VA House Dems map',
                    'path': start_path + 'Maps/House Dems map/HB7001.shp',
                    'district_colname': 'OBJECTID',
                    'show': False},
# =============================================================================
#         'gop_bell1':     {'name': 'VA House GOP (Bell 1)',
#                     'path': start_path + 'Maps/GOP map bell/HB7002_shapefile.shp',
#                     'district_colname': 'OBJECTID',
#                     'show': False},
# =============================================================================
        'gop_bell2':     {'name': 'VA House GOP (Bell)',
                    'path': start_path + 'Maps/GOP map bell substitute/HB7002_ANS.shp',
                    'district_colname': 'OBJECTID',
                    'show': False}, 
        'gop_jones':    {'name': 'VA House GOP (Jones)',
                    'path': start_path + 'Maps/GOP map jones/HB7003.shp',
                    'district_colname': 'OBJECTID',
                    'show': False},
        'new_VA':    {'name': 'New VA Majority',
                    'path': start_path + 'Maps/New VA Majority/VA NVM Map Submission 20180926.shp',
                    'district_colname': 'District',
                    'show': False}
        }
        
common_colname = 'district_no'

# identify relevant districts
affected = [63, 69, 70, 71, 74, 77, 80, 89, 90, 92, 95]
adjacent= [27, 55, 61, 62, 64, 66, 68, 72, 73, 75, 76, 78, 79, 81, 83, 85, 91, 93, 94, 96, 97, 100]
bh = [str(i) for i in affected + adjacent]

affected_label = 'Ruled unconstitutional as enacted'
adjacent_label = 'Adjacent to a district ruled unconstitutional'

#%%
# get census block geography with BVAP and VAP data
census_blocks = '/mapping/VA/2010 Census/Census Blocks with Population/tabblock2010_51_pophu.shp'

P10_table = '/mapping/VA/2010 Census/P10 Race for 18+ Population by Block/nhgis0003_ds172_2010_block.csv'

blocks = gpd.read_file(census_blocks)

race = pd.read_csv(P10_table)[1:]

# column codes
bvap = 'H74004'
vap = 'H74001'

blocks['GISJOIN'] = 'G' + blocks['STATEFP10'] + blocks['COUNTYFP10'].apply(lambda x: x.zfill(4)) + blocks['TRACTCE10'].apply(lambda x: x.zfill(7)) + blocks['BLOCKCE'].apply(lambda x: x.zfill(4))

blocks_w_race = blocks.merge(race.loc[:, ['GISJOIN', bvap, vap]], on='GISJOIN')
blocks_w_race = blocks_w_race.rename(columns={bvap: 'BVAP', vap: 'VAP'})
blocks_w_race = blocks_w_race.astype({'BVAP': int, 'VAP': int})

for mapname in maps:
    df = gpd.read_file(maps[mapname]['path'])
    
    df = df.rename(columns={maps[mapname]['district_colname']: common_colname})
        
    df[common_colname] = df[common_colname].astype(str)
    df = df[df[common_colname].isin(bh)]
    
    df = ai.aggregate(blocks_w_race, df, source_columns=['BVAP', 'VAP'], method='greatest_area')[1]

    df['prop_BVAP_' + mapname] = df['BVAP'] / df['VAP']
    df = df.rename(columns={'BVAP': 'BVAP_' + mapname,
                            'VAP': 'VAP_' + mapname})

    df.loc[df[common_colname].isin([str(i) for i in affected]), 'status'] = affected_label
    df.loc[df[common_colname].isin([str(i) for i in adjacent]), 'status'] = adjacent_label

    maps[mapname]['df'] = df

keys = list(maps)
mapname = keys[0]
df = maps[mapname]['df'][[common_colname, 'status'] + [i + '_' + mapname for i in ['BVAP', 'VAP', 'prop_BVAP']]]
for mapname in keys[1:]:
    df = df.merge(maps[mapname]['df'][[common_colname] + [i + '_' + mapname for i in ['BVAP', 'VAP', 'prop_BVAP']]],
                      on=common_colname)

df[common_colname] = df[common_colname].astype(int)
sorted = df.sort_values(by=['status', common_colname], ascending=[False, True])
sorted

sorted.to_csv('/Analysis/BVAP/bvap_comparison.csv', index=False, float_format='%.3f')


mean = pd.DataFrame(df.loc[df['status']==affected_label, ['prop_BVAP_' + i for i in maps]].mean()).T.rename(index={0: 'mean BVAP in affected districts'})
mean.to_csv('/Analysis/BVAP/mean_bvap_comparison.csv', index=False, float_format='%.3f')

def markdown_table(df, precision=3, showindex=False):
    return tabulate.tabulate(df, headers=df.columns, floatfmt=f'.{precision}g', tablefmt='pipe', showindex=showindex)

with open("/Analysis/BVAP/README.md", "w") as text_file:
    print('Proportion of voting-age population that identifies as Black or African-American (one race only), by district.\n', file=text_file)
    print(markdown_table(mean, showindex=True), file=text_file)
    print('\n\n', file=text_file)
    print(markdown_table(sorted), file=text_file)
