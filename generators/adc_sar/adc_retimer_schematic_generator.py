# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
# noinspection PyUnresolvedReferences,PyCompatibility
from builtins import *

import cProfile
import pprint

import bag
from bag.layout import RoutingGrid, TemplateDB
#from adc_sar.sampler import NPassGateWClk
from abs_templates_ec.adc_sar.sampler import NPassGateWClk
import yaml

impl_lib = 'adc_retimer_ec'

if __name__ == '__main__':
    prj = bag.BagProject()
    lib_name = 'adc_sar_templates'
    cell_name = 'adc_retimer'

    params = dict(
        lch=16e-9,
        pw=4,
        nw=4,
        m_ibuf=8,
        m_obuf=8,
        m_latch=2,
        num_slices=8,
        num_bits=9,
        device_intent='fast'
    )
    load_from_file=True

    yamlfile_spec="adc_sar_spec.yaml"
    yamlfile_size="adc_sar_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        params['num_slices']=specdict['n_interleave']
        params['num_bits']=specdict['n_bit']



    # create design module and run design method.
    print('designing module')
    dsn = prj.create_design_module(lib_name, cell_name)
    print('design parameters:\n%s' % pprint.pformat(params))
    dsn.design(**params)

    # implement the design
    print('implementing design with library %s' % impl_lib)
    dsn.implement_design(impl_lib, top_cell_name=cell_name, erase=True)

