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


yaml_file = pkg_resources.resource_filename(__name__, os.path.join('netlist_info', 'sarsamp.yaml'))


# noinspection PyPep8Naming
class adc_sar_templates__sarsamp(Module):
    """Module for library adc_sar_templates cell sarsamp.

    Fill in high level description here.
    """

    def __init__(self, bag_config, parent=None, prj=None, **kwargs):
        Module.__init__(self, bag_config, yaml_file, parent=parent, prj=prj, **kwargs)

    def design(self, lch, pw, nw, m_sw, m_sw_arr, m_inbuf_list, m_outbuf_list, device_intent='fast'):
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
        self.parameters['m_sw'] = m_sw
        self.parameters['m_sw_arr'] = m_sw_arr
        self.parameters['m_inbuf_list'] = m_inbuf_list
        self.parameters['m_outbuf_list'] = m_outbuf_list
        self.parameters['device_intent'] = device_intent
        #switch
        self.array_instance('ISWP0', ['ISWP<%d:0>'%(m_sw_arr-1)])
        self.array_instance('ISWN0', ['ISWN<%d:0>'%(m_sw_arr-1)])
        for swp in self.instances['ISWP0']:
            swp.design(lch=lch, pw=pw, nw=nw, m=m_sw, device_intent=device_intent)
        for swn in self.instances['ISWN0']:
            swn.design(lch=lch, pw=pw, nw=nw, m=m_sw, device_intent=device_intent)
        #input buffer
        name_list=[]
        term_list=[]
        for i, m_in in enumerate(m_inbuf_list):
            in_pin = 'in_int<%d>'%(i-1)
            out_pin = 'in_int<%d>'%i
            term_list.append({'I': in_pin, 'O':out_pin})
            name_list.append('IBUFA%d'%i)
        term_list[0]['I']='ckin'
        term_list[-1]['O']='ckpg'
        self.array_instance('IBUFA0', name_list, term_list=term_list)
        for inst, m in zip(self.instances['IBUFA0'], m_inbuf_list):
            inst.design(lch=lch, pw=pw, nw=nw, m=m, device_intent=device_intent)

        #input buffer
        name_list=[]
        term_list=[]
        for i, m_in in enumerate(m_outbuf_list):
            in_pin = 'out_int<%d>'%(i-1)
            out_pin = 'out_int<%d>'%i
            term_list.append({'I': in_pin, 'O':out_pin})
            name_list.append('IBUFB%d'%i)
        term_list[0]['I']='ckpg'
        term_list[-1]['O']='ckout'
        self.array_instance('IBUFB0', name_list, term_list=term_list)
        for inst, m in zip(self.instances['IBUFB0'], m_outbuf_list):
            inst.design(lch=lch, pw=pw, nw=nw, m=m, device_intent=device_intent)

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
