# -*- coding: utf-8 -*-

import pprint

import bag
import laygo
import numpy as np
import yaml
import matplotlib.pyplot as plt

cell_name = 'momcap_center_1x'
impl_lib = 'adc_sar_generated'

print('creating BAG project')
prj = bag.BagProject()

#lvs
# run lvs
print('running rcx')
rcx_passed, rcx_log = prj.run_rcx(impl_lib, cell_name)
if not rcx_passed:
    raise Exception('oops rcx died.  See RCX log file %s' % lvs_log)
print('rcx passed')

