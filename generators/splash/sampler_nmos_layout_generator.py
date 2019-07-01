# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
# noinspection PyUnresolvedReferences,PyCompatibility
from builtins import *

import cProfile
import pprint
import yaml

import bag
from bag.layout import RoutingGrid, TemplateDB
from abs_templates_ec.adc_sar.sampler import NPassGateWClk
#from adc_sar.sampler import NPassGateWClk

#impl_lib = 'adc_sar_generated'
impl_lib = 'adc_sampler_ec'

if __name__ == '__main__':
    prj = bag.BagProject()
    lib_name = 'adc_ec_templates'
    cell_name = 'sampler_nmos'

    #params = dict(
    #    lch=16e-9,
    #    wp=8,
    #    wn=8,
    #    fgn=20,
    #    fg_inbuf_list=[(10, 10), (20, 20)],
    #    fg_outbuf_list=[(4, 4), (24, 24)],
    #    nduml=4,
    #    ndumr=6,
    #    nsep=2,
    #    intent='ulvt',
    #)
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
    layout_params = dict(
        ptap_w=10,
        ntap_w=10,
        pgr_w=5,
        ngr_w=5,
        num_track_sep=2,
        io_width=2,
        guard_ring_nf=2,
        tot_width=224,
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
        params['wp']=sizedict['pw']*2
        params['wn']=sizedict['nw']*2
        params['fgn']=int(sizedict['sarsamp']['m_sw']*sizedict['sarsamp']['m_sw_arr']/2)
        params['fg_inbuf_list']=[]
        params['fg_outbuf_list']=[]
        for m in sizedict['sarsamp']['m_inbuf_list']:
             params['fg_inbuf_list']+=[(m, m)]
        for m in sizedict['sarsamp']['m_outbuf_list']:
             params['fg_outbuf_list']+=[(m, m)]
    
    # template and grid information
    layers = [4, 5, 6, 7]
    spaces = [0.056, 0.100, 0.092, 0.100]
    widths = [0.040, 0.080, 0.100, 0.080]
    bot_dir = 'x'
    routing_grid = RoutingGrid(prj.tech_info, layers, spaces, widths, bot_dir)
    temp_db = TemplateDB('template_libs.def', routing_grid, impl_lib, use_cybagoa=True)

    # create design module and run design method.
    print('designing module')
    dsn = prj.create_design_module(lib_name, cell_name)
    print('design parameters:\n%s' % pprint.pformat(params))
    dsn.design_specs(**params)

    # implement the design
    print('implementing design with library %s' % impl_lib)
    dsn.implement_design(impl_lib, top_cell_name=cell_name, erase=True)

    # generate the layout
    layout_params = dsn.get_layout_params(**layout_params)
    pprint.pprint(layout_params)
    cProfile.runctx('temp_db.new_template(params=layout_params, temp_cls=NPassGateWClk, debug=False)',
                    globals(), locals(), filename='passgate_stats.data')
    temp = temp_db.new_template(params=layout_params, temp_cls=NPassGateWClk, debug=False)
    temp_db.batch_layout(prj, [temp], [cell_name], debug=True)
    #temp.write_summary_file('%s.yaml' % cell_name, impl_lib, cell_name)
    temp.write_summary_file('adc_sampler_ec.yaml', impl_lib, cell_name)
    ''' 
    #lvs
    print('running lvs')
    lvs_passed, lvs_log = prj.run_lvs(impl_lib, cell_name)
    if not lvs_passed:
        raise Exception('oops lvs died.  See LVS log file %s' % lvs_log)
    print('lvs passed')
    '''

