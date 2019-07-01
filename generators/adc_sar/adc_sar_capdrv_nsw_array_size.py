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
m_list = [2,2,2,2,2,2,4,8]
num_bits = 8
m_min = 2
m_max = 8

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
    cmax=sizedict['capdac']['c_m']*(2**(specdict['n_bit']-1))*specdict['c_unit']/2
    vincm=specdict['v_in_cm']
    vdd=specdict['vdd']
    tdac_target=outdict['system']['t_dac']
    num_bits=specdict['n_bit']-1

mos_config = bag.BagProject().tech_info.tech_params['mos']
root_dir = mos_config['mos_char_root']
pmos_db = bag.tech.mos.MosCharDB(root_dir, pmos_type, ['intent', 'l'],
                                 env_list, intent=intent, l=l,
                                 method='spline')
nmos_db = bag.tech.mos.MosCharDB(root_dir, nmos_type, ['intent', 'l'],
                                 env_list, intent=intent, l=l,
                                 method='spline')

#calculate
# sw transistor
vbs = vincm
vgs = vdd-vincm
vds = vincm
mdrv = nmos_db.query(w=pw, vbs=vbs, vgs=vgs, vds=vds)

# parameter calculation
m0 = 2.3*cmax/(tdac_target*np.abs(mdrv['gds'])-2.3*mdrv['cdd']) #90% settling (+cal). Need to be updated if other settling target is needed
m0 = 2**(np.ceil(np.log2(m0)))
m_opt=min(max(m0, m_min), m_max)
c_in_opt=mdrv['cgg']*m_opt
m_iter=int(m_opt)
m_list_new=[]
for i in range(num_bits):
    m_list_new = [m_iter]+m_list_new
    m_iter=min(max(int(m_iter/2), m_min), m_max)
m_list = m_list_new

if save_to_file==True:
    with open(yamlfile_output, 'r') as stream:
        outdict = yaml.load(stream)
    outdict['capdrv']['c_in']=float(c_in_opt)
    with open(yamlfile_output, 'w') as stream:
        yaml.dump(outdict, stream)
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    sizedict['capdrv']['m_list']=m_list_new
    with open(yamlfile_size, 'w') as stream:
        yaml.dump(sizedict, stream)

print('capdrv size results - m_list:'+str(m_list_new))

