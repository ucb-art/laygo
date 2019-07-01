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
cl = 60e-15
m_list=[8, 12, 16]
m_buf_list=[6, 8, 10]
m_rgnn_list=[6, 8, 10]
m_rst_list=[4, 6, 8]

load_from_file=True
save_to_file=True #update sizing yaml file
estimate_cload=False #true if you want calculate the cload from previous sizing. 
yamlfile_spec="adc_sar_spec.yaml"
yamlfile_size="adc_sar_size.yaml"
yamlfile_output="adc_sar_output.yaml"

vdd = 0.8
vincm = 0.15
vth = 0.3
vregen_target = vdd*0.9 #target regeneration
tckq_target = 70e-12
vn_in = 0.000 #input noise stddev
gamma = 1 
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
    m_list=sizedict['salatch_preset']['m']
    m_buf_list=sizedict['salatch_preset']['m_buf']
    m_rgnn_list=sizedict['salatch_preset']['m_rgnn']
    m_rst_list=sizedict['salatch_preset']['m_rst']
    vamp=outdict['system']['v_bit']/2
    vincm=specdict['v_in_cm']
    vdd=specdict['vdd']
    vregen_target = vdd*0.9
    tckq_target=outdict['system']['t_comp']
    vnin_target=outdict['system']['v_comp_noise']

mos_config = bag.BagProject().tech_info.tech_params['mos']
root_dir = mos_config['mos_char_root']
pmos_db = bag.tech.mos.MosCharDB(root_dir, pmos_type, ['intent', 'l'],
                                 env_list, intent=intent, l=l,
                                 method='spline')
nmos_db = bag.tech.mos.MosCharDB(root_dir, nmos_type, ['intent', 'l'],
                                 env_list, intent=intent, l=l,
                                 method='spline')
#results
res_dict=dict()
res_dict['con']=[]
res_dict['ion']=[]
res_dict['ton']=[]
res_dict['cint0']=[]
res_dict['cint1']=[]
res_dict['iint']=[]
res_dict['tint']=[]
res_dict['gm_rgn']=[]
res_dict['trgn']=[]
res_dict['cbuf']=[]
res_dict['ibuf']=[]
res_dict['tbuf']=[]
res_dict['tckq']=[]
res_dict['vnin']=[]
m_opt=m_list[-1]
m_buf_opt=m_buf_list[-1]
m_rgnn_opt=m_rgnn_list[-1]
m_rst_opt=m_rst_list[-1]

# input transistor
vbs = vdd*0.1 #heuristic from mclk
vgs = vincm-vdd
vds = vth-vdd
min0=pmos_db.query(w=pw, vbs=vbs, vgs=vgs, vds=vds)
# regen_p transistor
vbs = 0.0
vgs = -vdd/2
vds = -vdd/2
mrgnp=pmos_db.query(w=pw, vbs=vbs, vgs=vgs, vds=vds)
# regen_n transistor
vbs = 0.0
vgs = vdd/2
vds = vdd/2
mrgnn=nmos_db.query(w=nw, vbs=vbs, vgs=vgs, vds=vds)
# buf_n transistor
vbs = 0.0
vgs = vdd/2
vds = vdd/2
mbufn=nmos_db.query(w=nw, vbs=vbs, vgs=vgs, vds=vds)
# buf_p transistor
vbs = 0.0
vgs = -vdd/2
vds = -vdd/2
mbufp=pmos_db.query(w=pw, vbs=vbs, vgs=vgs, vds=vds)
# resetn transistor
vbs = 0.0
vgs = 0.0
vds = vdd/2
mrstn=nmos_db.query(w=nw, vbs=vbs, vgs=vgs, vds=vds)


for m, m_buf, m_rgnn, m_rst in zip(m_list, m_buf_list, m_rgnn_list, m_rst_list):
    #multiplier
    m_in = m #input pair
    m_clk = 2*max(2, m_in-2) #clock
    m_rstn = int(m_rst)
    m_buf= int(m_buf)
    m_rgnn = int(m_rgnn)
    m_rgnp = int(m_rgnn)+2*m_rstn-2
    # clk transistor
    vbs = 0.0
    vgs = -vdd
    vds = -vdd*0.1 #heuristic, does not affect the result much
    mclk=pmos_db.query(w=pw, vbs=vbs, vgs=vgs, vds=vds)
    
    #timing calculation
    # turn on time
    con=min0['css']*m_in*2+mclk['cdd']*m_clk 
    ion=np.abs(mclk['ids'])*m_clk
    ton=con/ion*vth
    # integration time
    cint0=min0['cdd']*m_in+(mrgnp['css']+mrgnp['cgs'])*m_rgnp+mrstn['cdd']*m_rstn
    cint1=(mrgnp['cdd']+mrgnp['cgg'])*m_rgnp+(mrgnn['cdd']+mrgnn['cgg'])*m_rgnn+(mbufn['cgg']+mbufp['cgg'])*m_buf+mrstn['cdd']*m_rstn
    iint=np.abs(mclk['ids'])*m_clk
    gmint=min0['gm']*m_in
    tint=cint0/iint*vth+cint1/iint*vth
    vint=gmint*tint/cint1*vamp
    # regeneration time
    gm_rgn=mrgnn['gm']*m_rgnn+mrgnp['gm']*m_rgnp
    trgn=2.3*cint1/gm_rgn*log10(vregen_target/vint)
    # buffer delay
    cbuf=mbufn['cdd']*m_buf+mbufp['cdd']*m_buf+cl
    ibuf=mbufn['ids']*m_buf
    tbuf=cbuf/ibuf*vdd/2

    #total delay
    tckq=ton+tint+trgn+tbuf
    
    #noise calculation
    kt=1.38*10e-23*300
    vn_in_tot = (kt/gamma/(min0['gm']*m_in)**3*min0['gds']*cint1/(tint**2)+vn_in**2)**0.5
    #vn_in_tot = (kt*gamma/c1+vn_in**2)**0.5
    #print('vnin:',vn_in_tot)

    res_dict['con'].append(con)
    res_dict['ion'].append(ion)
    res_dict['ton'].append(ton)
    res_dict['cint0'].append(cint0)
    res_dict['cint1'].append(cint1)
    res_dict['iint'].append(iint)
    res_dict['tint'].append(tint)
    res_dict['gm_rgn'].append(gm_rgn)
    res_dict['trgn'].append(trgn)
    res_dict['tbuf'].append(tbuf)
    res_dict['tckq'].append(tckq)
    res_dict['vnin'].append(vn_in_tot)
    
    if tckq < tckq_target and vn_in_tot < vnin_target: # meets specification
        if m < m_opt:
            m_opt=m
            m_buf_opt=m_buf
            m_rgnn_opt=m_rgnn
            m_rst_opt=m_rst 

c_in_opt=min0['cgg']*m_opt

if save_to_file==True:
    with open(yamlfile_output, 'r') as stream:
        outdict = yaml.load(stream)
    outdict['salatch']['c_in']=float(c_in_opt)
    with open(yamlfile_output, 'w') as stream:
        yaml.dump(outdict, stream)
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    sizedict['salatch']['m']=m_opt
    sizedict['salatch']['m_buf']=m_buf_opt
    sizedict['salatch']['m_rgnn']=m_rgnn_opt
    sizedict['salatch']['m_rst']=m_rst_opt
    with open(yamlfile_size, 'w') as stream:
        yaml.dump(sizedict, stream)

print('salatch size results - m:'+str(m_opt)+' m_rgnn:'+str(m_rgnn_opt)+' m_rst:'+str(m_rst_opt)+' m_buf:'+str(m_buf_opt))

