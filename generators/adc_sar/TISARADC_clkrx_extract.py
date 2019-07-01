# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
import numpy as np
import yaml

lib_name = 'adc_sar_templates'
cell_name = 'TISARADC_clkrx_0'
impl_lib = 'ADC_TOP_manual'

print('creating BAG project')
prj = bag.BagProject()

# run rcx
print('running rcx')
rcx_passed, rcx_log = prj.run_rcx(impl_lib, cell_name)
if not rcx_passed:
    raise Exception('oops rcx died.  See RCX log file %s' % rcx_log)
print('rcx passed')
