# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas               as pd
import plotly.graph_objects as go

import datetime
import dash_table

from DataSource import *

from plotly.subplots import make_subplots

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# get data from multiple data sources
owid_us_data = OurWorldInData().get_US_data()

owid_us_data.to_csv('owid_us_data.csv')
jh_data      = JohnHopkins().get_US_data()

us_covid19_test_data = CovidTracking().get_full_data()
us_covid19_test_data.to_csv('us_covid19_test_data.csv')

# merge 2 panda data frames into 1 data frame
merged_df = pd.merge(owid_us_data,
                 us_covid19_test_data[['date', 'totalTestResultsIncrease']],
                 on='date')

merged_df.to_csv('merge_df.csv')

# replace NaN with 0
merged_df = merged_df.fillna(0)

# generate 'positive_rate' column
merged_df['positive_rate']       = merged_df.apply(lambda row: (row.new_cases / row.totalTestResultsIncrease) * 100 if row.totalTestResultsIncrease else 0, axis = 1)
merged_df['NewNewConfirmedSMA7'] = merged_df.new_cases.rolling(7).mean()

app.layout = html.Div(style={'marginLeft': 200, 'marginRight': 200}, children=[
    html.H3(
        'COVID-19 TracKer',
        style={
            'textAlign': 'left',
            'color': '#636efa',
            'family':"Courier New, monospace"
        }),

    html.Div([
        html.P(children=[html.Strong('Coronavirus Disease 2019 (COVID-19)'), html.Span(' is a disease that was first identified in Wuhan, \
        China, and later spread throughout the world. This project has 2 main purposes:')]),
        html.Div(style={'marginLeft': 50}, children=[
            html.Li('Collect and publish the data required to understand the COVID-19 outbreak in the United States'),
            html.Li('For me to learn Dash, Plotly, Docker & several AWS Services')]),
        html.P(html.I('Any questions or suggestions, please contact me at tduongcs [at] gmail [dot] com'))
    ]),
    html.Br(),

    html.Div(
        dcc.Checklist(
            id='overall-plot-checkboxes',
            options=[
                {'label': 'New Cases', 'value': 'NewCases'},
                {'label': '7-Days Moving Average', 'value': 'SevenDay'},
                {'label': 'Number of Tests', 'value': 'TestNumbers'},
                {'label': 'Positive Rate', 'value': 'PositiveRate', 'disabled':True}
            ],
            value=['NewCases', 'SevenDay'],
            labelStyle={'display': 'inline-block', 'cursor': 'pointer', 'margin-left':'25px'},
            style={'border':'1px solid', 'padding': '0.4em'}),
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
                options=[{'label':name, 'value':name} for name in jh_data['Province/State'].unique()],
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

    html.Br(),

    html.Div(
        'Copyright © 2020 Tu Duong. All Rights Reserved',
        style={
            'textAlign': 'center'
        })

])


@app.callback(
    dash.dependencies.Output('overall_plot', 'figure'),
    [dash.dependencies.Input('overall-plot-checkboxes', 'value')]
)
def update_output_div(input_value):

    fig = make_subplots(specs=[[{'secondary_y': True}]])

    if 'TestNumbers' in input_value:
        fig.add_trace(go.Bar(name='US Daily Tests',
                        x=merged_df.date,
                        y=merged_df.totalTestResultsIncrease,
                        marker_color='darkblue',
                        opacity=0.3))

    if 'NewCases' in input_value:
        fig.add_trace(go.Bar(name='US Daily New Cases',
                        x=merged_df.date,
                        y=merged_df.new_cases,
                        marker_color='darkblue'))

    if 'SevenDay' in input_value:
        fig.add_trace(go.Scatter(
                    x=merged_df.date, 
                    y=merged_df.NewNewConfirmedSMA7,
                    mode='lines', line=dict(
                        width=3, color='rgb(100,140,240)'
                    ),
                    name='7-Days Moving Average'))

    if 'PositiveRate' in input_value:
        fig.add_trace(go.Scatter(name='Positive Rate',
                            x=merged_df.date,
                            y=merged_df.positive_rate,
                            opacity=0.8,
                            marker_color='rgb(255, 127, 14)'),
                    secondary_y="True")
        fig.update_layout(yaxis2_range=[0, merged_df.positive_rate.max()+15])

    fig.update_layout(
        title={
            'text': "COVID-19 Daily Numbers in United States"
        },
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

    data                        = jh_data[ jh_data[ 'Province/State'] == input_value ].copy()
    data['NewConfirmed']        = data.CumConfirmed.diff().fillna(0)
    data['NewNewConfirmedSMA7'] = data.NewConfirmed.rolling(7).mean()

    fig = go.Figure( [go.Bar(
                            x=data.date, 
                            y=data.NewConfirmed, 
                            marker_color='darkblue',
                            name='New Cases')])

    fig.add_trace(
                go.Scatter(
                    x=data.date, y=data.NewNewConfirmedSMA7,
                    mode='lines', line=dict(
                        width=3, color='rgb(100,140,240)'
                    ),
                    name='7-Days Moving Average'
                )
    )

    if input_value is None:
        title = "COVID-19 Daily New Cases"
    else:
        title = "COVID-19 Daily New Cases in %s" %input_value

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
    app.run_server(host="0.0.0.0")
