import numpy as np
import pandas as pd

from bokeh.io import curdoc
from bokeh.layouts import row, column, widgetbox, layout
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.widgets import Select, RadioButtonGroup, TextInput, Div
from bokeh.plotting import figure
from bokeh.tile_providers import WMTSTileSource

# region ids
region_ids = [1282, 1232, 1181, 1231, 1230, 1281, 1180, 1233, 1333, 1179, 1334,
       1130, 1229, 1178, 1384, 1182, 1234, 1332, 1129, 1228, 1128, 1177,
       1127, 1285, 1383, 1385, 1283, 1286, 1734, 1783, 1126, 1280, 1227,
       1235, 2118, 1131, 1076, 1335, 1183, 2068, 1284, 1077, 1337, 1287,
       2168, 1075, 1125, 1336, 1331, 1132, 1338, 1386, 2119, 1436, 1437,
       1279, 1387, 1174, 1224, 1382, 1326, 1327, 1173, 1388, 1176, 1184,
       1431, 1223, 1390, 1389, 1278, 1684, 1376, 1530, 1273, 1175, 1482,
       1438, 1483, 1339, 2069, 1480, 1222, 1533, 1434, 1435, 1377, 1272,
       1380, 1439, 1274, 1532, 1442, 1378, 1172, 1426, 1580, 1733, 1225,
       1630, 1441, 1221]
region_ids.sort()

# load data
orig_ts = pd.read_csv('data/taxi_aggregate.csv', parse_dates=['date'])
orig_ts = orig_ts.pivot_table(index='date', columns='region', values='trip_count')

pred_ts = [None] * 6
pred_ts[0] = pd.read_csv('data/taxi_pred1h.csv', parse_dates=['date'])
pred_ts[1] = pd.read_csv('data/taxi_pred2h.csv', parse_dates=['date'])
pred_ts[2] = pd.read_csv('data/taxi_pred3h.csv', parse_dates=['date'])
pred_ts[3] = pd.read_csv('data/taxi_pred4h.csv', parse_dates=['date'])
pred_ts[4] = pd.read_csv('data/taxi_pred5h.csv', parse_dates=['date'])
pred_ts[5] = pd.read_csv('data/taxi_pred6h.csv', parse_dates=['date'])

region_coords = pd.read_csv('data/regions.csv', index_col='region')

# helper functions
def fetch_orig_value(region):
    return orig_ts[region].values

def fetch_pred_time(hour, region):
    data = pred_ts[hour]
    return data[data.region==region].date.values

def fetch_pred_value(hour, region):
    data = pred_ts[hour]
    return data[data.region==region].y.values

# global states
region = 1075
phour = 0

# make sources
orig_source = ColumnDataSource(data={'x': orig_ts.index, 'y': fetch_orig_value(region)})
pred_source = ColumnDataSource(data={'x': fetch_pred_time(phour, region), 'y': fetch_pred_value(phour, region)})
region_source = ColumnDataSource(data={'x': [region_coords.loc[region].x0], 'y': [region_coords.loc[region].y0]})

# region selector
def on_region_changed(attr, old, new):
    global region
    region = int(new)        
    orig_source.data['y'] = fetch_orig_value(region)
    pred_source.data['x'] = fetch_pred_time(phour, region)
    pred_source.data['y'] = fetch_pred_value(phour, region)
    region_source.data['x'] = [region_coords.loc[region].x0]
    region_source.data['y'] = [region_coords.loc[region].y0]

region_sel = Select(title='Регион:', options=[str(region) for region in region_ids], width=350)
region_sel.on_change('value', on_region_changed)

# hour selector
def on_hour_click(value):
    global phour
    phour = value
    pred_source.data['x'] = fetch_pred_time(phour, region)
    pred_source.data['y'] = fetch_pred_value(phour, region)    

phour_sel = RadioButtonGroup(labels=['Час +1', 'Час +2', 'Час +3', 'Час +4', 'Час +5', "Час +6"], active=0, width=500)
phour_sel.on_click(on_hour_click)

# tile service
cartodb_tiles = WMTSTileSource(url='http://tiles.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png')

# map widget
map_widget = figure(width=350, height=350, tools='pan, wheel_zoom, reset')
map_widget.axis.visible = False
map_widget.add_tile(cartodb_tiles)
map_widget.rect(x=region_coords.x0, y=region_coords.y0, width=1236, height=1236, 
                color='deepskyblue', line_color='grey', fill_alpha=0.2)
map_widget.rect(x='x', y='y', source=region_source, width=1236, height=1236, 
                color='lightcoral', fill_alpha=0.8)

#hover = HoverTool(tooltips=[('Прогноз', "@y")])

# plot widget
plot_widget = figure(width=900, height=500, x_axis_type='datetime', tools='pan, wheel_zoom, reset, resize')
plot_widget.line('x', 'y', source=orig_source, color='navy', alpha=0.8, line_width=1, legend='Фактические данные')
plot_widget.line('x', 'y', source=pred_source, color='firebrick', alpha=0.8, line_width=1, legend='Прогнозируемые данные')

# head
head = Div(text="""<h2>Прогноз количества вызовов такси в Нью-Йорке в июне месяце.<h2>""", width=800)

#widgets1 = row([column([region_sel, map_widget]),
#               column([widgetbox(phour_sel), plot_widget])])               

widgets2 = column(row(head),
                  row(region_sel, phour_sel),
                  row(map_widget, plot_widget))

#widgets = layout([
#    [region_sel, phour_sel],
#    [map_widget, plot_widget],
#], sizing_mode='fixed')

# document
curdoc().add_root(widgets2)
curdoc().title = 'Такси Нью-Йорка - Прогнозирование временных рядов на карте'