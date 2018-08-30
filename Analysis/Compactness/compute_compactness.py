import continuous_measures as cm
import geopandas as gpd
import pandas as pd
%load_ext autoreload
%autoreload 2

maps = {'reform': {'name': 'Reform map',
                   'path': '../../Maps/Reform map/Districts map bethune-hill final.shp',
                   'district_colname': 'DISTRICT',
                   'show': True},
        'enacted': {'name': 'Enacted map',
                    'path': '../../Maps/Enacted map/enacted.shp',
                    'district_colname': 'ID',
                    'show': False},
        'dems':    {'name': 'VA House Dems map',
                    'path': '../../Maps/House Dems map/HB7001.shp',
                    'district_colname': 'OBJECTID',
                    'show': False}
        }

metrics = {'reock': cm.reock,
           'schwartzberg': cm.schwartzberg,
           'c_hull_ratio': cm.c_hull_ratio,
           'polsby_popper': cm.polsby_popper}

# identify relevant districts
affected = [63, 69, 70, 71, 74, 77, 80, 89, 90, 92, 95]
adjacent= [27, 55, 61, 62, 64, 66, 68, 72, 73, 75, 76, 78, 79, 81, 83, 85, 91, 93, 94, 96, 97, 100]
bh = [str(i) for i in affected + adjacent]

for mapname in maps:
    df = gpd.read_file(maps[mapname]['path'])
    
    df = df.rename(columns={maps[mapname]['district_colname']: 'district'})
        
    df['district'] = df['district'].astype(str)
    df = df[df['district'].isin(bh)]
    
    for m in metrics:
        df[m] = metrics[m](df)
    df['map'] = mapname
    maps[mapname]['df'] = df
    

with open('README.md', 'w') as file:
    file.write('Compactness scores for relevant maps:\n\n')
    file.write('| Mean compactness metrics | Reock | Convex hull ratio | Polsby-Popper | Schwartzberg |\n')
    file.write('| ------ | ------ | ------ | ------ | ------ |\n')
    for mapname in maps:
        file.write('| __{}__ |'.format(maps[mapname]['name']))
        
        for m in ['reock', 'c_hull_ratio', 'polsby_popper', 'schwartzberg']:
            file.write(' {:.3} |'.format(maps[mapname]['df'].loc[:, m].mean()))
        file.write('\n')
    file.close()
