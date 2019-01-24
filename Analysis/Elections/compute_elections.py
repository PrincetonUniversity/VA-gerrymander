import geopandas as gpd
import pandas as pd
import sys
sys.path.append('/Users/hwheelen/Documents/GitHub/gerrymander-geoprocessing/areal_interpolation')
from areal_interpolation import areal_interpolation as ai
import tabulate
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
#%config InlineBackend.figure_format = 'svg'

unconstitutional_only = False

start_path = '/Users/hwheelen/Documents/GitHub/VA-gerrymander/'
maps = {'reform': {'name': 'PGP Reform map',
                   'path': start_path + 'Maps/Reform map/Districts map bethune-hill final.shp',
                   'district_colname': 'DISTRICT',  'color': '#E77500',
                   'show': True},
        'enacted': {'name': 'Enacted map',
                    'path': start_path + 'Maps/Enacted map/enacted.shp',
                    'district_colname': 'ID',  'color': 'black',
                    'show': False},
        'SM_court_order': {'name': 'Special Master (Court Ordered Modules)',
                    'path':start_path + 'Maps/Special Master Map/Court Order Map/Groffman_Court_Order.shp',
                    'district_colname': 'District_N', 'color': 'purple',
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
precincts = '/Users/hwheelen/Documents/GitHub/VA-gerrymander/Maps/VA Precincts/Precincts with CD/Elections/VA_Precincts_CD_and_Elections.shp'
precincts = gpd.read_file(precincts)

#potential_cols = ['locality', 'precinct', 'loc_prec', 'prop_D_LG', 'prop_D_p', 'prop_D_G', 'prop_D_AG', 'prop_D_P', 'index', 'geometry']

#vote_cols = [i for i in precincts.columns if not any([i==j for j in potential_cols])]
vote_cols = ['G18DHOR','G18DSEN', 'G18OHOR', 'G18OSEN', 'G18RHOR', 'G18RSEN', 'G17DGOV',
       'G17DLTG', 'G17DATG', 'G17DHOD', 'G17RGOV', 'G17RLTG', 'G17RATG',
       'G17RHOD', 'G17OHOD', 'G17OGOV', 'G16DPRS', 'G16RPRS', 'G16OPRS',
       'G16DHOR', 'G16RHOR', 'G16OHOR']
for mapname in maps:
        df = gpd.read_file(maps[mapname]['path'])

        df = df.rename(columns={maps[mapname]['district_colname']: common_colname})

        df[common_colname] = df[common_colname].astype(str)
        df = df[df[common_colname].isin(bh)]
        df['map'] = mapname
        df = ai.aggregate(precincts, df, source_columns=vote_cols, method='fractional_area')[1]

        df.loc[df[common_colname].isin([str(i) for i in affected]), 'status'] = affected_label
        df.loc[df[common_colname].isin([str(i) for i in adjacent]), 'status'] = adjacent_label

        maps[mapname]['df'] = df
all = pd.concat([maps[mapname]['df'] for mapname in maps], sort=False)

total = all[['district_no','map',
       'G18DHOR', 'G18DSEN', 'G18OHOR', 'G18OSEN', 'G18RHOR', 'G18RSEN',
       'G17DGOV', 'G17DLTG', 'G17DATG', 'G17DHOD', 'G17RGOV', 'G17RLTG',
       'G17RATG', 'G17RHOD', 'G17OHOD', 'G17OGOV', 'G16DPRS', 'G16RPRS',
       'G16OPRS', 'G16DHOR', 'G16RHOR', 'G16OHOR']]

table = total
table['Clinton16']=table['G16DPRS']/(table['G16DPRS']+table['G16RPRS'])
table['Trump16']=table['G16RPRS']/(table['G16DPRS']+table['G16RPRS'])

table['HouseOfRep16Dem']=table['G16DHOR']/(table['G16DHOR']+table['G16RHOR'])
table['HouseOfRep16Rep']=table['G16RHOR']/(table['G16DHOR']+table['G16RHOR'])

table['Gov17_Northam']=table['G17DGOV']/(table['G17DGOV']+table['G17RGOV'])
table['Gov17_Gillespie']=table['G17RGOV']/(table['G17DGOV']+table['G17RGOV'])

table['LtGov17_Fairfax']=table['G17DLTG']/(table['G17DLTG']+table['G17RLTG'])
table['LtGov17_Vogel']=table['G17RLTG']/(table['G17DLTG']+table['G17RLTG'])

table['AtGen17_Herring']=table['G17DATG']/(table['G17DATG']+table['G17RATG'])
table['AtGen17_Adams']=table['G17RATG']/(table['G17DATG']+table['G17RATG'])

table['HouseOfDel17Dem']=table['G17DHOD']/(table['G17DHOD']+table['G17RHOD'])
table['HouseOfDel17Rep']=table['G17RHOD']/(table['G17DHOD']+table['G17RHOD'])

table['Sen18_Kaine']=table['G18DSEN']/(table['G18DSEN']+table['G18RSEN'])
table['Sen18_Stewart']=table['G18RSEN']/(table['G18DSEN']+table['G18RSEN'])

table['HouseOfRep16Dem']=table['G18DHOR']/(table['G18DHOR']+table['G18RHOR'])
table['HouseOfRep16Rep']=table['G18RHOR']/(table['G18DHOR']+table['G18RHOR'])

elecs = table [['district_no','map','Clinton16','Trump16','HouseOfRep16Dem','HouseOfRep16Rep','Gov17_Northam','Gov17_Gillespie','LtGov17_Fairfax',
                 'LtGov17_Vogel','AtGen17_Herring', 'AtGen17_Adams','HouseOfDel17Dem', 'HouseOfDel17Rep', 'Sen18_Kaine','Sen18_Stewart']]
elecs ['district_no']= elecs['district_no'].astype(int)
elecs = elecs.sort_values('district_no')       
elecs.to_csv('/Users/hwheelen/Documents/GitHub/VA-gerrymander/Analysis/Elections/elections_comparison.csv', index=True, float_format='%.3f')
elecs_dem=elecs[['district_no','map','Clinton16', 'HouseOfRep16Dem','Gov17_Northam','LtGov17_Fairfax', 
                 'AtGen17_Herring','HouseOfDel17Dem','Sen18_Kaine']]
pres16 = {'Clinton v. Trump (2016)': ['G16DPRS', 'G16RPRS']}
other_elections = {'Kaine v. Stewart (2018)': ['G18DSEN', 'G18RSEN'],'Northam v. Gillespie (2017)': ['G17DGOV', 'G17RGOV'],
                   'Fairfax v. Vogel (2017)': ['G17DLTG', 'G17RLTG'],'Herring v. Adams (2017)': ['G17DATG', 'G17RATG']}

all_elex = {**pres16, **other_elections}

#%%
figs = {'election_results': {'maps': [i for i in maps],
                             'elections': all_elex},
        'election_results_pres_only': {'maps': ['reform', 'enacted', 'SM_court_order' ],
                                       'elections': pres16}}
maps['SM_court_order']['name'] = 'Special Master \n  (Court Ordered Modules)'
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
        axis.legend(loc='upper left',prop={'size': 9})
        candidate = election.split(' ')[0]
        axis.set_ylabel(f'{candidate} voteshare')
        axis.set_xlabel(f'District, ranked by {candidate} voteshare')
    else:
        ax[0].legend(loc='upper left',prop={'size': 8})
        ax[0].set_ylabel('Candidate 1 voteshare')
        ax[0].set_xlabel('District, ranked by candidate 1 voteshare')

    fig.savefig(f'/Users/hwheelen/Documents/GitHub/VA-gerrymander/Analysis/Elections/2{f}.pdf', bbox_inches='tight')
#%%
#make markdown
def markdown_table(df, precision=3, showindex=False):
    return tabulate.tabulate(df, headers=df.columns, floatfmt=f'.{precision}g', tablefmt='pipe', showindex=showindex)

with open("/Users/hwheelen/Documents/GitHub/VA-gerrymander/Analysis/Elections/README.md", "w") as text_file:
    print('Various election outcomes:\n', file=text_file)
    print(markdown_table(elecs_dem, showindex=False), file=text_file)
    print('\n\n', file=text_file)
    print(markdown_table(elecs, showindex=False), file=text_file)
