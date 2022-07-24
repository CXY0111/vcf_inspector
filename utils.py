import pandas as pd
import os, sys
import re
import json
from tqdm import tqdm
from io import BytesIO
import base64
import plotly.graph_objects as go


def fig_to_uri(in_fig, close_all=True, **save_args):
    # https://github.com/4QuantOSS/DashIntro/blob/master/notebooks/Tutorial.ipynb
    """
    Save a figure as a URI    type: (plt.Figure) -> str
    :param in_fig:
    :return:
    """
    out_img = BytesIO()
    in_fig.savefig(out_img, format='png', **save_args)
    if close_all:
        in_fig.clf()
        plt.close('all')
    out_img.seek(0)  # rewind file
    encoded = base64.b64encode(out_img.read()).decode("ascii").replace("\n", "")
    return "data:image/png;base64,{}".format(encoded)


def venn_diagram(files, caller):
    """
    get the venn diagram numbers(uniqueA,common,uniqueB) given the two vcf files

    :param files: list of paths to vcf file
    :param caller: compare the variants with the selected filter
    :return: common number, uniqueA number, uniqueB number
    :rtype: int
    """
    if len(files) == 2:
        dfA = pd.read_table(files[0], header=None)
        dfB = pd.read_table(files[1], header=None)

        if caller == 'vcf_all':
            dfA = dfA[[0, 1]]
            dfB = dfB[[0, 1]]
        else:  # if caller in ['af','dbsnp','ffpe','merge','PASS','proximity']
            dfA = dfA[dfA[2] == caller][[0, 1]]
            dfB = dfB[dfB[2] == caller][[0, 1]]

        # return common, uniqueA, uniqueB in venn diagram
        return len(pd.merge(dfA, dfB, how='inner')), \
               len(dfA.merge(dfB, indicator=True, how='left').loc[lambda x: x['_merge'] != 'both']), \
               len(dfA.merge(dfB, indicator=True, how='right').loc[lambda x: x['_merge'] != 'both'])
    elif len(files) == 3:
        dfA = pd.read_table(files[0], header=None)
        dfB = pd.read_table(files[1], header=None)
        dfC = pd.read_table(files[2], header=None)

        if caller == 'vcf_all':
            dfA = dfA[[0, 1]]
            dfB = dfB[[0, 1]]
            dfC = dfC[[0, 1]]
        else:  # if caller in ['af','dbsnp','ffpe','merge','PASS','proximity']
            dfA = dfA[dfA[2] == caller][[0, 1]]
            dfB = dfB[dfB[2] == caller][[0, 1]]
            dfC = dfC[dfC[2] == caller][[0, 1]]

        dfA['A'] = dfA[0] + '_' + dfA[1].astype('str')
        dfB['B'] = dfB[0] + '_' + dfB[1].astype('str')
        dfC['C'] = dfC[0] + '_' + dfC[1].astype('str')

        # https://towardsdatascience.com/professional-venn-diagrams-in-python-638abfff39cc
        A = set(dfA.A)
        B = set(dfB.B)
        C = set(dfC.C)

        AB_overlap = A & B  # compute intersection of set A & set B
        AC_overlap = A & C
        BC_overlap = B & C
        ABC_overlap = A & B & C
        A_rest = A - AB_overlap - AC_overlap  # see left graphic
        B_rest = B - AB_overlap - BC_overlap
        C_rest = C - AC_overlap - BC_overlap
        AB_only = AB_overlap - ABC_overlap  # see right graphic
        AC_only = AC_overlap - ABC_overlap
        BC_only = BC_overlap - ABC_overlap
        return len(AB_overlap), len(AC_overlap), len(BC_overlap), len(ABC_overlap), len(A_rest), len(B_rest), len(
            C_rest), len(AB_only), len(AC_only), len(BC_only)


