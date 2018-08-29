import folium
import geopandas as gpd
%matplotlib inline
import numpy as np
import shapely.ops as so
import random

# get spaced out colors, shuffle them
import matplotlib
cmap = matplotlib.cm.get_cmap('gist_rainbow')
colors = cmap(np.linspace(0,1,33))
np.random.seed(105)
np.random.shuffle(colors)

affected = [63, 69, 70, 71, 74, 77, 80, 89, 90, 92, 95]
adjacent= [27, 55, 61, 62, 64, 66, 68, 72, 73, 75, 76, 78, 79, 81, 83, 85, 91, 93, 94, 96, 97, 100]
bh = affected + adjacent

bounds = [[36.482, -78.91], [38.22,-75.19]]

################## #
# load enacted map #
################## #
enacted_map = 'Maps/Enacted map/enacted.shp'
df_enacted = gpd.read_file(enacted_map)

# turn non-BH districts into a single shape
nonBH = so.cascaded_union(df_enacted.loc[~df_enacted['ID'].isin(bh), 'geometry'])

# filter to just relevant districts
df_enacted = df_enacted[df_enacted['ID'].isin(bh)]

# some stuff for labeling
df_enacted['Empty'] = ''


###################
# load reform map #
###################

reform_map = 'Maps/Reform map/Districts map bethune-hill final.shp'
df_reform = gpd.read_file(reform_map)[1:]
df_reform['DISTRICT'] = df_reform['DISTRICT'].astype(str)

# some stuff for labeling
df_reform['Empty'] = ''


#######################
# load house Dems map #
#######################

dem_map = 'Maps/House Dems map/HB7001.shp'
df_dem = gpd.read_file(dem_map)

# filter to relevant districts
df_dem = df_dem[df_dem['OBJECTID'].isin(bh)]

# some stuff for labeling
df_dem['Empty'] = ''


# assign colors as shuffled above
def rgb_to_hex(rgb):
    f = lambda x: int(x*255)
    return '#%02X%02X%02X' % (f(rgb[0]), f(rgb[1]), f(rgb[2]))
    
for i, district in enumerate(bh):
    color = rgb_to_hex(colors[i])
    # color = '#%02X%02X%02X' % (int(colors[i][0]*255),int(colors[i][1]*255),int(colors[i][2]*255))
    df_enacted.loc[df_enacted['ID']==district, 'color'] = color
    df_reform.loc[df_reform['DISTRICT'].astype(int)==district, 'color'] = color
    df_dem.loc[df_dem['OBJECTID']==district, 'color'] = color

style_function = lambda x: {'fillColor': x['properties']['color'] if 'color' in x['properties'] else '#fff',
                            'fillOpacity': 0.35,
                            'weight': 1.4,
                            'color': '#888'}

highlight_function = lambda x: {'fillColor': x['properties']['color'] if 'color' in x['properties'] else '#fff',
                            'fillOpacity': 0.65,
                            'weight': 1.4,
                            'color': '#888'}


###################
# make folium map #
###################

m = folium.Map(tiles=None, control_scale=True, min_lat=bounds[0][0], max_lat=bounds[1][0], min_lon=bounds[0][1], max_lon=bounds[1][1], max_bounds=True)

tooltip_reform = folium.features.GeoJsonTooltip(['Empty', 'DISTRICT'], aliases=['Reform map', 'District'])
folium.features.GeoJson(df_reform, name='Reform map', style_function=style_function, highlight_function=highlight_function, show=True, tooltip=tooltip_reform).add_to(m)

tooltip_enacted = folium.features.GeoJsonTooltip(['Empty', 'ID'], aliases=['Enacted map', 'District'])
folium.features.GeoJson(df_enacted, name='Enacted map', style_function=style_function, highlight_function=highlight_function, show=False, tooltip=tooltip_enacted).add_to(m)

tooltip_dem = folium.features.GeoJsonTooltip(['Empty', 'OBJECTID'], aliases=['VA House Dems map', 'District'])
folium.features.GeoJson(df_dem, name='VA House Dems map', style_function=style_function, highlight_function=highlight_function, show=False, tooltip=tooltip_dem).add_to(m)

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

m.save('Maps/interactive/map_comparison.html')

