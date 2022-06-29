from dash import Dash, html, dcc, Input, Output, State, dash_table, callback
import pandas as pd
import plotly.express as px
from utils import venn_diagram, chart, get_filters_dict, get_used_filters, data_prepare
import plotly.graph_objects as go
from dash.dash_table.Format import Format, Scheme, Trim
import os

# # on katmai
# filedict = {'CTSP-AD3X_RunA': '/diskmnt/Projects/Users/chen.xiangyu/dash/b17d5672-572f-463b-88ad-0ac7b06156ad/call'
#                               '-snp_indel_proximity_filter/execution/output/ProximityFiltered.vcf',
#             'CTSP-AD3X_RunB': '/diskmnt/Projects/Users/chen.xiangyu/dash/0f45d954-d951-4927-a2ba-476e319a6a88/call'
#                               '-snp_indel_proximity_filter/execution/output/ProximityFiltered.vcf'}
# on compute1
filedict = {'CTSP-AD3X_RunA': '/storage1/fs1/m.wyczalkowski/Active/cromwell-data/cromwell-workdir/cromwell-executions'
                              '/tindaisy2.ffpe.cwl/b17d5672-572f-463b-88ad-0ac7b06156ad/call'
                              '-snp_indel_proximity_filter/execution/output/ProximityFiltered.vcf',
            'CTSP-AD3X_RunB': '/storage1/fs1/m.wyczalkowski/Active/cromwell-data/cromwell-workdir/cromwell-executions'
                              '/tindaisy2.ffpe.cwl/0f45d954-d951-4927-a2ba-476e319a6a88/call'
                              '-snp_indel_proximity_filter/execution/output/ProximityFiltered.vcf'}
# my_output = html.Div(style={'width': '95%'})

app = Dash(__name__)

app.layout = html.Div([
    # title
    html.H1(children='This is web application to analyze and compare TinDaisy'),

    # add new vcf files
    html.Div([
        html.Label('Please add path of new vcf files.'),

        html.Div([
            html.Label('Name: ')
        ], style={'width': '4%', 'display': 'inline-block'}),

        html.Div([
            dcc.Input(value='example: CTSP-AD3X_RunA', type='text', id='filename', style={'width': '95%'}),
        ], style={'width': '20%', 'display': 'inline-block'}),

        html.Div([
            html.Label('Path: ')
        ], style={'width': '4%', 'display': 'inline-block'}),

        html.Div([
            dcc.Input(value='on katmai,example: /diskmnt/Projects/Users/chen.xiangyu/dash/' \
                            'b17d5672-572f-463b-88ad-0ac7b06156ad/call-snp_indel_proximity_filter/' \
                            'execution/output/ProximityFiltered.vcf', type='text', id='path', style={'width': '98%'})
        ], style={'width': '45%', 'display': 'inline-block'}),

        html.Div([
            html.Button('Submit', id='submit-val', n_clicks=0, style={'width': '95%'}),
        ], style={'width': '10%', 'display': 'inline-block'}),

        html.Div(id='output-state')

    ], style={'padding': '10px 5px'}),

    # venn diagram
    html.Div([
        html.H2('Venn Diagram: '),

        html.Div([
            dcc.Dropdown(
                list(filedict.keys()),
                'CTSP-AD3X_RunA',
                id='name1',
            ),
        ], style={'width': '47%', 'display': 'inline-block'}),

        html.Div([
            # placerholder
        ], style={'width': '4%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                list(filedict.keys()),
                'CTSP-AD3X_RunB',
                id='name2',
            ),
        ], style={'width': '47%', 'display': 'inline-block', }),
    ], style={'padding': '50px 5px', }),  # 'backgroundColor': '#FFD482'
    html.Div([
        html.Div([
            html.Div([
                # placerholder
            ], style={'padding': '50px'}),

            html.Div([
                html.Label('Filters:'),
                dcc.RadioItems([],
                               'vcf_all',
                               id='caller', labelStyle={'display': 'block'}
                               ),
            ])

        ], style={'width': '8%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        html.Div([
            dcc.Graph(
                id='venn_diagram',
            )
        ], style={'width': '40%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        html.Div([
            # placeholder
        ], style={'width': '3%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        html.Div([
            dcc.Markdown("""**Description of filters:**"""),
            html.Pre(id='description', style={'border': 'thin lightgrey solid', 'overflowX': 'scroll'})
        ], style={'width': '47%', 'display': 'inline-block', 'verticalAlign': 'top', }),  # 'backgroundColor': '#FFD482'
    ]),

    # chart
    html.Div([
        html.H4(children='Chart of all VCF files:'),
        # my_output
        html.Div(id='my_output',style={'width': '95%'}),
        # html.Div([
        #     dash_table.DataTable(id='chart')
        #     # html.Table(
        #     #     id='chart',
        #     #     style={'width': '90%','backgroundColor': '#111111'}
        #     # )
        # ],style={'backgroundColor': '#FFD482'}),  # )
        # html.Table(id='chart',)
    ], style={'padding': '0px 20px 20px 20px'})
])


@app.callback(
    Output('venn_diagram', 'figure'),
    Input('name1', 'value'),
    Input('name2', 'value'),
    Input('caller', 'value'))
