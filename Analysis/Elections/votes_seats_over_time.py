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
import matplotlib.ticker as ticker

maps = {'enacted': {'name': 'Enacted map',
                    'path': 'Maps/Enacted map/enacted.shp',
                    'district_colname': 'ID',  'color': 'black',
                    'show': False},
        'SM_court_order': {'name': 'Special Master (Court Ordered Modules)',
                    'path': 'Maps/Special Master Map/Court Order Map/Groffman_Court_Order.shp',
                    'district_colname': 'District_N', 'color': 'purple',
                    'show': False}
        }

common_colname = 'district_no'

affected_label = 'Ruled unconstitutional as enacted'
adjacent_label = 'Adjacent to a district ruled unconstitutional'

for mapname in maps:
    df = gpd.read_file(maps[mapname]['path'])

    df = df.rename(columns={maps[mapname]['district_colname']: common_colname})

    df[common_colname] = df[common_colname].astype(str)

    maps[mapname]['df'] = df

maps['SM_court_order']['df'] = maps['SM_court_order']['df'].append(maps['enacted']['df'].loc[~maps['enacted']['df'][common_colname].isin(maps['SM_court_order']['df'][common_colname])], sort=True, ignore_index=True).sort_values(common_colname)

#%%
# get census block geography with BVAP and VAP data
precincts = gpd.read_file('Maps/VA Precincts/Precincts with CD/Elections/VA_Precincts_CD_and_Elections.shp')

vote_cols = ['G18DHOR','G18DSEN', 'G18OHOR', 'G18OSEN', 'G18RHOR', 'G18RSEN', 'G17DGOV',
       'G17DLTG', 'G17DATG', 'G17DHOD', 'G17RGOV', 'G17RLTG', 'G17RATG',
       'G17RHOD', 'G17OHOD', 'G17OGOV', 'G16DPRS', 'G16RPRS', 'G16OPRS',
       'G16DHOR', 'G16RHOR', 'G16OHOR']
precincts[vote_cols] = precincts[vote_cols].astype(float)

for mapname in maps:
    df = maps[mapname]['df']
    df['map'] = mapname
    df = ai.aggregate(precincts, df, source_columns=vote_cols, method='fractional_area')[1]
    
    maps[mapname]['df'] = df

all = pd.concat([maps[mapname]['df'] for mapname in maps], sort=False)

races = {'Clinton16': 'G16.PRS',
         'HouseOfRep16Dem': 'G16.HOR',
         'Gov17_Northam': 'G17.GOV',
         'LtGov17_Fairfax': 'G17.LTG',
         'AtGen17_Herring': 'G17.ATG',
         'HouseOfDel17Dem': 'G17.HOD',
         'Sen18_Kaine': 'G18.SEN',
         'HouseOfRep18Dem': 'G18.HOR'}

table = all.copy()
for race, code in races.items():
    table[race] = table[code.replace('.', 'D')] / (table[code.replace('.', 'D')] + table[code.replace('.', 'R')])
table['district_no'] = table['district_no'].astype(int)
table = table.reset_index()[['district_no', 'map'] + list(races.keys())].sort_values(['map', 'district_no'])


#%%
en = 'enacted'
sm = 'SM_court_order'

vs_en = np.array([table.loc[table['map']==en, race].mean() for race in races.keys()])
ss_en = np.array([sum(table.loc[table['map']==en, race]>.5)/100 for race in races.keys()])
ss_sm = np.array([sum(table.loc[table['map']==sm, race]>.5)/100 for race in races.keys()])


#%%
# key_races = ['Clinton16', 'LtGov17_Fairfax', 'Sen18_Kaine']
# xticklabels = ['2016 (Pres.)', '2017 (Lt. Gov.)', '2018 (US Sen.)']
# note_keys = np.where([i in key_races for i in races.keys()])[0]
# 
# fig, ax = plt.subplots(figsize=(5,5))
# ax.plot(vs_en[note_keys], color='blue', label='Dem. 2-party vote share')
# ax.scatter(range(3), vs_en[note_keys], color='blue')
# 
# ax.plot(ss_en[note_keys], color='black', label='Dem. seat share, 2011 Enacted map')
# ax.scatter(range(3), ss_en[note_keys], color='black')
# 
# ax.plot(ss_sm[note_keys], color='black', linestyle='--',  label='Dem. seat share, 2019 Special Master map')
# ax.scatter(range(3), ss_sm[note_keys], color='black')
# 
# ax.legend(loc='lower left')
# yticks = np.linspace(.35, .65, 7)
# ax.set(xticks=range(3),
#         xticklabels=xticklabels,
#         yticks=yticks,
#         yticklabels=[f'{int(100*i)}%' for i in yticks],
#         ylim=[.31, .68],
#         xlim=[-.5, 2.5])
# 
# ax.yaxis.set_minor_locator(ticker.MultipleLocator(.01))
# ax.grid(b=True, which='major', color='w', linewidth=2, axis='y')
# ax.grid(b=True, which='minor', color=(.99, .99, .99), linewidth=.5, axis='y')
# ax.grid(b=True, which='major', color='w', linewidth=0, axis='x')
# ax.axhline(.5, color=(.5, .5, .5), linewidth=2.5);
# fig.savefig('dem_trend3_fairfax.png', dpi=300, bbox_inches='tight')



#%%
races = [['Clinton16'], ['Gov17_Northam', 'LtGov17_Fairfax', 'AtGen17_Herring'], ['Sen18_Kaine']]

vs_en = [np.mean([table.loc[table['map']==en, i].mean() for i in year]) for year in races]
ss_en = np.array([np.mean([sum(table.loc[table['map']==en, i]>.5) for i in year]) for year in races])/100
ss_sm = np.array([np.mean([sum(table.loc[table['map']==sm, i]>.5) for i in year]) for year in races])/100

xticklabels = ['2016', '2017', '2018']

fig, ax = plt.subplots(figsize=(5,5))
ax.plot(vs_en, color='blue', label='Dem. 2-party vote share')
ax.scatter(range(3), vs_en, color='blue')

ax.plot(ss_en, color='black', label='Dem. seat share, 2011 Enacted map')
ax.scatter(range(3), ss_en, color='black')

ax.plot(ss_sm, color='black', linestyle='--',  label='Dem. seat share, 2019 Special Master map')
ax.scatter(range(3), ss_sm, color='black')

ax.legend(loc='lower left')
yticks = np.linspace(.35, .65, 7)
ax.set(xticks=range(3),
        xticklabels=xticklabels,
        yticks=yticks,
        yticklabels=[f'{int(100*i)}%' for i in yticks],
        ylim=[.31, .68],
        xlim=[-.5, 2.5])
# ax.xaxis.set_major_locator(ticker.MultipleLocator(.05))
# ax.xaxis.set_minor_locator(ticker.MultipleLocator(.25))
# 
# ax.yaxis.set_major_locator(ticker.MultipleLocator(.05*N))
ax.yaxis.set_minor_locator(ticker.MultipleLocator(.01))
ax.grid(b=True, which='major', color='w', linewidth=2, axis='y')
ax.grid(b=True, which='minor', color=(.99, .99, .99), linewidth=.5, axis='y')
ax.grid(b=True, which='major', color='w', linewidth=0, axis='x')
ax.axhline(.5, color=(.5, .5, .5), linewidth=2.5);
fig.savefig('dem_trend3_2017avg.png', dpi=300, bbox_inches='tight')

