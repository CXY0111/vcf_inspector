from dash import Dash, html, dcc, Input, Output, State, dash_table, callback
import plotly.express as px
from utils import venn_diagram, chart, get_filters_dict, get_used_filters, data_prepare, load_input_paths, \
    load_input_names, load_input_dict
import plotly.graph_objects as go
from dash.dash_table.Format import Format, Scheme, Trim
import re
import os
import argparse


parser = argparse.ArgumentParser(description="VCF inspector")
parser.add_argument("-i", "--input", type=str, dest="input", default='input_files.txt',
                    help="input a txt file that contains paths each line")
args = parser.parse_args()
input_file = args.input
filelist = load_input_paths(input_file)
filenames = load_input_names(input_file)
filedict = load_input_dict(input_file)
# # on katmai
# filelist = ['/diskmnt/Projects/Users/chen.xiangyu/dash/b17d5672-572f-463b-88ad-0ac7b06156ad/',
#             '/diskmnt/Projects/Users/chen.xiangyu/dash/0f45d954-d951-4927-a2ba-476e319a6a88/']
# # on compute1
# filelist = ['/storage1/fs1/dinglab//Active/Projects/rmashl/cromwell-data/cromwell-workdir/cromwell-executions/tindaisy2.cwl/04491d22-a7f7-4a60-a9c6-22ba9ab45b50/analysis',
#             '/storage1/fs1/dinglab/Active/Projects/rmashl/cromwell-data/cromwell-workdir/cromwell-executions/tindaisy2.cwl/7b1d90ac-f6ed-40cf-a00c-46352499c71a/analysis']
# # save filedict to json
# save_filelist_json(filelist)
# first, prepare the data
data_prepare(filelist)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    # title
    html.H1(children='This is web application to analyze and compare TinDaisy'),

    # html.Label('Please add path of new vcf files.'),
    #
    # # add new vcf files
    # html.Div([
    #
    #     html.Div([
    #         html.Label('Path: ')
    #     ], style={'width': '4%', 'display': 'inline-block'}),
    #
    #     html.Div([
    #         dcc.Input(value='/diskmnt/Projects/Users/chen.xiangyu/dash/' \
    #                         'b17d5672-572f-463b-88ad-0ac7b06156ad/', type='text', id='path', style={'width': '98%'})
    #     ], style={'width': '85%', 'display': 'inline-block'}),
    #
    #     html.Div([
    #         html.Button('Submit', id='submit-val', n_clicks=0, style={'width': '95%'}),
    #     ], style={'width': '10%', 'display': 'inline-block'}),
    #
    #     html.Div(id='output-state')
    #
    # ], style={'padding': '10px 0px'}),

    # venn diagram
    html.Div([
        html.H2('Venn Diagram: '),

        html.Div([
            dcc.Dropdown(
                filenames,
                filenames[0],
                id='name1',
            ),
            dcc.RadioItems(id='name1-radio'),
        ], style={'width': '47%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        html.Div([
            # placerholder
        ], style={'width': '4%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        html.Div([
            dcc.Dropdown(
                filenames,
                filenames[1],
                id='name2',
            ),
            dcc.RadioItems(id='name2-radio'),
        ], style={'width': '47%', 'display': 'inline-block', 'verticalAlign': 'top'}),
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
        html.Div([
            html.Div(id='my_output', style={'width': '95%'}),
        ])

    ], style={'padding': '0px 20px 20px 20px'})
])


@app.callback(
    Output('name1-radio', 'options'),
    Input('name1', 'value'))
def set_name1_radio_options(selected_name):
    path = filedict[selected_name]
    selected_cromwell_workflow_id = re.search('[0-9|a-z]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12}',
                                              path).group(0)
    res = []
    out = 'dat/' + selected_cromwell_workflow_id + '/'
    if os.path.exists(out + 'ProximityFiltered.txt'):
        res.append('ProximityFiltered')
    if os.path.exists(out + 'mutect_somatic_depth_filter.output.txt'):
        res.append('mutect_somatic_depth_filter')
    if os.path.exists(out + 'pindel_somatic_depth_filter.output.txt'):
        res.append('pindel_somatic_depth_filter')
    if os.path.exists(out + 'strelka_indel_somatic_depth_filter.output.txt'):
        res.append('strelka_indel_somatic_depth_filter')
    if os.path.exists(out + 'strelka_snv_somatic_depth_filter.output.txt'):
        res.append('strelka_snv_somatic_depth_filter')
    if os.path.exists(out + 'varscan_indel_somatic_depth_filter.output.txt'):
        res.append('varscan_indel_somatic_depth_filter')
    if os.path.exists(out + 'varscan_snv_somatic_depth_filter.output.txt'):
        res.append('varscan_snv_somatic_depth_filter')
    return [{'label': i, 'value': i} for i in res]


