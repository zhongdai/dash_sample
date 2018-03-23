# -*- coding: utf-8 -*-
"""Profiling Tool Demo"""

import dash
from plotly import tools
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
    dcc.Markdown("""
## Profiling Tool (Demo)
This is a profile tool to enable users compare two (or three) data sets, and check the different of distribution on same attributes.

- Select two or three groups
- Compare against **ONE** attribute, it displays the all values for this attribute on X
- If select the 2nd attribute, it generates N plots based on the 2nd attribute (N is the unique values of 2nd attribute)
"""),
    html.Hr(),
    html.Label('Select Data Group:'),
    dcc.Dropdown(
        id = 'dd-groups',
        options = [ {'label':g, 'value': g} for g in groups ],
        value = groups[:2],
        multi = True
    ),
    html.Label('Measurement'),

    dcc.RadioItems(
        id = 'dd-measurement',
        options=[
            {'label': '% of Sub Total', 'value': 'PCT'},
            {'label': 'Compare to Base', 'value': 'BASE'},
        ],
        value='PCT'
    ),
    html.Label('Select base attribute:'),
    dcc.Dropdown(
        id = 'dd-attr1',
        options=[ {'label': name, 'value': name} for name in attrs ],
        value=attrs[0]
    ),
    html.Label('Select 2nd attribute:'),
    dcc.Dropdown(
        id = 'dd-attr2',
        options=[{'label':'N/A', 'value':'N/A'}] + [ {'label': name, 'value': name} for name in attrs ],
        value= 'N/A'
    ),
    html.Hr(),
    dcc.Graph(
        id='my-graph'
    ),
], className="container")


@app.callback(
    Output('my-graph', 'figure'),
    [
        Input('dd-groups', 'value'),
        Input('dd-attr1', 'value'),
        Input('dd-attr2', 'value'),
        Input('dd-measurement', 'value')
    ])
def update_figure(groups, attr1, attr2, measure):

    if len(groups) > 3:
        return html.Div([html.H4('Can not select more than 3 groups')])

    if attr2 != 'N/A':
        # three colors
        group_colors = [
            'rgb(31, 119, 180)',
            'rgb(255, 127, 14)',
            'rgb(44, 160, 44)'
        ]
        attr2_values = summary_df[attr2].unique()
        num_of_attr2_values = len(attr2_values)
        height = num_of_attr2_values * 500
        sub_plot_titles = ["{} = {}".format(attr2, v) for v in attr2_values]

        fig = tools.make_subplots(rows=num_of_attr2_values, 
            cols=1, 
            subplot_titles=tuple(sub_plot_titles))

        for row_id, attr2_v in enumerate(attr2_values, start=1):
            if row_id == 1:
                showlegend = True
            else:
                showlegend = False
            row_df = summary_df[summary_df[attr2] == attr2_v] 
            for group_id, group_value in enumerate(groups, start=1):
                sub_df = row_df[row_df['Group'] == group_value]
                count_df = sub_df.groupby(attr1).sum()['Count'] / sub_df.sum()['Count'] 

                # Speical handling for measure = Base
                if measure == 'BASE':
                    yaxis_title = 'Compare to Base'
                    if group_value == 'Base':
                        base_pct = count_df
                    count_df = count_df - base_pct
                else:
                    yaxis_title = '% of Sub Total'

                bar_plot = go.Bar(x = count_df.index, 
                                  y = count_df.values.tolist(), 
                                  marker=dict( color=group_colors[group_id-1]),
                                  legendgroup = group_value,
                                  showlegend = showlegend,
                                  name = group_value)
                # run n times, n = num of groups
                fig.append_trace(bar_plot, row_id, 1)
        layout = {
            'height': height,
            'title': "Compare based on {} and {}".format(attr1, attr2),
        }

        for i in range(num_of_attr2_values):
            layout["yaxis{}".format(i+1)] = {'title': yaxis_title}
            layout["xaxis{}".format(i+1)] = {'title': attr1}

        fig['layout'].update(layout)
        return fig
    else:
        height = 500
        fig = tools.make_subplots(rows=1, cols=1)
        for group_value in groups:
            sub_df = summary_df[summary_df['Group'] == group_value]
            count_df = sub_df.groupby(attr1).sum()['Count'] / sub_df.sum()['Count'] 

            # Speical handling for measure = Base
            if measure == 'BASE':
                yaxis_title = 'Compare to Base'
                if group_value == 'Base':
                    base_pct = count_df
                count_df = count_df - base_pct
            else:
                yaxis_title = '% of Sub Total'

            bar_plot = go.Bar(x = count_df.index, 
                              y = count_df.values.tolist(), 
                              name = group_value)
                # run n times, n = num of groups
            fig.append_trace(bar_plot, 1, 1)

        layout = {
            'height': height,
            'title': "Compare based on {}".format(attr1),
            'xaxis1': {'title': attr1},
            'yaxis1': {'title': yaxis_title}
        }
        fig['layout'].update(layout)
        return fig



app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    app.run_server(debug=True)