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
#yamlfile_spec_output="adc_sar_spec_output.yaml"
yamlfile_size="adc_sar_size.yaml"
yamlfile_output="adc_sar_output.yaml"

adc_retimer_m = 2
if load_from_file==True:
    with open(yamlfile_spec, 'r') as stream:
        specdict = yaml.load(stream)
    with open(yamlfile_output, 'r') as stream:
        outdict = yaml.load(stream)
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    adc_retimer_m=sizedict['adc_retimer']['m']
sarret_m=1
sarret_fo=adc_retimer_m

if save_to_file==True:
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    sizedict['sarret']['m']=sarret_m
    sizedict['sarret']['fo']=sarret_fo
    with open(yamlfile_size, 'w') as stream:
        yaml.dump(sizedict, stream)

print('sarret size results - m:'+str(sarret_m)+', fo:'+str(sarret_fo))

