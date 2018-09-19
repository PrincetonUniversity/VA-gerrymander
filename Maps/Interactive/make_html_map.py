import folium
import geopandas as gpd
import numpy as np
import shapely
import fileinput
import matplotlib.cm as cm
import pandas as pd
import json

make_BVAP_choropleth = False

# Color conversion helper function
def rgb_to_hex(rgb):
    def f(x): return int(x * 255)
    return '#%02X%02X%02X' % (f(rgb[0]), f(rgb[1]), f(rgb[2]))

# set the color map
cmap = cm.get_cmap('gist_rainbow')

# create 33 colors and shuffle
colors = cmap(np.linspace(0, 1, 33))
np.random.seed(105)
np.random.shuffle(colors)

# identify relevant districts
affected = [63, 69, 70, 71, 74, 77, 80, 89, 90, 92, 95]
adjacent = [27, 55, 61, 62, 64, 66, 68, 72, 73, 75, 76, 78, 79, 81, 83, 85,
            91, 93, 94, 96, 97, 100]
bh = [str(i) for i in affected + adjacent]

# Set colors for each district
colordict = {}
affected_label = 'Ruled unconstitutional as enacted'
adjacent_label = 'Adjacent to a district ruled unconstitutional'
for i, district in enumerate(affected):
    colordict[str(district)] = {'status': affected_label,
                                'color': rgb_to_hex(colors[i])}
for i, district in enumerate(adjacent):
    colordict[str(district)] = {'status': adjacent_label,
                                'color': rgb_to_hex(colors[i + len(affected)])}

# manually adjust colors:
colordict['62']['color'] = '#002235'
colordict['83']['color'] = colordict['95']['color']
colordict['81']['color'] = '#330035'
colordict['64']['color'] = colordict['61']['color']
colordict['97']['color'] = colordict['75']['color']

# Create dataframe from the color dictionary
color_df = pd.DataFrame.from_dict(colordict, orient='index')

# map boundaries, SW and NE points
bounds = [[36.482, -78.91], [38.22, -75.19]]

maps = {'reform': {'name': 'PGP Reform',
                   'path': 'Maps/Reform map/Districts map ' +
                           'bethune-hill final.shp',
                   'district_colname': 'DISTRICT',
                   'show': True},
        'enacted': {'name': 'Enacted',
                    'path': 'Maps/Enacted map/enacted.shp',
                    'district_colname': 'ID',
                    'show': False},
        'dems':    {'name': 'VA House Dems',
                    'path': 'Maps/House Dems map/HB7001.shp',
                    'district_colname': 'OBJECTID',
                    'show': False},
        'gop':    {'name': 'VA House GOP',
                   'path': 'Maps/GOP map/HB7002_shapefile.shp',
                   'district_colname': 'OBJECTID',
                   'show': False}
        }

common_colname = 'district_no'

