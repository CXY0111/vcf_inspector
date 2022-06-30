import json

def load_dict(filename):
    with open(filename) as f:
        dict = json.loads(f.read())
    return dict

print(load_dict('stored_vcf_filedict.json'))
