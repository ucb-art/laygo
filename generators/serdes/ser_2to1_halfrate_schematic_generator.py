# -*- coding: utf-8 -*-

import pprint

import bag
import laygo
import numpy as np
import yaml

lib_name = 'serdes_templates'
cell_name = 'ser_2to1_halfrate'
impl_lib = 'serdes_generated'
params = dict(
    lch = 16e-9,
    pw = 4,
    nw = 4,
    m_ser = 1,
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
    cell_name='ser_2to1_halfrate'
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
dsn.implement_design(impl_lib, top_cell_name=cell_name, erase=True)

