import folium
import geopandas as gpd
import numpy as np
import shapely
import fileinput
import matplotlib.cm as cm
import pandas as pd
import json

#%%

# Color conversion helper function
def rgb_to_hex(rgb):
    f = lambda x: int(x*255)
    return '#%02X%02X%02X' % (f(rgb[0]), f(rgb[1]), f(rgb[2]))

# Define outline color
outline_col = '#42f4ee'

# set the color map
cmap = cm.get_cmap('gist_rainbow')

# create 33 colors and shuffle
colors = cmap(np.linspace(0,1,33))
np.random.seed(105)
np.random.shuffle(colors)

# identify relevant districts
affected = [63, 69, 70, 71, 74, 77, 80, 89, 90, 92, 95]
adjacent= [27, 55, 61, 62, 64, 66, 68, 72, 73, 75, 76, 78, 79, 81, 83, 85, \
           91, 93, 94, 96, 97, 100]
bh = [str(i) for i in affected + adjacent]

# Set colors for each dictionary
colordict = {}
affected_label = 'Ruled unconstitutional as enacted'
adjacent_label = 'Adjacent to a district ruled unconstitutional'
for i, district in enumerate(affected):
    colordict[str(district)] = {'status': affected_label,
                                'color': rgb_to_hex(colors[i])}
for i, district in enumerate(adjacent):
    colordict[str(district)] = {'status': adjacent_label,
                                'color': rgb_to_hex(colors[i+len(affected)])}
    
# manually adjust colors:
colordict['62']['color'] = '#002235'
colordict['83']['color'] = colordict['95']['color']
colordict['81']['color'] = '#330035'
colordict['64']['color'] = colordict['61']['color']
colordict['97']['color'] = colordict['75']['color']

# Create dataframe from the color dictionary
color_df = pd.DataFrame.from_dict(colordict, orient='index')

# map boundaries, SW and NE points
bounds = [[36.482, -78.91], [38.22,-75.19]]

start_path = 'C:/Users/conno/Documents/GitHub/VA-gerrymander/'

maps = {'reform': {'name': 'Reform',
                   'path': start_path + 'Maps/Reform map/Districts map ' + \
                           'bethune-hill final.shp',
                   'district_colname': 'DISTRICT',
                   'show': True},
        'enacted': {'name': 'Enacted',
                    'path': start_path + 'Maps/Enacted map/enacted.shp',
                    'district_colname': 'ID',
                    'show': False},
        'dems':    {'name': 'VA House Dems',
                    'path': start_path + 'Maps/House Dems map/HB7001.shp',
                    'district_colname': 'OBJECTID',
                    'show': False}
        }

common_colname = 'district_no'

# Iterate through every option on the interactive map
for mapname in maps:
    # load in dataframe
    df = gpd.read_file(maps[mapname]['path'])
    
    # Merge all of the non Bethune-Hill districts into one district
    if mapname=='enacted':
        nonBH = shapely.ops.cascaded_union(df.loc[\
                                                  ~df[maps['enacted']\
                                                      ['district_colname']]\
                                                      .isin(bh), 'geometry'])
    
    # Make the identifying column name district_no
    df = df.rename(columns={maps[mapname]['district_colname']: common_colname})
    df[common_colname] = df[common_colname].astype(str)
    
    # Filter out districts that are not Bethune-Hill districts
    df = df[df[common_colname].isin(bh)]
    
    # assign colors as shuffled
    df = df.merge(color_df, left_on=common_colname, right_index=True)
    
    # for labeling purposes
    df['Empty'] = ''
    
    # Place dataframe into the maps dict
    maps[mapname]['df'] = df
    
# Create style functions for fill and outline maps
style_fill = lambda x: {'fillColor': x['properties']['color'] if 'color'\
                                            in x['properties'] else '#fff',
                            'fillOpacity': 0.2 if x['properties']['status']==\
                                                adjacent_label else 0.58,
                            'weight': 1.5 if x['properties']['status']==\
                                            adjacent_label else 3.2,
                            'color': '#888'}

# Create highlight functions for fill and highlight maps
highlight_fill = lambda x: {'fillColor': x['properties']['color'] if \
                                'color' in x['properties'] else '#fff',
                                'fillOpacity': 0.7,
                                'weight': 1.5,
                                'color': '#888'}
                            

#======================
# style for choropleths
#======================

ch_colors = ['#000004', '#33095e', '#781c6d', '#bb3754', '#ed6925', \
             '#fcb519', '#fcffa4']
             
# POP
 
pop_bnds = [0, 500, 1000, 2000, 3000, 5000, 10000]