@app.callback(
    Output('name1-radio', 'value'),
    Input('name1-radio', 'options'))
def set_name1_radio_value(available_options):
    return available_options[0]['value']


@app.callback(
    Output('name2-radio', 'options'),
    Input('name2', 'value'))
def set_name2_radio_options(selected_name):
    path = filedict[selected_name]
    selected_cromwell_workflow_id = re.search('[0-9|a-z]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12}',
                                              path).group(0)
    res = []
    out = 'dat/' + selected_cromwell_workflow_id + '/'
    if os.path.exists(out + 'ProximityFiltered.txt'):
        res.append('ProximityFiltered')
    if os.path.exists(out + 'mutect_somatic_depth_filter.output.txt'):
        res.append('mutect_somatic_depth_filter')
    if os.path.exists(out + 'pindel_somatic_depth_filter.output.txt'):
        res.append('pindel_somatic_depth_filter')
    if os.path.exists(out + 'strelka_indel_somatic_depth_filter.output.txt'):
        res.append('strelka_indel_somatic_depth_filter')
    if os.path.exists(out + 'strelka_snv_somatic_depth_filter.output.txt'):
        res.append('strelka_snv_somatic_depth_filter')
    if os.path.exists(out + 'varscan_indel_somatic_depth_filter.output.txt'):
        res.append('varscan_indel_somatic_depth_filter')
    if os.path.exists(out + 'varscan_snv_somatic_depth_filter.output.txt'):
        res.append('varscan_snv_somatic_depth_filter')
    return [{'label': i, 'value': i} for i in res]


@app.callback(
    Output('name2-radio', 'value'),
    Input('name2-radio', 'options'))
def set_name2_radio_value(available_options):
    return available_options[0]['value']


@app.callback(
    Output('caller', 'options'),
    Input('name1', 'value'),
    Input('name1-radio', 'value'),
    Input('name2', 'value'),
    Input('name2-radio', 'value'))
def update_filter_radio_options(name1, name1_radio, name2, name2_radio):
    path1 = filedict[name1]
    cromwell_workflow_id1 = re.search('[0-9|a-z]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12}',
                                      path1).group(0)
    if name1_radio == 'ProximityFiltered':
        path1 = 'dat/' + cromwell_workflow_id1 + '/' + name1_radio + '.txt'
    else:
        path1 = 'dat/' + cromwell_workflow_id1 + '/' + name1_radio + '.output.txt'

    path2 = filedict[name2]
    cromwell_workflow_id2 = re.search('[0-9|a-z]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12}',
                                      path2).group(0)
    if name2_radio == 'ProximityFiltered':
        path2 = 'dat/' + cromwell_workflow_id2 + '/' + name2_radio + '.txt'
    else:
        path2 = 'dat/' + cromwell_workflow_id2 + '/' + name2_radio + '.output.txt'
    return get_used_filters([path1, path2])




@app.callback(
    Output('venn_diagram', 'figure'),
    Input('name1', 'value'),
    Input('name1-radio', 'value'),
    Input('name2', 'value'),
    Input('name2-radio', 'value'),
    Input('caller', 'value'))
def update_graph(name1, name1_radio, name2, name2_radio, caller):
    path1 = filedict[name1]
    cromwell_workflow_id1 = re.search('[0-9|a-z]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12}',
                                      path1).group(0)
    if name1_radio == 'ProximityFiltered':
        path1 = 'dat/' + cromwell_workflow_id1 + '/' + name1_radio + '.txt'
    else:
        path1 = 'dat/' + cromwell_workflow_id1 + '/' + name1_radio + '.output.txt'

    path2 = filedict[name2]
    cromwell_workflow_id2 = re.search('[0-9|a-z]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12}',
                                      path2).group(0)
    if name2_radio == 'ProximityFiltered':
        path2 = 'dat/' + cromwell_workflow_id2 + '/' + name2_radio + '.txt'
    else:
        path2 = 'dat/' + cromwell_workflow_id2 + '/' + name2_radio + '.output.txt'

    com, ua, ub = venn_diagram(path1, path2, caller)

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
    Output('description', 'children'),
    Input('name1', 'value'),
    Input('name1-radio', 'value'),
    Input('name2', 'value'),
    Input('name2-radio', 'value'),
    Input('caller', 'options'))
