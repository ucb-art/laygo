# -*- coding: utf-8 -*-
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

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
# noinspection PyUnresolvedReferences,PyCompatibility
from builtins import *

import os
import pkg_resources

from bag.design import Module


yaml_file = pkg_resources.resource_filename(__name__, os.path.join('netlist_info', 'sarlogic_wret_v2_array.yaml'))


# noinspection PyPep8Naming
class adc_sar_templates__sarlogic_wret_v2_array(Module):
    """Module for library adc_sar_templates cell sarlogic_wret_v2_array.

    Fill in high level description here.
    """

    def __init__(self, bag_config, parent=None, prj=None, **kwargs):
        Module.__init__(self, bag_config, yaml_file, parent=parent, prj=prj, **kwargs)

    def design(self, lch, pw, nw, m, num_inv_bb, num_bits, device_intent='fast'):
        """To be overridden by subclasses to design this module.

        This method should fill in values for all parameters in
        self.parameters.  To design instances of this module, you can
        call their design() method or any other ways you coded.

        To modify schematic structure, call:

        rename_pin()
        delete_instance()
        replace_instance_master()
        reconnect_instance_terminal()
        restore_instance()
        array_instance()
        """
        self.parameters['lch'] = lch
        self.parameters['pw'] = pw
        self.parameters['nw'] = nw
        self.parameters['m'] = m
        self.parameters['num_inv_bb'] = num_inv_bb
        self.parameters['num_bits'] = num_bits
        self.parameters['device_intent'] = device_intent
        #array generation
        name_list=[]
        term_list=[]
        for i in range(num_bits):
            term_list.append({'SB': 'SB<%d>'%(i), 
                              'ZP': 'ZP<%d>'%(i),
                              'ZMID': 'ZMID<%d>'%(i),
                              'ZM': 'ZM<%d>'%(i),
                              'RETO': 'RETO<%d>'%(i),
                             })
            name_list.append('ISL%d'%(i))
        self.array_instance('ISL0', name_list, term_list=term_list)
        for i in range(num_bits):
            self.instances['ISL0'][i].design(lch=lch, pw=pw, nw=nw, m=m, device_intent=device_intent)

        self.rename_pin('SB<0>','SB<%d:0>'%(num_bits-1))
        self.rename_pin('ZP<0>','ZP<%d:0>'%(num_bits-1))
        self.rename_pin('ZMID<0>','ZMID<%d:0>'%(num_bits-1))
        self.rename_pin('ZM<0>','ZM<%d:0>'%(num_bits-1))
        self.rename_pin('RETO<0>','RETO<%d:0>'%(num_bits-1))

        if num_inv_bb==0:
            self.delete_instance('IBUFP0')
            self.delete_instance('IBUFN0')
            self.delete_instance('IBUFP1')
            self.delete_instance('IBUFN1')
            self.delete_instance('IBUFP2')
            self.delete_instance('IBUFN2')

        else:
            name_list_p=[]
            name_list_n=[]
            term_list=[]
            for i in range(num_bits):
                for j in range(num_inv_bb):
                    if j==(num_inv_bb-1):
                        term_list.append({'G': 'ZP%d'%(j)+'<%d>'%(i),
                                  'D': 'ZP<%d>'%(i),
                                 })
                    else:
                        term_list.append({'G': 'ZP%d'%(j)+'<%d>'%(i),
                                  'D': 'ZP%d'%(j+1)+'<%d>'%(i),
                                 })
                    name_list_p.append('IBUFP0%d'%(j)+'<%d>'%(i))
                    name_list_n.append('IBUFN0%d'%(j)+'<%d>'%(i))
            self.array_instance('IBUFP0', name_list_p, term_list=term_list)
            self.array_instance('IBUFN0', name_list_n, term_list=term_list)
            for i in range(num_bits*num_inv_bb):
                self.instances['IBUFP0'][i].design(w=pw, l=lch, nf=m, intent=device_intent)
                self.instances['IBUFN0'][i].design(w=pw, l=lch, nf=m, intent=device_intent)
            name_list_p=[]
            name_list_n=[]
            term_list=[]
            for i in range(num_bits):
                for j in range(num_inv_bb):
                    if j==(num_inv_bb-1):
                        term_list.append({'G': 'ZMID%d'%(j)+'<%d>'%(i),
                                  'D': 'ZMID<%d>'%(i),
                                 })
                    else:
                        term_list.append({'G': 'ZMID%d'%(j)+'<%d>'%(i),
                                  'D': 'ZMID%d'%(j+1)+'<%d>'%(i),
                                 })
                    name_list_p.append('IBUFP1%d'%(j)+'<%d>'%(i))
                    name_list_n.append('IBUFN1%d'%(j)+'<%d>'%(i))
            self.array_instance('IBUFP1', name_list_p, term_list=term_list)
            self.array_instance('IBUFN1', name_list_n, term_list=term_list)
            for i in range(num_bits*num_inv_bb):
                self.instances['IBUFP1'][i].design(w=pw, l=lch, nf=m, intent=device_intent)
                self.instances['IBUFN1'][i].design(w=pw, l=lch, nf=m, intent=device_intent)
            name_list_p=[]
            name_list_n=[]
            term_list=[]
            for i in range(num_bits):
                for j in range(num_inv_bb):
                    if j==(num_inv_bb-1):
                        term_list.append({'G': 'ZM%d'%(j)+'<%d>'%(i),
                                  'D': 'ZM<%d>'%(i),
                                 })
                    else:
                        term_list.append({'G': 'ZM%d'%(j)+'<%d>'%(i),
                                  'D': 'ZM%d'%(j+1)+'<%d>'%(i),
                                 })
                    name_list_p.append('IBUFP2%d'%(j)+'<%d>'%(i))
                    name_list_n.append('IBUFN2%d'%(j)+'<%d>'%(i))
            self.array_instance('IBUFP2', name_list_p, term_list=term_list)
            self.array_instance('IBUFN2', name_list_n, term_list=term_list)
            for i in range(num_bits*num_inv_bb):
                self.instances['IBUFP2'][i].design(w=pw, l=lch, nf=m, intent=device_intent)
                self.instances['IBUFN2'][i].design(w=pw, l=lch, nf=m, intent=device_intent)
            self.add_pin('VBB', 'inputOutput')


    def get_layout_params(self, **kwargs):
        """Returns a dictionary with layout parameters.

        This method computes the layout parameters used to generate implementation's
        layout.  Subclasses should override this method if you need to run post-extraction
        layout.

        Parameters
        ----------
        kwargs :
            any extra parameters you need to generate the layout parameters dictionary.
            Usually you specify layout-specific parameters here, like metal layers of
            input/output, customizable wire sizes, and so on.

        Returns
        -------
        params : dict[str, any]
            the layout parameters dictionary.
        """
        return {}

    def get_layout_pin_mapping(self):
        """Returns the layout pin mapping dictionary.

        This method returns a dictionary used to rename the layout pins, in case they are different
        than the schematic pins.

        Returns
        -------
        pin_mapping : dict[str, str]
            a dictionary from layout pin names to schematic pin names.
        """
        return {}
