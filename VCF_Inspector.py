from dash import Dash, html, dcc, Input, Output, State, dash_table, callback
from utils import venn_diagram, chart, get_filters_dict, get_used_filters, data_prepare, load_input_paths, \
    load_input_names, load_input_dict, get_radio_options, name_to_dir_path, dir_to_file_path, draw_venn_figure
from dash.dash_table.Format import Format, Scheme, Trim
import dash_daq as daq
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
    html.H1(children='VCF inspector'),
    html.H4(children='--This is web application to analyze and compare TinDaisy'),

    # venn diagram
    html.Div([

        html.Div([
            html.H2('Venn Diagram: ', style={'width': '30%', 'display': 'inline-block'}),

            html.Div([
                # placeholder
            ], style={'display': 'inline-block', 'width': '40%', }),

            html.Div([
                daq.ToggleSwitch(id='venn-type-switch',
                                 value=False,
                                 label=['Venn2', 'Venn3'],
                                 style={'width': '200px', })
            ], style={'display': 'inline-block', 'width': '30%', }),

        ]),

        html.Div([
            html.Div([
                dcc.Dropdown(
                    filenames,
                    filenames[0],
                    id='name1',
                ),
                dcc.RadioItems(id='name1-radio'),
            ], id='name1_div', style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}),

            html.Div([
                # placerholder
            ], style={'width': '3%', 'display': 'inline-block', 'verticalAlign': 'top'}),

            html.Div([
                dcc.Dropdown(
                    filenames,
                    filenames[1],
                    id='name2',
                ),
                dcc.RadioItems(id='name2-radio'),
            ], id='name2_div', style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}),

            html.Div([
                # placerholder
            ], style={'width': '3%', 'display': 'inline-block', 'verticalAlign': 'top'}),

            html.Div([
                dcc.Dropdown(
                    filenames,
                    filenames[2],
                    id='name3',
                ),
                dcc.RadioItems(id='name3-radio'),
            ], id='name3_div', style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        ])

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
            html.Div(id='my_output',
                     style={'width': '95%'}),
            dcc.Interval(
                id="load_interval",
                n_intervals=0,
                max_intervals=0,  # <-- only run once
                interval=1
            )
        ])

    ], style={'padding': '0px 20px 20px 20px'})
])


@app.callback(
    Output('name1-radio', 'options'),
    Input('name1', 'value'))
def set_name1_radio_options(selected_name):
    path = name_to_dir_path(filedict, selected_name)
    res = get_radio_options(path)
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
    path = name_to_dir_path(filedict, selected_name)
    res = get_radio_options(path)
    return [{'label': i, 'value': i} for i in res]


@app.callback(
    Output('name2-radio', 'value'),
    Input('name2-radio', 'options'))
def set_name2_radio_value(available_options):
    return available_options[0]['value']


@app.callback(
    Output('name3-radio', 'options'),
    Input('name3', 'value'))
def set_name3_radio_options(selected_name):
    path = name_to_dir_path(filedict, selected_name)
    res = get_radio_options(path)
    return [{'label': i, 'value': i} for i in res]


@app.callback(
    Output('name3-radio', 'value'),
    Input('name3-radio', 'options'))
def set_name3_radio_value(available_options):
    return available_options[0]['value']


@app.callback(
    Output('caller', 'options'),
    Input('name1', 'value'),
    Input('name1-radio', 'value'),
    Input('name2', 'value'),
    Input('name2-radio', 'value'),
    Input('name3', 'value'),
    Input('name3-radio', 'value'),
    Input('venn-type-switch', 'value'))
def update_filter_radio_options(name1, name1_radio, name2, name2_radio, name3, name3_radio, venn_type):
    paths = []

    path1 = name_to_dir_path(filedict, name1)
    path1 = dir_to_file_path(path1,name1_radio)
    paths.append(path1)

    path2 = name_to_dir_path(filedict, name2)
    path2 = dir_to_file_path(path2,name2_radio)
    paths.append(path2)

    if venn_type:
        path3 = name_to_dir_path(filedict, name3)
        path3 = dir_to_file_path(path3,name3_radio)
        paths.append(path3)

    return get_used_filters(paths)


