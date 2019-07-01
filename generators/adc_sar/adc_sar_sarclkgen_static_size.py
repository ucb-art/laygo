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

num_bits=9
sarfsm_m=2
salatch_m=12
sarclkgen_fo=4
sarclkgen_m=2
sarclkgen_ndelay=1

if load_from_file==True:
    with open(yamlfile_spec, 'r') as stream:
        specdict = yaml.load(stream)
    with open(yamlfile_output, 'r') as stream:
        outdict = yaml.load(stream)
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    num_bits=specdict['n_bit']
    sarfsm_m=sizedict['sarfsm']['m']
    salatch_m=sizedict['salatch']['m']
mload1=int(salatch_m*2/2) #salatch clock load for sarclkb
mload2=int(sarfsm_m*num_bits) #fsm load for sarclk
mload=max(mload1, mload2)
m=int(2**np.ceil(np.log2(18))/2)
sarclkgen_m=int(m/sarclkgen_fo/2)

if save_to_file==True:
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    sizedict['sarclkgen']['fo']=sarclkgen_fo
    sizedict['sarclkgen']['m']=sarclkgen_m
    with open(yamlfile_size, 'w') as stream:
        yaml.dump(sizedict, stream)

print('sarclkgen size results - m:'+str(sarclkgen_m)+' fo:'+str(sarclkgen_fo))

