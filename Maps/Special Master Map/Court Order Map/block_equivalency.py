import geopandas as gpd
import pandas as pd
import sys
sys.path.append('/Users/wtadler/Repos/gerrymander-geoprocessing/areal_interpolation')
from areal_interpolation import aggregate as ag
import tabulate
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

#%config InlineBackend.figure_format = 'svg'

blox = gpd.read_file('/Volumes/GoogleDrive/Team Drives/princeton_gerrymandering_project/mapping/VA/2010 Census/Census Blocks with Population/tabblock2010_51_pophu.shp')
# enacted = gpd.read_file('/Users/wtadler/Repos/VA-gerrymander/Maps/Enacted map/enacted.shp')
enacted = pd.read_csv('/Users/wtadler/Repos/VA-gerrymander/Maps/Enacted map/block_equivalency.txt', header=None, names=['BLOCKID10', 'District_N']).astype(str)

court_order = gpd.read_file('/Users/wtadler/Repos/VA-gerrymander/Maps/Special Master Map/Court Order Map/Groffman_Court_Order.shp')

unchanged = enacted[~enacted['District_N'].isin(set(court_order['District_N']))]
need_assignment = enacted[enacted['District_N'].isin(set(court_order['District_N']))]

census = ag(blox.loc[blox['BLOCKID10'].isin(need_assignment['BLOCKID10']), ['BLOCKID10', 'geometry']],
            court_order[['District_N', 'geometry']],
            target_columns='District_N')[0]

pd.concat([census[['BLOCKID10', 'District_N']], unchanged[['BLOCKID10', 'District_N']]]).sort_values('BLOCKID10').to_csv('Maps/Special Master Map/Court Order Map/block_equivalency.csv', index=False)