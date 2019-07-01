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

c_m=1
if load_from_file==True:
    with open(yamlfile_spec, 'r') as stream:
        specdict = yaml.load(stream)
    with open(yamlfile_output, 'r') as stream:
        outdict = yaml.load(stream)
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    c_m=outdict['system']['c_m']

if save_to_file==True:
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    sizedict['capdac']['c_m']=c_m
    with open(yamlfile_size, 'w') as stream:
        yaml.dump(sizedict, stream)

print('capdac size results - c_m:'+str(c_m))