def update_description(name1, name1_radio, name2, name2_radio, options):
    for path in filelist:
        if filedict[name1] in path:
            path1 = path
        if filedict[name2] in path:
            path2 = path
    if name1_radio == 'ProximityFiltered':
        path1 += 'call-snp_indel_proximity_filter/execution/output/ProximityFiltered.vcf'
    else:
        path1 += 'call-depth_filter_' + name1_radio[:-21] + '/execution/somatic_depth_filter.output.vcf'

    if name2_radio == 'ProximityFiltered':
        path2 += 'call-snp_indel_proximity_filter/execution/output/ProximityFiltered.vcf'
    else:
        path2 += 'call-depth_filter_' + name2_radio[:-21] + '/execution/somatic_depth_filter.output.vcf'
    filters_dict = get_filters_dict(path1, path2)
    strs = ''
    for keys, values in filters_dict.items():
        # print(keys)
        # print(values)
        if keys in options:
            strs += '\n  ' + keys + ': ' + values
    return strs


@callback(
    Output('my_output', component_property='children'),
    Input('name1-radio', 'options'),
    Input('name2-radio', 'options'))
def update_chart(name1_radio, name2_radio):
    children_list = []
    name1_radio_list = [row['value'] for row in name1_radio]
    name2_radio_list = [row['value'] for row in name2_radio]
    union_list = list(set(name1_radio_list).union(set(name2_radio_list)))

    count = 0
    print('Making charts:')
    for vcf_file_type in union_list:
        count += 1
        children_list.append(
            html.Label(vcf_file_type)
        )

        print('({}/{}) Making {} chart......'.format(count,len(union_list),vcf_file_type))
        df_res = chart(filedict,vcf_file_type)
        columns = []
        for i in df_res.columns:
            if i != 'total':
                columns.append(
                    {"name": i, "id": i, "type": 'numeric', "format": Format(precision=2, scheme=Scheme.percentage)})
            else:
                columns.append({"name": i, "id": i, "type": 'numeric'})
        children_list.append(
            dash_table.DataTable(data=df_res.to_dict('records'),
                                 columns=columns,
                                 # tooltip_data=[{column: {'value': value, 'type': 'markdown'}
                                 #                for column, value in row.items()
                                 #                } for row in df_res[['names']].to_dict('records')],
                                 # Overflow into ellipsis
                                 style_cell={
                                     'overflow': 'hidden',
                                     'textOverflow': 'ellipsis',
                                     'maxWidth': 0,
                                 },
                                 tooltip_delay=0,
                                 tooltip_duration=None
                                 )
        )
    return html.Div(
        children=children_list
    )


# @app.callback(
#     Output('output-state', 'children'),
#     Input('submit-val', 'n_clicks'),
#     State('path', 'value'))
# def add_new_vcf(n_clicks, path):
#     tmp = u'''
#             The Button has been pressed {} times,nothing has been added.
#         '''.format(n_clicks)
#     cromwell_workflow_id = re.search('[0-9|a-z]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12}',path).group(0)
#     if os.path.exists(path):
#         filelist = load_filelist_id('stored_vcf_filelist.json')
#         if cromwell_workflow_id in filelist:
#             tmp = 'Sorry, the path has been added'
#         else:
#             filelist.append(path)
#             save_filelist(filelist)
#             data_prepare(filelist)
#             tmp = u'''
#                 {} has been added successfully.
#             '''.format(cromwell_workflow_id)
#     else:
#         tmp = 'The path deos not exists.'
#
#     return tmp


# @app.callback(
#     Output('name1', 'options'),
#     Output('name2', 'options'),
#     Input('submit-val', 'n_clicks'))
# def update_names(n_clicks):
#
#     name1_options = load_filelist_id('stored_vcf_filelist.json')
#
#     # if os.path.exists(path):
#     #     if path not in list(filedict.values()) and filename not in list(filedict.keys()):
#     #         name1_options += [filename]
#     return name1_options, name1_options


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080, debug=True)
