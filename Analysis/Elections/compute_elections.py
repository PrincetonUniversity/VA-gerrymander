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

maps = {'reform': {'name': 'PGP Reform map',
                   'path': 'Maps/Reform map/Districts map bethune-hill final.shp',
                   'district_colname': 'DISTRICT',
                   'show': True,
                   'color': 'orange'},
        'enacted': {'name': 'Enacted map',
                    'path': 'Maps/Enacted map/enacted.shp',
                    'district_colname': 'ID',
                    'show': False,
                    'color': 'violet'},
        'dems':    {'name': 'VA House Dems map',
                    'path': 'Maps/House Dems map/HB7001.shp',
                    'district_colname': 'OBJECTID',
                    'show': False,
                    'color': 'blue'},
        'gop':     {'name': 'VA House GOP Map', 
                    'path': 'Maps/GOP map bell substitute/HB7002_ANS.shp',
                    'district_colname': 'OBJECTID',
                    'show': False,
                    'color': 'red'},
        'new_VA':  {'name': 'New VA Majority',
                    'path': 'Maps/New VA Majority/VA NVM Map Submission 20180926.shp',
                    'district_colname': 'District',
                    'show': False,
                    'color': 'green'}
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

pres16 = {'Clinton v. Trump (2016)': ['P_DEM_16_x', 'P_REP_16_x']}
other_elections = {'Clinton v. Sanders (2016)': ['P_HC_16_x', 'P_BS_16_x'],
             'Northam v. Gillespie (2017)': ['G_DEM_17_x', 'G_REP_17_x'],
             'Fairfax v. Vogel (2017)': ['LG_DEM_17_', 'LG_REP_17_'],
             'Herring v. Adams (2017)': ['AG_DEM_17_', 'AG_REP_17_']}

all_elex = {**pres16, **other_elections}

#%%
figs = {'election_results': {'maps': [i for i in maps],
                             'elections': all_elex},
        'election_results_pres_only': {'maps': ['reform', 'dems', 'gop', 'new_VA'],
                                       'elections': pres16}}

for f in figs:
    elections = figs[f]['elections']
    n_elex = len(elections)
    fig, ax = plt.subplots(1, n_elex, figsize=(n_elex*5, 3))

    for i, election in enumerate(elections):
        if n_elex==1:
            axis=ax
        else:
            axis=ax[i]
            
        for mapname in figs[f]['maps']:
            # print(mapname)
            df = maps[mapname]['df']
            v = df[elections[election][0]] / (df[elections[election][0]] + df[elections[election][1]])
            axis.scatter(range(len(v)), sorted(v), label=maps[mapname]['name'], s=15, color=maps[mapname]['color'], alpha=.7, linewidth=1.5, facecolor='none')
            axis.axhline(.5)
            axis.set_title(election)
            axis.set_ylim([.3, 1])
    
    if n_elex==1:
        axis.legend(loc='upper left')
        candidate = election.split(' ')[0]
        axis.set_ylabel(f'{candidate} voteshare')
        axis.set_xlabel(f'District, ranked by {candidate} voteshare')
    else:
        ax[0].legend(loc='upper left')
        ax[0].set_ylabel('Candidate 1 voteshare')
        ax[0].set_xlabel('District, ranked by candidate 1 voteshare')
    
    fig.savefig(f'Analysis/Elections/{f}.pdf', bbox_inches='tight')

