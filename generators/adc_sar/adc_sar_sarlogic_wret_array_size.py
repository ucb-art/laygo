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

load_from_file=True
save_to_file=True #update sizing yaml file
yamlfile_spec="adc_sar_spec.yaml"
yamlfile_size="adc_sar_size.yaml"
yamlfile_output="adc_sar_output.yaml"

sarret_m=1
sarret_fo=2
capdrv_m_max=8
k_upsize=1
if load_from_file==True:
    with open(yamlfile_spec, 'r') as stream:
        specdict = yaml.load(stream)
    with open(yamlfile_output, 'r') as stream:
        outdict = yaml.load(stream)
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    sarret_m=sizedict['sarret']['m']
    sarret_fo=sizedict['sarret']['fo']
    capdrv_m_max=max(sizedict['capdrv']['m_list'])
    k_upsize=outdict['sarabe']['k_upsize']

sarlogic_m=int(2**np.ceil(np.log2((capdrv_m_max+sarret_m)/4))*k_upsize) #4x fanout

if save_to_file==True:
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    sizedict['sarlogic']['m']=sarlogic_m
    with open(yamlfile_size, 'w') as stream:
        yaml.dump(sizedict, stream)

print('sarlogic size results - m:'+str(sarlogic_m))