style_pop = lambda x: {'fillColor': ch_colors[0] if x['properties']['Pop_Dens'] >= pop_bnds[0] and x['properties']['Pop_Dens'] <= pop_bnds[1] 
                         else ch_colors[1] if x['properties']['Pop_Dens'] >= pop_bnds[1] and x['properties']['Pop_Dens'] <= pop_bnds[2] 
                         else ch_colors[2] if x['properties']['Pop_Dens'] >= pop_bnds[2] and x['properties']['Pop_Dens'] <= pop_bnds[3] 
                         else ch_colors[3] if x['properties']['Pop_Dens'] >= pop_bnds[3] and x['properties']['Pop_Dens'] <= pop_bnds[4] 
                         else ch_colors[4] if x['properties']['Pop_Dens'] >= pop_bnds[4] and x['properties']['Pop_Dens'] <= pop_bnds[5] 
                         else ch_colors[5] if x['properties']['Pop_Dens'] >= pop_bnds[5] and x['properties']['Pop_Dens'] <= pop_bnds[6] 
                         else ch_colors[6],
                         'fillOpacity': 1,
                         'weight': 1,
                         'color': ch_colors[0] if x['properties']['Pop_Dens'] >= pop_bnds[0] and x['properties']['Pop_Dens'] <= pop_bnds[1] 
                         else ch_colors[1] if x['properties']['Pop_Dens'] >= pop_bnds[1] and x['properties']['Pop_Dens'] <= pop_bnds[2] 
                         else ch_colors[2] if x['properties']['Pop_Dens'] >= pop_bnds[2] and x['properties']['Pop_Dens'] <= pop_bnds[3] 
                         else ch_colors[3] if x['properties']['Pop_Dens'] >= pop_bnds[3] and x['properties']['Pop_Dens'] <= pop_bnds[4] 
                         else ch_colors[4] if x['properties']['Pop_Dens'] >= pop_bnds[4] and x['properties']['Pop_Dens'] <= pop_bnds[5] 
                         else ch_colors[5] if x['properties']['Pop_Dens'] >= pop_bnds[5] and x['properties']['Pop_Dens'] <= pop_bnds[6] 
                         else ch_colors[6]}
                                
# VAP

vap_bnds = [0, 500, 1000, 2000, 3000, 5000, 10000]

style_vap = lambda x: {'fillColor': ch_colors[0] if x['properties']['VAP_Dens'] >= vap_bnds[0] and x['properties']['VAP_Dens'] <= vap_bnds[1] 
                         else ch_colors[1] if x['properties']['VAP_Dens'] >= vap_bnds[1] and x['properties']['VAP_Dens'] <= vap_bnds[2] 
                         else ch_colors[2] if x['properties']['VAP_Dens'] >= vap_bnds[2] and x['properties']['VAP_Dens'] <= vap_bnds[3] 
                         else ch_colors[3] if x['properties']['VAP_Dens'] >= vap_bnds[3] and x['properties']['VAP_Dens'] <= vap_bnds[4] 
                         else ch_colors[4] if x['properties']['VAP_Dens'] >= vap_bnds[4] and x['properties']['VAP_Dens'] <= vap_bnds[5] 
                         else ch_colors[5] if x['properties']['VAP_Dens'] >= vap_bnds[5] and x['properties']['VAP_Dens'] <= vap_bnds[6] 
                         else ch_colors[6],
                         'fillOpacity': 1,
                         'weight': 1,
                         'color': ch_colors[0] if x['properties']['VAP_Dens'] >= vap_bnds[0] and x['properties']['VAP_Dens'] <= vap_bnds[1] 
                         else ch_colors[1] if x['properties']['VAP_Dens'] >= vap_bnds[1] and x['properties']['VAP_Dens'] <= vap_bnds[2] 
                         else ch_colors[2] if x['properties']['VAP_Dens'] >= vap_bnds[2] and x['properties']['VAP_Dens'] <= vap_bnds[3] 
                         else ch_colors[3] if x['properties']['VAP_Dens'] >= vap_bnds[3] and x['properties']['VAP_Dens'] <= vap_bnds[4] 
                         else ch_colors[4] if x['properties']['VAP_Dens'] >= vap_bnds[4] and x['properties']['VAP_Dens'] <= vap_bnds[5] 
                         else ch_colors[5] if x['properties']['VAP_Dens'] >= vap_bnds[5] and x['properties']['VAP_Dens'] <= vap_bnds[6] 
                         else ch_colors[6]}
                                
# BVAP

bvap_bnds = [0, 200, 500, 1000, 1500, 2500, 5000]

