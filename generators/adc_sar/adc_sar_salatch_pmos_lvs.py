# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
import numpy as np
import yaml

cell_name = 'salatch_pmos'
cell_name_standalone = 'salatch_pmos_standalone'
impl_lib = 'adc_sar_generated'

print('creating BAG project')
prj = bag.BagProject()

#lvs
# run lvs
print('running lvs')
lvs_passed, lvs_log = prj.run_lvs(impl_lib, cell_name)
if not lvs_passed:
    raise Exception('oops lvs died.  See LVS log file %s' % lvs_log)
print('lvs passed')

'''
lvs_passed, lvs_log = prj.run_lvs(impl_lib, cell_name_standalone)
if not lvs_passed:
    raise Exception('oops lvs died.  See LVS log file %s' % lvs_log)
print('lvs passed')
'''