def draw_venn_figure(number_list):
    """
    Draw the figure of venn diagram. number_list==3 -> venn2; number_list==7 -> venn3

    :param number_list: return of function venn_diagram.
                        venn2 = [ua, com, ub]
                        venn3 = [A_rest, B_rest, C_rest, AB_only, AC_only, BC_only, ABC_overlap]
    :return: fig of venn diagram
    :rtype: fig
    """

    venn_type = 'venn2' if len(number_list) == 3 else 'venn3'
    fig = go.Figure()

    # add trace of numbers
    if venn_type == 'venn2':
        fig.add_trace(go.Scatter(
            x=[0.8, 1.75, 2.7, 0.8, 1.75, 2.7],
            y=[1, 1, 1, 0.75, 0.75, 0.75],
            text=["SetA", "Common", "SetB", number_list[0], number_list[1], number_list[2]],
            mode="text",
            textfont=dict(
                color="black",
                size=18,
                family="Arail",
            ),
            name='trace0'
        ))
    else:  # venn_type == 'venn3'
        fig.add_trace(go.Scatter(
            x=[-0.25, 7.25, 3.5],
            y=[1, 1, 7.5],
            text=["SetA", "SetB", "SetC"],
            mode="text",
            textfont=dict(
                color="black",
                size=20,
                family="Arail",
            ),
            name='Sets'
        ))
        # Create scatter trace of text labels
        fig.add_trace(go.Scatter(
            x=[1.5, 5.5, 3.5],
            y=[1.5, 1.5, 6],
            text=[number_list[0], number_list[1], number_list[2]],
            mode="text",
            textfont=dict(
                color="black",
                size=17,
                family="Arail",
            ),
            name='only_trace'
        ))

        fig.add_trace(go.Scatter(
            x=[3.5, 2, 5, 3.5],
            y=[1.5, 4.25, 4.25, 3.25],
            text=[number_list[3], number_list[4], number_list[5], number_list[6]],
            mode="text",
            textfont=dict(
                color="black",
                size=14,
                family="Arail",
            ),
            name='common_trace'
        ))

    # Update axes properties
    fig.update_xaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=False,
    )

    fig.update_yaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=False,
        scaleanchor="x",
        scaleratio=1,
    )

    if venn_type == 'venn2':
        # Add circles
        fig.add_shape(type="circle",
                      line_color="blue", fillcolor="blue",
                      x0=0.25, y0=0, x1=2.25, y1=2
                      )
        fig.add_shape(type="circle",
                      line_color="gray", fillcolor="gray",
                      x0=1.25, y0=0, x1=3.25, y1=2
                      )
    else:  # venn_type == 'venn3'
        # Add circles
        fig.add_shape(type="circle",
                      line_color="blue", fillcolor="blue",
                      x0=-0.25, y0=0, x1=4.75, y1=5
                      )
        fig.add_shape(type="circle",
                      line_color="gray", fillcolor="gray",
                      x0=2.25, y0=0, x1=7.25, y1=5
                      )
        fig.add_shape(type="circle",
                      line_color="yellow", fillcolor="yellow",
                      x0=1, y0=2.25, x1=6, y1=7.25
                      )
    fig.update_shapes(opacity=0.3, xref="x", yref="y")

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0})

    fig.layout.plot_bgcolor = 'rgba(0,0,0,0)'

    return fig


def chart(filedict, vcf_file_type):
    """
    get the distribution of each vcf file in the file dict

    :param filedict: filedict that contains all the vcf files
    :param vcf_file_type: which kind of vcf file, ProximityFiltered? mutect_somatic_depth_filter?
    :return: df of the distribution
    :rtype: dataframe
    """

    filelist = list(filedict.values())
    if vcf_file_type == 'ProximityFiltered':
        out_list = ['dat/' + re.search('[0-9|a-z]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12}', path).group(
            0) + '/ProximityFiltered.txt' for path in filelist]
    else:
        out_list = ['dat/' + re.search('[0-9|a-z]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12}', path).group(
            0) + '/' + vcf_file_type + '.output.txt' for path in filelist]
    used_filters = get_used_filters(out_list)
    if 'vcf_all' in used_filters:
        used_filters.remove('vcf_all')
    df_res = pd.DataFrame(columns=['name'] + used_filters + ['total'])
    for name, path in filedict.items():
        numbers = {}
        cromwell_workflow_id = re.search('[0-9|a-z]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12}',
                                         path).group(0)
        numbers['name'] = name
        if vcf_file_type == 'ProximityFiltered':
            path = 'dat/' + re.search('[0-9|a-z]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12}', path).group(
                0) + '/ProximityFiltered.txt'
        else:
            path = 'dat/' + re.search('[0-9|a-z]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12}', path).group(
                0) + '/' + vcf_file_type + '.output.txt'
        df = pd.read_table(path, header=None)
        total = len(df)
        for filter in used_filters:
            numbers[filter] = len(df[df[2].str.contains(filter)]) / total

        numbers['total'] = total
        df_res = df_res.append(numbers, ignore_index=True)
    return df_res


