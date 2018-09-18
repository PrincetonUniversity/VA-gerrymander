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
outline_col = '#ffffff'

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

maps = {'reform': {'name': 'PGP Reform',
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
                    'show': False},
        'gop':    {'name': 'VA House GOP',
                    'path': start_path + 'Maps/GOP map/HB7002_shapefile.shp',
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
style_out = lambda x: {'fillColor': x['properties']['color'] \
                                if 'color' in x['properties'] else '#fff',
                            'color': outline_col,
                            'fillOpacity': 0,
                            'weight': 1.5}
                            
highlight_out = lambda x: {'fillColor': '#adadad',
                                'fillOpacity': 0.4,
                                'weight': 3,
                                'color': outline_col}

#======================
# style for choropleths
#======================

ch_colors = ['#000004', '#33095e', '#781c6d', '#bb3754', '#ed6925', \
             '#fcb519', '#fcffa4']

# Proportion BVAP

prop_bnds = [0.0, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9]

style_prop = lambda x: {'fillColor': ch_colors[0] if x['properties']['Perc_BVAP'] >= prop_bnds[0] and x['properties']['Perc_BVAP'] <= prop_bnds[1] \
                         else ch_colors[1] if x['properties']['Perc_BVAP'] >= prop_bnds[1] and x['properties']['Perc_BVAP'] <= prop_bnds[2] \
                         else ch_colors[2] if x['properties']['Perc_BVAP'] >= prop_bnds[2] and x['properties']['Perc_BVAP'] <= prop_bnds[3] \
                         else ch_colors[3] if x['properties']['Perc_BVAP'] >= prop_bnds[3] and x['properties']['Perc_BVAP'] <= prop_bnds[4] \
                         else ch_colors[4] if x['properties']['Perc_BVAP'] >= prop_bnds[4] and x['properties']['Perc_BVAP'] <= prop_bnds[5] \
                         else ch_colors[5] if x['properties']['Perc_BVAP'] >= prop_bnds[5] and x['properties']['Perc_BVAP'] <= prop_bnds[6] \
                         else ch_colors[6],
                         'fillOpacity': 0.8,
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

# Load Choropleth Dataframe
choro_path = "C:/Users/conno/Documents/GitHub/VA-gerrymander/Maps/Relevant census tracts/BH_Tracts.json"
choro_json = gpd.read_file(choro_path)
choro_json['Perc_BVAP'] = choro_json['Perc_BVAP'].round(3)

# create tooltips
tooltip_prop = folium.features.GeoJsonTooltip(['Perc_BVAP'], aliases=['Proportion BVAP'])

# create choropleth names
prop_name = 'Prop BVAP'

# ==========
# # Add maps
# ==========

# Prop
folium.features.GeoJson(choro_json, name=prop_name, control=False,
                        style_function=style_prop, tooltip=tooltip_prop,
                        overlay=True).add_to(m)

# non-relevant VA districts
folium.features.GeoJson(nonBH, show=True, control=False, \
                        style_function=lambda x: \
                        {'fillColor': '#000', 'weight': 0, 'fillOpacity': .5},\
                         name='nonBH districts', \
                         tooltip='Non-affected districts').add_to(m)

# Set up maps with outline
for mapname in maps:
    tooltip = folium.features.GeoJsonTooltip(['Empty', 'status', \
                                              common_colname],\
                                             aliases=[maps[mapname]['name'],\
                                                      'Status', 'District'])
    folium.features.GeoJson(maps[mapname]['df'],
                            name=maps[mapname]['name'],
                            style_function=style_out,
                            highlight_function=highlight_out,
                            show=maps[mapname]['show'],
                            tooltip=tooltip,
                            overlay=False).add_to(m)
    
# Add open street map as a raaster layer
folium.raster_layers.TileLayer(control=True, min_zoom=8, overlay=True, show=True).add_to(m)

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

legend_box = '''

<div id="Legend Proportion BVAP" style="position: fixed; bottom: 20px; right: 12px; border: 0px; z-index: 9999; font-size: 13px; border-radius: 5px; background-color: #fff; padding: 8px; box-shadow: 0px 2px 4px #888; opacity: 1; width: 160px; max-width: 45em; overflow: auto; white-space: nowrap">
	     <style>
	/* basic positioning */
	
	.legend {
	  list-style: none;
	  padding-left: 0;
	}
	
	.legend li {
	  float: left;
	  margin-right: 2px;
	}
	
	.legend span {
	  border: 1px solid #ccc;
	  float: left;
	  width: 12px;
	  height: 12px;
	  margin: 2px;
	}
	
	/* your colors */
	
	.legend .choro1 {
	  background-color: #000004;
	}
	
	.legend .choro2 {
	  background-color: #33095e;
	}
	
	.legend .choro3 {
	  background-color: #781c6d;
	}
	
	.legend .choro4 {
	  background-color: #bb3754;
	}
	
	.legend .choro5 {
	  background-color: #ed6925;
	}
	
	.legend .choro6 {
	  background-color: #fcb519;
	}
	
	.legend .choro7 {
	  background-color: #fcffa4;
	}
	
	</style>
	
	<font size="5">Legend</font><br>
	<font size="3" id="Legend Title">Proportion BVAP</font><br>
	<ul class="legend">
	  <li><span class="choro1"></span> 0.00 - 0.25</li><br>
	  <li><span class="choro2"></span> 0.25 - 0.40</li><br>
	  <li><span class="choro3"></span> 0.40 - 0.50</li><br>
	  <li><span class="choro4"></span> 0.50 - 0.60</li><br>
	  <li><span class="choro5"></span> 0.60 - 0.75</li><br>
	  <li><span class="choro6"></span> 0.75 - 0.90</li><br>
	  <li><span class="choro7"></span> 0.90 - 1.00</li><br>
	</ul>
	</div>
'''

m.get_root().html.add_child(folium.Element(legend_box))


folium.map.FitBounds(bounds).add_to(m)

m.get_root().header.add_child(folium.Element(
    '<meta name="viewport" content="width=device-width,'
    ' initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />'
))

filename = "C:/Users/conno/Documents/GitHub/VA-gerrymander/Maps/Interactive/map_comparison.html"
m.save(filename)

