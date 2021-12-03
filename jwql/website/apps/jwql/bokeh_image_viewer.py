import os

from astropy.io import fits
from astropy.visualization import ZScaleInterval
from bokeh.io import curdoc
from bokeh.embed import components
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, LinearColorMapper, ColorBar, CustomJS, RadioButtonGroup
from bokeh.plotting import figure
import glob
import numpy as np

from jwql.utils.utils import get_config

def bokeh_view(file_root):

    print(file_root)
    file_path = os.path.join(get_config()['filesystem'], 'public', file_root[:7], file_root.split('_')[0])
    files = sorted(glob.glob(os.path.join(file_path, '{}*.fits'.format(file_root))))
    print(files)

    print(file_path)

    data = fits.getdata(files[0], 'SCI')
    #data = data[0:100,0:100]
    n_y, n_x = data.shape
    source = ColumnDataSource(data={'active': [fits.getdata(files[0], 'SCI').astype('float')]})
    data = {'sci': [fits.getdata(files[0], 'SCI').astype('float') * 1.5],
            'err': [fits.getdata(files[0], 'ERR').astype('float')],
            'dq': [fits.getdata(files[0], 'DQ').astype('float')]}

    # limits = {}
    # for key in data.keys():
    #     z = ZScaleInterval()
    #     vmin, vmax = z.get_limits(data[key][0])
    #     limits['{}_vmin'.format(key)] = vmin
    #     limits['{}_vmax'.format(key)] = vmax
    # source_vmin = ColumnDataSource(data={})
    # limits = ColumnDataSource(data=limits)

    z = ZScaleInterval()
    vmin, vmax = z.get_limits(data['sci'][0])
    print('1')
    p = figure(tooltips=[("x", "$x"), ("y", "$y"), ("value", "@active")], match_aspect=True, x_range=(0, n_x), y_range=(0, n_y),
               tools='pan, wheel_zoom, reset, save, hover', active_scroll="wheel_zoom")
    print('2')
    # must give a vector of image data for image parameter
    color_mapper = LinearColorMapper(palette="Greys256", low=vmin, high=vmax)
    im = p.image(image='active', x=0, y=0, dw=n_x, dh=n_y, color_mapper=color_mapper, level="image", source=source)
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=12, border_line_color=None, location=(0,0), orientation='horizontal')
    p.add_layout(color_bar, 'below')
    print('3')
    p.grid.grid_line_width = 0.5

    # Add buttons to change image type viewed
    LABELS = ["uncal", "rate", "cal"]

    # callback = CustomJS(args=dict(source=source), code="""
    #    console.log('hi');
    #    const data = source.data;
    #    var old = data['sci'];
    #    var new = data['err'];
    #    old = new;
    #    source.change.emit();
    #     """)
    print('3.....')
    callback = CustomJS(args=dict(source=source, data=data), code="""
       //console.log(source.data['active']);

       console.log(source.data['active'][0]);
       console.log(data['sci'][0]);

       //const data = source.data;
       //const new_data = [data['sci']][0];
       //data['active'] = new_data;
       source.data['active'][0] = data['sci'][0]
       source.change.emit();
       //console.log(source.data['active']);
    """)
    print('3.....')
    radio_button_group = RadioButtonGroup(labels=LABELS, active=0)
    print('3.....')
    radio_button_group.js_on_click(callback)
    #print(im.data_source.data['image'])
    print('4')
    
    layout = column(radio_button_group, p)
    print('5')
    script, div = components(layout)
    print('6')

    return div, script
