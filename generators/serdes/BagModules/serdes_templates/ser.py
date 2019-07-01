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


yaml_file = pkg_resources.resource_filename(__name__, os.path.join('netlist_info', 'ser.yaml'))


# noinspection PyPep8Naming
class serdes_templates__ser(Module):
    """Module for library serdes_templates cell ser.

    Fill in high level description here.
    """

    def __init__(self, bag_config, parent=None, prj=None, **kwargs):
        Module.__init__(self, bag_config, yaml_file, parent=parent, prj=prj, **kwargs)

    def design(self, lch, pw, nw, num_ser=10, m_dff=1, m_latch=1, m_cbuf1=2, m_cbuf2=8, m_pbuf1=2, m_pbuf2=8, m_mux=2, m_out=2, device_intent='fast'):
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
        div_name_list=[]
        div_term_list=[]

        VSS_pin = 'VSS'
        VDD_pin = 'VDD'
        sub_ser = int(num_ser/2)

        for i in range(sub_ser-1):
            j=sub_ser-i-1
            EN_pin = 'p%dbuf'%j
            ENB_pin = 'p%dbufb'%j
            in_pin = 'in<%d>'%j
            FFO_pin = 'samp_p%d'%j
            pb1in_pin = 'p%d'%j
            pb2in_pin = 'p%di'%j
            pb3in_pin = 'p%dbuf'%j
            pb3out_pin = 'p%dbufb'%j
            FFDIVO_pin = 'p%d'%j
            if i==0:
                FFDIVI_pin = 'p0'
            else:
                FFDIVI_pin = 'p%d'%(j+1)

            mux_term_list.append({'I': FFO_pin, 'O':'outb', 'EN':EN_pin, 'ENB':ENB_pin, 'VSS':VSS_pin, 'VDD':VDD_pin})
            mux_name_list.append('ITINV%d'%j)
            FF_term_list.append({'I': in_pin, 'O':FFO_pin, 'CLK':'p0buf', 'VSS':VSS_pin, 'VDD':VDD_pin})
            FF_name_list.append('IFF%d'%j)
            pb3_term_list.append({'I': pb3in_pin, 'O':pb3out_pin, 'VSS':VSS_pin, 'VDD':VDD_pin})
            pb3_name_list.append('IP%dBUF3'%j)
            pb2_term_list.append({'I': pb2in_pin, 'O':pb3in_pin, 'VSS':VSS_pin, 'VDD':VDD_pin})
            pb2_name_list.append('IP%dBUF2'%j)
            pb1_term_list.append({'I': pb1in_pin, 'O':pb2in_pin, 'VSS':VSS_pin, 'VDD':VDD_pin})
            pb1_name_list.append('IP%dBUF1'%j)
            div_term_list.append({'I': FFDIVI_pin, 'O':FFDIVO_pin, 'CLK':'clk', 'ST':'VSS', 'RST':'RST', 'VSS':VSS_pin, 'VDD':VDD_pin})
            div_name_list.append('IDIV%d'%j)

        #print(term_list)
        #print(name_list)

        self.instances['IINVOUT'].design(lch=lch, pw=pw, nw=nw, m=m_out, device_intent=device_intent)   
        self.instances['ITINV0'].design(lch=lch, pw=pw, nw=nw, m=m_mux, device_intent=device_intent)   
        self.instances['ILATCH0'].design(lch=lch, pw=pw, nw=nw, m=m_latch, device_intent=device_intent)   
        self.instances['IFF0'].design(lch=lch, pw=pw, nw=nw, m=m_dff, device_intent=device_intent)   
        self.instances['IP0BUF3'].design(lch=lch, pw=pw, nw=nw, m=m_pbuf2, device_intent=device_intent)   
        self.instances['IP0BUF2'].design(lch=lch, pw=pw, nw=nw, m=m_pbuf2, device_intent=device_intent)   
        self.instances['IP0BUF1'].design(lch=lch, pw=pw, nw=nw, m=m_pbuf1, device_intent=device_intent)   
        self.instances['ICBUF1'].design(lch=lch, pw=pw, nw=nw, m=m_cbuf1, device_intent=device_intent)   
        self.instances['ICBUF2'].design(lch=lch, pw=pw, nw=nw, m=m_cbuf2, device_intent=device_intent)   
        self.instances['IDIV0'].design(lch=lch, pw=pw, nw=nw, m=m_dff, device_intent=device_intent)   
        self.instances['ISR'].design(lch=lch, pw=pw, nw=nw, m=2, device_intent=device_intent)   
        #self.instances['IOUT'].design(lch=lch, pw=pw, nw=nw, m=m_dff, device_intent=device_intent)   #dff
        #self.instances['IIN'].design(lch=lch, pw=pw, nw=nw, m=m_dff, device_intent=device_intent)   #dff
        #self.instances['IDIV'].design(lch=lch, pw=pw, nw=nw, m=m_dff, device_intent=device_intent)   #dff
        self.array_instance('ITINV1', mux_name_list, term_list=mux_term_list) 
        for inst in self.instances['ITINV1']:
            inst.design(lch=lch, pw=pw, nw=nw, m=m_mux, device_intent=device_intent)
        self.array_instance('IFF1', FF_name_list, term_list=FF_term_list) 
        for inst in self.instances['IFF1']:
            inst.design(lch=lch, pw=pw, nw=nw, m=m_dff, device_intent=device_intent)
        self.array_instance('IP1BUF3', pb3_name_list, term_list=pb3_term_list) 
        for inst in self.instances['IP1BUF3']:
            inst.design(lch=lch, pw=pw, nw=nw, m=m_pbuf2, device_intent=device_intent)
        self.array_instance('IP1BUF2', pb2_name_list, term_list=pb2_term_list) 
        for inst in self.instances['IP1BUF2']:
            inst.design(lch=lch, pw=pw, nw=nw, m=m_pbuf2, device_intent=device_intent)
        self.array_instance('IP1BUF1', pb1_name_list, term_list=pb1_term_list) 
        for inst in self.instances['IP1BUF1']:
            inst.design(lch=lch, pw=pw, nw=nw, m=m_pbuf1, device_intent=device_intent)
        self.array_instance('IDIV1', div_name_list, term_list=div_term_list) 
        for inst in self.instances['IDIV1']:
            inst.design(lch=lch, pw=pw, nw=nw, m=m_dff, device_intent=device_intent)

        #for inst in self.instances['I0']:
        #    inst.design(lch=lch, pw=pw, nw=nw, m_dff=m_dff, m_inv1=m_inv1, m_inv2=m_inv2,
        #        m_tgate=m_tgate, num_bits=num_bits, m_capsw=m_capsw, device_intent=device_intent)

        self.reconnect_instance_terminal('ISR', 'S', 'p1bufb')
        self.reconnect_instance_terminal('ISR', 'R', 'p'+str(int(sub_ser/2)+1)+'bufb')
        
        self.rename_pin('in<0>','in<%d:0>'%(sub_ser-1))

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
