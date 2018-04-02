# !pip install dash
# !pip install dash-renderer
# !pip install dash-html-components
# !pip install dash-core-components
# !pip install plotly --upgrade


import plotly.plotly as py
from plotly.grid_objs import Grid, Column

import time
import numpy as np

from skimage import io

import os
from os import listdir
from os.path import isfile, join


import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

import pickle

import dash_html_components as html
import base64

vertical_slice_frames_path = r'/media/cbios/capstone_files/Kaggle/vertical_slice_frames'
horizontal_slice_frames_path =r'/media/cbios/capstone_files/Kaggle/horizontal_slice_frames/'

# dynamically generate slice list
if os.path.exists('file_list'):
    with open ('file_list', 'rb') as fp:
        all_slices = pickle.load(fp)
else:
    all_slices = [f for f in listdir(vertical_slice_frames_path) if isfile(join(vertical_slice_frames_path, f))]
    with open('file_list', 'wb') as fp:
        pickle.dump(all_slices, fp)

# dynamically generate unique subject scan id list
if os.path.exists('subject_list'):
    with open ('subject_list', 'rb') as fp:
        subject_scan_set = pickle.load(fp)
        subject_scan_set = sorted(subject_scan_set)
else:
    subject_scan_set = set()
    for f in all_slices:
        if len(f) > 10:
            subj_scan_id = f.split('_')[0].replace('a3d','')
            subject_scan_set.add(subj_scan_id)
    print(len(subject_scan_set))

    with open('subject_list', 'wb') as fp:
        pickle.dump(subject_scan_set, fp)

# dynamically update s


app = dash.Dash()

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}
# add logo
image_filename = os.getcwd() + r'/logo.png'
print(image_filename)
current_scan_id = 0
with open('current_scan_id', 'wb') as fp:
        pickle.dump(current_scan_id, fp)
small_slider_value = 7
medium_slider_value = 31
large_slider_value = 330


def compute_expensive_data():
    t=datetime.now()
    d = {'time' : pd.Series(np.array([t.minute, t.second]), index=['minute', 'second'])}
    dat = pd.DataFrame(d).to_json()

    return  dat

small_encoded_image = base64.b64encode(open(image_filename, 'rb').read())
medium_encoded_image = base64.b64encode(open(horizontal_slice_frames_path+subject_scan_set[current_scan_id]+r'/a3daps_'+str(medium_slider_value)+'.png', 'rb').read())
large_encoded_image = base64.b64encode(open(vertical_slice_frames_path+r'/'+subject_scan_set[current_scan_id]+r'a3d_'+str(large_slider_value)+'.png', 'rb').read())


#print(len(encoded_image))


app.layout = html.Div(style={'backgroundColor': colors['background']},
    children=[
    
    html.H1(children='Homeland Security',style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='''APEX Threat Simulation Laboratory''',style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Label('Slider'),
    dcc.Slider(
        id='scan-slider',
        min=0,
        max=len(subject_scan_set),
        marks={i: 'Label {}'.format(i) if i == 1 else str(i) for i in range(1, len(subject_scan_set))},
        value=5,
    ),
   
     html.Div([

    html.Img(id='small_data',src='data:image/png;base64,{}'.format(small_encoded_image.decode())),
    dcc.Slider(
        id='small-slider',
        min=0,
        max=15,
        marks={i: 'Label {}'.format(i) if i == 1 else str(i) for i in range(0, 15)},
        value=small_slider_value,
        className='overview',
    )
    ]),

    html.Div([
        html.Img(id='medium_data',src='data:image/png;base64,{}'.format(medium_encoded_image.decode())),
    dcc.Slider(
        id='medium-slider',
        min=0,
        max=63,
        marks={i: 'Label {}'.format(i) if i == 1 else str(i) for i in range(0, 63)},
        value=medium_slider_value,
    )
    ],className='medium-view'),
    html.Div([
        html.Img(id='large_data',src='data:image/png;base64,{}'.format(large_encoded_image.decode())),
    dcc.Slider(
        id='large-slider',
        min=0,
        max=659,
        marks={i: 'Label {}'.format(i) if i == 1 else str(i) for i in range(0, 659)},
        value=large_slider_value,
    )
    ],className='large-view'),
   
])


@app.callback(
    dash.dependencies.Output('small-slider', 'disabled'),
    [dash.dependencies.Input('scan-slider', 'value')])
def update_selected_subject(selected_uuid):
    with open('current_scan_id', 'wb') as fp:
        pickle.dump(selected_uuid, fp)
    update_small_source(small_slider_value)
    update_medium_source(medium_slider_value)
    update_large_source(large_slider_value)
    return False

#small-slider & small_data
@app.callback(
    dash.dependencies.Output('small_data', 'src'),
    [dash.dependencies.Input('small-slider', 'value')])
def update_small_source(s_slider_value):
    with open ('current_scan_id', 'rb') as fp:
        current_scan_id = pickle.load(fp)
    small_slider_value = s_slider_value
    file_name = horizontal_slice_frames_path+subject_scan_set[current_scan_id]+r'/'+str(small_slider_value)+'.png'
    print("shit")
    small_encoded_image = base64.b64encode(open(file_name, 'rb').read())
    return 'data:image/png;base64,{}'.format(small_encoded_image.decode()) 

#medium-slider & medium_data
@app.callback(
    dash.dependencies.Output('medium_data', 'src'),
    [dash.dependencies.Input('medium-slider', 'value')])
def update_medium_source(m_slider_value):
    with open ('current_scan_id', 'rb') as fp:
        current_scan_id = pickle.load(fp)
    medium_slider_value = m_slider_value
    medium_encoded_image = base64.b64encode(open(horizontal_slice_frames_path+subject_scan_set[current_scan_id]+r'/a3daps_'+str(medium_slider_value)+'.png', 'rb').read())
    return 'data:image/png;base64,{}'.format(medium_encoded_image.decode()) 

#large-slider & large_data
@app.callback(
    dash.dependencies.Output('large_data', 'src'),
    [dash.dependencies.Input('large-slider', 'value')])
def update_large_source(l_slider_value):
    with open ('current_scan_id', 'rb') as fp:
        current_scan_id = pickle.load(fp)
    large_slider_value = l_slider_value
    large_encoded_image = base64.b64encode(open(vertical_slice_frames_path+r'/'+subject_scan_set[current_scan_id]+r'a3d_'+str(large_slider_value)+'.png', 'rb').read())
    return 'data:image/png;base64,{}'.format(large_encoded_image.decode()) 



if __name__ == '__main__':
    app.run_server(debug=True,port=8080)#,threaded=True)
