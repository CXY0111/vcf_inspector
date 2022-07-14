from dash import Dash, html, dcc, Input, Output, State, dash_table, callback
import pandas as pd
import plotly.express as px
from utils import venn_diagram, chart, get_filters_dict, get_used_filters, data_prepare, save_filedict, load_filedict
import plotly.graph_objects as go
from dash.dash_table.Format import Format, Scheme, Trim
import json
import os

app = Dash(__name__)
# on katmai
filedict = {'CTSP-AD3X_RunA': '/diskmnt/Projects/Users/chen.xiangyu/dash/b17d5672-572f-463b-88ad-0ac7b06156ad/call'
                              '-snp_indel_proximity_filter/execution/output/ProximityFiltered.vcf',
            'CTSP-AD3X_RunB': '/diskmnt/Projects/Users/chen.xiangyu/dash/0f45d954-d951-4927-a2ba-476e319a6a88/call'
                              '-snp_indel_proximity_filter/execution/output/ProximityFiltered.vcf'}
# # on compute1
# filedict = {'CTSP-AD3X_RunA': '/storage1/fs1/m.wyczalkowski/Active/cromwell-data/cromwell-workdir/cromwell-executions'
#                               '/tindaisy2.ffpe.cwl/b17d5672-572f-463b-88ad-0ac7b06156ad/call'
#                               '-snp_indel_proximity_filter/execution/output/ProximityFiltered.vcf',
#             'CTSP-AD3X_RunB': '/storage1/fs1/m.wyczalkowski/Active/cromwell-data/cromwell-workdir/cromwell-executions'
#                               '/tindaisy2.ffpe.cwl/0f45d954-d951-4927-a2ba-476e319a6a88/call'
#                               '-snp_indel_proximity_filter/execution/output/ProximityFiltered.vcf'}
# save filedict to json
filename = 'stored_vcf_filedict.json'
with open(filename, 'w') as f:
    f.write(json.dumps(filedict))
