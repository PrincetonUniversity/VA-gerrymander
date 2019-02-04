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
import numpy as np

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
# avg the 2017 races
use_races = [['Clinton16'], ['Gov17_Northam', 'LtGov17_Fairfax', 'AtGen17_Herring'], ['Sen18_Kaine']]

vs_en = [np.mean([table.loc[table['map']==en, i].mean() for i in year]) for year in use_races]
ss_en = np.array([np.mean([sum(table.loc[table['map']==en, i]>.5) for i in year]) for year in use_races])/100
ss_sm = np.array([np.mean([sum(table.loc[table['map']==sm, i]>.5) for i in year]) for year in use_races])/100

xticklabels = ['2016', '2017', '2018']
#%%
fig, ax = plt.subplots(figsize=(5,5))
ax.plot(vs_en, color='blue', label='Dem. 2-party vote share')
ax.scatter(range(3), vs_en, color='blue')

ax.plot(ss_en, color='black', label='Dem. seat share, 2011 Enacted map')
ax.scatter(range(3), ss_en, color='black')

ax.plot(ss_sm, color='black', linestyle='--',  label='Dem. seat share, 2019 Special Master map')
ax.scatter(range(3), ss_sm, color='black')

ax.legend(loc='lower left')
yticks = np.linspace(.35, .65, 7)
xlim=[-.5, 2.5]
ylim=[.31, .68]
ax.set(xticks=range(3),
        xticklabels=xticklabels,
        yticks=yticks,
        yticklabels=[f'{int(100*i)}%' for i in yticks],
        ylim=ylim,
        xlim=xlim,
        title='Democrats are gaining strength in Virginia. \nSo much strength, that they win overwhelmingly under either map.')

ax.yaxis.set_minor_locator(ticker.MultipleLocator(.01))
ax.grid(b=True, which='major', color='w', linewidth=2, axis='y')
ax.grid(b=True, which='minor', color=(.99, .99, .99), linewidth=.5, axis='y')
ax.grid(b=True, which='major', color='w', linewidth=0, axis='x')
ax.axhline(.5, color=(.5, .5, .5), linewidth=2.5);

caption = '''


The Democratic share of the vote in recent statewide elections
(blue line) has been steadily increasing. Projected seat share
under the 2011 Enacted map (solid black line) and the 2019 Special
Master map (dashed black line) were obtained for each election
by aggregating precinct-level results. Note that, in a single-member
district system such as the House of Delegates, a discrepancy
between vote share and seat share (also known as the “winners’
bonus”) is expected. It is not at all unusual for the seat margin
to be double that of the vote margin, as in the 2017 and 2018
elections shown here. Electoral precinct data and maps were compiled
by the Princeton Gerrymandering Project. Electoral data was used
from 2016 Presidential, 2017 Governor, Lt. Governor, Atty. Gen.,
and 2018 U.S. Senator races.'''

ax.text(xlim[0], ylim[0], caption, ha='left', va='top', fontsize=9, color='gray')
fig.savefig('Analysis/Elections/votes_seats_over_time.pdf', bbox_inches='tight')



#%%
xticklabels = list(races.keys())
vs_en = [np.mean(table.loc[table['map']==en, race]) for race in xticklabels]
ss_en = np.array([sum(np.array(table.loc[table['map']==en, race])>.5) for race in xticklabels])/100
ss_sm = np.array([sum(np.array(table.loc[table['map']==sm, race])>.5) for race in xticklabels])/100



fig, ax = plt.subplots(figsize=(5,5))
ax.plot(vs_en, color='blue', label='Dem. 2-party vote share')

ax.plot(ss_en, color='black', label='Dem. seat share, 2011 Enacted map')

ax.plot(ss_sm, color='black', linestyle='--',  label='Dem. seat share, 2019 Special Master map')
races.keys()

ax.legend(loc='lower left')
yticks = np.linspace(.35, .65, 7)
xlim = [-.5, 7.5]
ax.set(xticks=range(len(races)),
        yticks=yticks,
        yticklabels=[f'{int(100*i)}%' for i in yticks],
        ylim=[.31, .68],
        xlim=xlim)
ax.set_xticklabels(xticklabels, rotation=45, ha='right')
ax.yaxis.set_minor_locator(ticker.MultipleLocator(.01))
# ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
ax.grid(b=True, which='major', color='w', linewidth=2, axis='y')
ax.grid(b=True, which='minor', color=(.99, .99, .99), linewidth=.5, axis='y')
ax.grid(b=True, which='major', color='w', linewidth=1, axis='x')
ax.axhline(.5, color=(.5, .5, .5), linewidth=2.5);
fig.savefig('Analysis/Elections/votes_seats_over_time_all_races.pdf', bbox_inches='tight')

