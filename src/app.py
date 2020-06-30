# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas               as pd
import plotly.graph_objects as go

from flask_caching   import Cache
from plotly.subplots import make_subplots

import utils
from DataSource      import *


CACHE_TIMEOUT = 43200 # seconds = 12 hour

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': '.cache'
})

app.config.suppress_callback_exceptions = True

# get data from multiple data sources
ds_owid   = OurWorldInData()
ds_jh     = JohnHopkins()

owid_us_data = ds_owid.get_US_data(True)
jh_us_data   = ds_jh.get_US_data()

owid_us_data['new_cases_SMA7'] = owid_us_data.new_cases.rolling(7).mean()
owid_us_data['positive_rate']  = owid_us_data.apply(lambda row: utils.calculate_positive_rate(row.new_cases, row.new_tests), axis=1)


def serve_layout():
    layout = html.Div(
        style={'marginLeft': 200, 'marginRight': 200}, 
        children=[
            html.H3(
                'COVID-19 TracKer',
                style={
                    'textAlign': 'left',
                    'color': '#1d3d63',
                    'family':"Courier New, monospace"
                }),

            html.Div([
                html.P(children=[html.Strong('Coronavirus Disease 2019 (COVID-19)'), html.Span(' is a disease that was first identified in Wuhan, \
                China, and later spread throughout the world. This project has 2 main purposes:')]),
                html.Div(style={'marginLeft': 50}, children=[
                    html.Li('Collect and publish the data required to understand the COVID-19 outbreak in the United States'),
                    html.Li('For me to learn Dash, Plotly, Docker & several AWS Services')]),
                html.P(html.I(children=[html.Span('Any questions or suggestions, please contact me at '), html.Strong('tduongcs [at] gmail [dot] com')]))
            ]),
            html.Br(),

            html.Div(
                dcc.Checklist(
                    id='overall-plot-checkboxes',
                    options=[
                        {'label': 'New Cases', 'value': 'NewCases'},
                        {'label': 'New Cases Moving Average', 'value': 'NewCases_SMA7'},
                        {'label': 'New Tests', 'value': 'NewTests'},
                        {'label': 'Positive Rate', 'value': 'PositiveRate'}
                    ],
                    value=['NewCases', 'NewCases_SMA7'],
                    labelStyle={'display': 'inline-block', 'cursor': 'pointer', 'margin-left':'25px'},
                    style={'border':'1px solid', 'padding': '0.4em', 'border-style': 'outset'}),
                style={'text-align': 'center', 'padding': '1em'}
            ),
            
            html.Div([dcc.Graph(id="overall_plot", config={ 'displayModeBar': False })]),
            html.Br(),
            html.Div([

                html.Div([
                        html.H6("""Select your State""",
                                style={'margin-right': '2em'})]
                ),

                html.Div([
                    dcc.Dropdown(
                        id='state-dropdown',
                        options=[{'label':name, 'value':name} for name in jh_us_data.state.unique()],
                        style=dict(
                                    width='50%',
                                    verticalAlign="middle"
                                )
                    )]),
                    html.Div([dcc.Graph(
                                        id="state_new_case_plot",
                                        config={ 'displayModeBar': False })
                    ]),
                ]),

            html.Hr(),
            html.Div(
                'Copyright © 2020 Tu Duong. All Rights Reserved',
                style={
                    'textAlign': 'center'
                })
        ]
    )
    return layout

## App title, keywords and tracking tag (optional).
app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=UA-161733256-2"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', 'UA-161733256-2');
        </script>
        <meta name="keywords" content="COVID-19,Coronavirus,Dash,Python,Dashboard,Cases,Statistics,tud">
        <title>COVID-19 TracKer by Tu Duong</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
       </footer>
    </body>
</html>"""

app.layout = serve_layout

@app.callback(
    dash.dependencies.Output('overall_plot', 'figure'),
    [dash.dependencies.Input('overall-plot-checkboxes', 'value')]
)
def update_overall_plot(input_value):

    fig = make_subplots(specs=[[{'secondary_y': True}]])
    
    if 'NewCases' in input_value:
        fig.add_trace(go.Bar(name='Daily New Cases',
                        x=owid_us_data.date,
                        y=owid_us_data.new_cases,
                        marker_color='darkblue'))

    if 'NewCases_SMA7' in input_value:
        fig.add_trace(go.Scatter(
                    x=owid_us_data.date, 
                    y=owid_us_data.new_cases_SMA7,
                    mode='lines', line=dict(
                        width=3, color='rgb(100,140,240)'
                    ),
                    name='7 days Moving Average'))
        fig.update_yaxes(rangemode='nonnegative')
    
    if 'NewTests' in input_value:
        fig.add_trace(go.Bar(name='Daily New Tests',
                        x=owid_us_data.date,
                        y=owid_us_data.new_tests,
                        marker_color='darkblue',
                        opacity=0.3))

    if 'PositiveRate' in input_value:
        fig.add_trace(go.Scatter(name='Positive Rate',
                            x=owid_us_data.date,
                            y=owid_us_data.positive_rate,
                            opacity=0.8,
                            marker_color='rgb(255, 127, 14)'),
                    secondary_y="True")
        fig.update_yaxes(rangemode='nonnegative')
    
    fig.update_layout(
        title={'text': "COVID-19 Daily Numbers in United States"},
        barmode='overlay',
        plot_bgcolor='rgb(245,245,245)',
        legend=dict(
            x=0.02,
            y=0.95),
        margin=dict(l=0, r=0, b=0, t=50)
    )

    fig.update_yaxes(title_text='Number of People',  color='darkblue',          secondary_y=False)
    fig.update_yaxes(title_text='Positive Rate (%)', color='rgb(255, 127, 14)', secondary_y=True)

    return fig


@app.callback(
    dash.dependencies.Output('state_new_case_plot', 'figure'),
    [dash.dependencies.Input('state-dropdown', 'value')]
)
def update_output_div(input_value):

    data                   = jh_us_data[ jh_us_data.state == input_value ].copy()
    data['new_cases']      = data.cum_confirmed.diff().fillna(0)
    data['new_cases_SMA7'] = data.new_cases.rolling(7).mean()

    fig = go.Figure( [go.Bar(
                            x=data.date, 
                            y=data.new_cases, 
                            marker_color='darkblue',
                            name='New Cases')])

    fig.add_trace(
                go.Scatter(
                    x=data.date, 
                    y=data.new_cases_SMA7,
                    mode='lines', 
                    line=dict(
                        width=3, 
                        color='rgb(100,140,240)'
                    ),
                    name='7 days Moving Average'
                )
    )
    fig.update_yaxes(rangemode='nonnegative')

    title = "COVID-19 Daily New Cases"

    if input_value is not None:
        title = title + " in " + input_value

    fig.update_layout(
            title={'text': title},
            plot_bgcolor='rgb(245,245,245)',
            legend=dict(
                        x=0.02,
                        y=0.95),
            margin=dict(l=0, r=0, b=0, t=70)
    )
    return fig


if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8050)