def get_filters_dict(vcf_file_list):  # vcf_file1, vcf_file2
    """
    Read two vcf files to get all the filters and their description

    :param vcf_file_list: list of Paths to a vcf files.
    :return: dict of all filters and description
    :rtype: dict
    """

    vcf_dict = {}
    for vcf_file in vcf_file_list:
        with open(vcf_file, 'r') as invcf:
            for line in invcf:
                if line.startswith('#'):
                    if 'FILTER=' in line:
                        str1 = re.findall('<([^】]+)>', line)[0]
                        if (
                                str1.split(',')[0].split('=')[1],
                                str1.split(',')[1].split('=')[1][1:-1]) not in vcf_dict.items():
                            vcf_dict[str1.split(',')[0].split('=')[1]] = str1.split(',')[1].split('=')[1][1:-1]

    # vcf_dict = []
    # with open(vcf_file1, 'r') as invcf:
    #     for line in invcf:
    #         if line.startswith('#'):
    #             if 'FILTER=' in line:
    #                 vcf_dict.append(re.findall('<([^】]+)>', line)[0])
    # vcf_dict = {item.split(',')[0].split('=')[1]: item.split(',')[1].split('=')[1][1:-1] for item in vcf_dict}
    #
    # with open(vcf_file2, 'r') as invcf:
    #     for line in invcf:
    #         if line.startswith('#'):
    #             if 'FILTER=' in line:
    #                 str1 = re.findall('<([^】]+)>', line)[0]
    #                 if (
    #                         str1.split(',')[0].split('=')[1],
    #                         str1.split(',')[1].split('=')[1][1:-1]) not in vcf_dict.items():
    #                     vcf_dict[str1.split(',')[0].split('=')[1]] = str1.split(',')[1].split('=')[1][1:-1]

    return vcf_dict


def get_used_filters(path_list):
    """
    Read two filterd vcf file(which is a txt file with chr,pos,filter) and return all the filters used in this two vcf files

    :param path_list: Path list of filterd vcf files
    :return: all the filters used in this two vcf files
    :rtype: list
    """
    df_res = pd.DataFrame(columns=[0, 1, 2])
    filters = []
    for path in path_list:
        df = pd.read_table(path, header=None)
        for item in pd.concat([df_res, df])[2].unique():
            if ';' in item:
                for i in item.split(';'):
                    if i not in filters:
                        filters.append(i)
            else:
                # print(item)
                if item not in filters:
                    filters.append(item)
    return ['vcf_all'] + filters


def data_prepare(filelist):
    """
        prepare the data to be used.

        :param filelist: file list that contains all the vcf files
        :return: None
        :rtype: None
        """
    print('Data Prepare:')
    for path in filelist:
        if not os.path.exists(path):
            sys.exit('Please check the input file path')
        cromwell_workflow_id = re.search('[0-9|a-z]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12}',
                                         path).group(0)
        out = 'dat/' + cromwell_workflow_id + '/'
        # create a folder name with its cromwell_workflow_id in dat
        if not os.path.exists(out):
            os.system('mkdir -p ' + out)

        print('Processing', cromwell_workflow_id)
        directories = ['call-snp_indel_proximity_filter', 'call-depth_filter_mutect', 'call-depth_filter_pindel',
                       'call-depth_filter_strelka_indel', 'call-depth_filter_strelka_snv',
                       'call-depth_filter_varscan_indel', 'call-depth_filter_varscan_snv']
        for dir in tqdm(directories):
            if dir == 'call-snp_indel_proximity_filter':
                vcf_path = path + dir + '/execution/output/ProximityFiltered.vcf'
                vcf_out = out + 'ProximityFiltered.txt'
                if os.path.exists(vcf_path) and not os.path.exists(vcf_out):
                    os.system('grep -v "^#" ' + vcf_path + ' | cut -f 1,2,7 | sort > ' + vcf_out)
            else:
                vcf_path = path + dir + '/execution/somatic_depth_filter.output.vcf'
                filter = re.sub('call-depth_filter_', '', dir)
                vcf_out = out + filter + '_somatic_depth_filter.output.txt'
                if os.path.exists(vcf_path) and not os.path.exists(vcf_out):
                    os.system('grep -v "^#" ' + vcf_path + ' | cut -f 1,2,7 | sort > ' + vcf_out)
        # # check and create txt file for out vcf all
        # if os.path.exists(
        #         path + 'call-snp_indel_proximity_filter/execution/output/ProximityFiltered.vcf') and not os.path.exists(
        #     out + 'ProximityFiltered.txt'):
        #     os.system(
        #         'grep -v "^#" ' + path + 'call-snp_indel_proximity_filter/execution/output/ProximityFiltered.vcf | cut -f 1,2,7 | sort > ' + out + 'ProximityFiltered.txt')
        # ### before merge vcfs ###
        # # mutect
        # if os.path.exists(
        #         path + 'call-depth_filter_mutect/execution/somatic_depth_filter.output.vcf') and not os.path.exists(
        #     out + 'mutect_somatic_depth_filter.output.txt'):
        #     os.system(
        #         'grep -v "^#" ' + path + 'call-depth_filter_mutect/execution/somatic_depth_filter.output.vcf | cut -f 1,2,7 | sort > ' + out + 'mutect_somatic_depth_filter.output.txt')
        # # pindel
        # if os.path.exists(
        #         path + 'call-depth_filter_pindel/execution/somatic_depth_filter.output.vcf') and not os.path.exists(
        #     out + 'pindel_somatic_depth_filter.output.txt'):
        #     os.system(
        #         'grep -v "^#" ' + path + 'call-depth_filter_pindel/execution/somatic_depth_filter.output.vcf | cut -f 1,2,7 | sort > ' + out + 'pindel_somatic_depth_filter.output.txt')
        # # strelka_indel
        # if os.path.exists(
        #         path + 'call-depth_filter_strelka_indel/execution/somatic_depth_filter.output.vcf') and not os.path.exists(
        #     out + 'strelka_indel_somatic_depth_filter.output.txt'):
        #     os.system(
        #         'grep -v "^#" ' + path + 'call-depth_filter_strelka_indel/execution/somatic_depth_filter.output.vcf | cut -f 1,2,7 | sort > ' + out + 'strelka_indel_somatic_depth_filter.output.txt')
        # # strelka_snv
        # if os.path.exists(
        #         path + 'call-depth_filter_strelka_snv/execution/somatic_depth_filter.output.vcf') and not os.path.exists(
        #     out + 'strelka_snv_somatic_depth_filter.output.txt'):
        #     os.system(
        #         'grep -v "^#" ' + path + 'call-depth_filter_strelka_snv/execution/somatic_depth_filter.output.vcf | cut -f 1,2,7 | sort > ' + out + 'strelka_snv_somatic_depth_filter.output.txt')
        # # varscan_indel
        # if os.path.exists(
        #         path + 'call-depth_filter_varscan_indel/execution/somatic_depth_filter.output.vcf') and not os.path.exists(
        #     out + 'varscan_indel_somatic_depth_filter.output.txt'):
        #     os.system(
        #         'grep -v "^#" ' + path + 'call-depth_filter_varscan_indel/execution/somatic_depth_filter.output.vcf | cut -f 1,2,7 | sort > ' + out + 'varscan_indel_somatic_depth_filter.output.txt')
        # # varscan_snv
        # if os.path.exists(
        #         path + 'call-depth_filter_varscan_snv/execution/somatic_depth_filter.output.vcf') and not os.path.exists(
        #     out + 'varscan_snv_somatic_depth_filter.output.txt'):
        #     os.system(
        #         'grep -v "^#" ' + path + 'call-depth_filter_varscan_snv/execution/somatic_depth_filter.output.vcf | cut -f 1,2,7 | sort > ' + out + 'varscan_snv_somatic_depth_filter.output.txt')