style_bvap = lambda x: {'fillColor': ch_colors[0] if x['properties']['BVAP_Dens'] >= bvap_bnds[0] and x['properties']['BVAP_Dens'] <= bvap_bnds[1] 
                         else ch_colors[1] if x['properties']['BVAP_Dens'] >= bvap_bnds[1] and x['properties']['BVAP_Dens'] <= bvap_bnds[2] 
                         else ch_colors[2] if x['properties']['BVAP_Dens'] >= bvap_bnds[2] and x['properties']['BVAP_Dens'] <= bvap_bnds[3] 
                         else ch_colors[3] if x['properties']['BVAP_Dens'] >= bvap_bnds[3] and x['properties']['BVAP_Dens'] <= bvap_bnds[4] 
                         else ch_colors[4] if x['properties']['BVAP_Dens'] >= bvap_bnds[4] and x['properties']['BVAP_Dens'] <= bvap_bnds[5] 
                         else ch_colors[5] if x['properties']['BVAP_Dens'] >= bvap_bnds[5] and x['properties']['BVAP_Dens'] <= bvap_bnds[6] 
                         else ch_colors[6],
                         'fillOpacity': 1,
                         'weight': 1,
                         'color': ch_colors[0] if x['properties']['BVAP_Dens'] >= bvap_bnds[0] and x['properties']['BVAP_Dens'] <= bvap_bnds[1] 
                         else ch_colors[1] if x['properties']['BVAP_Dens'] >= bvap_bnds[1] and x['properties']['BVAP_Dens'] <= bvap_bnds[2] 
                         else ch_colors[2] if x['properties']['BVAP_Dens'] >= bvap_bnds[2] and x['properties']['BVAP_Dens'] <= bvap_bnds[3] 
                         else ch_colors[3] if x['properties']['BVAP_Dens'] >= bvap_bnds[3] and x['properties']['BVAP_Dens'] <= bvap_bnds[4] 
                         else ch_colors[4] if x['properties']['BVAP_Dens'] >= bvap_bnds[4] and x['properties']['BVAP_Dens'] <= bvap_bnds[5] 
                         else ch_colors[5] if x['properties']['BVAP_Dens'] >= bvap_bnds[5] and x['properties']['BVAP_Dens'] <= bvap_bnds[6] 
                         else ch_colors[6]}
                                

# Proportion BVAP

prop_bnds = [0.0, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9]

style_prop = lambda x: {'fillColor': ch_colors[0] if x['properties']['Perc_BVAP'] >= prop_bnds[0] and x['properties']['Perc_BVAP'] <= prop_bnds[1] \
                         else ch_colors[1] if x['properties']['Perc_BVAP'] >= prop_bnds[1] and x['properties']['Perc_BVAP'] <= prop_bnds[2] \
                         else ch_colors[2] if x['properties']['Perc_BVAP'] >= prop_bnds[2] and x['properties']['Perc_BVAP'] <= prop_bnds[3] \
                         else ch_colors[3] if x['properties']['Perc_BVAP'] >= prop_bnds[3] and x['properties']['Perc_BVAP'] <= prop_bnds[4] \
                         else ch_colors[4] if x['properties']['Perc_BVAP'] >= prop_bnds[4] and x['properties']['Perc_BVAP'] <= prop_bnds[5] \
                         else ch_colors[5] if x['properties']['Perc_BVAP'] >= prop_bnds[5] and x['properties']['Perc_BVAP'] <= prop_bnds[6] \
                         else ch_colors[6],
                         'fillOpacity': 1,
                         'weight': 1,
                         'color': ch_colors[0] if x['properties']['Perc_BVAP'] >= prop_bnds[0] and x['properties']['Perc_BVAP'] <= prop_bnds[1] \
                         else ch_colors[1] if x['properties']['Perc_BVAP'] >= prop_bnds[1] and x['properties']['Perc_BVAP'] <= prop_bnds[2] \
                         else ch_colors[2] if x['properties']['Perc_BVAP'] >= prop_bnds[2] and x['properties']['Perc_BVAP'] <= prop_bnds[3] \
                         else ch_colors[3] if x['properties']['Perc_BVAP'] >= prop_bnds[3] and x['properties']['Perc_BVAP'] <= prop_bnds[4] \
                         else ch_colors[4] if x['properties']['Perc_BVAP'] >= prop_bnds[4] and x['properties']['Perc_BVAP'] <= prop_bnds[5] \
                         else ch_colors[5] if x['properties']['Perc_BVAP'] >= prop_bnds[5] and x['properties']['Perc_BVAP'] <= prop_bnds[6] \
                         else ch_colors[6]}

