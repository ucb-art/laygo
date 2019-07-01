# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
import numpy as np
import yaml

lib_name = 'adc_sar_templates'
cell_name = 'doubleSA_pmos_2nd'
cell_name_standalone = 'doubleSA_pmos_standalone'
impl_lib = 'adc_sar_generated'
tb_lib = 'adc_sar_testbenches'
tb_cell = 'salatch_pmos_tb_tran'
tb_noise_cell = 'salatch_pmos_tb_trannoise'

params = dict(
    lch=16e-9,
    pw=4,
    nw=4,
    m=8, #larger than 8, even number
    m_d=8, #larger than 8, even number
    m_rst=4,
    m_rst_d=4,
    m_rgnn=4,
    m_rgnp_d=4,
    m_buf=8,
    device_intent='fast',
    )

load_from_file=True
yamlfile_spec="adc_sar_spec.yaml"
yamlfile_size="adc_sar_size.yaml"

if load_from_file==True:
    with open(yamlfile_spec, 'r') as stream:
        specdict = yaml.load(stream)
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    #params['m']=sizedict['salatch_m']
    #params['m_rst']=sizedict['salatch_m_rst']
    #params['m_rgnn']=sizedict['salatch_m_rgnn']
    #params['m_buf']=sizedict['salatch_m_buf']
    params['m']=sizedict['salatch']['m']
    params['m_d']=sizedict['salatch']['m_d']
    params['m_rst']=sizedict['salatch']['m_rst']
    params['m_rst_d']=sizedict['salatch']['m_rst_d']
    params['m_rgnn']=sizedict['salatch']['m_rgnn']
    params['m_rgnp_d']=sizedict['salatch']['m_rgnp_d']
    params['m_buf']=sizedict['salatch']['m_buf']
    params['lch']=sizedict['lch']
    params['pw']=sizedict['pw']
    params['nw']=sizedict['nw']
    params['device_intent']=sizedict['device_intent']

print('creating BAG project')
prj = bag.BagProject()

# create design module and run design method.
print('designing module')
dsn = prj.create_design_module(lib_name, cell_name)
print('design parameters:\n%s' % pprint.pformat(params))
dsn.design(**params)

# implement the design
print('implementing design with library %s' % impl_lib)
dsn.implement_design(impl_lib, top_cell_name=cell_name, erase=True)
#dsn.implement_design(impl_lib, top_cell_name=cell_name_standalone, erase=True)

