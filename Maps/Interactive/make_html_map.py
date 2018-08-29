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

bounds = [[36.482, -78.91], [38.22,-75.19]]

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

m = folium.Map(tiles=None, control_scale=True) #min_lat=bounds[0][0], max_lat=bounds[1][0], min_lon=bounds[0][1], max_lon=bounds[1][1])

tooltip_reform = folium.features.GeoJsonTooltip(['Empty', 'DISTRICT'], aliases=['Reform map', 'District'])

folium.features.GeoJson(df_reform, name='Reform map', style_function=style_function, show=True, tooltip=tooltip_reform).add_to(m)

tooltip_enacted = folium.features.GeoJsonTooltip(['Empty', 'ID'], aliases=['Enacted map', 'District'])
folium.features.GeoJson(df_enacted, name='Enacted map', style_function=style_function, show=False, tooltip=tooltip_enacted).add_to(m)

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

m.save('map_comparison.html')

