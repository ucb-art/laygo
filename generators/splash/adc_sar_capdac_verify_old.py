# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
import numpy as np
import yaml
import matplotlib.pyplot as plt

lib_name = 'adc_sar_templates'
cell_name = 'capdac'
impl_lib = 'adc_sar_generated'
tester_cell_name = 'capdac_tester' #intermediate cell for programmable testbench generation
tb_lib = 'adc_sar_testbenches'
#tb_cell = 'capdac_8b_tb_tran'
tb_cell = 'capdac_tb_tran'

#spec
vh=0.3
vl=0.0
vcm=0.15
per=1e-9
num_bits=8

verify_lvs = False
extracted = False
verify_tran = True

load_from_file=True
yamlfile_spec="adc_sar_spec.yaml"
yamlfile_size="adc_sar_size.yaml"

if load_from_file==True:
    with open(yamlfile_spec, 'r') as stream:
        specdict = yaml.load(stream)
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    vh=specdict['v_in']
    vl=0.0
    vcm=specdict['v_in']/2
    num_bits=specdict['n_bit']-1

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

# transfer curve test
if verify_tran==True:
    # transient test
    print('creating testbench %s__%s' % (impl_lib, tb_cell))
    tb = prj.create_testbench(tb_lib, tb_cell, impl_lib, tester_cell_name, impl_lib)
    tb.set_parameter('pvh', vh)
    tb.set_parameter('pvl', vl)
    tb.set_parameter('pvcm', vcm)
    tb.set_parameter('pper', per)

    tb.set_simulation_environments(['tt'])
    tb.add_output("vout_tran", """getData("/O" ?result 'tran)""")

    if extracted:
        tb.set_simulation_view(impl_lib, cell_name, 'calibre')

    tb.update_testbench()

    print('running simulation')
    tb.run_simulation()

    print('loading results')
    results = bag.data.load_sim_results(tb.save_dir)
    vout = results["vout_tran"]

    #print('tckq:'+str(results['tckq']))
    #print('q_samp_fF:'+str(results['q_samp_fF']))
    tvec = results['time']
    vvec = vout[:]

    #plt.figure(1)
    #plt.plot(tvec, vvec)
    #plt.show(block=False)

    t_next=1.25*per
    code=0
    dac_v=[]
    dac_code=[]
    for i, t in enumerate(tvec):
        if t>t_next and code<2**num_bits: #256:
            t_next+=0.5*per
            #print(code, vvec[i])
            dac_code.append(code)
            dac_v.append(vvec[i])
            code+=1
    plt.figure(1)
    plt.plot(dac_code, dac_v)
    plt.show(block=False)
    plt.grid()
    plt.xlabel('code')
    plt.ylabel('v') 
