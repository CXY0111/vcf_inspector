from dash import Dash, html, dcc, Input, Output, State, dash_table, callback
import plotly.express as px
from utils import venn_diagram, chart, get_filters_dict, get_used_filters, data_prepare, load_input_paths, \
    load_input_names, load_input_dict, get_radio_options, fig_to_uri
import plotly.graph_objects as go
from dash.dash_table.Format import Format, Scheme, Trim
import re
import os
import argparse
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3
from collections import Counter

# parser = argparse.ArgumentParser(description="VCF inspector")
# parser.add_argument("-i", "--input", type=str, dest="input", default='input_files.txt',
#                     help="input a txt file that contains paths each line")
# args = parser.parse_args()
# input_file = args.input
# filelist = load_input_paths(input_file)
# filenames = load_input_names(input_file)
# filedict = load_input_dict(input_file)
# # first, prepare the data
# data_prepare(filelist)


def start_app(input_file,filelist,filenames,filedict):
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = Dash(__name__, external_stylesheets=external_stylesheets)

    app.layout = html.Div([
        # title
        html.H1(children='VCF inspector'),
        html.H4(children='--This is web application to analyze and compare TinDaisy'),

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
            ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}),

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
            ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}),

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
            ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}),

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
                # dcc.Graph(id='venn_diagram',),
                html.Img(id='venn_diagram', src='')
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
        path = filedict[selected_name]
        selected_cromwell_workflow_id = re.search('[0-9|a-z]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12}',
                                                  path).group(0)

        out = 'dat/' + selected_cromwell_workflow_id + '/'
        res = get_radio_options(out)
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

        out = 'dat/' + selected_cromwell_workflow_id + '/'
        res = get_radio_options(out)
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
        path = filedict[selected_name]
        selected_cromwell_workflow_id = re.search('[0-9|a-z]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12}',
                                                  path).group(0)

        out = 'dat/' + selected_cromwell_workflow_id + '/'
        res = get_radio_options(out)
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
        Input('name3-radio', 'value'), )
    def update_filter_radio_options(name1, name1_radio, name2, name2_radio, name3, name3_radio):
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

        path3 = filedict[name3]
        cromwell_workflow_id3 = re.search('[0-9|a-z]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12}',
                                          path3).group(0)
        if name3_radio == 'ProximityFiltered':
            path3 = 'dat/' + cromwell_workflow_id3 + '/' + name3_radio + '.txt'
        else:
            path3 = 'dat/' + cromwell_workflow_id3 + '/' + name3_radio + '.output.txt'

        return get_used_filters([path1, path2, path3])


    @app.callback(
        Output('venn_diagram', 'src'),
        Input('name1', 'value'),
        Input('name1-radio', 'value'),
        Input('name2', 'value'),
        Input('name2-radio', 'value'),
        Input('name3', 'value'),
        Input('name3-radio', 'value'),
        Input('caller', 'value'),)
    def update_graph(name1, name1_radio, name2, name2_radio, name3, name3_radio, caller):
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

        path3 = filedict[name3]
        cromwell_workflow_id3 = re.search('[0-9|a-z]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12}',
                                          path3).group(0)
        if name3_radio == 'ProximityFiltered':
            path3 = 'dat/' + cromwell_workflow_id3 + '/' + name3_radio + '.txt'
        else:
            path3 = 'dat/' + cromwell_workflow_id3 + '/' + name3_radio + '.output.txt'

        # com, ua, ub = venn_diagram([path1, path2], caller)
        AB_overlap, AC_overlap, BC_overlap, ABC_overlap, A_rest, B_rest, C_rest, AB_only, AC_only, BC_only = venn_diagram(
            [path1, path2, path3], caller)

        sets = Counter()  # set order A, B, C
        sets['100'] = A_rest  # 100 denotes A on, B off, C off
        sets['010'] = B_rest  # 010 denotes A off, B on, C off
        sets['001'] = C_rest  # 001 denotes A off, B off, C on
        sets['110'] = AB_only  # 110 denotes A on, B on, C off
        sets['101'] = AC_only  # 101 denotes A on, B off, C on
        sets['011'] = BC_only  # 011 denotes A off, B on, C on
        sets['111'] = ABC_overlap  # 011 denotes A on, B on, C on
        labels = ('UA', 'UB', 'UC')

        fig, ax1 = plt.subplots(1, 1)
        # ax1 = plt.gca()
        # veen3 parameter (A_rest, B_rest, AB_overlap, C_rest, AC_overlap, BC_overlap, ABC_overlap)
        venn3(subsets=sets, set_labels=labels)
        # venn2((ua,com,ub), set_labels=('UA', 'UB'))
        ax1.set_title(
            'AB_only=' + str(AB_only) + ',AC_only=' + str(AC_only) + ',BC_only=' + str(BC_only) + '\nABC_overlap=' + str(
                ABC_overlap), y=-0.1)
        out_url = fig_to_uri(fig)

        return out_url


    @app.callback(
        Output('description', 'children'),
        Input('name1', 'value'),
        Input('name1-radio', 'value'),
        Input('name2', 'value'),
        Input('name2-radio', 'value'),
        Input('name3', 'value'),
        Input('name3-radio', 'value'),
        Input('caller', 'options'))
    def update_description(name1, name1_radio, name2, name2_radio, name3, name3_radio, options):
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

        if name2_radio == 'ProximityFiltered':
            path2 += 'call-snp_indel_proximity_filter/execution/output/ProximityFiltered.vcf'
        else:
            path2 += 'call-depth_filter_' + name2_radio[:-21] + '/execution/somatic_depth_filter.output.vcf'

        if name3_radio == 'ProximityFiltered':
            path3 += 'call-snp_indel_proximity_filter/execution/output/ProximityFiltered.vcf'
        else:
            path3 += 'call-depth_filter_' + name3_radio[:-21] + '/execution/somatic_depth_filter.output.vcf'

        filters_dict = get_filters_dict([path1, path2])
        strs = ''
        for keys, values in filters_dict.items():
            # print(keys)
            # print(values)
            if keys in options:
                strs += '\n  ' + keys + ': ' + values
        return strs


    @callback(
        Output('my_output', component_property='children'),
        # Input('name1-radio', 'options'),
        # Input('name2-radio', 'options'),
        Input('load_interval', 'n_intervals'))
    def update_chart(n):  # name1_radio, name2_radio,
        union_list = []
        for file in filelist:
            cromwell_workflow_id = re.search('[0-9|a-z]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12}',
                                             file).group(0)
            out = 'dat/' + cromwell_workflow_id + '/'
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

    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="VCF inspector")
    parser.add_argument("-i", "--input", type=str, dest="input", default='input_files.txt',
                        help="input a txt file that contains paths each line")
    args = parser.parse_args()
    input_file = args.input
    filelist = load_input_paths(input_file)
    filenames = load_input_names(input_file)
    filedict = load_input_dict(input_file)
    # first, prepare the data
    data_prepare(filelist)
    app = start_app(input_file,filelist,filenames,filedict)
    print('aaa')
    app.run_server(host='0.0.0.0', port=8080, debug=False, dev_tools_silence_routes_logging=True)
