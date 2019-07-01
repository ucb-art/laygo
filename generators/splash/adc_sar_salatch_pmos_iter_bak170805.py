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

files=[
    'laygo/generators/adc_sar/adc_sar_salatch_pmos_layout_generator.py',
    #'laygo/generators/adc_sar/adc_sar_salatch_pmos_layout_generator_standalone.py',
    'laygo/generators/adc_sar/adc_sar_salatch_pmos_schematic_generator.py',
    'laygo/generators/adc_sar/adc_sar_salatch_pmos_lvs.py',
    'laygo/generators/adc_sar/adc_sar_salatch_pmos_extract.py',
    'laygo/generators/adc_sar/adc_sar_salatch_pmos_verify.py',
    ]

yamlfile_size="adc_sar_size.yaml"         #size dict
yamlfile_output="adc_sar_output.yaml"         #output dict
#reset scratch
with open(yamlfile_output, 'r') as stream:
    outdict = yaml.load(stream)
    outdict['scratch']['tckq']=[]
    outdict['scratch']['q_samp_fF']=[]
with open(yamlfile_output, 'w') as stream:
    yaml.dump(outdict, stream)
with open(yamlfile_size, 'r') as stream:
    sizedict = yaml.load(stream)
    m_list=sizedict['salatch_preset']['m']
    m_buf_list=sizedict['salatch_preset']['m_buf']
    m_rgnn_list=sizedict['salatch_preset']['m_rgnn']
    m_rst_list=sizedict['salatch_preset']['m_rst']
for m, m_buf, m_rgnn, m_rst in zip(m_list, m_buf_list, m_rgnn_list, m_rst_list):
    #write to file
    #outdict=dict()
    sizedict['salatch']['m']=m
    sizedict['salatch']['m_rst']=m_rst
    sizedict['salatch']['m_rgnn']=m_rgnn
    sizedict['salatch']['m_buf']=m_buf
    with open(yamlfile_size, 'w') as stream:
        yaml.dump(sizedict, stream)

    for f in files:
        execfile(f)
