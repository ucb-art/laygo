#!/usr/bin/python
########################################################################################################################
#
# Copyright (c) 2014, Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#   disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#    following disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
########################################################################################################################

"""logic schematic template generation script"""
import pprint
import bag
#from six import iteritems

print('creating BAG project')
prj = bag.BagProject()

lib_name = 'logic_templates'
tech_lib = prj.bag_config['database']['schematic']['tech_lib']
impl_lib = tech_lib+'_logic_templates'

params = dict(lch=20e-9, pw=4, nw=4, device_intent='fast', m=1)

cell_name_dict={'tie':[2],
                'tie_wovdd':[2],
                'bcap':[4,8],
                'bcap2':[8],
                'dcap':[2,4,8],
                'dcap2':[4,8],
                'inv':[1,2,4,8,16,32],
                'tgate':[2,4,8],
                'nsw':[2,4,8,12,16],
                'nsw_wovdd':[2,4,8,12,16],
                'tinv':[1,2,4,8],
                'tinv_small':[1],
                'nand':[1,2,4,8,16],
                'nand_match': [2, 4, 8, 16],
                'nor':[2,4,8],
                'latch_2ck':[1,2,4,8],
                'latch_2ck_rstbh':[2,4],
                'dff':[1, 2, 4],
                'dff_rsth':[1, 2, 4],
                'oai22':[1],
                'oai22_skewed':[1],
                'mux2to1':[1,2,4,8],
                'ndsr':[1, 2],
               }

# create design module and run design method.
#for cell_name_prim, m_list in iteritems(cell_name_dict):
for cell_name_prim, m_list in cell_name_dict.items():
    for m in m_list:
        cell_name=cell_name_prim+'_'+str(m)+'x'
        print('logic primitive:'+cell_name)
        dsn = prj.create_design_module(lib_name, cell_name_prim)
        params['m']=m
        print('design parameters:\n%s' % pprint.pformat(params))
        dsn.design(**params)
    
        # implement the design
        print('implementing design with library %s' % impl_lib)
        dsn.implement_design(impl_lib, top_cell_name=cell_name, erase=True)





