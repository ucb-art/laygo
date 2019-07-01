# -*- coding: utf-8 -*-

import pprint

import bag
import laygo
import numpy as np
import yaml


lib_name = 'clk_dis_templates'
temp_name = 'capdac'
cell_name = 'capdac'
impl_lib = 'clk_dis_generated'

load_from_file=False
yamlfile_system_input="adc_sar_dsn_system_input.yaml"

if load_from_file==True:
    with open(yamlfile_system_input, 'r') as stream:
        sysdict_i = yaml.load(stream)
    cell_name='capdac_'+str(sysdict_i['n_bit']-1)+'b'

params = dict(
	num_bits = 5,
	unit_cell = 2,
    )
load_from_file=True
yamlfile_spec="adc_sar_spec.yaml"
yamlfile_size="adc_sar_size.yaml"
if load_from_file==True:
    with open(yamlfile_spec, 'r') as stream:
        specdict = yaml.load(stream)
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    params['unit_cell']=sizedict['clk_dis_cdac']['m']
    params['num_bits']=sizedict['clk_dis_cdac']['num_bits']

print('creating BAG project')
prj = bag.BagProject()

# create design module and run design method.
print('designing module')
dsn = prj.create_design_module(lib_name, temp_name)
print('design parameters:\n%s' % pprint.pformat(params))
dsn.design(**params)

# implement the design
print('implementing design with library %s' % impl_lib)
dsn.implement_design(impl_lib, top_cell_name=cell_name, erase=True)

