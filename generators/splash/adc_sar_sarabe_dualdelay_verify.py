# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
import numpy as np
import yaml
import matplotlib.pyplot as plt

lib_name = 'adc_sar_templates'
cell_name = 'sarabe_dualdelay'
impl_lib = 'adc_sar_generated'
#tb_lib = 'adc_sar_testbenches'
tb_cell = 'sarabe_dualdelay_tb_tran'

#spec
trf=20e-12
vdd=0.8
cload=20e-15
#corners=['tt', 'ff', 'ss']
corners=['tt'] #, 'ff', 'ss']
verify_lvs = False
extracted_calibre = False
extracted_pvs = True
verify_tran = True

params = dict(
    lch=16e-9,
    pw=4,
    nw=4,
    num_bits=9,
    ckgen_m=2, 
    ckgen_fo=2,
    ckgen_ndelay=1, 
    logic_m=1, 
    fsm_m=1, 
    ret_m=2, 
    ret_fo=2, 
    device_intent='fast',
    )

load_from_file=True
save_to_file=True
yamlfile_spec="adc_sar_spec.yaml"
yamlfile_size="adc_sar_size.yaml"
yamlfile_output="adc_sar_output.yaml"

if load_from_file==True:
    with open(yamlfile_spec, 'r') as stream:
        specdict = yaml.load(stream)
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    with open(yamlfile_output, 'r') as stream:
        outdict = yaml.load(stream)
    trf=specdict['trf_fo4']
    vdd=specdict['vdd']
    cload=outdict['capdrv']['c_in']
    num_bits=specdict['n_bit']
    params['num_bits']=specdict['n_bit']
    params['ckgen_m']=sizedict['sarclkgen']['m']
    params['ckgen_fo']=sizedict['sarclkgen']['fo']
    params['ckgen_ndelay']=sizedict['sarclkgen']['ndelay']
    params['logic_m']=sizedict['sarlogic']['m']
    params['fsm_m']=sizedict['sarfsm']['m']
    params['ret_m']=sizedict['sarret']['m']
    params['ret_fo']=sizedict['sarret']['fo']
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
    #tb = prj.create_testbench(tb_lib, tb_cell, impl_lib, cell_name, impl_lib)
    tb_dsn = prj.create_design_module(lib_name, tb_cell)
    tb_dsn.design(**params)
    tb_dsn.implement_design(impl_lib, top_cell_name=tb_cell, erase=True)
    tb = prj.configure_testbench(impl_lib, tb_cell)
    tb.set_parameter('trf', trf)
    tb.set_parameter('vdd', vdd)
    tb.set_parameter('cload', cload)

    tb.set_simulation_environments(corners)
    tb.add_output("vsaom", """getData("/SAOM" ?result 'tran)""")
    tb.add_output("vzp", """getData("/ZP<%d>" ?result 'tran)"""%(num_bits-1))

    measstr='delay(?wf1 VT("/SAOM"), ?value1 VAR("vdd")/2, ?edge1 "either", ?nth1 1, ?td1 0.0, ?tol1 nil, ?wf2 VT("/ZP<%d>"), ?value2 VAR("vdd")/2, ?edge2 "either", ?nth2 1, ?tol2 nil,  ?td2 nil , ?stop nil, ?multiple nil)'%(num_bits-1)
    #print(measstr)
    tb.add_output('delay', measstr)

    if extracted_calibre:
        tb.set_simulation_view(impl_lib, cell_name, 'calibre')
    if extracted_pvs:
        tb.set_simulation_view(impl_lib, cell_name, 'av_extracted')

    tb.update_testbench()

    print('running simulation')
    tb.run_simulation()

    print('loading results')
    results = bag.data.load_sim_results(tb.save_dir)

    vsaom = results["vsaom"]
    vzp = results["vzp"]
    delay = results["delay"]
    tvec = results['time']
    plt.figure(1)
    plt.hold(True)
    if len(corners)==1:
        vsaom = [vsaom]
        vzp = [vzp]
    for i, c in enumerate(corners):
        vvec = vsaom[i][:]
        plt.plot(tvec, vvec, label=c)
        vvec = vzp[i][:]
        plt.plot(tvec, vvec, label=c)
    plt.legend()
    plt.show(block=False)

    print('tdelay:'+str(results['delay']))

    if save_to_file==True:
        with open(yamlfile_output, 'r') as stream:
            outdict = yaml.load(stream)
        if len(corners)==1:
            outdict['sarabe']['t_delay']=float(results['delay'])
        else:
            outdict['sarabe']['t_delay']=float(results['delay'][0])
        with open(yamlfile_output, 'w') as stream:
            yaml.dump(outdict, stream)

