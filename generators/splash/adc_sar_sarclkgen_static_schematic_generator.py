# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
import numpy as np
import yaml

lib_name = 'adc_sar_templates'
cell_name = 'sarclkgen_static'
impl_lib = 'adc_sar_generated'

params = dict(
    lch=16e-9,
    pw=4,
    nw=4,
    m=2,
    fo=2,
    ndelay=1,
    fast=False,
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
    params['m']=sizedict['sarclkgen']['m']
    params['fo']=sizedict['sarclkgen']['fo']
    params['ndelay']=sizedict['sarclkgen']['ndelay']
    params['fast']=sizedict['sarclkgen']['fast']
    params['fastest']=sizedict['sarclkgen']['fastest']
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

