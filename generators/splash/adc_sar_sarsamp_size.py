# -*- coding: utf-8 -*-

import pprint

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from math import log10
import yaml

import bag
import bag.tech.mos

#parameters
pmos_type='pch'
nmos_type='nch'
#env_list = ['tt', 'ff', 'ss', 'sf', 'fs', 'ff_hot', 'ss_hot']
env_list = ['tt']
l = 16e-9
intent = 'ulvt'
pw = 4
nw = 4
csamp = 60e-15
m_sw = 4
m_sw_arr = 6
m_inbuf_list = [16, 24]
m_outbuf_list = [8, 32]
m_sw_list = [4, 4, 4, 4]
m_sw_arr_list = [2, 4, 8, 12]
m_inbuf_list_list = [[4, 6], [8, 12], [16, 24], [24, 36]]
m_outbuf_list_list = [[2, 8], [4, 16], [8, 32], [12, 48]]

load_from_file=True
save_to_file=True #update sizing yaml file
yamlfile_spec="adc_sar_spec.yaml"
#yamlfile_spec_output="adc_sar_spec_output.yaml"
yamlfile_size="adc_sar_size.yaml"
yamlfile_output="adc_sar_output.yaml"

vdd = 0.8
vincm = 0.15
if load_from_file==True:
    with open(yamlfile_spec, 'r') as stream:
        specdict = yaml.load(stream)
    with open(yamlfile_output, 'r') as stream:
        outdict = yaml.load(stream)
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    l=sizedict['lch']
    pw=sizedict['pw']
    nw=sizedict['nw']
    intent=sizedict['device_intent']
    csamp=sizedict['capdac']['c_m']*(2**(specdict['n_bit']-1))*specdict['c_unit']
    m_sw=sizedict['sarsamp']['m_sw']
    m_sw_arr=sizedict['sarsamp']['m_sw_arr']
    m_inbuf_list=sizedict['sarsamp']['m_inbuf_list']
    m_outbuf_list=sizedict['sarsamp']['m_outbuf_list']
    m_sw_list=sizedict['sarsamp_preset']['m_sw']
    m_sw_arr_list=sizedict['sarsamp_preset']['m_sw_arr']
    m_inbuf_list_list=sizedict['sarsamp_preset']['m_inbuf_list']
    m_outbuf_list_list=sizedict['sarsamp_preset']['m_outbuf_list']
    vincm=specdict['v_in_cm']
    vdd=specdict['vdd']
    fbw_target=specdict['fbw_samp']

mos_config = bag.BagProject().tech_info.tech_params['mos']
root_dir = mos_config['mos_char_root']
pmos_db = bag.tech.mos.MosCharDB(root_dir, pmos_type, ['intent', 'l'],
                                 env_list, intent=intent, l=l,
                                 method='spline')
nmos_db = bag.tech.mos.MosCharDB(root_dir, nmos_type, ['intent', 'l'],
                                 env_list, intent=intent, l=l,
                                 method='spline')
res_dict=dict()
res_dict['rsw']=[]
res_dict['ctot']=[]
res_dict['wbw']=[]
res_dict['fbw']=[]
m_sw_opt=m_sw_list[-1]
m_sw_arr_opt=m_sw_arr_list[-1]
m_inbuf_list_opt=m_inbuf_list_list[-1]
m_outbuf_list_list=m_outbuf_list_list[-1]

# sw transistor
vbs = vincm
vgs = vdd-vincm
vds = vincm
msw = nmos_db.query(w=pw, vbs=vbs, vgs=vgs, vds=vds)

#sweep and calculate
for m_sw, m_sw_arr in zip(m_sw_list, m_sw_arr_list):
    m=m_sw*m_sw_arr
    # parameter calculation
    ctot = msw['cdd']*m+csamp
    rsw = 1/msw['gds']/m
    wbw = 1/ctot/rsw
    fbw = wbw/6.28

    res_dict['rsw'].append(rsw)
    res_dict['ctot'].append(ctot)
    res_dict['wbw'].append(wbw)
    res_dict['fbw'].append(fbw)
 
    if fbw > fbw_target: # meets specification
        if m_sw*m_sw_arr < m_sw_opt*m_sw_arr_opt:
            m_sw_opt=m_sw
            m_sw_arr_opt=m_sw_arr

c_in_opt=0.5*(msw['cdd']+msw['css'])*m_sw_opt*m_sw_arr_opt
c_out_opt=0.5*(msw['cdd']+msw['css'])*m_sw_opt*m_sw_arr_opt
c_clk_opt=msw['cgg']*m_sw_opt*m_sw_arr_opt

if save_to_file==True:
    with open(yamlfile_output, 'r') as stream:
        outdict = yaml.load(stream)
    outdict['sarsamp']['c_in']=float(c_in_opt)
    outdict['sarsamp']['c_out']=float(c_in_opt)
    outdict['sarsamp']['c_clk']=float(c_in_opt)
    with open(yamlfile_output, 'w') as stream:
        yaml.dump(outdict, stream)
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    sizedict['sarsamp']['m_sw']=m_sw_opt
    sizedict['sarsamp']['m_sw_arr']=m_sw_arr_opt
    with open(yamlfile_size, 'w') as stream:
        yaml.dump(sizedict, stream)

print('sarsamp size results - m_sw:'+str(m_sw_opt)+' m_sw_arr:'+str(m_sw_arr_opt))

