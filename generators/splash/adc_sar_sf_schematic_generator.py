# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
import numpy as np
import yaml

lib_name = 'adc_sar_templates'
cell_name = 'sourceFollower'
impl_lib = 'adc_sar_generated'
tb_lib = 'adc_sar_testbenches'
# tb_cell = 'salatch_pmos_tb_tran'
# tb_noise_cell = 'salatch_pmos_tb_trannoise'

params = dict(
    lch=16e-9,
    nw=4,
    m_mirror=8,
    m_bias=8,
    m_off=2,
    m_in=4,
    m_bias_dum=4,
    m_in_dum=4,
    m_byp=8,
    m_byp_bias=4,
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
    params['m_mirror']=sizedict['sourceFollower']['m_mirror']
    params['m_bias']=sizedict['sourceFollower']['m_bias']
    params['m_off']=sizedict['sourceFollower']['m_off']
    params['m_in']=sizedict['sourceFollower']['m_in']
    params['m_bias_dum']=sizedict['sourceFollower']['m_bias_dum']
    params['m_in_dum']=sizedict['sourceFollower']['m_in_dum']
    params['m_byp']=sizedict['sourceFollower']['m_byp']
    params['m_byp_bias']=sizedict['sourceFollower']['m_byp_bias']
    params['bias_current']=sizedict['sourceFollower']['bias_current']
    params['lch']=sizedict['lch']
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
dsn.implement_design(impl_lib, top_cell_name=cell_name)
#dsn.implement_design(impl_lib, top_cell_name=cell_name_standalone, erase=True)

