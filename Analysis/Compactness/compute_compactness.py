import sys
sys.path.append('/Analysis/Compactness')
import continuous_measures as cm
import geopandas as gpd
import pandas as pd
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
                    'show': False},
        'SM_few_changes': {'name': 'Special Master (fewest changes from Enacted)',
                    'path':'/Users/hwheelen/Documents/GitHub/VA-gerrymander/Maps/Special Master Map/fewest changes/FewestChangesSM.shp',
                    'district_colname': 'District_N',
                    'show': False},
        'SM_most_changes': {'name': 'Special Master (most changes from Enacted)',
                    'path':'/Users/hwheelen/Documents/GitHub/VA-gerrymander/Maps/Special Master Map/most changes/MostChangesSM.shp',
                    'district_colname': 'District_N',
                    'show': False}
        }

metrics = {'Reock (higher is better)': cm.reock,
           'Schwartzberg (lower is better)': cm.schwartzberg,
           'Convex hull ratio (higher is better)': cm.c_hull_ratio,
           'Polsby-Popper (higher is better)': cm.polsby_popper}

# identify relevant districts
affected = [63, 69, 70, 71, 74, 77, 80, 89, 90, 92, 95]
adjacent= [27, 55, 61, 62, 64, 66, 68, 72, 73, 75, 76, 78, 79, 81, 83, 85, 91, 93, 94, 96, 97, 100]
bh = [str(i) for i in affected + adjacent]

common_colname = 'district_no'

for mapname in maps:
    df = gpd.read_file(maps[mapname]['path'])

    df = df.rename(columns={maps[mapname]['district_colname']: common_colname})

    df[common_colname] = df[common_colname].astype(str)
    df = df[df[common_colname].isin(bh)]

    for m in metrics:
        # df[m + '_' + mapname] = metrics[m](df)
        df[m] = metrics[m](df)
    df['map'] = mapname
    df[common_colname] = df[common_colname].astype(int)
    maps[mapname]['df'] = df

all = pd.concat([maps[mapname]['df'] for mapname in maps], sort=False)
mean = all.pivot_table(values=metrics.keys(), index='map')

all = all.pivot_table(values=metrics.keys(), index=['map', common_colname]).sort_values(by=[common_colname, 'map'])

all.to_csv('/Analysis/Compactness/compactness_comparison.csv', index=True, float_format='%.3f')
mean.to_csv('Analysis/Compactness/mean_compactness_comparison.csv', index=True, float_format='%.3f')

def markdown_table(df, precision=3, showindex=False):
    return tabulate.tabulate(df, headers=df.columns, floatfmt=f'.{precision}g', tablefmt='pipe', showindex=showindex)

with open("/Analysis/Compactness/README.md", "w") as text_file:
    print('Various compactness metrics:\n', file=text_file)
    print(markdown_table(mean, showindex=True), file=text_file)
    print('\n\n', file=text_file)
    print(markdown_table(pd.DataFrame(all.to_records()), showindex="never"), file=text_file)