def update_graph(name1, name2, caller):
    com, ua, ub = venn_diagram(filedict[name1], filedict[name2], caller)

    fig = go.Figure()

    # Create scatter trace of text labels
    fig.add_trace(go.Scatter(
        x=[1, 1.75, 2.5, 1, 1.75, 2.5],
        y=[1, 1, 1, 0.75, 0.75, 0.75],
        text=["$Unique RunA$", "$Common$", "$Unique RunB$", ua, com, ub],
        mode="text",
        textfont=dict(
            color="black",
            size=18,
            family="Arail",
        ),
        name='trace0'
    ))

    # Update axes properties
    fig.update_xaxes(
        showticklabels=False,
        showgrid=True,
        zeroline=False,
    )

    fig.update_yaxes(
        showticklabels=False,
        showgrid=True,
        zeroline=False,
    )

    # Add circles
    fig.add_shape(type="circle",
                  line_color="blue", fillcolor="blue",
                  x0=0.25, y0=0, x1=2.25, y1=2
                  )
    fig.add_shape(type="circle",
                  line_color="gray", fillcolor="gray",
                  x0=1.25, y0=0, x1=3.25, y1=2
                  )
    fig.update_shapes(opacity=0.3, xref="x", yref="y")

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0})

    return fig


@app.callback(
    Output('output-state', 'children'),
    State('filename', 'value'),
    State('path', 'value'),
    Input('submit-val', 'n_clicks')
)
def add_new_vcf(filename, path, n_clicks):
    tmp = u'''
            The Button has been pressed {} times,nothing has been added.
        '''.format(n_clicks)
    if n_clicks >= 1:
        if os.path.exists(path):

            if path in list(filedict.values()):
                tmp = 'Sorry, the path has been added'
            elif filename in list(filedict.keys()):
                tmp = 'Sorry, the filename has been used'
            else:
                filedict[filename] = path
                tmp = u'''
                    {} has been added successfully.
                '''.format(filename)
            # print('1')
            # print(filedict)
        else:
            tmp = 'The path deos not exists.'

    return tmp


@app.callback(
    Output('name1', 'options'),
    # Input('name1', 'options'),
    # State('filename', 'value'),
    # State('path', 'value'),
    Input('submit-val', 'n_clicks'))
# def update_name1(name1_options, filename, path, n_clicks):
def update_name1(n_clicks):
    name1_options = list(filedict.keys())

    # if os.path.exists(path):
    #     if path not in list(filedict.values()) and filename not in list(filedict.keys()):
    #         name1_options += [filename]
    return name1_options


@app.callback(
    Output('name2', 'options'),
    # Input('name2', 'options'),
    # State('filename', 'value'),
    # State('path', 'value'),
    Input('submit-val', 'n_clicks'))
# def update_name1(name2_options, filename, path, n_clicks):
def update_name2(n_clicks):
    name2_options = list(filedict.keys())

    # if os.path.exists(path):
    #     name2_options += [filename]
    return name2_options


@callback(
    Output('my_output', component_property='children'),
    Input('submit-val', 'n_clicks'))
def update_chart(n_clicks):
    df_res = chart(filedict)
    columns = []
    for i in df_res.columns:
        if i != 'total':
            columns.append(
                {"name": i, "id": i, "type": 'numeric', "format": Format(precision=2, scheme=Scheme.percentage)})
        else:
            columns.append({"name": i, "id": i, "type": 'numeric'})
    return dash_table.DataTable(data=df_res.to_dict('records'),
                                columns=columns,
                                tooltip_data=[{column: {'value': str(filedict[value]), 'type': 'markdown'}
                                               for column, value in row.items()
                                               } for row in df_res[['name']].to_dict('records')],
                                # Overflow into ellipsis
                                style_cell={
                                    'overflow': 'hidden',
                                    'textOverflow': 'ellipsis',
                                    'maxWidth': 0,
                                },
                                tooltip_delay=0,
                                tooltip_duration=None
                                )


@app.callback(
    Output('caller', 'options'),
    Input('name1', 'value'),
    Input('name2', 'value'))
def update_radio_options(name1, name2):
    # path1 = 'dat/' + filedict[name1].split('/')[6] + '.txt'
    # path2 = 'dat/' + filedict[name2].split('/')[6] + '.txt'
    path1 = 'dat/' + filedict[name1][1:-3].replace('/','_')+'txt'
    path2 = 'dat/' + filedict[name2][1:-3].replace('/','_')+'txt'
    return get_used_filters(path1, path2)


@app.callback(
    Output('description', 'children'),
    Input('name1', 'value'),
    Input('name2', 'value'),
    Input('caller', 'options'))
def update_description(name1, name2, options):
    path1 = filedict[name1]
    path2 = filedict[name2]
    filters_dict = get_filters_dict(path1, path2)
    strs = ''
    for keys, values in filters_dict.items():
        # print(keys)
        # print(values)
        if keys in options:
            strs += '\n  ' + keys + ': ' + values
    return strs


if __name__ == '__main__':
    data_prepare(filedict)
    app.run_server(host='0.0.0.0', port=8080, debug=True)
