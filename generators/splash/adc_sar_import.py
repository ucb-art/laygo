# -*- coding: utf-8 -*-
import bag, yaml

#adc template name
lib_name = 'adc_sar_templates'

prj = bag.BagProject()

print('importing library: %s' % lib_name)
prj.import_design_library(lib_name)
print('finish importing library %s.' % lib_name)
