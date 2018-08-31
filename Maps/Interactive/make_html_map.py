import folium
import geopandas as gpd
import numpy as np
import shapely
import fileinput
import matplotlib.cm as cm
import pandas as pd


#%%
# get spaced out colors, shuffle them
cmap = cm.get_cmap('gist_rainbow')
colors = cmap(np.linspace(0,1,33))
np.random.seed(105)
np.random.shuffle(colors)

def rgb_to_hex(rgb):
    f = lambda x: int(x*255)
    return '#%02X%02X%02X' % (f(rgb[0]), f(rgb[1]), f(rgb[2]))

# identify relevant districts
affected = [63, 69, 70, 71, 74, 77, 80, 89, 90, 92, 95]
adjacent= [27, 55, 61, 62, 64, 66, 68, 72, 73, 75, 76, 78, 79, 81, 83, 85, 91, 93, 94, 96, 97, 100]
bh = [str(i) for i in affected + adjacent]

colordict = {}
affected_label = 'Ruled unconstitutional as enacted'
adjacent_label = 'Adjacent to a district ruled unconstitutional'
# assign status and pre-shuffled colors
for i, district in enumerate(affected):
    colordict[str(district)] = {'status': affected_label,
                                'color': rgb_to_hex(colors[i])}
for i, district in enumerate(adjacent):
    colordict[str(district)] = {'status': adjacent_label,
                                'color': rgb_to_hex(colors[i+len(affected)])}
    
# manually change some colors:
colordict['62']['color'] = '#002235'
colordict['83']['color'] = colordict['95']['color']
colordict['81']['color'] = '#330035'
colordict['64']['color'] = colordict['61']['color']
colordict['97']['color'] = colordict['75']['color']

color_df = pd.DataFrame.from_dict(colordict, orient='index')

# map boundaries, SW and NE points
bounds = [[36.55, -78.91], [38.5,-75]]

# info on what maps to load
maps = {'reform': {'name': 'PGP Reform map',
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

for mapname in maps:
    df = gpd.read_file(maps[mapname]['path'])
    
    if mapname=='enacted':
        nonBH = shapely.ops.cascaded_union(df.loc[~df[maps['enacted']['district_colname']].isin(bh), 'geometry'])
    
    df = df.rename(columns={maps[mapname]['district_colname']: common_colname})
    df[common_colname] = df[common_colname].astype(str)
    df = df[df[common_colname].isin(bh)]
    
    # assign colors and status
    df = df.merge(color_df, left_on=common_colname, right_index=True)
    
    # for labeling purposes
    df['Empty'] = ''
    
    maps[mapname]['df'] = df

# polygon style
style_function = lambda x: {'fillColor': x['properties']['color'] if 'color' in x['properties'] else '#fff',
                            'fillOpacity': 0.18 if x['properties']['status']==adjacent_label else 0.55,
                            'weight': 1.5,
                            'color': '#888'}

# style when mousing over
highlight_function = lambda x: {'fillColor': x['properties']['color'] if 'color' in x['properties'] else '#fff',
                                'fillOpacity': 0.7,
                                'weight': 1.5,
                                'color': '#888'}


###################
# make folium map #
###################

m = folium.Map(tiles=None, control_scale=True, min_lat=bounds[0][0], max_lat=bounds[1][0], min_lon=bounds[0][1], max_lon=bounds[1][1], max_bounds=True)

for mapname in maps:
    tooltip = folium.features.GeoJsonTooltip(['Empty', 'status', common_colname],
                                             aliases=[maps[mapname]['name'], 'Status', 'District'])
    folium.features.GeoJson(maps[mapname]['df'],
                            name=maps[mapname]['name'],
                            style_function=style_function,
                            highlight_function=highlight_function,
                            show=maps[mapname]['show'],
                            tooltip=tooltip,
                            overlay=False).add_to(m)


# non-relevant VA districts
folium.features.GeoJson(nonBH, show=True, control=False, style_function=lambda x: {'fillColor': '#000', 'weight': 0, 'fillOpacity': .5}, name='nonBH districts', tooltip='Non-affected districts').add_to(m)

folium.raster_layers.TileLayer(control=False, min_zoom=8).add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

folium.map.FitBounds(bounds).add_to(m)

m.get_root().header.add_child(folium.Element(
    '<meta name="viewport" content="width=device-width,'
    ' initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />'
))

info_box = '''
     <div style="position: fixed; top: 12px; left: 70px; border: 0px; z-index: 9999; font-size: 13px; border-radius: 5px; background-color: #fff; padding: 8px; box-shadow: 0px 2px 4px #888; opacity: 0.85; width: calc(100% - 270px); max-width: 45em; overflow: auto; white-space: nowrap">
     <b style="font-size: 16px">Accompanying maps for "<a style="color: #e77500" href="https://pilotonline.com/opinion/columnist/guest/article_7a44a308-abb4-11e8-bec1-0361d680b78f.html">Lawmakers should fix inequitable district lines</a>"<br></b><b><em>The Virginian-Pilot</em>, August 30, 2018</b><br>
     Ben Williams, William T. Adler, and Samuel S.-H. Wang of the <a style="color: #e77500" href="http://gerrymander.princeton.edu/">Princeton Gerrymandering Project</a><br>
     Additional work by Connor Moffatt and Jacob Wachspress<br>
     More info <a style="color: #e77500" href="https://github.com/PrincetonUniversity/VA-gerrymander">here</a>
      </div>
    '''
m.save('Maps/interactive/map_comparison_no_infobox.html')    
m.get_root().html.add_child(folium.Element(info_box))
m.save('Maps/interactive/map_comparison.html')    


