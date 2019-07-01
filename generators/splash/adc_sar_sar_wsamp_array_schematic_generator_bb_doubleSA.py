# -*- coding: utf-8 -*-

import pprint

import bag
import numpy as np
import yaml

lib_name = 'adc_sar_templates'
cell_name = 'sar_wsamp_bb_doubleSA_array'
impl_lib = 'adc_sar_generated'

params = dict(
    sar_lch=16e-9,
    sar_pw=4,
    sar_nw=4,
    sar_sa_m=8,
    sar_sa_m_d=8,
    sar_sa_m_rst=4,
    sar_sa_m_rst_d=4,
    sar_sa_m_rgnn=4,
    sar_sa_m_rgnp_d=4,
    sar_sa_m_buf=8,
    sar_drv_m_list=[2,2,2,2,2,2,4,8],
    sar_ckgen_m=2, 
    sar_ckgen_fo=2, 
    sar_ckgen_ndelay=1, 
    sar_ckgen_fast=True, 
    sar_logic_m=1, 
    sar_fsm_m=1, 
    sar_ret_m=2, 
    sar_ret_fo=2, 
    sar_device_intent='fast',
    sar_c_m=1,
    sar_rdx_array=[1,2,4,8,16,32,64,128],
    samp_lch=16e-9,
    samp_wp=8,
    samp_wn=8,
    samp_fgn=12,
    samp_fg_inbuf_list=[(8, 8), (14, 14)],
    samp_fg_outbuf_list=[(4, 4), (24, 24)],
    samp_nduml=10,
    samp_ndumr=4,
    samp_nsep=2,
    samp_intent='ulvt',
    samp_use_laygo=False,
    use_offset=True,
    num_slices=8,
)
load_from_file=True
yamlfile_spec="adc_sar_spec.yaml"
yamlfile_size="adc_sar_size.yaml"
if load_from_file==True:
    with open(yamlfile_spec, 'r') as stream:
        specdict = yaml.load(stream)
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    params['sar_sa_m']=sizedict['salatch']['m']
    params['sar_sa_m_d']=sizedict['salatch']['m_d']
    params['sar_sa_m_rst']=sizedict['salatch']['m_rst']
    params['sar_sa_m_rst_d']=sizedict['salatch']['m_rst_d']
    params['sar_sa_m_rgnn']=sizedict['salatch']['m_rgnn']
    params['sar_sa_m_rgnp_d']=sizedict['salatch']['m_rgnp_d']
    params['sar_sa_m_buf']=sizedict['salatch']['m_buf']
    params['doubleSA']=sizedict['salatch']['doubleSA']
    params['vref_sf_m_mirror'] = sizedict['sourceFollower_vref']['m_mirror']
    params['vref_sf_m_bias'] = sizedict['sourceFollower_vref']['m_bias']
    params['vref_sf_m_off'] = sizedict['sourceFollower_vref']['m_off']
    params['vref_sf_m_in'] = sizedict['sourceFollower_vref']['m_in']
    params['vref_sf_m_bias_dum'] = sizedict['sourceFollower_vref']['m_bias_dum']
    params['vref_sf_m_in_dum'] = sizedict['sourceFollower_vref']['m_in_dum']
    params['vref_sf_m_byp'] = sizedict['sourceFollower_vref']['m_byp']
    params['vref_sf_m_byp_bias'] = sizedict['sourceFollower_vref']['m_byp_bias']
    params['vref_sf_bias_current'] = sizedict['sourceFollower_vref']['bias_current']
    params['vref_sf']=specdict['use_vref_sf']
    params['sar_drv_m_list']=sizedict['capdrv']['m_list']
    params['sar_logic_m']=sizedict['sarlogic']['m']
    params['num_inv_bb']=sizedict['sarlogic']['num_inv_bb']
    params['sar_fsm_m']=sizedict['sarfsm']['m']
    params['sar_ret_m']=sizedict['sarret']['m']
    params['sar_ret_fo']=sizedict['sarret']['fo']
    params['sar_ckgen_m']=sizedict['sarclkgen']['m']
    params['sar_ckgen_fo']=sizedict['sarclkgen']['fo']
    params['sar_ckgen_ndelay']=sizedict['sarclkgen']['ndelay']
    params['sar_ckgen_fast']=sizedict['sarclkgen']['fast']
    params['sar_ckgen_fastest']=sizedict['sarclkgen']['fastest']
    params['sar_c_m']=sizedict['capdac']['c_m']
    params['sar_rdx_array']=specdict['rdx_array']
    params['num_bits']=specdict['n_bit']
    params['samp_use_laygo']=specdict['samp_use_laygo']
    params['num_slices']=specdict['n_interleave']
    params['sar_lch']=sizedict['lch']
    params['sar_pw']=sizedict['pw']
    params['sar_nw']=sizedict['nw']
    params['sar_device_intent']=sizedict['device_intent']
    params['samp_lch']=sizedict['lch']
    #params['samp_pw']=sizedict['pw']
    #params['samp_nw']=sizedict['nw']
    params['samp_intent']=sizedict['device_intent']
    params['sf_lch'] = sizedict['lch']
    params['sf_nw'] = sizedict['nw']
    params['sf_m_mirror'] = sizedict['sourceFollower']['m_mirror']
    params['sf_m_bias'] = sizedict['sourceFollower']['m_bias']
    params['sf_m_in'] = sizedict['sourceFollower']['m_in']
    params['sf_m_off'] = sizedict['sourceFollower']['m_off']
    params['sf_m_bias_dum'] = sizedict['sourceFollower']['m_bias_dum']
    params['sf_m_in_dum'] = sizedict['sourceFollower']['m_in_dum']
    params['sf_m_byp'] = sizedict['sourceFollower']['m_byp']
    params['sf_m_byp_bias'] = sizedict['sourceFollower']['m_byp_bias']
    params['sf_intent'] = sizedict['device_intent']
    params['bias_current'] = sizedict['sourceFollower']['bias_current']
    params['use_sf'] = specdict['use_sf']
    params['use_offset']=sizedict['use_offset']

#sampler sizing
if params['samp_use_laygo']==True:
    params['samp_wp']=params['sar_pw']
    params['samp_wn']=params['sar_nw']
    params['samp_fgn']=sizedict['sarsamp']['m_sw_arr']
    params['samp_fg_inbuf_list']=sizedict['sarsamp']['m_inbuf_list']
    params['samp_fg_outbuf_list']=sizedict['sarsamp']['m_outbuf_list']
else:
    params['samp_wp']=params['sar_pw']
    params['samp_wn']=params['sar_nw']
    params['samp_fgn']=sizedict['sarsamp']['m_sw_arr']*sizedict['sarsamp']['m_sw']
    params['samp_fg_inbuf_list']=sizedict['sarsamp']['m_inbuf_list']
    params['samp_fg_outbuf_list']=sizedict['sarsamp']['m_outbuf_list']

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

