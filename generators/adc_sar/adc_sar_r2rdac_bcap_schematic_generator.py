# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
import numpy as np
import yaml

lib_name = 'adc_sar_templates'
cell_name = 'r2r_dac_bcap_array'
impl_lib = 'adc_sar_generated'
tb_lib = 'adc_sar_testbenches'

params = dict(
    lch=16e-9,
    nw=4,
    pw=4,
    m_bcap=2,
    num_series=4,
    num_bits=5,
    num_dacs=16,
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
    params['m_bcap']=sizedict['r2rdac']['m_bcap']
    params['num_series']=sizedict['r2rdac']['num_series']
    params['num_bits']=sizedict['r2rdac']['num_bits']
    params['num_dacs']=sizedict['r2rdac_array']['num_hori']*sizedict['r2rdac_array']['num_vert']
    params['lch']=sizedict['lch']
    params['nw']=sizedict['nw']
    params['pw']=sizedict['pw']
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
dsn.implement_design(impl_lib, top_cell_name=cell_name)
#dsn.implement_design(impl_lib, top_cell_name=cell_name_standalone, erase=True)

