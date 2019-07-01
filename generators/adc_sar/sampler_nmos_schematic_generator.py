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

#impl_lib = 'adc_sar_generated'
impl_lib = 'adc_sampler_ec'
if __name__ == '__main__':
    prj = bag.BagProject()
    lib_name = 'adc_ec_templates'
    cell_name = 'sampler_nmos'

    params = dict(
        lch=16e-9,
        wp=8,
        wn=8,
        fgn=12,
        fg_inbuf_list=[(8, 8), (14, 14)],
        fg_outbuf_list=[(4, 4), (24, 24)],
        nduml=10,
        ndumr=4,
        nsep=2,
        intent='ulvt',
    )

    load_from_file=True
    yamlfile_spec="adc_sar_spec.yaml"
    yamlfile_size="adc_sar_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        params['lch']=sizedict['lch']
        params['wp']=sizedict['sampler_nmos']['wp']
        params['wn']=sizedict['sampler_nmos']['wn']
        params['fgn']=sizedict['sampler_nmos']['fgn']
        params['fg_inbuf_list']=sizedict['sampler_nmos']['fg_inbuf_list']
        params['fg_outbuf_list']=sizedict['sampler_nmos']['fg_outbuf_list']
        params['nduml']=sizedict['sampler_nmos']['nduml']
        params['ndumr']=sizedict['sampler_nmos']['ndumr']
        params['nsep']=sizedict['sampler_nmos']['nsep']
        '''
        params['wp']=sizedict['pw']*2
        params['wn']=sizedict['nw']*2
        params['fgn']=int(sizedict['sarsamp']['m_sw']*sizedict['sarsamp']['m_sw_arr']/2)
        params['fg_inbuf_list']=[]
        params['fg_outbuf_list']=[]
        for m in sizedict['sarsamp']['m_inbuf_list']:
             params['fg_inbuf_list']+=[(m, m)]
        for m in sizedict['sarsamp']['m_outbuf_list']:
             params['fg_outbuf_list']+=[(m, m)]
        '''
    
    # create design module and run design method.
    print('designing module')
    dsn = prj.create_design_module(lib_name, cell_name)
    print('design parameters:\n%s' % pprint.pformat(params))
    dsn.design_specs(**params)

    # implement the design
    print('implementing design with library %s' % impl_lib)
    dsn.implement_design(impl_lib, top_cell_name=cell_name, erase=True)

