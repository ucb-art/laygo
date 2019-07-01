# -*- coding: utf-8 -*-

import pprint

import bag
import laygo
import numpy as np
import yaml
import matplotlib.pyplot as plt

lib_name = 'adc_sar_templates'
cell_name = 'capdac'
tb_cell = 'capdac_tb_tran'
tb_noise_cell = 'capdac_tb_noise'
impl_lib = 'adc_sar_generated'

#spec and parameters
vh=0.3
vl=0.0
vcm=0.15
per=1e-9
corners=['tt'] #, 'ff', 'ss']
params = dict(
    num_bits = 8,
    c_m = 1,
    rdx_array = [1, 2, 4, 8, 16, 32, 64, 128],
    )

extracted_calibre = True
extracted_pvs = False
verify_tran = True
verify_noise = False

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
    vh=specdict['v_in']
    vl=0.0
    vcm=specdict['v_in']/2
    fsamp=specdict['fsamp']
    params['num_bits']=specdict['n_bit']-1
    params['c_m']=sizedict['capdac']['c_m']
    params['rdx_array']=specdict['rdx_array']

print('creating BAG project')
prj = bag.BagProject()



# transfer curve test
if verify_tran==True:

    #hotfix: remove orig_state
    prj.impl_db._eval_skill('delete_cellview( "%s" "%s" "%s" )' % (impl_lib, tb_cell, 'orig_state'))

    print('creating testbench %s__%s' % (impl_lib, tb_cell))
    tb_dsn = prj.create_design_module(lib_name, tb_cell)
    tb_dsn.design(**params)
    tb_dsn.implement_design(impl_lib, top_cell_name=tb_cell, erase=True)
    tb = prj.configure_testbench(impl_lib, tb_cell)
    # transient test
    tb.set_parameter('pvh', vh)
    tb.set_parameter('pvl', vl)
    tb.set_parameter('pvcm', vcm)
    tb.set_parameter('pper', per)
    tb.set_parameter('tsim', per*2*(2**params['num_bits']))

    tb.set_simulation_environments(corners)
    tb.add_output("vout_tran", """getData("/O" ?result 'tran)""")

    if extracted_calibre:
        tb.set_simulation_view(impl_lib, cell_name, 'calibre')
    if extracted_pvs:
        tb.set_simulation_view(impl_lib, cell_name, 'av_extracted')

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
        if t>t_next and code<2**params['num_bits']: #256:
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

# noise test
if verify_noise==True:
    #hotfix: remove orig_state
    prj.impl_db._eval_skill('delete_cellview( "%s" "%s" "%s" )' % (impl_lib, tb_noise_cell, 'orig_state'))

    print('creating testbench %s__%s' % (impl_lib, tb_noise_cell))
    tb_noise_dsn = prj.create_design_module(lib_name, tb_noise_cell)
    tb_noise_dsn.design(**params)
    tb_noise_dsn.implement_design(impl_lib, top_cell_name=tb_noise_cell, erase=True)
    tb_noise = prj.configure_testbench(impl_lib, tb_noise_cell)
    # transient test
    tb_noise.set_parameter('fsamp', fsamp)

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
    vnoise = results['Vnoise']
    print('vnoise:'+str(vnoise))

    if save_to_file==True:
        with open(yamlfile_output, 'r') as stream:
            outdict = yaml.load(stream)
        outdict['capdac']['vnoise']=float(vnoise)
        with open(yamlfile_output, 'w') as stream:
            yaml.dump(outdict, stream)