def get_radio_options(out):
    res = []
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
    return res


def save_filelist_json(filelist):
    filename = 'dat/stored_vcf_filelist.json'
    with open(filename, 'w') as f:
        f.write(json.dumps(filelist))


def load_filelist_json(filename):
    filename = 'dat/' + filename
    with open(filename) as f:
        filelist = json.loads(f.read())
    return filelist


def load_input_paths(input_file):
    res = []
    with open(input_file, "r") as txt_file:
        lines = txt_file.readlines()
        for line in lines:
            line = re.sub('\n', '', line)
            if not line or line.startswith('#'):
                continue
            line = re.sub('.+:', '', line)

            if line[-1] != '/':
                line += '/'
            res.append(line)
    return res


def load_input_names(input_file):
    res = []
    with open(input_file, "r") as txt_file:
        lines = txt_file.readlines()
        for line in lines:
            line = re.sub('\n', '', line)
            if not line or line.startswith('#'):
                continue
            line = re.sub(':.+', '', line)

            res.append(line)
    return res


def load_input_dict(input_file):
    result_dict = {}
    with open(input_file, "r") as txt_file:
        lines = txt_file.readlines()
        for line in lines:
            line = re.sub('\n', '', line)
            if not line or line.startswith('#'):
                continue
            name = line.split(':')[0]
            path = line.split(':')[1]
            if path[-1] != '/':
                path += '/'
            result_dict[name] = path
    return result_dict


def name_to_dir_path(filedict, name):
    """
    get the path to the dat directory from name

    :param filedict: file dict that contains pair of name and directory path
    :param name: name of the path
    :return: path
    :rtype: str
    """

    path = filedict[name]
    cromwell_workflow_id = re.search('[0-9|a-z]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12}',
                                     path).group(0)
    path = 'dat/' + cromwell_workflow_id + '/'

    return path


def dir_to_file_path(dir, name_radio):
    """
    get the path to the dat directory from name

    :param dir: path to the dat directory
    :param name_radio: which file to choose
    :return: path
    :rtype: str
    """
    if name_radio == 'ProximityFiltered':
        dir += name_radio + '.txt'
    else:
        dir += name_radio + '.output.txt'

    return dir
