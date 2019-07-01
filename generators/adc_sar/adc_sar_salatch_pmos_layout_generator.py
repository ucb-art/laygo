import yaml

def execfile(filepath, globals=None, locals=None):
    if globals is None:
        globals = {}
    globals.update({
        "__file__": filepath,
        "__name__": "__main__",
    })
    import os
    with open(filepath, 'rb') as file:
        exec(compile(file.read(), filepath, 'exec'), globals, locals)

load_from_file=True
yamlfile_spec="adc_sar_spec.yaml"
yamlfile_size="adc_sar_size.yaml"

if load_from_file==True:
    with open(yamlfile_spec, 'r') as stream:
        specdict = yaml.load(stream)
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    doubleSA=sizedict['salatch']['doubleSA']

if doubleSA == False:
    files=[
        'laygo/generators/adc_sar/adc_sar_salatch_pmos_only_layout_generator.py',
        ]
else:
    files=[
        'laygo/generators/adc_sar/adc_sar_doubleSA_pmos_1st_layout_generator.py',
        'laygo/generators/adc_sar/adc_sar_doubleSA_pmos_2nd_layout_generator.py',
        'laygo/generators/adc_sar/adc_sar_doubleSA_pmos_layout_generator.py',
        ]

for f in files:
    execfile(f)