# first, prepare the data
data_prepare(filedict)





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
                list(load_filedict('stored_vcf_filedict.json').keys()),
                'CTSP-AD3X_RunA',
                id='name1',
            ),
        ], style={'width': '47%', 'display': 'inline-block'}),

        html.Div([
            # placerholder
        ], style={'width': '4%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                list(load_filedict('stored_vcf_filedict.json').keys()),
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
    com, ua, ub = venn_diagram(load_filedict('stored_vcf_filedict.json')[name1], load_filedict('stored_vcf_filedict.json')[name2], caller)

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
    if os.path.exists(path):

        if path in list(load_filedict('stored_vcf_filedict.json').values()):
            tmp = 'Sorry, the path has been added'
        elif filename in list(load_filedict('stored_vcf_filedict.json').keys()):
            tmp = 'Sorry, the filename has been used'
        else:
            filedict = load_filedict('stored_vcf_filedict.json')
            filedict[filename] = path
            out = 'dat/' + path[1:-3].replace('/', '_') + 'txt'
            if not os.path.exists(out):
                os.system('grep -v "^#" ' + path + ' | cut -f 1,2,7 | sort > ' + out)
            save_filedict(filedict)
            tmp = u'''
                {} has been added successfully.
            '''.format(filename)
        # print(filedict)
    else:
        tmp = 'The path deos not exists.'

    return tmp


@app.callback(
    Output('name1', 'options'),
    Output('name2', 'options'),
    Input('submit-val', 'n_clicks'))
# def update_name1(name1_options, filename, path, n_clicks):
def update_names(n_clicks):

    name1_options = list(load_filedict('stored_vcf_filedict.json').keys())

    # if os.path.exists(path):
    #     if path not in list(filedict.values()) and filename not in list(filedict.keys()):
    #         name1_options += [filename]
    return name1_options, name1_options



@callback(
    Output('my_output', component_property='children'),
    Input('submit-val', 'n_clicks'))
def update_chart(n_clicks):
    df_res = chart(load_filedict('stored_vcf_filedict.json'))
    columns = []
    for i in df_res.columns:
        if i != 'total':
            columns.append(
                {"name": i, "id": i, "type": 'numeric', "format": Format(precision=2, scheme=Scheme.percentage)})
        else:
            columns.append({"name": i, "id": i, "type": 'numeric'})
    return dash_table.DataTable(data=df_res.to_dict('records'),
                                columns=columns,
                                tooltip_data=[{column: {'value': str(load_filedict('stored_vcf_filedict.json')[value]), 'type': 'markdown'}
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
    path1 = 'dat/' + load_filedict('stored_vcf_filedict.json')[name1][1:-3].replace('/','_')+'txt'
    path2 = 'dat/' + load_filedict('stored_vcf_filedict.json')[name2][1:-3].replace('/','_')+'txt'
    return get_used_filters(path1, path2)


@app.callback(
    Output('description', 'children'),
    Input('name1', 'value'),
    Input('name2', 'value'),
    Input('caller', 'options'))
def update_description(name1, name2, options):
    path1 = load_filedict('stored_vcf_filedict.json')[name1]
    path2 = load_filedict('stored_vcf_filedict.json')[name2]
    filters_dict = get_filters_dict(path1, path2)
    strs = ''
    for keys, values in filters_dict.items():
        # print(keys)
        # print(values)
        if keys in options:
            strs += '\n  ' + keys + ': ' + values
    return strs




if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080, debug=True)




#################################### utils.py #########################################################################
import pandas as pd
import os
import re
import json


def venn_diagram(file1, file2, caller):
    """
        get the venn diagram numbers(uniqueA,common,uniqueB) given the two vcf files

        :param file1: path to vcf file1
        :param file2: path to vcf file2
        :param caller: compare the variants with the selected filter
        :return: common number, uniqueA number, uniqueB number
        :rtype: int
        """
    # out1 = 'dat/' + file1.split('/')[6] + '.txt'
    # out2 = 'dat/' + file2.split('/')[6] + '.txt'
    out1 = 'dat/' + file1[1:-3].replace('/', '_') + 'txt'
    out2 = 'dat/' + file2[1:-3].replace('/', '_') + 'txt'
    if not os.path.exists(out1):
        os.system('grep -v "^#" ' + file1 + ' | cut -f 1,2,7 | sort > ' + out1)
    if not os.path.exists(out2):
        os.system('grep -v "^#" ' + file2 + ' | cut -f 1,2,7 | sort > ' + out2)

    dfA = pd.read_table(out1, header=None)
    dfB = pd.read_table(out2, header=None)

    # if caller in ['af','dbsnp','ffpe','merge','PASS','proximity']:
    if caller == 'vcf_all':
        dfA_filter = dfA[[0, 1]]
        dfB_filter = dfB[[0, 1]]
    else:
        dfA_filter = dfA[dfA[2] == caller][[0, 1]]
        dfB_filter = dfB[dfB[2] == caller][[0, 1]]
    # else:
    #     dfA_filter = dfA[dfA[2] == 'PASS'][[0, 1]]
    #     dfB_filter = dfB[dfB[2] == 'PASS'][[0, 1]]

    # return common, uniqueA, uniqueB in venn diagram
    return len(pd.merge(dfA_filter, dfB_filter, how='inner')), \
           len(dfA_filter.merge(dfB_filter, indicator=True, how='left').loc[lambda x: x['_merge'] != 'both']), \
           len(dfA_filter.merge(dfB_filter, indicator=True, how='right').loc[lambda x: x['_merge'] != 'both'])


# # caller = ['af', 'dbsnp', 'ffpe', 'merge', 'PASS', 'proximity']
def set_details(caller):
    if not os.path.exists('RunA.txt') and not os.path.exists('RunB.txt'):
        root = '/diskmnt/Projects/Users/chen.xiangyu/dash/'
        file1 = root + 'b17d5672-572f-463b-88ad-0ac7b06156ad/call-snp_indel_proximity_filter/execution/output' \
                       '/ProximityFiltered.vcf '
        file2 = root + '0f45d954-d951-4927-a2ba-476e319a6a88/call-snp_indel_proximity_filter/execution/output' \
                       '/ProximityFiltered.vcf '
        os.system('grep -v "^#" ' + file1 + ' | cut -f 1,2,7 | sort > RunA.txt')
        os.system('grep -v "^#" ' + file2 + ' | cut -f 1,2,7 | sort > RunB.txt')
    dfA = pd.read_table('RunA.txt', header=None)
    dfB = pd.read_table('RunB.txt', header=None)

    common = pd.merge(dfA, dfB, how='inner', left_on=[0, 1], right_on=[0, 1], suffixes=('_left', '_right'))
    left_only = dfA.merge(dfB, indicator=True, how='left').loc[lambda x: x['_merge'] != 'both']
    right_only = dfA.merge(dfB, indicator=True, how='right').loc[lambda x: x['_merge'] != 'both']

    return len(left_only[left_only[2] == caller]), len(common[common['2_left'] == caller]), \
           len(common[common['2_right'] == caller]), len(right_only[right_only[2] == caller]), \
           len(left_only[left_only[2].str.contains(caller)]), len(common[common['2_left'].str.contains(caller)]), \
           len(common[common['2_right'].str.contains(caller)]), len(right_only[right_only[2].str.contains(caller)]), \
           len(left_only), len(common), len(right_only)


def chart(filedict):
    """
        get the distribution of each vcf file in the file dict

        :param filedict: filedict that contains all the vcf files
        :return: df of the distribution
        :rtype: dataframe
        """
    df_res = pd.DataFrame(columns=['name', 'PASS', 'af', 'dbsnp', 'ffpe', 'merge', 'proximity', 'total'])
    for name, path in filedict.items():
        # out = 'dat/' + path.split('/')[6] + '.txt'
        out = 'dat/' + path[1:-3].replace('/', '_') + 'txt'

        df = pd.read_table(out, header=None)
        total = len(df)
        pass_number = len(df[df[2].str.contains('PASS')])
        af_number = len(df[df[2].str.contains('af')])
        dbsnp_number = len(df[df[2].str.contains('af')])
        ffpe_number = len(df[df[2].str.contains('ffpe')])
        merge_number = len(df[df[2].str.contains('merge')])
        proximity_number = len(df[df[2].str.contains('proximity')])

        df_res = df_res.append(
            {'name': name, 'PASS': pass_number / total, 'af': af_number / total, 'dbsnp': dbsnp_number / total,
             'ffpe': ffpe_number / total, 'merge': merge_number / total,
             'proximity': proximity_number / total, 'total': total}, ignore_index=True)
    return df_res


def get_filters_dict(vcf_file1, vcf_file2):
    """
    Read two vcf files to get all the filters and their description

    :param vcf_file2: Path to a filtered vcf file 1.
    :param vcf_file1: Path to a filtered vcf file 2.
    :return: dict of all filters and description
    :rtype: dict
    """
    vcf_dict = []
    with open(vcf_file1, 'r') as invcf:
        for line in invcf:
            if line.startswith('#'):
                if 'FILTER=' in line:
                    vcf_dict.append(re.findall('<([^】]+)>', line)[0])
    vcf_dict = {item.split(',')[0].split('=')[1]: item.split(',')[1].split('=')[1][1:-1] for item in vcf_dict}

    with open(vcf_file2, 'r') as invcf:
        for line in invcf:
            if line.startswith('#'):
                if 'FILTER=' in line:
                    str1 = re.findall('<([^】]+)>', line)[0]
                    if (
                    str1.split(',')[0].split('=')[1], str1.split(',')[1].split('=')[1][1:-1]) not in vcf_dict.items():
                        vcf_dict[str1.split(',')[0].split('=')[1]] = str1.split(',')[1].split('=')[1][1:-1]

    return vcf_dict


def get_used_filters(path1, path2):
    """
    Read two filterd vcf file(which is a txt file with chr,pos,filter) and return all the filters used in this two vcf files

    :param path2: Path to filterd vcf files 2
    :param path1: Path to filterd vcf files 1
    :return: all the filters used in this two vcf files
    :rtype: list
    """
    dfA = pd.read_table(path1, header=None)
    dfB = pd.read_table(path2, header=None)
    filters = []
    for item in pd.concat([dfA, dfB])[2].unique():
        if ';' in item:
            for i in item.split(';'):
                if i not in filters:
                    filters.append(i)
        else:
            # print(item)
            if item not in filters:
                filters.append(item)

    return ['vcf_all'] + filters


def data_prepare(filedict):
    """
        prepare the data to be used.

        :param filedict: filedict that contains all the vcf files
        :return: None
        :rtype: None
        """
    for name, path in filedict.items():
        out = 'dat/' + path[1:-3].replace('/', '_') + 'txt'
        if not os.path.exists(out):
            os.system('grep -v "^#" ' + path + ' | cut -f 1,2,7 | sort > ' + out)


def save_filedict(filedict):
    filename = 'stored_vcf_filedict.json'
    with open(filename, 'w') as f:
        f.write(json.dumps(filedict))


def load_filedict(filename):
    with open(filename) as f:
        filedict = json.loads(f.read())
    return filedict










