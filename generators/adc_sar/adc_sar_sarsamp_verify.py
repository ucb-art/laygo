# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
import numpy as np
import yaml
import matplotlib.pyplot as plt

lib_name = 'adc_sar_templates'
cell_name = 'sarsamp'
impl_lib = 'adc_sar_generated'
#tb_lib = 'adc_sar_testbenches'
tb_cell = 'sarsamp_tb_ac'
#tb_noise_cell = 'salatch_pmos_tb_trannoise'

#spec
cload=60e-15
cckload=60e-15
vcm=0.15
vdd=0.8
vck=0.8
#corners=['tt', 'ff', 'ss']
corners=['tt'] #, 'ff', 'ss']

verify_lvs = False
extracted_calibre = False
extracted_pvs = True
verify_ac = True
verify_noise = False

params = dict(
    lch=16e-9,
    pw=4,
    nw=4,
    m_sw=4,
    m_sw_arr=6,
    m_inbuf_list=[16, 24],
    m_outbuf_list=[8, 32],
    device_intent='fast',
    )

load_from_file=True
save_to_file=True
yamlfile_spec="adc_sar_spec.yaml"
#yamlfile_spec_output="adc_sar_spec_output.yaml"
yamlfile_size="adc_sar_size.yaml"
yamlfile_output="adc_sar_output.yaml"

if load_from_file==True:
    with open(yamlfile_spec, 'r') as stream:
        specdict = yaml.load(stream)
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    with open(yamlfile_output, 'r') as stream:
        outdict = yaml.load(stream)
    vincm=specdict['v_in_cm']
    vdd=specdict['vdd']
    vck=specdict['vdd']
    cload=sizedict['capdac']['c_m']*(2**(specdict['n_bit']-1))*specdict['c_unit']
    fbw_target=specdict['fbw_samp']
    params['m_sw']=sizedict['sarsamp']['m_sw']
    params['m_sw_arr']=sizedict['sarsamp']['m_sw_arr']
    params['m_inbuf_list']=sizedict['sarsamp']['m_inbuf_list']
    params['m_outbuf_list']=sizedict['sarsamp']['m_outbuf_list']
    params['lch']=sizedict['lch']
    params['pw']=sizedict['pw']
    params['nw']=sizedict['nw']
    params['device_intent']=sizedict['device_intent']
    params['tgate']=specdict['samp_with_tgate']

print('creating BAG project')
prj = bag.BagProject()

#lvs
if verify_lvs==True:
    # run lvs
    print('running lvs')
    lvs_passed, lvs_log = prj.run_lvs(impl_lib, cell_name)
    if not lvs_passed:
        raise Exception('oops lvs died.  See LVS log file %s' % lvs_log)
    print('lvs passed')

# transient test
if verify_ac==True:
    #hotfix: remove orig_state
    prj.impl_db._eval_skill('delete_cellview( "%s" "%s" "%s" )' % (impl_lib, tb_cell, 'orig_state'))

    print('creating testbench %s__%s' % (impl_lib, tb_cell))
    tb_dsn = prj.create_design_module(lib_name, tb_cell)
    tb_dsn.design(**params)
    tb_dsn.implement_design(impl_lib, top_cell_name=tb_cell, erase=True)
    tb = prj.configure_testbench(impl_lib, tb_cell)
    tb.set_parameter('cload', cload)
    tb.set_parameter('vck', vck)
    tb.set_parameter('vcm', vincm)
    tb.set_parameter('vdd', vdd)
    tb.set_parameter('fmax', fbw_target*20)

    tb.set_simulation_environments(corners)
    tb.add_output("outdm_ac", """getData("/OUTDM" ?result 'ac)""")

    if extracted_calibre:
        tb.set_simulation_view(impl_lib, cell_name, 'calibre')
    if extracted_pvs:
        tb.set_simulation_view(impl_lib, cell_name, 'av_extracted')

    tb.update_testbench()

    print('running simulation')
    tb.run_simulation()

    print('loading results')
    results = bag.data.load_sim_results(tb.save_dir)

    vout = results["outdm_ac"]
    fbw = results["fbw"]
    fvec = results['freq']
    plt.figure(1)
    plt.hold(True)
    if len(corners)==1:
        vout = [vout]
    for i, c in enumerate(corners):
        vvec = vout[i][:]
        plt.plot(fvec, vvec, label=c)
    plt.legend()
    plt.show(block=False)

    print('fbw:'+str(results['fbw']))

    if save_to_file==True:
        with open(yamlfile_output, 'r') as stream:
            outdict = yaml.load(stream)
        if len(corners)==1:
            outdict['sarsamp']['fbw']=float(results['fbw'])
        else:
            outdict['sarsamp']['fbw']=float(results['fbw'][0])
        with open(yamlfile_output, 'w') as stream:
            yaml.dump(outdict, stream)

