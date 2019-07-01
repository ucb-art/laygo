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


yaml_file = pkg_resources.resource_filename(__name__, os.path.join('netlist_info', 'sarlogic_wret_v2_array_bb_pe.yaml'))


# noinspection PyPep8Naming
class adc_sar_templates__sarlogic_wret_v2_array_bb_pe(Module):
    """Module for library adc_sar_templates cell sarlogic_wret_v2_array_bb_pe.

    Fill in high level description here.
    """

    def __init__(self, bag_config, parent=None, prj=None, **kwargs):
        Module.__init__(self, bag_config, yaml_file, parent=parent, prj=prj, **kwargs)

    def design(self, lch, pw, nw, m, m_dl, m_xor, m_buf, num_bits, num_inv_dl, device_intent='fast'):
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
        self.parameters['m_dl'] = m_dl
        self.parameters['m_xor'] = m_xor
        self.parameters['m_buf'] = m_buf
        self.parameters['num_bits'] = num_bits
        self.parameters['num_inv_dl'] = num_inv_dl
        self.parameters['device_intent'] = device_intent
        #array generation
        name_list=[]
        term_list=[]
        for i in range(num_bits):
            term_list.append({'SB': 'SB<%d>'%(i), 
                              'ZP': 'ZP0<%d>'%(i),
                              'ZMID': 'ZMID0<%d>'%(i),
                              'ZM': 'ZM0<%d>'%(i),
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
        #Pulse generator
        term_list=[]
        for i in range(1):
            term_list.append({'A': 'ZM0<%d:0>'%(num_bits-1), 
                              'O': 'p_ZM0<%d:0>'%(num_bits-1),
                              'OA': 'd_ZM0<%d:0>'%(num_bits-1),
                             })
        self.array_instance('IPG0', ['IPG0<%d:0>'%(num_bits-1)], term_list=term_list)
        self.instances['IPG0'][0].design(lch=lch, pw=pw, nw=nw, m_dl=m_dl, m_xor=m_xor, num_inv_dl=num_inv_dl, device_intent=device_intent)
        term_list=[]
        for i in range(1):
            term_list.append({'A': 'ZP0<%d:0>'%(num_bits-1), 
                              'O': 'p_ZP0<%d:0>'%(num_bits-1),
                              'OA': 'd_ZP0<%d:0>'%(num_bits-1),
                             })
        self.array_instance('IPG1', ['IPG1<%d:0>'%(num_bits-1)], term_list=term_list)
        self.instances['IPG1'][0].design(lch=lch, pw=pw, nw=nw, m_dl=m_dl, m_xor=m_xor, num_inv_dl=num_inv_dl, device_intent=device_intent)
        term_list=[]
        for i in range(1):
            term_list.append({'A': 'ZMID0<%d:0>'%(num_bits-1), 
                              'O': 'p_ZMID0<%d:0>'%(num_bits-1),
                              'OA': 'd_ZMID0<%d:0>'%(num_bits-1),
                             })
        self.array_instance('IPG2', ['IPG2<%d:0>'%(num_bits-1)], term_list=term_list)
        self.instances['IPG2'][0].design(lch=lch, pw=pw, nw=nw, m_dl=m_dl, m_xor=m_xor, num_inv_dl=num_inv_dl, device_intent=device_intent)
        #NOR
        term_list=[]
        for i in range(1):
            term_list.append({'A': 'VSS,p_ZM0<%d:1>'%(num_bits-1), 
                              'B': 'd_ZM0<%d:0>'%(num_bits-1),
                             })
        self.array_instance('INOR0', ['INOR0<%d:0>'%(num_bits-1)], term_list=term_list)
        self.instances['INOR0'][0].design(lch=lch, pw=pw, nw=nw, m=2, device_intent=device_intent)
        term_list=[]
        for i in range(1):
            term_list.append({'A': 'VSS,p_ZP0<%d:1>'%(num_bits-1), 
                              'B': 'd_ZP0<%d:0>'%(num_bits-1),
                             })
        self.array_instance('INOR1', ['INOR1<%d:0>'%(num_bits-1)], term_list=term_list)
        self.instances['INOR1'][0].design(lch=lch, pw=pw, nw=nw, m=2, device_intent=device_intent)
        term_list=[]
        for i in range(1):
            term_list.append({'A': 'VSS,p_ZMID0<%d:1>'%(num_bits-1), 
                              'B': 'd_ZMID0<%d:0>'%(num_bits-1),
                             })
        self.array_instance('INOR2', ['INOR2<%d:0>'%(num_bits-1)], term_list=term_list)
        self.instances['INOR2'][0].design(lch=lch, pw=pw, nw=nw, m=2, device_intent=device_intent)
        #BUF
        term_list=[]
        for i in range(1):
            term_list.append({'O': 'ZM<%d:0>'%(num_bits-1), 
                             })
        self.array_instance('IBUF0', ['IBUF0<%d:0>'%(num_bits-1)], term_list=term_list)
        self.instances['IBUF0'][0].design(lch=lch, pw=pw, nw=nw, m=m_buf, device_intent=device_intent)
        term_list=[]
        for i in range(1):
            term_list.append({'O': 'ZP<%d:0>'%(num_bits-1), 
                             })
        self.array_instance('IBUF1', ['IBUF1<%d:0>'%(num_bits-1)], term_list=term_list)
        self.instances['IBUF1'][0].design(lch=lch, pw=pw, nw=nw, m=m_buf, device_intent=device_intent)
        term_list=[]
        for i in range(1):
            term_list.append({'O': 'ZMID<%d:0>'%(num_bits-1), 
                             })
        self.array_instance('IBUF2', ['IBUF2<%d:0>'%(num_bits-1)], term_list=term_list)
        self.instances['IBUF2'][0].design(lch=lch, pw=pw, nw=nw, m=m_buf, device_intent=device_intent)
        #self.instances['INOR0'].design(lch=lch, pw=pw, nw=nw, m=2, device_intent=device_intent)
        #self.instances['IBUF0'].design(lch=lch, pw=pw, nw=nw, m=m_buf, device_intent=device_intent)

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
