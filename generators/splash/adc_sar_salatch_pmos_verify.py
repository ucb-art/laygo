# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
import numpy as np
import yaml
import matplotlib.pyplot as plt

lib_name = 'adc_sar_templates'
cell_name = 'salatch_pmos'
impl_lib = 'adc_sar_generated'
#tb_lib = 'adc_sar_testbenches'
tb_cell = 'salatch_pmos_tb_tran'
tb_noise_cell = 'salatch_pmos_tb_trannoise'

#spec
cload=60e-15
vamp_tran=1e-3
vamp_noise=1e-3
vcm=0.15
vdd=0.8
#corners=['tt', 'ff', 'ss']
corners=['tt'] #, 'ff', 'ss']

verify_lvs = False
extracted_calibre = False
extracted_pvs = True
verify_tran = True
verify_noise = True

params = dict(
    lch=16e-9,
    pw=4,
    nw=4,
    m=8, #larger than 8, even number
    m_rst=4,
    m_rgnn=4,
    m_buf=8,
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
    vamp_tran=outdict['system']['v_bit']/2
    vamp_noise=outdict['system']['v_comp_noise']/2
    vincm=specdict['v_in_cm']
    vdd=specdict['vdd']
    params['m']=sizedict['salatch']['m']
    params['m_rst']=sizedict['salatch']['m_rst']
    params['m_rgnn']=sizedict['salatch']['m_rgnn']
    params['m_buf']=sizedict['salatch']['m_buf']
    params['lch']=sizedict['lch']
    params['pw']=sizedict['pw']
    params['nw']=sizedict['nw']
    params['device_intent']=sizedict['device_intent']

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
if verify_tran==True:
    #hotfix: remove orig_state
    prj.impl_db._eval_skill('delete_cellview( "%s" "%s" "%s" )' % (impl_lib, tb_cell, 'orig_state'))

    print('creating testbench %s__%s' % (impl_lib, tb_cell))
    tb_dsn = prj.create_design_module(lib_name, tb_cell)
    tb_dsn.design(**params)
    tb_dsn.implement_design(impl_lib, top_cell_name=tb_cell, erase=True)
    tb = prj.configure_testbench(impl_lib, tb_cell)
    tb.set_parameter('cload', cload)
    tb.set_parameter('vamp', vamp_tran)
    tb.set_parameter('vcm', vincm)
    tb.set_parameter('vdd', vdd)

    tb.set_simulation_environments(corners)

    tb.add_output("outdm_tran", """getData("/OUTDM" ?result 'tran)""")
    tb.add_output("clkb_tran", """getData("/CLKB" ?result 'tran)""")

    if extracted_calibre:
        tb.set_simulation_view(impl_lib, cell_name, 'calibre')
    if extracted_pvs:
        tb.set_simulation_view(impl_lib, cell_name, 'av_extracted')

    tb.update_testbench()

    print('running simulation')
    tb.run_simulation()

    print('loading results')
    results = bag.data.load_sim_results(tb.save_dir)

    vout = results["outdm_tran"]
    clkbout = results["clkb_tran"]
    tvec = results['time']
    plt.figure(1)
    plt.hold(True)
    if len(corners)==1:
        clkbout = [clkbout]
        vout = [vout]
    vvec = clkbout[0][:]
    plt.plot(tvec, vvec, label='clkb')
    for i, c in enumerate(corners):
        vvec = vout[i][:]
        plt.plot(tvec, vvec, label=c)
    plt.legend()
    plt.show(block=False)

    print('t_ckq:'+str(results['tckq']))
    print('q_samp_fF:'+str(results['q_samp_fF']))

    if save_to_file==True:
        with open(yamlfile_output, 'r') as stream:
            outdict = yaml.load(stream)
        if len(corners)==1:
            outdict['salatch']['t_ckq']=float(results['tckq'])
            outdict['salatch']['q_samp_fF']=float(results['q_samp_fF'])
            #outdict['scratch']['t_ckq'].append(float(results['tckq']))
            #outdict['scratch']['q_samp_fF'].append(float(results['q_samp_fF']))
        else:
            outdict['salatch']['t_ckq']=float(results['tckq'][0])
            outdict['salatch']['q_samp_fF']=float(results['q_samp_fF'][0])
            #outdict['scratch']['t_ckq'].append(float(results['tckq'][0]))
            #outdict['scratch']['q_samp_fF'].append(float(results['q_samp_fF'][0]))
        with open(yamlfile_output, 'w') as stream:
            yaml.dump(outdict, stream)

# transient noise test
if verify_noise==True:
    #hotfix: remove orig_state
    prj.impl_db._eval_skill('delete_cellview( "%s" "%s" "%s" )' % (impl_lib, tb_noise_cell, 'orig_state'))

    print('creating testbench %s__%s' % (impl_lib, tb_noise_cell))
    tb_noise_dsn = prj.create_design_module(lib_name, tb_noise_cell)
    tb_noise_dsn.design(**params)
    tb_noise_dsn.implement_design(impl_lib, top_cell_name=tb_noise_cell, erase=True)
    tb_noise = prj.configure_testbench(impl_lib, tb_noise_cell)
    tb_noise.set_parameter('cload', cload)
    tb_noise.set_parameter('vamp', vamp_noise)
    tb_noise.set_parameter('vcm', vincm)
    tb_noise.set_parameter('vdd', vdd)

    tb_noise.set_simulation_environments(corners)

    if extracted_calibre:
        tb_noise.set_simulation_view(impl_lib, cell_name, 'calibre')
    if extracted_pvs:
        tb_noise.set_simulation_view(impl_lib, cell_name, 'av_extracted')

    tb_noise.update_testbench()

    print('running simulation')
    tb_noise.run_simulation()

    print('loading results')
    results = bag.data.load_sim_results(tb_noise.save_dir)
    print('0/1 ratio (0.841 for 1sigma):'+str(results['zero_one_ratio']))
