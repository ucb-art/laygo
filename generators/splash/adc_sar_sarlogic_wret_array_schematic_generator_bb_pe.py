# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
import numpy as np
import yaml

lib_name = 'adc_sar_templates'
cell_name = 'sarlogic_wret_v2_array_bb_pe'
impl_lib = 'adc_sar_generated'

params = dict(
    lch=16e-9,
    pw=4,
    nw=4,
    m=1,
    m_xor=2,
    num_bits=9,
    device_intent='fast',
    )
load_from_file=True

yamlfile_system_input="adc_sar_spec.yaml"
yamlfile_size="adc_sar_size.yaml"
if load_from_file==True:
    with open(yamlfile_system_input, 'r') as stream:
        sysdict_i = yaml.load(stream)
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    cell_name='sarlogic_wret_v2_array_bb_pe'
    params['m_dl']=sizedict['sarlogic']['m_dl']
    params['m_xor']=sizedict['sarlogic']['m_xor']
    params['m_buf']=sizedict['sarlogic']['m_buf']
    params['num_inv_dl']=sizedict['sarlogic']['num_inv_dl']
    params['m']=sizedict['sarlogic']['m']
    params['num_bits']=sysdict_i['n_bit']
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

