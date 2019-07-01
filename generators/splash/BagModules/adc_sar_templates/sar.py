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


yaml_file = pkg_resources.resource_filename(__name__, os.path.join('netlist_info', 'sar.yaml'))


# noinspection PyPep8Naming
class adc_sar_templates__sar(Module):
    """Module for library adc_sar_templates cell sar.

    Fill in high level description here.
    """

    def __init__(self, bag_config, parent=None, prj=None, **kwargs):
        Module.__init__(self, bag_config, yaml_file, parent=parent, prj=prj, **kwargs)

    def design(self, lch, pw, nw, sa_m, sa_m_rst, sa_m_rgnn, sa_m_buf, drv_m_list, ckgen_m, ckgen_fo, ckgen_ndelay, logic_m, fsm_m, ret_m, ret_fo, c_m, rdx_array, num_bits, device_intent):
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
        self.parameters['sa_m'] = sa_m
        self.parameters['sa_m_rst'] = sa_m_rst
        self.parameters['sa_m_rgnn'] = sa_m_rgnn
        self.parameters['sa_m_buf'] = sa_m_buf
        self.parameters['drv_m_list'] = drv_m_list
        self.parameters['ckgen_m'] = ckgen_m
        self.parameters['ckgen_fo'] = ckgen_fo
        self.parameters['ckgen_ndelay'] = ckgen_ndelay
        self.parameters['logic_m'] = logic_m
        self.parameters['fsm_m'] = fsm_m
        self.parameters['ret_m'] = ret_m
        self.parameters['ret_fo'] = ret_fo
        self.parameters['c_m'] = c_m
        self.parameters['rdx_array'] = rdx_array
        self.parameters['num_bits'] = num_bits
        self.parameters['device_intent'] = device_intent
        self.instances['IAFE0'].design(lch=lch, pw=pw, nw=nw, sa_m=sa_m, sa_m_rst=sa_m_rst, sa_m_rgnn=sa_m_rgnn, sa_m_buf=sa_m_buf, drv_m_list=drv_m_list, num_bits=num_bits-1, c_m=c_m, rdx_array=rdx_array, device_intent=device_intent)
        self.instances['IABE0'].design(lch=lch, pw=pw, nw=nw, ckgen_m=ckgen_m, ckgen_fo=ckgen_fo, ckgen_ndelay=ckgen_ndelay, logic_m=logic_m, fsm_m=fsm_m, ret_m=ret_m, ret_fo=ret_fo, num_bits=num_bits, device_intent=device_intent)
        #rewiring
        self.reconnect_instance_terminal(inst_name='IAFE0', term_name='VOL<%d:0>'%(num_bits-2), net_name='VOL<%d:0>'%(num_bits-2))
        self.reconnect_instance_terminal(inst_name='IAFE0', term_name='VOR<%d:0>'%(num_bits-2), net_name='VOR<%d:0>'%(num_bits-2))
        pin_enl_term=','.join(['ENL%d<2:0>'%(i) for i in range(num_bits-1)])
        pin_enr_term=','.join(['ENR%d<2:0>'%(i) for i in range(num_bits-1)])
        pin_enl=','.join(['ZM<%d>,ZMID<%d>,ZP<%d>'%(i,i,i) for i in range(1, num_bits)])
        pin_enr=','.join(['ZP<%d>,ZMID<%d>,ZM<%d>'%(i,i,i) for i in range(1, num_bits)])
        self.reconnect_instance_terminal(inst_name='IAFE0', term_name=pin_enl_term, net_name=pin_enl)
        self.reconnect_instance_terminal(inst_name='IAFE0', term_name=pin_enr_term, net_name=pin_enr)
        '''
        pin_enl=''
        pin_enr=''
        for i in range(1, num_bits):
            pin_enl=pin_enl+'ZM<%d>,ZMID<%d>,ZP<%d>'%(i,i,i)
            pin_enr=pin_enr+'ZP<%d>,ZMID<%d>,ZM<%d>'%(i,i,i)
            if i<num_bits-1:
                pin_enl=pin_enl+','
                pin_enr=pin_enr+','
        self.reconnect_instance_terminal(inst_name='IAFE0', term_name='ENL0<2:0>', net_name=pin_enl)
        self.reconnect_instance_terminal(inst_name='IAFE0', term_name='ENR0<2:0>', net_name=pin_enr)
        '''
        self.reconnect_instance_terminal(inst_name='IABE0', term_name='ZP<%d:0>'%(num_bits-1), net_name='ZP<%d:0>'%(num_bits-1))
        self.reconnect_instance_terminal(inst_name='IABE0', term_name='ZMID<%d:0>'%(num_bits-1), net_name='ZMID<%d:0>'%(num_bits-1))
        self.reconnect_instance_terminal(inst_name='IABE0', term_name='ZM<%d:0>'%(num_bits-1), net_name='ZM<%d:0>'%(num_bits-1))
        self.reconnect_instance_terminal(inst_name='IABE0', term_name='ADCOUT<%d:0>'%(num_bits-1), net_name='ADCOUT<%d:0>'%(num_bits-1))
        self.reconnect_instance_terminal(inst_name='IABE0', term_name='SB<%d:0>'%(num_bits-1), net_name='SB<%d:0>'%(num_bits-1))
        #rename pins
        self.rename_pin('VOL<0>', 'VOL<%d:0>'%(num_bits-2))
        self.rename_pin('VOR<0>', 'VOR<%d:0>'%(num_bits-2))
        self.rename_pin('ZM<0>', 'ZM<%d:0>'%(num_bits-1))
        self.rename_pin('ZMID<0>', 'ZMID<%d:0>'%(num_bits-1))
        self.rename_pin('ZP<0>', 'ZP<%d:0>'%(num_bits-1))
        self.rename_pin('SB<0>', 'SB<%d:0>'%(num_bits-1))
        self.rename_pin('ADCOUT<0>', 'ADCOUT<%d:0>'%(num_bits-1))


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
