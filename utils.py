import pandas as pd
import os
import re


def venn_diagram(file1, file2, caller):
    # out1 = 'dat/' + file1.split('/')[6] + '.txt'
    # out2 = 'dat/' + file2.split('/')[6] + '.txt'
    out1 = 'dat/' + file1[1:-3].replace('/','_')+'txt'
    out2 = 'dat/' + file2[1:-3].replace('/','_')+'txt'
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


# caller = ['af', 'dbsnp', 'ffpe', 'merge', 'PASS', 'proximity']
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
    df_res = pd.DataFrame(columns=['name', 'PASS', 'af', 'dbsnp', 'ffpe', 'merge', 'proximity','total'])
    for name, path in filedict.items():
        # out = 'dat/' + path.split('/')[6] + '.txt'
        out = 'dat/' + path[1:-3].replace('/','_')+'txt'

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
             'proximity': proximity_number / total,'total': total}, ignore_index=True)
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
                    if (str1.split(',')[0].split('=')[1], str1.split(',')[1].split('=')[1][1:-1]) not in vcf_dict.items():
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
    for name, path in filedict.items():
        out = 'dat/' + path[1:-3].replace('/', '_') + 'txt'
        if not os.path.exists(out):
            os.system('grep -v "^#" ' + path + ' | cut -f 1,2,7 | sort > ' + out)
