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


yaml_file = pkg_resources.resource_filename(__name__, os.path.join('netlist_info', 'ser_3stage.yaml'))


# noinspection PyPep8Naming
class serdes_templates__ser_3stage(Module):
    """Module for library serdes_templates cell ser_3stage.

    Fill in high level description here.
    """

    def __init__(self, bag_config, parent=None, prj=None, **kwargs):
        Module.__init__(self, bag_config, yaml_file, parent=parent, prj=prj, **kwargs)

    def design(self, lch, pw, nw, num_ser=10, num_ser_3rd=4, m_dff=1, m_latch=1, m_cbuf1=2, m_cbuf2=8, m_pbuf1=2, m_pbuf2=8, m_mux=2, m_out=2, m_ser=1, device_intent='fast'):
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
        self.parameters['num_ser'] = num_ser
        self.parameters['num_ser_3rd'] = num_ser_3rd
        self.parameters['lch'] = lch
        self.parameters['pw'] = pw
        self.parameters['nw'] = nw
        self.parameters['m_dff'] = m_dff
        self.parameters['m_latch'] = m_latch
        self.parameters['m_cbuf1'] = m_cbuf1
        self.parameters['m_cbuf2'] = m_cbuf2
        self.parameters['m_pbuf1'] = m_pbuf1
        self.parameters['m_pbuf2'] = m_pbuf2
        self.parameters['m_mux'] = m_mux
        self.parameters['m_out'] = m_out
        self.parameters['m_ser'] = m_ser
        self.parameters['device_intent'] = device_intent

        mux_name_list=[]
        mux_term_list=[]
        FF_name_list=[]
        FF_term_list=[]
        pb3_name_list=[]
        pb3_term_list=[]
        pb2_name_list=[]
        pb2_term_list=[]
        pb1_name_list=[]
        pb1_term_list=[]
        ser_name_list=[]
        ser_term_list=[]

        VSS_pin = 'VSS'
        VDD_pin = 'VDD'
        sub_ser = int(num_ser/2)

        in_name=[]
        for i in range(num_ser):
            in1_name='in<%d>'%(num_ser*num_ser_3rd-1-i)
            for j in range((num_ser_3rd-1)*num_ser):
                if j%num_ser==i:
                    in1_name = in1_name+',in<%d>'%((num_ser_3rd-1)*num_ser-1-j)
            in_name.append(in1_name)

        for i in range(num_ser):
            j=num_ser-i-1
            in_pin = 'in<%d>'%j
            p1buf_pin = 'p1buf<%d>'%j
            ser_out = 'ser<%d>'%j

            ser_term_list.append({'in<%d:0>'%(num_ser_3rd-1): in_name[i], 'out':ser_out, 'clk_in':'divclk', 'RST':'RST', 'p1buf':p1buf_pin, 'VSS':VSS_pin, 'VDD':VDD_pin})
            ser_name_list.append('ISER%d'%j)

        self.instances['I0'].design(lch=lch, pw=pw, nw=nw, num_ser=num_ser, m_dff=m_dff, m_latch=m_latch, m_cbuf1=m_cbuf1, m_cbuf2=m_cbuf2, m_pbuf1=m_pbuf1, m_pbuf2=m_pbuf2, m_mux=m_mux, m_out=m_out, m_ser=m_ser, device_intent=device_intent)   

        self.array_instance('I1', ser_name_list, term_list=ser_term_list) 
        for inst in self.instances['I1']:
            inst.design(lch=lch, pw=pw, nw=nw, num_ser=num_ser_3rd*2, m_dff=m_dff, m_latch=m_latch, m_cbuf1=m_cbuf1, m_cbuf2=m_cbuf2, m_pbuf1=m_pbuf1, m_pbuf2=m_pbuf2, m_mux=m_mux, m_out=m_out, device_intent=device_intent)

        #for inst in self.instances['I0']:
        #    inst.design(lch=lch, pw=pw, nw=nw, m_dff=m_dff, m_inv1=m_inv1, m_inv2=m_inv2,
        #        m_tgate=m_tgate, num_bits=num_bits, m_capsw=m_capsw, device_intent=device_intent)


        self.reconnect_instance_terminal('I0', 'in<%d:0>'%(num_ser-1), 'ser<%d:0>'%(num_ser-1))
        
        self.rename_pin('in','in<%d:0>'%(num_ser*num_ser_3rd-1))

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
