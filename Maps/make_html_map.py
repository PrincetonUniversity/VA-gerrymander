import folium
import geopandas as gpd


affected = [63, 69, 70, 71, 74, 77, 80, 89, 90, 92, 95]
adjacent= [27, 55, 61, 62, 64, 66, 68, 72, 73, 75, 76, 78, 79, 81, 83, 85, 91, 93, 94, 96, 97, 100]
bh = affected + adjacent

reform_map = 'Reform map/Districts map bethune-hill final.shp'
df_reform = gpd.read_file(reform_map)[1:]


enacted_map = 'Enacted map/enacted.shp'
df_enacted = gpd.read_file(enacted_map)
df_enacted = df_enacted[df_enacted['ID'].isin(bh)]

m = folium.Map(location=[37.3, -77.1], tiles='openstreetmap',
                   zoom_start=8.4, control_scale=True)
m.choropleth(df_reform, fill_color='none', line_weight=2, line_color='purple', name='Reform map')
m.choropleth(df_enacted, fill_color='none', line_weight=2, line_color='green', name='Enacted map')
folium.LayerControl(collapsed=False).add_to(m)

m.save('map_comparison.html')