@app.callback(
    Output('venn_diagram', 'figure'),
    Input('name1', 'value'),
    Input('name1-radio', 'value'),
    Input('name2', 'value'),
    Input('name2-radio', 'value'),
    Input('name3', 'value'),
    Input('name3-radio', 'value'),
    Input('caller', 'value'),
    Input('venn-type-switch', 'value'))
def update_graph(name1, name1_radio, name2, name2_radio, name3, name3_radio, caller, venn_type):

    path1 = name_to_dir_path(filedict, name1)
    path1 = dir_to_file_path(path1, name1_radio)

    path2 = name_to_dir_path(filedict, name2)
    path2 = dir_to_file_path(path2, name2_radio)

    if venn_type:
        path3 = name_to_dir_path(filedict, name3)
        path3 = dir_to_file_path(path3, name3_radio)
        AB_overlap, AC_overlap, BC_overlap, ABC_overlap, A_rest, B_rest, C_rest, AB_only, AC_only, BC_only = \
            venn_diagram([path1, path2, path3], caller)
        fig = draw_venn_figure([AB_overlap, AC_overlap, BC_overlap, ABC_overlap, A_rest, B_rest, C_rest, AB_only, AC_only, BC_only])
    else:
        com, ua, ub = venn_diagram([path1, path2], caller)
        fig = draw_venn_figure([com, ua, ub])

    return fig


@app.callback(
    Output('description', 'children'),
    Input('name1', 'value'),
    Input('name1-radio', 'value'),
    Input('name2', 'value'),
    Input('name2-radio', 'value'),
    Input('name3', 'value'),
    Input('name3-radio', 'value'),
    Input('caller', 'options'),
    Input('venn-type-switch', 'value'))
def update_description(name1, name1_radio, name2, name2_radio, name3, name3_radio, options, venn_type):
    paths = []
    for path in filelist:
        if filedict[name1] in path:
            path1 = path
        if filedict[name2] in path:
            path2 = path
        if filedict[name3] in path:
            path3 = path
    if name1_radio == 'ProximityFiltered':
        path1 += 'call-snp_indel_proximity_filter/execution/output/ProximityFiltered.vcf'
    else:
        path1 += 'call-depth_filter_' + name1_radio[:-21] + '/execution/somatic_depth_filter.output.vcf'
    paths.append(path1)

    if name2_radio == 'ProximityFiltered':
        path2 += 'call-snp_indel_proximity_filter/execution/output/ProximityFiltered.vcf'
    else:
        path2 += 'call-depth_filter_' + name2_radio[:-21] + '/execution/somatic_depth_filter.output.vcf'
    paths.append(path2)

    if venn_type:
        if name3_radio == 'ProximityFiltered':
            path3 += 'call-snp_indel_proximity_filter/execution/output/ProximityFiltered.vcf'
        else:
            path3 += 'call-depth_filter_' + name3_radio[:-21] + '/execution/somatic_depth_filter.output.vcf'
        paths.append(path3)

    filters_dict = get_filters_dict(paths)
    strs = ''
    for keys, values in filters_dict.items():
        if keys in options:
            strs += '\n  ' + keys + ': ' + values
    return strs


@callback(
    Output('my_output', component_property='children'),
    Input('load_interval', 'n_intervals'))
def update_chart(n):  # name1_radio, name2_radio,
    union_list = []
    for name in filenames:
        out = name_to_dir_path(filedict,name)
        radion_options = get_radio_options(out)
        union_list = list(set(union_list).union(set(radion_options)))

    count = 0
    print('Making charts:')
    children_list = []
    for vcf_file_type in union_list:
        count += 1
        children_list.append(
            html.Label(vcf_file_type)
        )

        print('({}/{}) Making {} chart......'.format(count, len(union_list), vcf_file_type))
        df_res = chart(filedict, vcf_file_type)
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

@app.callback([Output('name1_div', 'style'),
               Output('name2_div', 'style'),
               Output('name3_div', 'style'), ],
              [Input('venn-type-switch', 'value')])
def update_style(venn_type):
    if venn_type:
        return {'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}, \
               {'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}, \
               {'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}
    else:
        return {'width': '46%', 'display': 'inline-block', 'verticalAlign': 'top'}, \
               {'width': '46%', 'display': 'inline-block', 'verticalAlign': 'top'}, \
               {'width': '1%', 'display': 'none', 'verticalAlign': 'top'}


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080, debug=False, dev_tools_silence_routes_logging=True)
