# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
import numpy as np
import yaml

lib_name = 'clk_dis_templates'
cell_name = 'clk_dis_viadel_cal'
impl_lib = 'clk_dis_generated'

params = dict(
    lch=30e-9,
    pw=4,
    nw=4,
    m_dff=2, 
	m_inv1=6, 
	m_inv2=8, 
	m_tgate=18, 
	m_capsw=2, 
	n_pd=4, 
	num_bits=5,
    unit_cell=2,
    num_ways=33,
    device_intent='fast',
    )
#generate_layout = False
#extract_layout = False
load_from_file=True
yamlfile_spec="adc_sar_spec.yaml"
yamlfile_size="adc_sar_size.yaml"
if load_from_file==True:
    with open(yamlfile_spec, 'r') as stream:
        specdict = yaml.load(stream)
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    params['num_ways']=specdict['n_interleave']+1
    params['lch']=sizedict['lch']
    params['pw']=sizedict['pw']
    params['nw']=sizedict['nw']
    params['device_intent']=sizedict['device_intent']
    params['m_dff']=sizedict['clk_dis_cell']['m_dff']
    params['m_inv1']=sizedict['clk_dis_cell']['m_inv1']
    params['m_inv2']=sizedict['clk_dis_cell']['m_inv2']
    params['m_tgate']=sizedict['clk_dis_cell']['m_tgate']
    params['unit_cell']=sizedict['clk_dis_cdac']['m']
    params['num_bits']=sizedict['clk_dis_cdac']['num_bits']
    params['m_capsw']=sizedict['clk_dis_capsw']['m']

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
