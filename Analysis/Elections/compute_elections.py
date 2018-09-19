import geopandas as gpd
import pandas as pd
import sys
sys.path.append('/Users/wtadler/Repos/gerrymander-geoprocessing/areal_interpolation')
import areal_interpolation as ai
import tabulate
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
%config InlineBackend.figure_format = 'svg'

unconstitutional_only = False


maps = {'reform': {'name': 'Reform map',
                   'path': 'Maps/Reform map/Districts map bethune-hill final.shp',
                   'district_colname': 'DISTRICT',
                   'show': True},
        'enacted': {'name': 'Enacted map',
                    'path': 'Maps/Enacted map/enacted.shp',
                    'district_colname': 'ID',
                    'show': False},
        'dems':    {'name': 'VA House Dems map',
                    'path': 'Maps/House Dems map/HB7001.shp',
                    'district_colname': 'OBJECTID',
                    'show': False}
        }

common_colname = 'district_no'

# identify relevant districts
affected = [63, 69, 70, 71, 74, 77, 80, 89, 90, 92, 95]
adjacent= [27, 55, 61, 62, 64, 66, 68, 72, 73, 75, 76, 78, 79, 81, 83, 85, 91, 93, 94, 96, 97, 100]

if unconstitutional_only:
    bh = [str(i) for i in affected]
else:
    bh = [str(i) for i in affected + adjacent]

affected_label = 'Ruled unconstitutional as enacted'
adjacent_label = 'Adjacent to a district ruled unconstitutional'

#%%
# get census block geography with BVAP and VAP data
precincts = 'Maps/Relevant precincts/BH_precincts_with_BVAP_VAP.shp'
precincts = gpd.read_file(precincts)

potential_cols = ['locality', 'precinct', 'NAME', 'BVAP', 'VAP', 'prop_BVAP', 'prop_D_LG', 'prop_D_p', 'prop_D_G', 'prop_D_AG', 'prop_D_P', 'index', 'geometry']

vote_cols = [i for i in precincts.columns if not any([i==j for j in potential_cols])]

for mapname in maps:
    df = gpd.read_file(maps[mapname]['path'])
    
    df = df.rename(columns={maps[mapname]['district_colname']: common_colname})
        
    df[common_colname] = df[common_colname].astype(str)
    df = df[df[common_colname].isin(bh)]
    
    df = ai.aggregate(precincts, df, source_columns=vote_cols, method='fractional_area')[1]

    df.loc[df[common_colname].isin([str(i) for i in affected]), 'status'] = affected_label
    df.loc[df[common_colname].isin([str(i) for i in adjacent]), 'status'] = adjacent_label

    maps[mapname]['df'] = df

elections = [['P_DEM_16_x', 'P_REP_16_x'],
             ['P_HC_16_x', 'P_BS_16_x'],
             ['G_DEM_17_x', 'G_REP_17_x'],
             ['LG_DEM_17_', 'LG_REP_17_'],
             ['AG_DEM_17_', 'AG_REP_17_']]

fig, ax = plt.subplots(1, len(elections), figsize=(20,3))
colors = {'reform': 'orange',
          'dems': 'blue',
          'enacted': 'red'}

for i, election in enumerate(elections):
    for mapname in maps:
        # print(mapname)
        df = maps[mapname]['df']
        v = df[election[0]] / (df[election[0]] + df[election[1]])
        ax[i].scatter(range(len(v)), sorted(v), label=mapname, s=9, color=colors[mapname])
        ax[i].axhline(.5)
        ax[i].set_title(f'{election[0]} v. {election[1]}')
        ax[i].set_ylim([.35, 1])
        
ax[0].legend()
ax[0].set_ylabel('Candidate 1 voteshare')
ax[0].set_xlabel('ranked district')
fig.savefig('Analysis/Elections/election_results.pdf', bbox_inches='tight')