# None
style_none = lambda x: {'fillColor': ch_colors[0],
                         'fillOpacity': 0,
                         'weight': 1,
                         'color': ch_colors[0],
                         'opacity': 0}

###################
# make folium map #
###################

# Initialize the Interactive map with the correct bounds
m = folium.Map(tiles=None, control_scale=True, min_lat=bounds[0][0], \
               max_lat=bounds[1][0], min_lon=bounds[0][1], \
               max_lon=bounds[1][1], max_bounds=True)


# Set up  maps with fill
for mapname in maps:
    tooltip = folium.features.GeoJsonTooltip(['Empty', 'status', \
                                              common_colname],\
                                             aliases=[maps[mapname]['name'],\
                                                      'Status', 'District'])
    folium.features.GeoJson(maps[mapname]['df'],
                            name=maps[mapname]['name'],
                            style_function=style_fill,
                            highlight_function=highlight_fill,
                            show=maps[mapname]['show'],
                            tooltip=tooltip,
                            overlay=True).add_to(m)

# Load Choropleth Dataframe
choro_path = "G:/Team Drives/princeton_gerrymandering_project/mapping/VA/Bethune Hill/BH Choro SHP/BH_Choro.json"
choro_json = gpd.read_file(choro_path)
choro_json['Perc_BVAP'] = choro_json['Perc_BVAP'].round(3)
choro_json['Pop_Dens'] = choro_json['Pop_Dens'].round()
choro_json['VAP_Dens'] = choro_json['VAP_Dens'].round()
choro_json['BVAP_Dens'] = choro_json['BVAP_Dens'].round()

# create tooltips
tooltip_pop = folium.features.GeoJsonTooltip(['Pop_Dens'], aliases=['POP / square mi'])
tooltip_vap = folium.features.GeoJsonTooltip(['VAP_Dens'], aliases=['VAP / square mi'])
tooltip_bvap = folium.features.GeoJsonTooltip(['BVAP_Dens'], aliases=['BVAP / square mi'])
tooltip_prop = folium.features.GeoJsonTooltip(['Perc_BVAP'], aliases=['Proportion BVAP'])

# create choropleth names
pop_name = 'POP / sq. mi'
vap_name = 'VAP / sq. mi'
bvap_name = 'BVAP / sq. mi'
prop_name = 'Prop BVAP'
none_name = 'OpenStreetMap'

# ==========
# # Add maps
# ==========

# None
folium.features.GeoJson(choro_json, name=none_name,
                        style_function=style_none,
                        overlay=False).add_to(m)

# POP
folium.features.GeoJson(choro_json, name=pop_name,
                        style_function=style_pop, tooltip=tooltip_pop,
                        overlay=False).add_to(m)

# VAP
folium.features.GeoJson(choro_json, name=vap_name,
                        style_function=style_vap, tooltip=tooltip_vap,
                        overlay=False).add_to(m)

# BVAP
folium.features.GeoJson(choro_json, name=bvap_name,
                        style_function=style_bvap, tooltip=tooltip_bvap,
                        overlay=False).add_to(m)

# Prop
folium.features.GeoJson(choro_json, name=prop_name,
                        style_function=style_prop, tooltip=tooltip_prop,
                        overlay=False).add_to(m)

# non-relevant VA districts
folium.features.GeoJson(nonBH, show=True, control=False, \
                        style_function=lambda x: \
                        {'fillColor': '#000', 'weight': 0, 'fillOpacity': .5},\
                         name='nonBH districts', \
                         tooltip='Non-affected districts').add_to(m)

# Add open street map as a raaster layer
folium.raster_layers.TileLayer(control=False, min_zoom=8).add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

info_box = '''
     <div style="position: fixed; top: 12px; left: 70px; border: 0px; z-index: 9999; font-size: 13px; border-radius: 5px; background-color: #fff; padding: 8px; box-shadow: 0px 2px 4px #888; opacity: 0.85; width: calc(100% - 270px); max-width: 45em; overflow: auto; white-space: nowrap">
     <b style="font-size: 16px">Accompanying maps for "<a style="color: #e77500" href="https://pilotonline.com/opinion/columnist/guest/article_7a44a308-abb4-11e8-bec1-0361d680b78f.html">Lawmakers should fix inequitable district lines</a>"<br></b><b><em>The Virginian-Pilot</em>, August 30, 2018</b><br>
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

filename = "C:/Users/conno/Documents/GitHub/VA-gerrymander/Maps/Interactive/map_comparison.html"
m.save(filename)

