# -*- coding: utf-8 -*-

import pprint

import bag
import laygo
import numpy as np
import yaml

lib_name = 'serdes_templates'
cell_name = 'des'
impl_lib = 'serdes_generated'
params = dict(
    num_des = 8,
    num_flop = 1,
    ext_clk = False,
    lch = 16e-9,
    pw = 4,
    nw = 4,
    m_des_dff=1, 
    clkbuf_list=[1,2,4,8], 
    divbuf_list=[1,2,4,8], 
    device_intent='fast',
    )
load_from_file=True
yamlfile_spec="serdes_spec.yaml"
yamlfile_size="serdes_size.yaml"

if load_from_file==True:
    with open(yamlfile_spec, 'r') as stream:
        specdict = yaml.load(stream)
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    #cell_name='des_1to'+str(specdict['num_des'])
    cell_name='des'
    suffix_name='_1to'+str(specdict['num_des'])
    params['num_des']=specdict['num_des']
    params['num_flop']=specdict['num_flop']
    params['ext_clk']=specdict['ext_clk']
    params['m_des_dff']=sizedict['m_des_dff']
    params['lch']=sizedict['lch']
    params['pw']=sizedict['pw']
    params['nw']=sizedict['nw']
    params['clkbuf_list']=sizedict['des_clkbuf_list']
    params['divbuf_list']=sizedict['des_divbuf_list']
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
# dsn.implement_design(impl_lib, top_cell_name=cell_name, suffix=suffix_name, erase=True)
dsn.implement_design(impl_lib, top_cell_name=cell_name+suffix_name, erase=True)

