# -*- coding: utf-8 -*-

import pprint

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

import bag
import bag.tech.mos

pmos_type='pch'
nmos_type='nch'
#env_list = ['tt', 'ff', 'ss', 'sf', 'fs', 'ff_hot', 'ss_hot']
env_list = ['tt']
l = 16e-9
intent = 'ulvt'
pw = 4
nw = 4
cl = 20e-15

vdd = 0.8
vincm = 0.2
vth = 0.3
vn_in = 0.000 #input noise stddev
gamma = 1 

mos_config = bag.BagProject().tech_info.tech_params['mos']
root_dir = mos_config['mos_char_root']
pmos_db = bag.tech.mos.MosCharDB(root_dir, pmos_type, ['intent', 'l'],
                                 env_list, intent=intent, l=l,
                                 method='spline')
nmos_db = bag.tech.mos.MosCharDB(root_dir, nmos_type, ['intent', 'l'],
                                 env_list, intent=intent, l=l,
                                 method='spline')

#multiplier
m = 8*2
m_sa = m
m_in = int(m_sa/2)
m_clkh = m_in
m_rstn = 1*2
m_buf=max(int(m_in-4*2), 1*2)
m_rgnn = m_in-2*m_rstn-m_buf
m_rgnp = m_rgnn+2*m_rstn-1*2
# clkh transistor
vbs = 0.0
vgs = -vdd
vds = -vdd/2
mclkh=pmos_db.query(w=pw, vbs=vbs, vgs=vgs, vds=vds)
# input transistor
vbs = 0.0
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
vgs = vdd
vds = vdd/2
mbufn=nmos_db.query(w=nw, vbs=vbs, vgs=vgs, vds=vds)
# buf_p transistor
vbs = 0.0
vgs = -vdd
vds = -vdd/2
mbufp=pmos_db.query(w=pw, vbs=vbs, vgs=vgs, vds=vds)
# resetn transistor
vbs = 0.0
vgs = 0.0
vds = vdd/2
mrstn=nmos_db.query(w=nw, vbs=vbs, vgs=vgs, vds=vds)

#timing calculation
# turn on time
#c=min0['cgs']*m_in+mclkh['cdb']*m_clkh
c=(min0['cgs']+min0['cds'])*m_in*2+mclkh['cdb']*m_clkh
ton=-c/mclkh['ids']/m_clkh*vth
print('ton:',ton)
# integration time
#c0=min0['cdb']*m_in+mrgnp['cgs']*m_rgnp
c0=min0['cdb']*m_in+(mrgnp['cgs']+mrgnp['cgd'])*m_rgnp+mrstn['cdb']*m_rstn
#c1=mrgnp['cdb']*m_rgnp+mrgnn['cdb']*m_rgnn+mbufn['cgs']*m_buf+mbufp['cgs']*m_buf
c1=(mrgnp['cdb']+mrgnp['cgs']+mrgnp['cds'])*m_rgnp+(mrgnn['cdb']+mrgnn['cgs']+mrgnn['cgd'])*m_rgnn+(mbufn['cgs']+mbufn['cgd'])*m_buf+(mbufp['cgs']+mbufp['cgd'])*m_buf+mrstn['cdb']*m_rstn
#tint=-c0/mclkh['ids']/m_clkh*vth*2-c0/mclkh['ids']/m_clkh*vth
tint=-c0/(mclkh['ids']/2)/m_clkh*vth*2-c1/(mclkh['ids']/2)/m_clkh*vth
print('tint:',tint)

# regeneration time
#c=mrgnp['cdb']*m_rgnp+mrgnn['cdb']*m_rgnn+mbufn['cgs']*m_buf+mbufp['cgs']*m_buf
trgn=c1/mrgnn['gm']/m_rgnn
print('trgn:',trgn)
print('c0:',c0)
print('c1:',c1)
print('cgs:',min0['cgs'])
print('cgsn:',mbufn['cgs'])
print('cgd:',min0['cgd'])
print('cgdn:',mbufn['cgd'])
print('cdb:',min0['cdb'])
print('w:',min0['w'])
print('vbs:',min0['vbs'])
print('vgs',min0['vgs'])
print('vds',min0['vds'])
print('ids',min0['ids'])
print('gm',min0['gm'])
'''
# buffer delay
c=cl+mbufn['cdb']*m_buf+mbufp['cdb']*m_buf
tbuf=c/mbufn['ids']/m_buf*vdd/2
print('tbuf:',tbuf)
tckq=ton+tint+trgn+tbuf
'''
tckq=ton+tint+trgn
print('tckq:',tckq)
#pprint.pprint(pmos_db.query(w=pw, vbs=vbs, vgs=vgs, vds=vds))

#noise calculation
kt=1.38*10e-23*300
vn_in_tot = (kt/gamma/(min0['gm']*m_in)**3*min0['gds']*c1/(tint**2)+vn_in**2)**0.5
#vn_in_tot = (kt*gamma/c1+vn_in**2)**0.5
print('vnin:',vn_in_tot)

#vbs = 0.0
#vgs = -0.4
#vds = -0.4
#pprint.pprint(nmos_db.query(w=w, vbs=vbs, vgs=vgs, vds=vds))

