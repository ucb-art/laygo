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


yaml_file = pkg_resources.resource_filename(__name__, os.path.join('netlist_info', 'pulse_gen.yaml'))


# noinspection PyPep8Naming
class adc_sar_templates__pulse_gen(Module):
    """Module for library adc_sar_templates cell pulse_gen.

    Fill in high level description here.
    """

    def __init__(self, bag_config, parent=None, prj=None, **kwargs):
        Module.__init__(self, bag_config, yaml_file, parent=parent, prj=prj, **kwargs)

    def design(self, lch, pw, nw, m_dl, m_xor, num_inv_dl, device_intent='fast'):
        """To be overridden by subclasses to design this m odule.

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
        self.parameters['m'] = m_dl
        self.parameters['m_xor'] = m_xor
        self.parameters['num_inv_dl'] = num_inv_dl
        self.parameters['device_intent'] = device_intent
        #XOR
        self.instances['XORNA'].design(w=nw, l=lch, nf=m_xor, intent=device_intent)
        self.instances['XORNAb0'].design(w=nw, l=lch, nf=m_xor, intent=device_intent)
        self.instances['XORNAb1'].design(w=nw, l=lch, nf=m_xor, intent=device_intent)
        self.instances['XORNAd'].design(w=nw, l=lch, nf=m_xor, intent=device_intent)
        self.instances['XORPA'].design(w=pw, l=lch, nf=m_xor, intent=device_intent)
        self.instances['XORPAb0'].design(w=pw, l=lch, nf=m_xor, intent=device_intent)
        self.instances['XORPAb1'].design(w=pw, l=lch, nf=m_xor, intent=device_intent)
        self.instances['XORPAd'].design(w=pw, l=lch, nf=m_xor, intent=device_intent)
        #BUF
        self.instances['IBUFN0'].design(w=nw, l=lch, nf=m_dl, intent=device_intent)
        self.instances['IBUFN1'].design(w=nw, l=lch, nf=m_dl, intent=device_intent)
        self.instances['IBUFP0'].design(w=pw, l=lch, nf=m_dl, intent=device_intent)
        self.instances['IBUFP1'].design(w=pw, l=lch, nf=m_dl, intent=device_intent)
        #array generation
        name_list_p=[]
        name_list_n=[]
        term_list=[]
        for i in range(num_inv_dl):
            if i==(num_inv_dl-1):
                term_list.append({'G': 'Ad%d'%(i), 
                          'D': 'Ad',
                         })
            elif i==0:
                term_list.append({'G': 'OA', 
                          'D': 'Ad%d'%(i+1),
                         })
            else:
                term_list.append({'G': 'Ad%d'%(i), 
                          'D': 'Ad%d'%(i+1),
                         })
            name_list_p.append('IDLP0%d'%(i))
            name_list_n.append('IDLN0%d'%(i))
        self.array_instance('IDLP0', name_list_p, term_list=term_list)
        self.array_instance('IDLN0', name_list_n, term_list=term_list)
        for i in range(num_inv_dl):
            self.instances['IDLP0'][i].design(w=pw, l=lch, nf=m_dl, intent=device_intent)
            self.instances['IDLN0'][i].design(w=pw, l=lch, nf=m_dl, intent=device_intent)

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
