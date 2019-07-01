# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
import numpy as np
import yaml

lib_name = 'adc_sar_templates'
cell_name = 'sarafe_nsw'
impl_lib = 'adc_sar_generated'
#tb_lib = 'adc_sar_testbenches'
#tb_cell = 'sarafe_tb_tran'

params = dict(
    lch=30e-9,
    pw=4,
    nw=4,
    sa_m=8,
    sa_m_rst=4,
    sa_m_rgnn=4,
    sa_m_buf=8,
    drv_m_list=[2,2,2,2,2,2,4,8],
    num_bits=8,
    c_m=1,
    rdx_array=[1,2,4,8,16,32,64,128],
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
    params['sa_m']=sizedict['salatch']['m']
    params['sa_m_rst']=sizedict['salatch']['m_rst']
    params['sa_m_rgnn']=sizedict['salatch']['m_rgnn']
    params['sa_m_buf']=sizedict['salatch']['m_buf']
    params['num_bits']=specdict['n_bit']-1
    params['c_m']=sizedict['capdac']['c_m']
    params['rdx_array']=specdict['rdx_array']
    params['drv_m_list']=sizedict['capdrv']['m_list']
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

