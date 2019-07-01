# -*- coding: utf-8 -*-

import pprint

import bag
import laygo
import numpy as np
import yaml

lib_name = 'serdes_templates'
cell_name = 'ser_3stage'
impl_lib = 'serdes_generated'
params = dict(
    lch = 16e-9,
    pw = 4,
    nw = 4,
    num_ser = 10,
    num_ser_3rd = 4,
    m_dff=1, 
    m_cbuf1=2, 
    m_cbuf2=8, 
    m_pbuf1=2, 
    m_pbuf2=8, 
    m_mux=2, 
    m_out=2, 
    m_ser=1, 
    device_intent='fast'
    )
load_from_file=True
yamlfile_spec="serdes_spec.yaml"
yamlfile_size="serdes_size.yaml"

if load_from_file==True:
    with open(yamlfile_spec, 'r') as stream:
        specdict = yaml.load(stream)
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    cell_name='ser_3stage'
    suffix_name='_'+str(int(specdict['num_ser']*specdict['num_ser_3rd']))+'to1'
    params['num_ser']=specdict['num_ser']
    params['num_ser_3rd']=specdict['num_ser_3rd']
    params['m_dff']=sizedict['m_dff']
    params['m_cbuf1']=sizedict['m_cbuf1']
    params['m_cbuf2']=sizedict['m_cbuf2']
    params['m_pbuf1']=sizedict['m_pbuf1']
    params['m_pbuf2']=sizedict['m_pbuf2']
    params['m_mux']=sizedict['m_mux']
    params['m_out']=sizedict['m_out']
    params['m_ser']=sizedict['m_ser']
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
dsn.implement_design(impl_lib, top_cell_name=cell_name+suffix_name, erase=True)