# Iterate through every option on the interactive map
for mapname in maps:
    # load in dataframe
    df = gpd.read_file(maps[mapname]['path'])

    # Merge all of the non Bethune-Hill districts into one district
    if mapname == 'enacted':
        nonBH = shapely.ops.cascaded_union(df.loc[~df[maps['enacted']
                                                      ['district_colname']]
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
    
###################
# styles          #
###################
def style_func(x, choropleth=False, highlight=False):
    if choropleth:
        color = '#fff'
    else:
        color = '#888'
    
    if highlight:
        if choropleth:
            fillColor = '#adadad'
            fillOpacity = 0.4
        else:
            fillColor = x['properties']['color'] if 'color' in x['properties'] else '#fff'
            fillOpacity = 0.7
        weight = 2 # should this be lower or higher for choropleth or not?

    else:
        fillColor = x['properties']['color'] if 'color' in x['properties'] else '#fff'
        if choropleth:
            fillOpacity = 0
        else:
            fillOpacity = 0.18 if x['properties']['status']==adjacent_label else 0.55
        weight = 1
    
    return {'fillColor': fillColor,
            'fillOpacity': fillOpacity,
            'color': color,
            'weight': weight}
            

#choropleth
inferno = lambda x: rgb_to_hex(cm.inferno(x))

choropleth_style_function = lambda x: {'fillColor': inferno(x['properties']['Perc_BVAP']),
                                       'fillOpacity': 0.8,
                                       'weight': 1,
                                       'color': inferno(x['properties']['Perc_BVAP'])}


###################
# make folium map #
###################

# Initialize the Interactive map with the correct bounds
m = folium.Map(tiles=None, control_scale=True, min_lat=bounds[0][0],
               max_lat=bounds[1][0], min_lon=bounds[0][1],
               max_lon=bounds[1][1], max_bounds=True)

if make_BVAP_choropleth:
    # Load Choropleth Dataframe
    choro_path = "Maps/Relevant census tracts/BH_Tracts.json"
    choro_json = gpd.read_file(choro_path)
    choro_json['Perc_BVAP'] = choro_json['Perc_BVAP'].round(3)

    tooltip = folium.features.GeoJsonTooltip(['Perc_BVAP'], aliases=['Proportion BVAP'])

    # prop BVAP choropleth
    folium.features.GeoJson(choro_json,
                            name='Prop BVAP',
                            control=False,
                            style_function=choropleth_style_function,
                            tooltip=tooltip,
                            overlay=True).add_to(m)

# non-relevant VA districts
folium.features.GeoJson(nonBH,
                        show=True,
                        control=False,
                        style_function=lambda x: {'fillColor': '#000', 'weight': 0, 'fillOpacity': .5},
                        name='nonBH districts',
                        tooltip='Non-affected districts').add_to(m)

# Set up maps with outline
for mapname in maps:
    tooltip = folium.features.GeoJsonTooltip(['Empty', 'status', common_colname],
                                             aliases=[maps[mapname]['name'], 'Status', 'District'])
    folium.features.GeoJson(maps[mapname]['df'],
                            name=maps[mapname]['name'],
                            style_function=lambda x: style_func(x, choropleth=make_BVAP_choropleth),
                            highlight_function=lambda x: style_func(x, choropleth=make_BVAP_choropleth, highlight=True),
                            show=maps[mapname]['show'],
                            tooltip=tooltip,
                            overlay=False).add_to(m)

# Add open street map as a raaster layer
folium.raster_layers.TileLayer(control=False, min_zoom=8, overlay=True, show=True).add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

PU_color = '#e77500'

css = f'''
<style>
.overlay_box {{
  position: fixed;
  border: 0;
  border-radius: 5px;
  background-color: #fff;
  padding: 8px;
  box-shadow: 0px 2px 4px #888;
  opacity: 0.85;
  overflow: auto;
  z-index: 9999;
}}

a {{
  color: {PU_color}
}}
</style>
'''

info_box = f'''
<style>
#info {{
  top: 12px;
  left: 70px;
  font-size: 13px;
  width: calc(100% - 230px);
  max-width: 45em;
}}

@media only screen and (max-width: 590px) {{
    #info_box {{
        display: none;
    }}
}}

#title {{
  font-size: 16px;
}}
</style>

<div id="info" class="overlay_box">
<b><span id="title">Accompanying maps for <a href="https://pilotonline.com/opinion/columnist/guest/article_7a44a308-abb4-11e8-bec1-0361d680b78f.html">Lawmakers should fix inequitable district lines</a>"</span><br>
<em>The Virginian-Pilot</em>, August 30, 2018<br></b>
Ben Williams, William T. Adler, and Samuel S.-H. Wang of the <a href="http://gerrymander.princeton.edu/">Princeton Gerrymandering Project</a><br>
Additional work by Connor Moffatt and Jacob Wachspress<br>
More info <a href="https://github.com/PrincetonUniversity/VA-gerrymander">here</a>
</div>
'''
    
legend_box = f'''
<style>
#legend {{
  bottom: 20px;
  right: 12px;
  width: 200px;
  max-width: 45em;
}}

#legend_text {{
  font-size: .91em;
  display: inherit;
  margin-bottom: 10px;
}}

#legend ul {{
  list-style: none;
  padding-left: 0;
}}

#legend li {{
  float: left;
  margin-right: 2px;
}}

.swatch {{
  border: 1px solid #ccc;
  float: left;
  width: 12px;
  height: 12px;
  margin: 2px;
}}

#legend .choro1 {{
  background-color: {inferno(0)};
}}

#legend .choro2 {{
  background-color: {inferno(0.25)};
}}

#legend .choro3 {{
  background-color: {inferno(0.5)};
}}

#legend .choro4 {{
  background-color: {inferno(0.75)};
}}

#legend .choro5 {{
  background-color: {inferno(0.999)};
}}
</style>

<div id="legend" class="overlay_box">
<span id="legend_text">Percentage of population that identifies as non-Hispanic Black (2010 Census), by Census Tract</span>
<ul>
  <li><span class="swatch choro1"></span>0%</li><br>
  <li><span class="swatch choro2"></span>25%</li><br>
  <li><span class="swatch choro3"></span>50%</li><br>
  <li><span class="swatch choro4"></span>75%</li><br>
  <li><span class="swatch choro5"></span>100%</li><br>
</ul>
</div>
'''

m.get_root().html.add_child(folium.Element(css))
m.get_root().html.add_child(folium.Element(info_box))

if make_BVAP_choropleth:
    m.get_root().html.add_child(folium.Element(legend_box))


folium.map.FitBounds(bounds).add_to(m)

# make mobile friendly
m.get_root().header.add_child(folium.Element(
    '<meta name="viewport" content="width=device-width,'
    ' initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />'
))

filename = "Maps/Interactive/map_comparison.html"
m.save(filename)

