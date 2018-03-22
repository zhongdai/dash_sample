# -*- coding: utf-8 -*-
"""Profiling Tool Demo"""

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import dash_table_experiments as dt

import pandas as pd

app =  dash.Dash()

df = pd.read_hdf('data.h5','data')
summary = df.groupby(df.columns.tolist()).size()
columns = df.columns.tolist() + ['Count']
summary_df = summary.reset_index()
summary_df.columns = columns

groups = summary_df.Group.unique().tolist()
attrs = list()
for item in summary_df.columns:
    # print(item)
    if item not in ('Group','Count'):
        attrs.append(item)


app.layout = html.Div([
    html.H4('Profiling Tool'),

    html.Label('Select Data Group:'),
    dcc.Dropdown(
        id = 'dd-groups',
        options = [ {'label':g, 'value': g} for g in groups ],
        value = groups[:2],
        multi = True
    ),

    html.Label('Select base attribute:'),
    dcc.Dropdown(
        id = 'dd-attr1',
        options=[ {'label': name, 'value': name} for name in attrs ],
        value=attrs[0]
    ),

    html.Label('Select additional attribute:'),
    dcc.Dropdown(
        id = 'dd-attr2',
        options=[ {'label': name, 'value': name} for name in attrs ],
        value=attrs[0]
    ),

    dcc.Graph(
        id='my-graph'
    ),
], className="container")

@app.callback(
    Output('my-graph', 'figure'),
    [
        Input('dd-groups', 'value'),
        Input('dd-attr1', 'value'),
        Input('dd-attr2', 'value')
    ])
def update_figure(groups, attr1, attr2):
    traces = []
    for i in groups:
        sub_df = summary_df[summary_df['Group'] == i]
        count_df = sub_df.groupby(attr1).sum()['Count'] / sub_df.sum()['Count'] 
        traces.append(go.Bar(
            x=count_df.index,
            y=count_df.values.tolist(),
            name=i
        ))
    return {
        'data': traces,
        'layout': go.Layout(
            xaxis = {
                'title':'Values for selected attribute'
            },
            yaxis = {
                'title':"% of Count"
            },
            hovermode='closest'
        )
    }

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    app.run_server(debug=True)