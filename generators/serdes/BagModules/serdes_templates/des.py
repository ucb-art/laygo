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


yaml_file = pkg_resources.resource_filename(__name__, os.path.join('netlist_info', 'des.yaml'))


# noinspection PyPep8Naming
class serdes_templates__des(Module):
    """Module for library serdes_templates cell des.

    Fill in high level description here.
    """

    def __init__(self, bag_config, parent=None, prj=None, **kwargs):
        Module.__init__(self, bag_config, yaml_file, parent=parent, prj=prj, **kwargs)

    def design(self, lch, pw, nw, m_des_dff, clkbuf_list, divbuf_list, num_flop, num_des, ext_clk, device_intent='fast'):
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
        self.parameters['num_flop'] = num_flop
        self.parameters['num_des'] = num_des
        self.parameters['lch'] = lch
        self.parameters['pw'] = pw
        self.parameters['nw'] = nw
        self.parameters['m_des_dff'] = m_des_dff
        self.parameters['clkbuf_list'] = clkbuf_list
        self.parameters['divbuf_list'] = divbuf_list
        self.parameters['device_intent'] = device_intent
        m_cbuf1 = clkbuf_list[0]
        m_cbuf2 = clkbuf_list[1]
        m_cbuf3 = clkbuf_list[2]
        m_cbuf4 = clkbuf_list[3]
        m_dbuf1 = divbuf_list[0]
        m_dbuf2 = divbuf_list[1]
        m_dbuf3 = divbuf_list[2]
        m_dbuf4 = divbuf_list[3]

        out_name_list=[]
        out_term_list=[]
        in_name_list=[]
        in_term_list=[]
        div_name_list=[]
        div_term_list=[]

        VSS_pin = 'VSS'
        VDD_pin = 'VDD'

        for i in range(num_des):
            
            dout_pin = 'dout<%d>'%i

            d_pin = 'd<%d>'%i
            if i==0:
                in_pin = 'in'
            else:
                in_pin = 'd<%d>'%(i-1)

            divo_pin = 'div<%d>'%(num_des-i-1)
            if i==0:
                divi_pin = 'div<%d>'%i
            else:
                divi_pin = 'div<%d>'%(num_des-i)
            if i in range(int((num_des+1)/2)):
                ST_pin = 'VSS'
                RST_pin = 'RST'
            else:
                ST_pin = 'RST'
                RST_pin = 'VSS'

            out_term_list.append({'I': d_pin, 'O':dout_pin, 'CLK':'clk_div', 'VSS':VSS_pin, 'VDD':VDD_pin})
            out_name_list.append('IOUT%d'%i)
            in_term_list.append({'I': in_pin, 'O':d_pin, 'CLK':'clk_int', 'VSS':VSS_pin, 'VDD':VDD_pin})
            in_name_list.append('IIN%d'%i)
            if ext_clk==False:
                div_term_list.append({'I': divi_pin, 'O':divo_pin, 'CLK':'clk_int', 'ST':ST_pin, 'RST':RST_pin, 'VSS':VSS_pin, 'VDD':VDD_pin})
                self.remove_pin('div<0>')
            else:
                div_term_list.append({'I': 'VSS', 'O':'VSS', 'CLK':'VSS', 'ST':ST_pin, 'RST':RST_pin, 'VSS':VSS_pin, 'VDD':VDD_pin})
            div_name_list.append('IDIV%d'%i)

        #print(term_list)
        #print(name_list)

        self.instances['ICBUF1'].design(lch=lch, pw=pw, nw=nw, m=m_cbuf1, device_intent=device_intent)
        self.instances['ICBUF2'].design(lch=lch, pw=pw, nw=nw, m=m_cbuf2, device_intent=device_intent)   
        self.instances['ICBUF3'].design(lch=lch, pw=pw, nw=nw, m=m_cbuf3, device_intent=device_intent)   
        self.instances['ICBUF4'].design(lch=lch, pw=pw, nw=nw, m=m_cbuf4, device_intent=device_intent)   
        self.instances['IDBUF1'].design(lch=lch, pw=pw, nw=nw, m=m_dbuf1, device_intent=device_intent)   
        self.instances['IDBUF2'].design(lch=lch, pw=pw, nw=nw, m=m_dbuf2, device_intent=device_intent)   
        self.instances['IDBUF3'].design(lch=lch, pw=pw, nw=nw, m=m_dbuf3, device_intent=device_intent)   
        self.instances['IDBUF4'].design(lch=lch, pw=pw, nw=nw, m=m_dbuf4, device_intent=device_intent)   
        #self.instances['IOUT'].design(lch=lch, pw=pw, nw=nw, m=m_dff, device_intent=device_intent)   #dff
        #self.instances['IIN'].design(lch=lch, pw=pw, nw=nw, m=m_dff, device_intent=device_intent)   #dff
        #self.instances['IDIV'].design(lch=lch, pw=pw, nw=nw, m=m_dff, device_intent=device_intent)   #dff
        self.array_instance('IOUT', out_name_list, term_list=out_term_list) 
        for inst in self.instances['IOUT']:
            inst.design(lch=lch, pw=pw, nw=nw, m=m_des_dff, device_intent=device_intent)
        self.array_instance('IIN', in_name_list, term_list=in_term_list) 
        for inst in self.instances['IIN']:
            inst.design(lch=lch, pw=pw, nw=nw, m=m_des_dff, device_intent=device_intent)
        self.array_instance('IDIV', div_name_list, term_list=div_term_list) 
        for inst in self.instances['IDIV']:
            inst.design(lch=lch, pw=pw, nw=nw, m=m_des_dff, device_intent=device_intent)

        #for inst in self.instances['I0']:
        #    inst.design(lch=lch, pw=pw, nw=nw, m_dff=m_dff, m_inv1=m_inv1, m_inv2=m_inv2,
        #        m_tgate=m_tgate, num_bits=num_bits, m_capsw=m_capsw, device_intent=device_intent)

        #self.reconnect_instance_terminal('I0', 'CAL<%d:0>'%(num_bits-1), 'CAL<%d:0>'%(num_bits-1))
        
        self.rename_pin('dout','dout<%d:0>'%(num_des-1))
        self.rename_pin('dout','dout<%d:0>'%(num_des-1))

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
