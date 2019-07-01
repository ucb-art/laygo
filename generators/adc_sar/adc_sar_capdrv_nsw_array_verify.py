# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
import numpy as np
import yaml
import matplotlib.pyplot as plt

lib_name = 'adc_sar_templates'
cell_name = 'capdrv_nsw_array'
impl_lib = 'adc_sar_generated'
#tb_lib = 'adc_sar_testbenches'
tb_cell = 'capdrv_nsw_array_tb_tran'

#spec
trf=20e-12
vref2=0.3
vref1=0.15
vref0=0
vdd=0.8
#corners=['tt', 'ff', 'ss']
corners=['tt'] #, 'ff', 'ss']
cvec=np.array([1,2,4,8,16,32,64,128])*1e-15
verify_lvs = False
extracted_calibre = False
extracted_pvs = True
verify_tran = True

params = dict(
    lch=16e-9,
    pw=4,
    nw=4,
    num_bits=8,
    m_list=[2,2,2,2,2,2,4,8],
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
    fbw_target=specdict['fbw_samp']
    num_bits=specdict['n_bit']-1
    cvec=np.array(specdict['rdx_array'])*specdict['c_unit']*sizedict['capdac']['c_m']
    vref2=specdict['v_in_cm']*2
    vref1=specdict['v_in_cm']*1
    vref0=specdict['v_in_cm']*0
    params['num_bits']=num_bits
    params['m_list']=sizedict['capdrv']['m_list'] 
    params['lch']=sizedict['lch']
    params['pw']=sizedict['pw']
    params['nw']=sizedict['nw']
    params['cvec']=cvec
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
    tb.set_parameter('vref0', vref0)
    tb.set_parameter('vref1', vref1)
    tb.set_parameter('vref2', vref2)

    tb.set_simulation_environments(corners)
    tb.add_output("ven2", """getData("/EN<2>" ?result 'tran)""")
    for i in range(num_bits):
        tb.add_output("vo%d"%i, """getData("/VO<%d>" ?result 'tran)"""%i)
        measstr='delay(?wf1 VT("/EN<2>"), ?value1 VAR("vdd")/2, ?edge1 "either", ?nth1 1, ?td1 0.0, ?tol1 nil, ?wf2 VT("/VO<%d>"), ?value2 (VAR("vref1")+0.9*(VAR("vref2")-VAR("vref1"))), ?edge2 "either", ?nth2 1, ?tol2 nil,  ?td2 nil , ?stop nil, ?multiple nil)'%i #90% settling
        tb.add_output("delay%d"%i, measstr)

    if extracted_calibre:
        tb.set_simulation_view(impl_lib, cell_name, 'calibre')
    if extracted_pvs:
        tb.set_simulation_view(impl_lib, cell_name, 'av_extracted')

    tb.update_testbench()

    print('running simulation')
    tb.run_simulation()

    print('loading results')
    results = bag.data.load_sim_results(tb.save_dir)

    ven = results["ven2"]
    vo = results["vo%d"%(num_bits-1)]
    tvec = results['time']
    plt.figure(1)
    plt.hold(True)
    if len(corners)==1:
        ven = [ven]
        vo = [vo]
    for i, c in enumerate(corners):
        vvec = ven[i][:]
        plt.plot(tvec, vvec, label=c)
        vvec = vo[i][:]
        plt.plot(tvec, vvec, label=c)
    plt.legend()
    plt.show(block=False)

    print('tdelay:'+str(results['delay%d'%(num_bits-1)]))

    if save_to_file==True:
        with open(yamlfile_output, 'r') as stream:
            outdict = yaml.load(stream)
        if len(corners)==1:
            outdict['capdrv']['t_delay']=float(results['delay%d'%(num_bits-1)])
        else:
            outdict['capdrv']['t_delay']=float(results['delay%d'%(num_bits-1)][0])
        with open(yamlfile_output, 'w') as stream:
            yaml.dump(outdict, stream)

