import folium
import geopandas as gpd
import numpy as np
import shapely
import fileinput
import matplotlib

# get spaced out colors, shuffle them
cmap = matplotlib.cm.get_cmap('gist_rainbow')
colors = cmap(np.linspace(0,1,33))
np.random.seed(105)
np.random.shuffle(colors)

# identify relevant districts
affected = [63, 69, 70, 71, 74, 77, 80, 89, 90, 92, 95]
adjacent= [27, 55, 61, 62, 64, 66, 68, 72, 73, 75, 76, 78, 79, 81, 83, 85, 91, 93, 94, 96, 97, 100]
bh = [str(i) for i in affected + adjacent]

# map boundaries, SW and NE points
bounds = [[36.482, -78.91], [38.22,-75.19]]

# info on what maps to load
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

def rgb_to_hex(rgb):
    f = lambda x: int(x*255)
    return '#%02X%02X%02X' % (f(rgb[0]), f(rgb[1]), f(rgb[2]))

for mapname in maps:
    df = gpd.read_file(maps[mapname]['path'])
    
    if mapname=='enacted':
        nonBH = shapely.ops.cascaded_union(df.loc[~df[maps['enacted']['district_colname']].isin(bh), 'geometry'])
    
    df[maps[mapname]['district_colname']] = df[maps[mapname]['district_colname']].astype(str)
    df = df[df[maps[mapname]['district_colname']].isin(bh)]
    
    # assign colors as shuffled
    for i, district in enumerate(bh):
        color = rgb_to_hex(colors[i])
        df.loc[df[maps[mapname]['district_colname']]==district, 'color'] = color

    # for labeling purposes
    df['Empty'] = ''
    
    maps[mapname]['df'] = df

# polygon style
style_function = lambda x: {'fillColor': x['properties']['color'] if 'color' in x['properties'] else '#fff',
                            'fillOpacity': 0.35,
                            'weight': 1.4,
                            'color': '#888'}

# style when mousing over
highlight_function = lambda x: {'fillColor': x['properties']['color'] if 'color' in x['properties'] else '#fff',
                            'fillOpacity': 0.65,
                            'weight': 1.4,
                            'color': '#888'}


###################
# make folium map #
###################

m = folium.Map(tiles=None, control_scale=True, min_lat=bounds[0][0], max_lat=bounds[1][0], min_lon=bounds[0][1], max_lon=bounds[1][1], max_bounds=True)

for mapname in maps:
    tooltip = folium.features.GeoJsonTooltip(['Empty', maps[mapname]['district_colname']],
                                             aliases=[maps[mapname]['name'], 'District'])
    folium.features.GeoJson(maps[mapname]['df'],
                            name=maps[mapname]['name'],
                            style_function=style_function,
                            highlight_function=highlight_function,
                            show=maps[mapname]['show'],
                            tooltip=tooltip).add_to(m)

# non-relevant VA districts
folium.features.GeoJson(nonBH, show=True, control=False, style_function=lambda x: {'fillColor': '#000', 'weight': 0, 'fillOpacity': .5}, name='nonBH districts', tooltip='Non-affected districts').add_to(m)

folium.raster_layers.TileLayer(control=False, min_zoom=8).add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

info_box = '''
     <div style="position: fixed; top: 12px; left: 70px; border: 0px; z-index: 9999; font-size: 13px; border-radius: 5px; background-color: #fff; padding: 8px; box-shadow: 0px 2px 4px #888; opacity: 0.85;">
     <b style="font-size: 16px">Accompanying maps for "A Fresh Start for Virginia Districting"</b><br>
     Ben Williams, William T. Adler, and Samuel S.-H. Wang of the <a style="color: #e77500" href="http://gerrymander.princeton.edu/">Princeton Gerrymandering Project</a><br>
     Additional work by Connor Moffatt and Jacob Wachspress<br>
     More info <a style="color: #e77500" href="https://github.com/PrincetonUniversity/VA-gerrymander">here</a>
      </div>
    '''
    
m.get_root().html.add_child(folium.Element(info_box))

folium.map.FitBounds(bounds).add_to(m)

m.get_root().header.add_child(folium.Element(
    '<meta name="viewport" content="width=device-width,'
    ' initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />'
))

filename = 'Maps/interactive/map_comparison.html'
m.save(filename)

# switch layer controls from checkbox to radio buttons by finding and replacing
with fileinput.FileInput(filename, inplace=True) as file:
    for line in file:
        print(line.replace('base_layers :', 'tmp'), end='')
with fileinput.FileInput(filename, inplace=True) as file:
    for line in file:
        print(line.replace('overlays :', 'base_layers :'), end='')
with fileinput.FileInput(filename, inplace=True) as file:
    for line in file:
        print(line.replace('tmp', 'overlays :'), end='')
        
