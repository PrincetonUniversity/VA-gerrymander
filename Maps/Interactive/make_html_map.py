import folium
import geopandas as gpd
%matplotlib inline
import numpy as np
import shapely.ops as so

np.random.seed(100)

affected = [63, 69, 70, 71, 74, 77, 80, 89, 90, 92, 95]
adjacent= [27, 55, 61, 62, 64, 66, 68, 72, 73, 75, 76, 78, 79, 81, 83, 85, 91, 93, 94, 96, 97, 100]
bh = affected + adjacent

enacted_map = '../Enacted map/enacted.shp'
df_enacted = gpd.read_file(enacted_map)

# turn non-BH districts into a single shape
nonBH = so.cascaded_union(df_enacted.loc[~df_enacted['ID'].isin(bh), 'geometry'])

# filter
df_enacted = df_enacted[df_enacted['ID'].isin(bh)]

# some stuff for labeling
df_enacted['Map'] = 'Enacted map'
df_enacted['Empty'] = ''

reform_map = '../Reform map/Districts map bethune-hill final.shp'
df_reform = gpd.read_file(reform_map)[1:]

# some stuff for labeling
df_reform['Map'] = 'Reform map'
df_reform['Empty'] = ''

r = lambda: np.random.randint(255)
random_color = lambda: '#%02X%02X%02X' % (r(),r(),r())

style_function = lambda x: {'fillColor': random_color(),
                            'fillOpacity': 0.35,
                            'weight': 1,
                            'color': '#888'}

m = folium.Map(tiles='openstreetmap', control_scale=True, min_zoom=8)

tooltip_reform = folium.features.GeoJsonTooltip(['Empty', 'DISTRICT'], aliases=['Reform map', 'District'])

folium.features.GeoJson(df_reform, name='Reform map', style_function=style_function, show=True, tooltip=tooltip_reform).add_to(m)

tooltip_enacted = folium.features.GeoJsonTooltip(['Empty', 'ID'], aliases=['Enacted map', 'District'])
folium.features.GeoJson(df_enacted, name='Enacted map', style_function=style_function, show=False, tooltip=tooltip_enacted).add_to(m)

folium.features.GeoJson(nonBH, show=True, control=False, style_function=lambda x: {'fillColor': '#000', 'weight': 0, 'fillOpacity': .5}, name='nonBH districts', tooltip='Non-affected districts').add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

folium.map.FitBounds([[36.482, -78.91], [38.22,-75.19]]).add_to(m)

m.get_root().header.add_child(folium.Element(
    '<meta name="viewport" content="width=device-width,'
    ' initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />'
))

m.save('map_comparison.html')

